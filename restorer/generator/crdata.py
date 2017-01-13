import collections

"""
Process data holder
"""
Process = collections.namedtuple('Process', [
    'pid',          # process id
    'ppid',         # process parent id
    'pgid',         # process group id
    'sid',          # process session id
    'state',        # process state
    'threads_ids',  # set of thread ids
    'fdt',          # file descriptor table: map from file descriptor to file id
    'vm_info',      # global vm info (start and end addresses of segments and other stuff)
    'vmas',         # array of VmArea structs, describing mappings in process vm
    'ids'           # various ids for process like it's namespace ids
])

"""
Regular file
"""
RegFile = collections.namedtuple('RegFile', [
    'path',
    'size',
    'pos',
    'flags',
    'mode'
])

"""
Structure, which describes one pipe
"""
PipeFile = collections.namedtuple('PipeFile', [
    'id',
    'flags'
])

"""
Virtual process memory global map
"""
VmInfo = collections.namedtuple('VmInfo', [
    'arg_start',
    'arg_end',
    'brk',
    'env_start',
    'env_end',
    'code_start',
    'code_end',
    'data_start',
    'data_end',
    'brk_start',
    'stack_start',
    'dumpable',
    'exe_file_id',
    'saved_auxv'
])

"""
Virtual memory area
"""
VmArea = collections.namedtuple('VmArea', [
    'start',
    'end',
    'pgoff',
    'shmid',
    'prot',
    'flags',
    'status',
    'fd',
    'fdflags'
])


class App:
    def __init__(self,
                 processes,
                 files):
        """
        :param processes: list of processes
        :param files:  map from file id to file structure
        """
        self.processes = processes
        self.files = files
        self.__proc_map = {p.pid: p for p in processes}
        self.__root = next(p for p in processes if p.ppid == 0)
        self.__fake_root = Process(pid=0, ppid=-1, pgid=-1, sid=-1,
                                   state=-1, threads_ids=[], fdt={},
                                   ids={}, vmas=[], vm_info={})
        self.__all_procs = processes + [self.__fake_root]

        def children_construct(acc, p):
            if p.ppid not in acc:
                acc[p.ppid] = []
            acc[p.ppid].append(p)
            if p.pid not in acc:
                acc[p.pid] = []
            return acc
        self.__proc_children = reduce(children_construct, self.__all_procs, {})

        def proc_files_construct(p):
            files_map = {}
            for fd, fid in p.fdt.iteritems():
                if fid not in files_map:
                    files_map[fid] = set()
                files_map[fid].add(fd)
            return files_map
        self.__proc_files = {p.pid: proc_files_construct(p) for p in self.__all_procs}

    def root_process(self):
        return self.__root

    def process_parent(self, proc):
        """
        :param proc: instance of `crdata.Process`
        :return: process parent as instance of `crdata.Process`
        """
        if proc == self.root_process():
            return self.__fake_root
        return self.__proc_map[proc.ppid]

    def file_by_id(self, fid):
        return self.files[fid]

    def process_files(self, proc):
        """
        :param proc: instance of `crdata.Process`
        :return: map from file structure to set of file descriptors
        """
        return self.__proc_files[proc.pid]

    def process_children(self, proc):
        """
        :param proc: instance of `crdata.Process`
        :return: list of process child processes
        """
        return self.__proc_children[proc.pid]



