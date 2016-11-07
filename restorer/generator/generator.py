from collections import defaultdict
from copy import copy
import json
import functools

import nodes


class Cmd():
    @staticmethod
    def setsid(pid):
        return {
            "#command": "SETSID",
            "pid": pid
        }

    @staticmethod
    def fork_child(pid, child_pid, max_fd):
        return {
            "#command": "FORK_CHILD",
            "pid": pid,
            "child_pid": child_pid,
            "max_fd": max_fd
        }

    @staticmethod
    def create_thread(pid, tid):
        return {
            "#command": "CREATE_THREAD",
            "pid": pid,
            "tid": tid
        }

    @staticmethod
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

    @staticmethod
    def close_fd(pid, fd):
        return {
            "#command": "CLOSE_FD",
            "pid": pid,
            "fd": fd
        }

    @staticmethod
    def duplicate_fd(pid, old_fd, new_fd):
        return {
            "#command": "DUP_FD",
            "pid": pid,
            "old_fd": old_fd,
            "new_fd": new_fd
        }

    @staticmethod
    def fini_cmd(pid):
        return {
            "#command": "FINI_CMD",
            "pid": pid
        }


class ProgramBuilder:
    def write_program(self, app, program_path):
        program = self.generate_program(app)
        with open(program_path, "w") as out:
            json.dump(program, out, indent=4)

    @staticmethod
    def generate_program(app):
        """Generate program for interpreter to restore process tree
        """

        # For now program can be divided into parts, where each part is
        # list of consequent commands which must be executed within context
        # of one process. Such part starts with command FORK_CHILD or FORK_ROOT.
        # So every such part is corresponds to process with some PID. Parent
        # process commands are always placed above child process commands.

        programs = dict([(int(p.pid), []) for p in app.get_all_processes()])
        programs[app.get_root().pid] = list()

        def add_cmd(cmd):
            programs[int(cmd["pid"])].append(cmd)

        # ====== setsid root process ===== TODO: does is always makes sense?
        add_cmd(Cmd.setsid(app.get_real_root().pid));

        # ====== dealing with regular file descriptors =======
        def process_reg_files(process):
            parent = app.get_process_by_pid(process.ppid)

            # current file descriptor table (fdt) == fdt just after fork() or clone()
            # which is inherited from parent process
            cur_fdt = dict((fd, f) for fd, f in parent.fdt.iteritems()
                           if isinstance(f, nodes.RegularFile))
            # two file descriptor may point to one file instance actually, so this is
            # map from file to set of file descriptors pointing to it
            cur_files = dict((f, set(fds)) for f, fds in parent.file_map.iteritems()
                             if isinstance(f, nodes.RegularFile))

            def del_fd(fd):
                cur_files[cur_fdt[fd]].remove(fd)
                if not cur_files[cur_fdt[fd]]:
                    cur_files.pop(cur_fdt[fd])
                cur_fdt.pop(fd)

            def add_fd(fd, file):
                cur_fdt[fd] = file
                if file not in cur_files:
                    cur_files[file] = set()
                cur_files[file].add(fd)

            # TODO: refactor this duplicating code
            if process.fdt is None or len(process.fdt) == 0:
                free_fd = 3  # 3 beacuse 0, 1, 2 are may be used by std our err and in
            else:
                free_fd = max(process.fdt) + 1

            # creating temporary file links not to loose some files during fd fixing
            # we don't need to create such link to file if file is already opened at least at
            # one desired file descriptor
            # it can be avoided by implementing more complex algorithm, but simplicity
            # is better for now
            for f in cur_files:
                if f in process.file_map and not process.file_map[f].intersection(cur_files[f]):
                    add_cmd(Cmd.duplicate_fd(process.pid, next(iter(cur_files[f])), free_fd))
                    add_fd(free_fd, f)
                    free_fd += 1

            # fixing fds
            for fd, f in process.fdt.iteritems():
                if not isinstance(f, nodes.RegularFile):
                    continue

                # file is already opened at proper fd in parent process
                # so it will be inherited and ok
                if fd in cur_fdt and cur_fdt[fd] == f:
                    continue

                # fd is already taken in parent process but for another file (not f)
                if fd in cur_fdt and cur_fdt[fd] != f:
                    if f not in cur_files:
                        # f is not opened at all
                        add_cmd(Cmd.close_fd(process.pid, fd))
                        add_cmd(Cmd.reg_open(process.pid, fd, f))
                    else:
                        # f is opened but at another fd
                        ofd = next(iter(cur_files[f]))
                        add_cmd(Cmd.duplicate_fd(process.pid, ofd, fd))
                    del_fd(fd)
                    add_fd(fd, f)

                elif fd not in cur_fdt and process.fdt[fd] in cur_files:
                    ofd = next(iter(cur_files[f]))
                    add_cmd(Cmd.duplicate_fd(process.pid, ofd, fd))
                    add_fd(fd, f)

                elif fd not in cur_fdt and process.fdt[fd] not in cur_files:
                    add_cmd(Cmd.reg_open(process.pid, fd, f))
                    add_fd(fd, f)

            # closing everything not opened in cur proc
            # temporary file links are closed here too
            for fd, f in cur_fdt.iteritems():
                if fd not in process.fdt:
                    add_cmd(Cmd.close_fd(process.pid, fd))

        # ========= reg_files processing end =========

        for p in app.get_all_processes():
            process_reg_files(p)

        # adding child forking as last command to every process program
        def forks_dfs(process):
            max_fd = max(process.fdt) if process.fdt else 3  # TODO: refactor this duplicating code
            add_cmd(Cmd.fork_child(process.ppid, process.pid, max_fd))
            for ch in app.get_children(process):
                forks_dfs(ch)

        forks_dfs(app.get_real_root())

        # adding fini command
        for p in app.get_all_processes():
            add_cmd(Cmd.fini_cmd(p.pid))

        # concatenate per process programs into final one
        def concat_programs(process, program=None):
            if program is None:
                program = []
            program.extend(programs[process.pid])
            for ch in app.get_children(process):
                concat_programs(ch, program)
            return program

        return concat_programs(app.get_root())
