import command
import crdata


def handle_regular_files(app):
    """
    Generates proper commands for processes in given application (process tree)
    to restore regular file descriptors table

    :type app: crdata.App
    :param app: application, for that commands will be generated
    :return: dictionary with structure: {pid: [command]}, i.e. for every pid
    you'll have list of commands
    """
    return {p.pid: __handle_regular_files_one_process(app, p) for p in app.processes}


def __handle_regular_files_one_process(app, process):
    """
    :type app: crdata.App
    :param app: application

    :type process: crdata.Process
    :param process: process, for which commands for regular files fdt restoration
    will be generated

    :return: list of commands
    """
    program = []
    parent = app.process_parent(process)

    # current file descriptor table (fdt) == fdt just after fork() or clone()
    # which is inherited from parent process
    cur_fdt = dict((fd, fid) for fd, fid in parent.fdt.iteritems()
                   if isinstance(app.file_by_id(fid), crdata.RegFile))
    # two file descriptor may point to one file instance actually, so this is
    # map from file to set of file descriptors pointing to it
    cur_files = dict(app.process_files(parent))

    def del_fd(fd):
        cur_files[cur_fdt[fd]].remove(fd)
        if not cur_files[cur_fdt[fd]]:
            cur_files.pop(cur_fdt[fd])
        cur_fdt.pop(fd)

    def add_fd(fd, fid):
        cur_fdt[fd] = fid
        if fid not in cur_files:
            cur_files[fid] = set()
        cur_files[fid].add(fd)

    # TODO: refactor this duplicating code
    if process.fdt is None or len(process.fdt) == 0:
        free_fd = 3  # 3 beacuse 0, 1, 2 are may be used by std out err and in
    else:
        free_fd = max(process.fdt) + 1

    # creating temporary file links not to loose some files during fd fixing
    # we don't need to create such link to file if file is already opened at least at
    # one desired file descriptor
    # it can be avoided by implementing more complex algorithm, but simplicity
    # is better for now
    goal_file_map = app.process_files(process)
    for f in cur_files:
        if f in goal_file_map and not goal_file_map[f].intersection(cur_files[f]):
            program.append(command.duplicate_fd(process.pid,
                                                next(iter(cur_files[f])),
                                                free_fd))
            add_fd(free_fd, f)
            free_fd += 1

    # fixing fds
    for fd, fid in process.fdt.iteritems():
        f = app.file_by_id(fid)
        if not isinstance(f, crdata.RegFile):
            continue

        # file is already opened at proper fd in parent process
        # so it will be inherited and ok
        if fd in cur_fdt and cur_fdt[fd] == fid:
            continue

        # fd is already taken in parent process but for another file (not f)
        if fd in cur_fdt and cur_fdt[fd] != fid:
            if fid not in cur_files:
                # f is not opened at all
                program.append(command.close_fd(process.pid, fd))
                program.append(command.reg_open(process.pid, fd, f))
            else:
                # f is opened but at another fd
                ofd = next(iter(cur_files[fid]))
                program.append(command.duplicate_fd(process.pid, ofd, fd))
            del_fd(fd)
            add_fd(fd, fid)

        elif fd not in cur_fdt and fid in cur_files:
            ofd = next(iter(cur_files[fid]))
            program.append(command.duplicate_fd(process.pid, ofd, fd))
            add_fd(fd, fid)

        elif fd not in cur_fdt and fid not in cur_files:
            program.append(command.reg_open(process.pid, fd, f))
            add_fd(fd, fid)

    # closing everything not opened in cur proc
    # temporary file links are closed here too
    for fd, fid in cur_fdt.iteritems():
        if fd not in process.fdt:
            program.append(command.close_fd(process.pid, fd))

    return program
