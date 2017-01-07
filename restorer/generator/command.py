def setsid(pid):
    return {
        "#command": "SETSID",
        "pid": pid
    }


def fork_child(pid, child_pid, max_fd):
    return {
        "#command": "FORK_CHILD",
        "pid": pid,
        "child_pid": child_pid,
        "max_fd": max_fd
    }


def create_thread(pid, tid):
    return {
        "#command": "CREATE_THREAD",
        "pid": pid,
        "tid": tid
    }


def reg_open(pid, fd, reg_file):
    return {
        "#command": "REG_OPEN",
        "pid": pid,
        "path": reg_file.file_path.path,
        "flags": reg_file.flags,
        "mode": reg_file.mode,
        "offset": reg_file.pos,
        "fd": fd
    }


def close_fd(pid, fd):
    return {
        "#command": "CLOSE_FD",
        "pid": pid,
        "fd": fd
    }


def duplicate_fd(pid, old_fd, new_fd):
    return {
        "#command": "DUP_FD",
        "pid": pid,
        "old_fd": old_fd,
        "new_fd": new_fd
    }


def fini_cmd(pid):
    return {
        "#command": "FINI_CMD",
        "pid": pid
    }
