import os
import json
import glob

import pycriu
import nodes


def load_img(img_path):
    with open(img_path, "r") as f:
        try:
            return pycriu.images.load(f, True)
        except pycriu.images.MagicException as exc:
            print("Incorrect magic in {}".format(img_path))
            return None


def load_json(img_path):
    with open(img_path, "r") as f:
        return json.load(f)


def load_item(source_path, item_name, item_type):
    loaders = {
        "img": load_img,
        "json": load_json
    }

    if item_type not in loaders:
        raise ValueError("Unknown item type {}".format(item_type))

    img_path = os.path.join(source_path, "{}.{}".format(item_name, item_type))
    if not os.path.isfile(img_path):
        return None
    return loaders[item_type](img_path)


def load(source_path, item_type):
    available_imgs = [os.path.splitext(os.path.basename(s))[0]
                      for s in glob.glob(os.path.join(source_path, "*.{}".format(item_type)))]

    processes = []
    files = {}

    def load_reg_files(img):
        file_paths = {}
        reg_files_item = load_item(source_path, img, item_type)
        for entry in reg_files_item["entries"]:
            if entry["name"] not in file_paths:
                file_paths[entry["name"]] = nodes.FilePath(entry["name"])
            if "size" not in entry:
                size = None
            else:
                size = entry["size"]
            flags = [s.strip() for s in entry["flags"].split("|")]
            rf = nodes.RegularFile(file_path=file_paths[entry["name"]],
                                   size=size,
                                   pos=entry["pos"],
                                   flags=flags,
                                   mode=entry["mode"])
            files[entry["id"]] = rf

    if "reg-files" in available_imgs:
        load_reg_files("reg-files")

    def load_pipes(img):
        pipes_item = load_item(source_path, img, item_type)
        for entry in pipes_item["entries"]:
            flags = [s.strip() for s in entry["flags"].split("|")]
            pf = nodes.PipeFile(pipe_id=entry["pipe_id"], flags=flags)
            files[entry["id"]] = pf

    if "pipes" in available_imgs:
        load_pipes("pipes")

    # reading every process specific data
    pstree_item = load_item(source_path, "pstree", item_type)
    for entry in pstree_item["entries"]:
        process = nodes.Process(pid=entry["pid"],
                                ppid=entry["ppid"])
        processes.append(process)
        for t in entry["threads"]:
            if t != 0:
                process.add_thread(t)

        core_item = load_item(source_path, "core-{}".format(entry["pid"]), item_type)
        core_entry = core_item["entries"][0]
        process.state = core_entry["tc"]["task_state"]
        # ids and mm (and ...) images are not stored for dead process
        if process.state == nodes.TaskState.DEAD:
            continue

        ids_item = load_item(source_path, "ids-{}".format(entry["pid"]), item_type)
        files_id = ids_item["entries"][0]["files_id"]

        # if no file descriptors fdinfo file is not created
        fd_info_item = load_item(source_path, "fdinfo-{}".format(files_id), item_type)
        if fd_info_item is not None:
            for fd_entry in fd_info_item["entries"]:
                process.add_file_descriptor(fd_entry["fd"], files[fd_entry["id"]])

        mm_item = load_item(source_path, "mm-{}".format(entry["pid"]), item_type)
        vma_items = mm_item["entries"][0]["vmas"]
        tmp_files = {}
        for vma_item in vma_items:
            flags = vma_item["flags"]
            if "MAP_PRIVATE" in flags:
                is_shared = False
            elif "MAP_SHARED" in flags:
                is_shared = True
            else:
                raise RuntimeError("Flags {} is not recoginzed".format(flags))
            is_anon = "MAP_ANON" in flags
            start = vma_item["start"]
            end = vma_item["end"]
            pgoff = vma_item["pgoff"]
            if is_anon and is_shared:
                shmid = vma_item["shmid"]
                if shmid not in tmp_files:
                    tmp_file = nodes.FilePath("/tmp/{}".format(vma_item["shmid"]))
                    tmp_files[shmid] = tmp_file
                vma = nodes.Vma(start, end, tmp_files[shmid], None, is_shared)
            elif not is_anon:
                shmid = vma_item["shmid"]
                vma = nodes.Vma(start, end, files[shmid].file_path, pgoff, is_shared)
            else:
                vma = nodes.Vma(start, end, None, None, is_shared)
            process.add_vma(vma)

    # assuming that processes in image are listed so child process always goes after parent
    root = next(p for p in processes if p.ppid == 0)
    app = nodes.Application(root)
    for p in processes:
        if p != root:
            app.add_process(p)
    return app


def load_from_jsons(source_path):
    return load(source_path, "json")


def load_from_imgs(source_path):
    return load(source_path, "img")
