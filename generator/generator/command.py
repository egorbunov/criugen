def setsid(pid):
    """
    setsid system call equivalent command
    """
    return {
        "#command": "SETSID",
        "pid": pid
    }


def fork_child(pid, child_pid, max_fd):
    """
    fork system call equivalent
    """
    return {
        "#command": "FORK_CHILD",
        "pid": pid,
        "child_pid": child_pid,
        "max_fd": max_fd
    }


def create_thread(pid, tid):
    """
    create thread command
    """
    return {
        "#command": "CREATE_THREAD",
        "pid": pid,
        "tid": tid
    }


def reg_open(pid, fd, reg_file):
    """
    regular file opening command
    """
    return {
        "#command": "REG_OPEN",
        "pid": pid,
        "path": reg_file.path,
        "flags": reg_file.flags,
        "mode": reg_file.mode,
        "offset": reg_file.pos,
        "fd": fd
    }


def close_fd(pid, fd):
    """
    close system call equivalent command
    """
    return {
        "#command": "CLOSE_FD",
        "pid": pid,
        "fd": fd
    }


def duplicate_fd(pid, old_fd, new_fd):
    """
    dup2 system call equivalent command
    """
    return {
        "#command": "DUP_FD",
        "pid": pid,
        "old_fd": old_fd,
        "new_fd": new_fd
    }


def fini_cmd(pid):
    """
    last command, sent to each interpreter (process), means, that
    there are no more commands for this pid to execute
    """
    return {
        "#command": "FINI_CMD",
        "pid": pid
    }


def register_vma(pid, vma_id, vma, fd=-1):
    """
    Command, which tells interpreter about vma in target process (just registering it)
    :param pid: process id
    :param vma_id: unique identifier of vma
    :type vma: crdata.VmArea
    :param vma: vma data structure
    :param fd: file descriptor in case this vma is backed by some file
    """
    return {
        "#command": "REGISTER_VMA",
        "pid": pid,
        "id": vma_id,
        "start": vma.start,
        "end": vma.end,
        "flags": list(vma.flags),
        "prot": list(vma.prot),
        "offset": vma.pgoff,
        "status": list(vma.status),
        "fd": fd,
        "fd_flags": vma.fdflags,
    }


def cleanup_restorer_vm(pid):
    """
    command, which tells interpreter to cleanup all it's own virtual
    memory mappings (interpreter will run special restorer executable in place, which
    do not collide with mappings of target process).
    """
    return {
        "#command": "CLEANUP_RESTORER_VM",  # like switching to special restorer context
        "pid": pid
    }


def map_vma(pid, vma_id, shmem_id=-1):
    """
    Command tells interpreter to create mapping (call mmap system call and all that),
    which was registered earlier with REGISTER_VMA command;
    """
    return {
        "#command": "MAP_VMA",
        "pid": pid,
        "id": vma_id,
        "shmem_id": shmem_id # > 0 in case if mapping is shared and anon (see create_shared_mem_file)
                             # TODO: is it the same as shmid field in crius VMA dump entry
    }


def unmap_vma(pid, vma_id):
    """
    Command to delete mapping from process (for example if it was inherited during forking, but
    not mapped in target child process)
    """
    return {
        "#command": "UNMAP_VMA",
        "pid": pid,
        "id": vma_id
    }


def create_shared_mem_file(pid, shmem_id):
    """
    Command, which tells interpreter to create anon shared file
    :param pid:
    :param shmem_id: id of the file to be created (to use it in futher commands)
    """
    return {
        "#command": "CREATE_SHARED_ANON_FILE",
        "pid": pid,
        "shmem_id": shmem_id
    }


def fill_vma_page(pid, vma_id, vma_pgoff, pagedump_pgoff):
    """
    Command, which tells interpreter to read page from page dump made by CRIU
    and fill one VMA page (vma is specified by vma_id) with it.
    :param pid: id of the target process
    :param vma_id: id of vma, which one page going to be filled
    :param vma_pgoff: offset (in pages) of the page to fill from VMA start
    :param pagedump_pgoff: offset (in pages) of the page to read from page dump (pages.img)
    """
    return {
        "#command": "FILL_VMA_PAGE",
        "pid": pid,
        "vma_id": vma_id,
        "vma_pgoff": vma_pgoff,
        "dump_pgoff": pagedump_pgoff
    }


def setup_vm_segments(pid, vm_info):
    """
    Command with data for setting up special memory areas starts and ends, like
    stack, heap and others
    :type pid: int
    :param pid: process, which must execute it

    :type vm_info: crdata.VmInfo
    :param vm_info: process virtual memory info structure
    :return:
    """
    return {
        "#command": "SETUP_SEGMENTS",
        "pid": pid,
        "arg_start": vm_info.arg_start,
        "arg_end": vm_info.arg_end,
        "brk": vm_info.brk,
        "env_start": vm_info.env_start,
        "env_end": vm_info.env_end,
        "code_start": vm_info.code_start,
        "code_end": vm_info.code_end,
        "data_start": vm_info.data_start,
        "data_end": vm_info.data_end,
        "brk_start": vm_info.brk_start,
        "stack_start": vm_info.stack_start,
        "exe_file_id": vm_info.exe_file_id,
        "saved_auxv": vm_info.saved_auxv
    }
