import os
import json

import pycriu
import nodes

def load_img(imgs_folder, img_name):
    img_path = os.path.join(imgs_folder, img_name)
    with open(img_path, "r") as f:
        try:
            return pycriu.images.load(f, True)
        except pycriu.images.MagicException as exc:
            print("Incorrect magic in {}".format(img_path))
            return None


def load_item(source_path, item_name, item_type):
    if item_type == "json":
        item_path = os.path.join(source_path, "{}.json".format(item_name))
        with open(item_path, "r") as f:
            return json.load(f)
    elif item_type == "img":
        return load_img(source_path, "{}.img".format(item_name))
    raise ValueError("Unknown item_type: {}".format(item_type))


def load(source_path, item_type):
    processes = []
    pstree_item = load_item(source_path, "pstree", item_type)
    reg_files = {}
    file_paths = {}
    reg_files_item = load_item(source_path, "reg-files", item_type)
    for entry in reg_files_item["entries"]:
        if entry["name"] not in file_paths:
            file_paths[entry["name"]] = nodes.FilePath(entry["name"])
        if "size" not in entry:
            size = None
        else:
            size = entry["size"]
        rf = nodes.RegularFile(file_paths[entry["name"]], size, entry["pos"])
        reg_files[entry["id"]] = rf

    for entry in pstree_item["entries"]:
        process = nodes.Process(pid = entry["pid"],
                                ppid = entry["ppid"])
        processes.append(process)
        for t in entry["threads"]:
            if t != 0:
                process.add_thread(t)

        core_item = load_item(source_path, "core-{}".format(entry["pid"]), item_type)
        core_entry = core_item["entries"][0]
        process.state = core_entry["tc"]["task_state"]
        if process.state == nodes.TaskState.DEAD:
            continue

        ids_item = load_item(source_path, "ids-{}".format(entry["pid"]), item_type)
        files_id = ids_item["entries"][0]["files_id"]
        fd_info_item = load_item(source_path, "fdinfo-{}".format(files_id), item_type)  
        for fd_entry in fd_info_item["entries"]:
            fd = nodes.FileDescriptor(fd_entry["fd"], reg_files[fd_entry["id"]])
            process.add_file_descriptor(fd)

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
                vma = nodes.Vma(start, end, reg_files[shmid].file_path, pgoff, is_shared)
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
