
from collections import defaultdict
from copy import copy
import json

import nodes


class ProgramBuilder():
    def _fork_cmd(self, pid, child_pid):
        return {
            "command"   : "FORK",
            "pid"       : pid,
            "child_pid" : child_pid
        }

    def _reg_open_cmd(self, pid, path, flags, mode, offset, fd):
        return {
            "command" : "REG_OPEN",
            "pid"     : pid,
            "path"    : path,
            "flags"   : flags,
            "mode"    : mode,
            "offset"  : offset,
            "fd"      : fd
        }

    def _close_cmd(self, pid, fd):
        return {
            "command"   : "CLOSE",
            "pid"       : pid,
            "fd"        : fd
        }

    def _dup2_cmd(self, pid, old_fd, new_fd):
        return {
            "command"   : "DUP2",
            "pid"       : pid,
            "old_fd"    : old_fd,
            "new_fd"    : new_fd
        }

    def write_program(self, app, program_path):
        program = self.generate_programm(app)
        with open(program_path, "w") as out:
            json.dump(program, out, indent=4)

    def subtree_files(self, app):
        from_process_to_files = {}
        def traverse(current):
            result = set()
            current_files = app.get_regular_files_by_process(current)
            result.update(current_files)
            for child in app.get_children(current):
                files = traverse(child)
                result.update(files)
            from_process_to_files[current] = result
            return result
        traverse(app.get_root_process())
        return from_process_to_files

    def file_owner(self, app, rf, subtree_files):
        def traverse(current):
            if rf in app.get_regular_files_by_process(current):
                return current
            children = app.get_children(current)
            children = [c for c in children if rf in subtree_files[c]]
            if len(children) > 1:
                return current
            return traverse(children[0])
        return traverse(app.get_root_process())

    def owned_files_by_process(self, app):
        subtree_files = self.subtree_files(app)
        result = defaultdict(set)
        for rf in app.regular_files:
            owner = self.file_owner(app, rf, subtree_files)
            result[owner].add(rf)
        return result

    def get_free_fd(self, fd_to_file):
        if not fd_to_file:
            return 0
        else:
            return min(fd_to_file) + 1

    def generate_programm(self, app):
        self.program = []
        
        process_to_owned_files = self.owned_files_by_process(app)
        process_to_opened_files = {}
        root = app.get_root_process()

        def fork_traverse(current, fd_to_file):
            files = process_to_owned_files[current]
            for f in files:
                fd = self.get_free_fd(fd_to_file)
                self._add_open(current.pid, f.path, fd)
                self._add_lseek(current.pid, fd, f.pos)
                fd_to_file[fd] = f
            process_to_opened_files[current] = fd_to_file

            children = app.get_children(current)
            for child in children:
                self._add_fork(current.pid, child.pid)

            for child in children:
                fork_traverse(child, copy(fd_to_file))

        fork_traverse(root, {})

        def reorder_traverse(current):
            opened_files = process_to_opened_files[current]
            for fd, f in opened_files.items():
                if not f in app.get_regular_files_by_process(current):
                    self._add_close(current.pid, fd)
                    del opened_files[fd]
            
            for descriptor in current.descriptors:
                if descriptor.fd in opened_files:
                    free_fd = self.get_free_fd(opened_files)
                    self._add_dup2(current.pid, fd, free_fd)
                    opened_files[free_fd] = opened_files[fd]
                    self._add_close(current.pid, fd)
                    del opened_files[fd]
                
                r = [fd for fd, sf in opened_files.items() if sf == descriptor.struct_file]
                if not r:
                    raise RuntimeError("Error in generator algorithm.")
                
                self._add_dup2(current.pid, r[0], descriptor.fd)
                opened_files[descriptor.fd] = opened_files[r[0]]

                expected_fd = current.get_file_descriptor(r[0])
                if not expected_fd or expected_fd.struct_file != opened_files[r[0]]:
                    self._add_close(current.pid, r[0])
                    del opened_files[r[0]]

            children = app.get_children(current)
            for child in children:
                reorder_traverse(child)

        reorder_traverse(root)

        return self.program

