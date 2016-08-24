
from collections import defaultdict
from copy import copy
import json
import functools

import nodes

class Cmd():
    @staticmethod
    def fork_root(pid):
        return {
            "#command" : "FORK_ROOT",
            "pid"     : pid
        }

    @staticmethod
    def fork_child(pid, child_pid):
        return {
            "#command"   : "FORK_CHILD",
            "pid"       : pid,
            "child_pid" : child_pid
        }

    @staticmethod
    def create_thread(pid, tid):
        return {
            "#command" : "CREATE_THREAD",
            "pid"     : pid,
            "tid"     : tid
        }

    @staticmethod
    def reg_open(pid, fd, reg_file):
        return {
            "#command" : "REG_OPEN",
            "pid"     : pid,
            "path"    : reg_file.file_path.path,
            "flags"   : reg_file.flags,
            "mode"    : reg_file.mode,
            "offset"  : reg_file.pos,
            "fd"      : fd
        }

    @staticmethod
    def close_fd(pid, fd):
        return {
            "#command"   : "CLOSE_FD",
            "pid"       : pid,
            "fd"        : fd
        }

    @staticmethod
    def move_fd(pid, old_fd, new_fd):
        return {
            "#command"   : "MOVE_FD",
            "pid"       : pid,
            "old_fd"    : old_fd,
            "new_fd"    : new_fd
        }

    @staticmethod
    def duplicate_fd(pid, old_fd, new_fd):
        return {
            "#command"   : "DUP_FD",
            "pid"       : pid,
            "old_fd"    : old_fd,
            "new_fd"    : new_fd
        }


class ProgramBuilder():
    def write_program(self, app, program_path):
        program = self.generate_programm(app)
        with open(program_path, "w") as out:
            json.dump(program, out, indent=4)


    def generate_programm(self, app):
        """Generate program for interpreter to restore process tree
        """

        # For now program can be divided into parts, where each part is
        # list of consequent commands which must be executed within context
        # of one process. Such part starts with command FORK_CHILD or FORK_ROOT.
        # So every such part is corresponds to process with some PID. Parent
        # process commands are always placed above child process commands. 
        
        programs = dict([(p.pid, []) for p in app.get_all_processes()])

        def add_cmd(proc, cmd):
            programs[proc.pid].append(cmd)

        # every process starts it's life after fork
        def forks_dfs(proc):
            if app.is_root_proc(proc):
                add_cmd(proc, Cmd.fork_root(proc.pid))
            else:
                add_cmd(proc, Cmd.fork_child(proc.ppid, proc.pid))
            for ch in app.get_children(proc):
                forks_dfs(ch)

        forks_dfs(app.get_root_process())

        # ====== dealing with regular file descriptors =======
        def process_reg_files(proc):
            par = app.get_process_by_pid(proc.ppid)

            cur_fdt = dict((fd, file) for fd, file in par.fdt.iteritems() 
                                      if isinstance(file, nodes.RegularFile) )
            cur_files = dict((file, set(fds)) for file, fds in par.file_map.iteritems()
                                               if isinstance(file, nodes.RegularFile))

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

            # creating temporary file links not to loose some files during fd fixing
            # (which may happen during restore)
            # it can be avoided by implementing more complex algorithm, but simplicity
            # is better for now
            free_fd = max(proc.fdt) + 1 if proc.fdt else 3 # 3 beacuse 0, 1, 2 are for stds...
            for file in cur_files:
                if file in proc.file_map:
                    add_cmd(proc, Cmd.duplicate_fd(proc.pid, next(iter(cur_files[file])), free_fd))
                    cur_files[file].add(free_fd)
                    cur_fdt[free_fd] = file
                    free_fd += 1

            # fixing fds
            for fd, file in proc.fdt.iteritems():
                if not isinstance(file, nodes.RegularFile):
                    continue
                if fd in cur_fdt and cur_fdt[fd] == file:
                    continue

                if fd in cur_fdt and cur_fdt[fd] != file:
                    if file not in cur_files:
                        add_cmd(proc, Cmd.close_fd(proc.pid, fd))
                        add_cmd(proc, Cmd.reg_open(proc.pid, fd, file))
                    else:
                        ofd = next(iter(cur_files[file]))
                        add_cmd(proc, Cmd.duplicate_fd(proc.pid, ofd, fd))
                    del_fd(fd)
                    add_fd(fd, file)

                elif fd not in cur_fdt and proc.fdt[fd] in cur_files:
                    ofd = next(iter(cur_files[file]))
                    add_cmd(proc, Cmd.duplicate_fd(proc.pid, ofd, fd))
                    add_fd(fd, file)

                elif fd not in cur_fdt and proc.fdt[fd] not in cur_files:
                    add_cmd(proc, Cmd.reg_open(proc.pid, fd, file))
                    add_fd(fd, file)

            # closing everything not opened in cur proc
            for fd, file in cur_fdt.iteritems():
                if fd not in proc.fdt:
                    add_cmd(proc, Cmd.close_fd(proc.pid, fd))
        # ========= reg_files processing end =========

        for p in app.get_all_processes():
            process_reg_files(p)

        # concatenate per process programs into final one
        def concat_programs(proc, program = []):
            program.extend(programs[proc.pid])
            for ch in app.get_children(proc):
                concat_programs(ch, program)
            return program

        return concat_programs(app.get_root_process())



