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


def cleanup_restorer_vm(pid):
    """
    command, which tells interpreter to cleanup all it's own virtual
    memory mappings and run special restorer executable in place, which
    do not collide with mappings of target process (with pid `pid`).
    """
    return {
        "#command": "START_RESTORER_CTX",
        "pid": pid
    }

def