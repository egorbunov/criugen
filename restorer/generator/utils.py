import nodes


class ApplicationComparator():
    def __init__(self, app1, app2):
        self.app1 = app1
        self.app2 = app2

    def compare_regular_files(self, rf1, rf2):
        return rf1.path == rf2.path and rf1.pos == rf2.pos

    def compare_descriptors(self, ds1, ds2):
        key = lambda d: d.fd
        ds1 = sorted(ds1, key=key)
        ds2 = sorted(ds2, key=key)
        if len(ds1) != len(ds2):
            return False
        for d1, d2 in zip(ds1, ds2):
            if d1.fd != d2.fd or \
                    not self.compare_regular_files(d1.struct_file, d2.struct_file):
                return False
        return True

    def compare_vmas(self, vmas1, vmas2):
        key = lambda vma: vma.start
        vmas1 = sorted(vmas1, key=key)
        vmas2 = sorted(vmas2, key=key)
        if len(vmas1) != len(vmas2):
            return False
        for vma1, vma2 in zip(vmas1, vmas2):
            if vma1.start != vma2.start or \
                    vma1.end != vma2.end or \
                    vma1.pgoff != vma2.pgoff or \
                    vma1.is_shared != vma2.is_shared:
                        return False
            if not vma1.file_path.path.startswith("/tmp/"):
                if vma1.file_path.path != vma2.file_path.path:
                    return False
            else:
                if vma1.file_path in self.tmp_file_paths_bijection:
                    file_path = self.tmp_file_paths_bijection[vma.file_path]
                    if vma2.file_path != file_path:
                        return False
                else:
                    self.tmp_file_paths_bijection[vma1.file_path] = vma2.file_path

    def compare_processes(self, p1, p2):
        return (p1.pid == p2.pid)  and \
                self.compare_descriptors(p1.descriptors, p2.descriptors) and \
                self.compare_vmas(p1.vmas, p2.vmas)

    def compare_process_trees(self, current1, current2):
        result = self.compare_processes(current1, current2)
        children1 = self.app1.get_children(current1)
        children2 = self.app2.get_children(current2)
        if len(children1) != len(children2):
            return False
        for (child1, child2) in zip(children1, children2):
            result &= self.compare_process_trees(child1, child2)
        return result

    def is_equals(self):
        self.tmp_file_paths_bijection = {}
        return self.compare_process_trees(self.app1.get_root_process(),
                                     self.app2.get_root_process())


class ApplicationView():
    def __init__(self, app):
        self.app = app

    def append(self, line, indent):
        self.result.append(" " * indent + line)

    def process(self, process, indent):
        fd_table = []
        for descriptor in process.descriptors:
            id = self.regular_files_ids[descriptor.struct_file]
            fd_table.append((descriptor.fd, id))
        fd_table.sort(key=lambda p: p[0])
        fds = map(lambda p: "fd {}: {}".format(*p), fd_table)
        self.append("Procces(pid={}, {}".format(process.pid, fds), indent)
        self.memory_mappings(process, indent)
        self.append(")", indent)

    def traverse(self, current, indent):
        self.process(current, indent)
        children = self.app.get_children(current)
        for child in children:
            self.traverse(child, indent + 2)

    def processes(self, indent):
        self.append("Processes(", indent)
        root = self.app.get_root_process()
        self.traverse(root, indent)
        self.append(")", indent)

    def regular_files(self, indent):
        self.append("RegularFiles(", indent)
        self.regular_files_ids = {}
        for i, rf in enumerate(self.app.get_regular_files()):
            self.regular_files_ids[rf] = i
            self.append("{}: RegularFile(path={}, size={}, pos={})".
                    format(i, rf.file_path.path, rf.size, rf.pos), indent)
        self.append(")", indent)

    def memory_mappings(self, process, indent):
        self.append("VMAS(", indent)
        for vma in process.vmas:
            if not vma.file_path:
                path = None
            else:
                path = vma.file_path.path
            pgoff = vma.pgoff
            self.append("start: {}, end: {}, is_shared: {}, file: {}, pgoff: {}".
                    format(vma.start, vma.end, vma.is_shared, path, pgoff), indent)
        self.append(")", indent)

    def text(self, indent=0):
        self.result = []
        self.append("Application(", indent)
        self.regular_files(indent)
        self.processes(indent)
        self.append(")", indent)
        return "\n".join(self.result)
