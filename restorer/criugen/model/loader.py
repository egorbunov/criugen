import glob
import json
import os

import pycriu

import crconstants
import crdata
from resource_handles import *


def __load_img(img_path):
    with open(img_path, "r") as f:
        try:
            return pycriu.images.load(f, True)
        except pycriu.images.MagicException as exc:
            print("Incorrect magic in {}".format(img_path))
            return None


def __load_json(img_path):
    with open(img_path, "r") as f:
        return json.load(f)


def __load_item(source_path, item_name, item_type):
    loaders = {
        "img": __load_img,
        "json": __load_json
    }

    if item_type not in loaders:
        raise ValueError("Unknown item type {}".format(item_type))

    img_path = os.path.join(source_path, "{}.{}".format(item_name, item_type))
    if not os.path.isfile(img_path):
        return None
    return loaders[item_type](img_path)


def __parse_one_reg_file(entry):
    size = None if "size" not in entry else entry["size"]
    flags = [s.strip() for s in entry["flags"].split("|")]
    return crdata.RegFile(id=entry["id"],
                          path=entry["name"],
                          size=size,
                          pos=entry["pos"],
                          flags=flags,
                          mode=entry["mode"])


def __parse_reg_files(reg_files_item):
    """
    Parses reg-files image
    :param reg_files_item: item, loaded from reg-files image
    :return: dictionary of file ids pointing to crdata.RegFile structure
    """
    return {entry["id"]: __parse_one_reg_file(entry) for entry in reg_files_item["entries"]}


def __parse_one_pipe_file(entry):
    flags = [s.strip() for s in entry["flags"].split("|")]
    return crdata.PipeFile(id=entry["pipe_id"], flags=flags)


def __parse_pipe_files(pipe_files_item):
    """
    Parses pipes image
    :param pipe_files_item: item, loaded from pipes image
    :return: dictionary of file ids pointing to crdata.PipeFile structure
    """
    return {entry["id"]: __parse_one_pipe_file(entry) for entry in pipe_files_item["entries"]}


def __parse_one_vma(e):
    return crdata.VmArea(
        start=e['start'],
        end=e['end'],
        pgoff=e['pgoff'],
        shmid=e['shmid'],
        prot=set([s.strip() for s in e['prot'].split("|")]),
        flags=set([s.strip() for s in e['flags'].split("|")]),
        status=set([s.strip() for s in e['status'].split("|")]),
        fd=e['fd'],
        fdflags=e['fdflags'] if 'fdflags' in e else None
    )


def __parse_vm_info(e):
    return crdata.VmInfo(
        arg_start=e['mm_arg_start'],
        arg_end=e['mm_arg_end'],
        brk=e['mm_brk'],
        env_start=e['mm_env_start'],
        env_end=e['mm_env_end'],
        code_start=e['mm_start_code'],
        code_end=e['mm_end_code'],
        data_start=e['mm_start_data'],
        data_end=e['mm_end_data'],
        brk_start=e['mm_start_brk'],
        stack_start=e['mm_start_stack'],
        dumpable=e['dumpable'],
        exe_file_id=e['exe_file_id'],
        saved_auxv=e['mm_saved_auxv']
    )


def __parse_mm(mm_item):
    """
    :param mm_item: item loaded from mm-{pid} image
    :return: (VmInfo, array of VmArea)
    """
    vm_info = __parse_vm_info(mm_item['entries'][0])
    vmas = [(idx + 1, __parse_one_vma(e)) for idx, e in enumerate(mm_item['entries'][0]['vmas'])]
    return vm_info, vmas


def __parse_pagemap(pagemap_item):
    """
    :param pagemap_item: item loaded from pagemap-{pid} image or from pagemap-shmem-{shmid} image
    """
    return crdata.PageMap(
        pages_id=pagemap_item['entries'][0]['pages_id'],
        maps=pagemap_item['entries'][1:]
    )


def __parse_shared_anon_pagemaps(source_path, image_type):
    """
    Parses all image files with names `pagemap-shmem-{shmid}.{image_type}'
    :param source_path: root directory of dumped images
    :param image_type: type of image item (json or img)
    :return:
    """
    shmem_pagemaps = [os.path.splitext(os.path.basename(s))[0]
                      for s in glob.glob(os.path.join(source_path, "pagemap-shmem-*.{}".format(image_type)))]
    return shmem_pagemaps


def __parse_one_process(process_item, source_path, image_type):
    pid = process_item["pid"]
    ppid = process_item["ppid"]
    pgid = process_item["pgid"]
    sid = process_item["sid"]
    threads = process_item["threads"]

    core_item = __load_item(source_path, "core-{}".format(pid), image_type)

    p_state = core_item["entries"][0]["tc"]["task_state"]
    if p_state == crconstants.TASK_STATE_DEAD:
        # dead task (as I got it's a zombie) is empty one...
        return crdata.Process(pid=pid, ppid=ppid, pgid=pgid,
                              sid=sid, state=p_state, threads_ids=threads,
                              fdt={}, ids={}, vmas=[], vm_info={})

    ids_item = __load_item(source_path, "ids-{}".format(pid), image_type)
    ids = ids_item["entries"][0]

    # building file descriptor table
    p_fdt = {}
    fd_info_item = __load_item(source_path, "fdinfo-{}".format(ids["files_id"]), image_type)
    if fd_info_item is not None:
        p_fdt = {FileDescriptor(e["fd"]): e["id"] for e in fd_info_item["entries"]}

    mm_item = __load_item(source_path, "mm-{}".format(pid), image_type)
    p_vminfo, p_vmas = __parse_mm(mm_item)

    pagemap_item = __load_item(source_path, "pagemap-{}".format(pid), image_type)
    pagemap = __parse_pagemap(pagemap_item)

    sigacts_item = __load_item(source_path, "sigacts-{}".format(pid), image_type)
    fs_item = __load_item(source_path, "fs-{}".format(pid), image_type)

    return crdata.Process(pid=pid, ppid=ppid, pgid=pgid,
                          sid=sid, threads_ids=threads,
                          state=p_state, fdt=p_fdt, ids={}, vmas=p_vmas,
                          vm_info=p_vminfo, page_map=pagemap)


def __load_processes(source_path, image_type):
    """
    :return: list of parsed processes
    """
    processes_item = __load_item(source_path, "pstree", image_type)
    return [__parse_one_process(e, source_path, image_type)
            for e in processes_item["entries"]]


def load(source_path, image_type):
    """
    :param source_path: path to images
    :param image_type: image extension
    """
    available_imgs = [os.path.splitext(os.path.basename(s))[0]
                      for s in glob.glob(os.path.join(source_path, "*.{}".format(image_type)))]

    reg_files = {}
    if "reg-files" in available_imgs:
        reg_files_item = __load_item(source_path, "reg-files", image_type)
        reg_files = __parse_reg_files(reg_files_item)

    pipe_files = {}
    if "pipes" in available_imgs:
        item = __load_item(source_path, "pipes", image_type)
        pipe_files = __parse_pipe_files(item)

    files = dict(reg_files.items() + pipe_files.items())

    # reading every process specific data
    # pstree_item = __load_item(source_path, "pstree", image_type)
    processes = __load_processes(source_path, image_type)
    return crdata.App(processes, files)


def load_from_jsons(source_path):
    return load(source_path, "json")


def load_from_imgs(source_path):
    return load(source_path, "img")
