
from collections import defaultdict
from copy import copy
import json
import functools

import nodes


class ProgramBuilder():
    @staticmethod
    def _fork_root_cmd(pid):
        return {
            "command" : "FORK_ROOT",
            "pid"     : pid
        }

    @staticmethod
    def _fork_child_cmd(pid, child_pid):
        return {
            "command"   : "FORK_CHILD",
            "pid"       : pid,
            "child_pid" : child_pid
        }

    @staticmethod
    def _create_thread_cmd(pid, tid):
        return {
            "command" : "CREATE_THREAD",
            "pid"     : pid,
            "tid"     : tid
        }

    @staticmethod
    def _reg_open_cmd(pid, path, flags, mode, offset, fd):
        return {
            "command" : "REG_OPEN",
            "pid"     : pid,
            "path"    : path,
            "flags"   : flags,
            "mode"    : mode,
            "offset"  : offset,
            "fd"      : fd
        }

    @staticmethod
    def _close_fd_cmd(pid, fd):
        return {
            "command"   : "CLOSE_FD",
            "pid"       : pid,
            "fd"        : fd
        }

    @staticmethod
    def _move_fd_cmd(pid, old_fd, new_fd):
        return {
            "command"   : "MOVE_FD",
            "pid"       : pid,
            "old_fd"    : old_fd,
            "new_fd"    : new_fd
        }

    @staticmethod
    def _duplicate_fd_cmd(pid, old_fd, new_fd):
        return {
            "command"   : "DUP_FD",
            "pid"       : pid,
            "old_fd"    : old_fd,
            "new_fd"    : new_fd
        }

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
        # No optimizing reordering is supported for now.
        
        programs = dict([(p.pid, []) for p in app.get_all_processes()])

        def files_dfs(proc):
            parent_fdt = []
            if not app.is_root(proc):
                parent_fdt = app.get_process_by_pid(proc.ppid).descriptors


