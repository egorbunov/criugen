import glob
import itertools
import json

import os
import pycriu

import crconstants
import crdata
# from resource_handles import *

# resource ids generator
__gen_resource_id = itertools.count()


def next_resource_id():
    """ generates new resource id
    :rtype: int
    """
    return next(__gen_resource_id)


def _load_img(img_path):
    with open(img_path, "r") as f:
        try:
            return pycriu.images.load(f, True)
        except pycriu.images.MagicException as exc:
            print("Incorrect magic in {}".format(img_path))
            return None


def _load_json(img_path):
    with open(img_path, "r") as f:
        return json.load(f)


def _load_item(source_path, item_name, item_type):
    loaders = {
        "img": _load_img,
        "json": _load_json
    }

    if item_type not in loaders:
        raise ValueError("Unknown item type {}".format(item_type))

    img_path = os.path.join(source_path, "{}.{}".format(item_name, item_type))
    if not os.path.isfile(img_path):
        return None
    return loaders[item_type](img_path)


def _parse_one_reg_file(entry):
    size = None if "size" not in entry else entry["size"]
    flags = [s.strip() for s in entry["flags"].split("|")]
    return crdata.RegFile(resource_id=next_resource_id(),
                          id=entry["id"],
                          path=entry["name"],
                          size=size,
                          pos=entry["pos"],
                          flags=flags,
                          mode=entry["mode"])


def _parse_one_pipe_file(entry):
    flags = [s.strip() for s in entry["flags"].split("|")]
    return crdata.PipeFile(
        resource_id=next_resource_id(),
        id=entry["pipe_id"],
        flags=flags
    )


def _parse_one_vma(e):
    return crdata.VmArea(
        resource_id=next_resource_id(),
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


def _parse_vm_info(e):
    return crdata.VmInfo(
        resource_id=next_resource_id(),
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


def _parse_pagemap(pagemap_item):
    """
    :param pagemap_item: item loaded from pagemap-{pid} image or from pagemap-shmem-{shmid} image
    """
    return crdata.PageMap(
        resource_id=next_resource_id(),
        pages_id=pagemap_item['entries'][0]['pages_id'],
        maps=pagemap_item['entries'][1:]
    )


def _parse_sigacts(sigact_item):
    """
    :param sigact_item: item loaded from sigacts-{pid} image 
    :return: array of sigaction descriptions
    :rtype: list[crdata.SignalAction]
    """
    return [
        crdata.SignalAction(
            resource_id=next_resource_id(),
            sigaction=e['sigaction'],
            flags=e['flags'],
            restorer=e['restorer'],
            mask=e['mask']
        )
        for e in sigact_item['entries']
    ]


def _parse_fs(fs_item):
    """
    :param fs_item: item loaded from fs-{pid} image
    :return: file system process properties
    :rtype: crdata.FSProps
    """
    return crdata.FSProps(
        resource_id=next_resource_id(),
        cwd_id=fs_item['entries'][0]['cwd_id'],
        root_id=fs_item['entries'][0]['root_id'],
        umask=fs_item['entries'][0]['umask']
    )


def _parse_task_core(core_item):
    """
    :param core_item: item, loaded from core-{pid}, where pid is not thread id, but
    process id, i.e. main thread id
    :return: task core object (tc item field)
    :rtype: crdata.ProcessCore
    """
    tc = core_item['entries'][0]['tc']
    return crdata.ProcessCore(
        resource_id=next_resource_id(),
        task_state=tc['task_state'],
        exit_code=tc['exit_code'],
        personality=tc['personality'],
        flags=tc['flags'],
        blk_sigset=tc['blk_sigset'],
        comm=tc['comm'],
        timers=tc['timers'],
        rlimits=tc['rlimits'],
        cg_set=tc['cg_set'],
        signals_s=tc['signals_s'],
        loginuid=tc['loginuid'],
        oom_score_adj=tc['oom_score_adj']
    )


def _parse_thread_core(core_item, thread_id):
    """
    :param core_item: item, loaded from core-{tid}, tid is a thread id
    :return: thread core object
    :rtype: crdata.ThreadCore
    """

    core = core_item['entries'][0]
    return crdata.ThreadCore(
        resource_id=next_resource_id(),
        thread_id=thread_id,
        mtype=core['mtype'],
        thread_info=core['thread_info'],
        thread_core=core['thread_core']
    )


def _parse_one_process(process_item, source_path, image_type):
    pid = process_item["pid"]
    ppid = process_item["ppid"]
    pgid = process_item["pgid"]
    sid = process_item["sid"]

    thread_ids = process_item["threads"]
    core_items = {tid: _load_item(source_path, "core-{}".format(tid), image_type)
                  for tid in thread_ids}

    process_core = _parse_task_core(core_items[pid])
    thread_cores = [_parse_thread_core(core_items[tid], tid) for tid in core_items]

    p_state = process_core.task_state
    if p_state == crconstants.TASK_STATE_DEAD:
        # dead task (as I got it's a zombie) is empty one...
        return crdata.Process(resource_id=next_resource_id(),
                              pid=pid, ppid=ppid, pgid=pgid,
                              sid=sid, thread_cores=[], core=None,
                              fdt={}, ids=None, vmas=[], vm_info=None, page_map=None)

    ids_item = _load_item(source_path, "ids-{}".format(pid), image_type)
    ids = ids_item["entries"][0]

    # building file descriptor table
    p_fdt = {}
    fd_info_item = _load_item(source_path, "fdinfo-{}".format(ids["files_id"]), image_type)
    if fd_info_item is not None:
        p_fdt = {e["fd"]: e["id"] for e in fd_info_item["entries"]}

    mm_item = _load_item(source_path, "mm-{}".format(pid), image_type)
    p_vminfo, p_vmas = _parse_mm(mm_item)

    pagemap_item = _load_item(source_path, "pagemap-{}".format(pid), image_type)
    pagemap = _parse_pagemap(pagemap_item)

    sigacts_item = _load_item(source_path, "sigacts-{}".format(pid), image_type)
    sigacts = _parse_sigacts(sigacts_item)

    fs_item = _load_item(source_path, "fs-{}".format(pid), image_type)
    fs_props = _parse_fs(fs_item)

    return crdata.Process(resource_id=next_resource_id(),
                          pid=pid,
                          ppid=ppid,
                          pgid=pgid,
                          sid=sid,
                          thread_cores=thread_cores,
                          core=process_core,
                          fdt=p_fdt,
                          ids={},
                          vmas=p_vmas,
                          vm_info=p_vminfo,
                          page_map=pagemap,
                          fs=fs_props,
                          sigact=sigacts)


def _parse_reg_files(reg_files_item):
    """
    Parses reg-files image
    :param reg_files_item: item, loaded from reg-files image
    :return: list of crdata.RegFile structures
    """
    return [_parse_one_reg_file(entry) for entry in reg_files_item["entries"]]


def _parse_pipe_files(pipe_files_item):
    """
    Parses pipes image
    :param pipe_files_item: item, loaded from pipes image
    :return: list of crdata.PipeFile structures
    """
    return [_parse_one_pipe_file(entry) for entry in pipe_files_item["entries"]]


def _parse_mm(mm_item):
    """
    :param mm_item: item loaded from mm-{pid} image
    :return: (VmInfo, array of VmArea)
    """
    vm_info = _parse_vm_info(mm_item['entries'][0])
    vmas = [_parse_one_vma(e) for e in mm_item['entries'][0]['vmas']]
    return vm_info, vmas


def _parse_shared_anon_pagemaps(source_path, image_type):
    """
    Parses all image files with names `pagemap-shmem-{shmid}.{image_type}'
    :param source_path: root directory of dumped images
    :param image_type: type of image item (json or img)
    :return: list of item names
    """
    shmem_pagemaps = [os.path.splitext(os.path.basename(s))[0]
                      for s in glob.glob(os.path.join(source_path, "pagemap-shmem-*.{}".format(image_type)))]
    return shmem_pagemaps


def _load_shared_anon_mems(source_path, image_type):
    """ Loads info about shared anon memory
    
    :param source_path: root directory of dumped images
    :param image_type: type of image items (json or img)
    :return: list of shared anon memory objects
    """
    image_names = _parse_shared_anon_pagemaps(source_path, image_type)

    shmems = []

    for img in image_names:
        shmid = img.split("-")[-1]
        pagemap_item = _load_item(source_path, img, image_type)
        pagemap = _parse_pagemap(pagemap_item)
        shmems.append(
            crdata.SharedAnonMem(
                resource_id=next_resource_id(),
                id=shmid, pagemap=pagemap)
        )

    return shmems


def _load_processes(source_path, image_type):
    """
    :return: list of parsed processes
    """
    processes_item = _load_item(source_path, "pstree", image_type)
    return [_parse_one_process(e, source_path, image_type)
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
        reg_files_item = _load_item(source_path, "reg-files", image_type)
        reg_files = _parse_reg_files(reg_files_item)

    pipe_files = {}
    if "pipes" in available_imgs:
        item = _load_item(source_path, "pipes", image_type)
        pipe_files = _parse_pipe_files(item)

    shared_anon_mem_list = _load_shared_anon_mems(source_path, image_type)

    # reading every process specific data
    processes = _load_processes(source_path, image_type)
    return crdata.Application(processes=processes,
                              regular_files=reg_files,
                              pipe_files=pipe_files,
                              shared_anon_mem=shared_anon_mem_list)


def load_from_jsons(source_path):
    return load(source_path, "json")


def load_from_imgs(source_path):
    return load(source_path, "img")
