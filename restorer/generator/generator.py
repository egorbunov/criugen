import command
import crdata
import itertools


def generate_program(app):
    """
    Generates and returns linearized program for process tree restoration
    :param app: application (instance of crdata.App)
    :return:
    """

    # For now program can be divided into parts, where each part is
    # list of consequent commands which must be executed within context
    # of one process. Such part starts with command FORK_CHILD or FORK_ROOT.
    # So every such part is corresponds to process with some PID. Parent
    # process commands are always placed above child process commands.

    setsid_cmds = __handle_sessions(app)
    reg_files_cmds = __handle_regular_files(app)
    forks_cmds = __handle_forks(app)
    final_programs = __join_programs(app, setsid_cmds, reg_files_cmds, forks_cmds)

    def concat_programs(process, program=None):
        if program is None:
            program = []
        program.extend(final_programs[process.pid])
        for ch in app.process_children(process):
            concat_programs(ch, program)
        return program

    return concat_programs(app.process_parent(app.root_process()))


def __join_programs(app, *args):
    pstree_pids = {p.pid for p in app.processes}
    all_pids = {0} | pstree_pids
    final = {pid: list(itertools.chain(*map(lambda x: x.get(pid, []), args)))
             for pid in all_pids}
    for p in pstree_pids:
        final[p].append(command.fini_cmd(p))
    return final


def __handle_regular_files(app):
    return {p.pid: __handle_regular_files_one_process(app, p) for p in app.processes}


def __handle_sessions(app):
    cmds = {}
    for p in app.processes:
        cmds[p.pid] = []
        if p.sid == p.pid:
            cmds[p.pid].append(command.setsid(p.pid))
    return cmds


def __handle_regular_files_one_process(app, process):
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


def __handle_forks(app):
    cmds = {}
    for p in app.processes:
        if p.ppid not in cmds:
            cmds[p.ppid] = []
        max_fd = max(p.fdt) if p.fdt else 3
        cmds[p.ppid].append(command.fork_child(p.ppid, p.pid, max_fd))
    return cmds


def __handle_vm(app):
    return {p.pid: [] for p in app.processes}
