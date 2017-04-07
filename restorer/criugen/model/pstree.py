import crdata
from resource import ResourceProvider


class ProcessTree(ResourceProvider):
    """
    Process tree built from processes list
    """

    @property
    def must_be_inherited(self):
        return False

    def get_dependencies(self, resource):
        return []

    @property
    def is_inherited(self):
        return False

    @property
    def is_sendable(self):
        return False

    def get_all_resources(self):
        return self.processes

    def get_resource_holders(self, resource):
        if type(resource) is not crdata.Process:
            raise TypeError("Resource is not a Process!")
        # we treat process parent as a resource holder
        # that does't mean, that process depends on it's parent lifetime, but
        # that that is okay from perspective, that parent process have all it's
        # rights to decide, when to create a child process. In this way parent
        # process may be considered as something, that holds it's children
        parent_process = self.proc_parent(resource)
        # parent process distinguish it's child with help of child's pid
        process_pid = resource.pid
        return [self.proc_parent(resource), [process_pid]]

    def __init__(self, processes):
        super(ProcessTree, self).__init__()
        self.processes = processes
        self.__fake_root = crdata.Process(pid=0, ppid=-1, pgid=-1, sid=-1,
                                          state=-1, threads_ids=[], fdt={},
                                          ids={}, vmas=[], vm_info={})
        self.__all_procs = processes + [self.__fake_root]
        self.__root = next(p for p in processes if p.ppid == 0)
        self.__proc_map = {p.pid: p for p in processes}

        def children_construct(acc, p):
            if p.ppid not in acc:
                acc[p.ppid] = []
            acc[p.ppid].append(p)
            if p.pid not in acc:
                acc[p.pid] = []
            return acc

        self.__proc_children = reduce(children_construct, self.__all_procs, {})

    def root_process(self):
        """
        :return: process tree root
        """
        return self.__root

    def proc_children(self, proc):
        """
        :param proc: process instance
        :return: list of children processes for given process,
                 list of crdata.Process
        """
        return self.__proc_children(proc)

    def proc_parent(self, proc):
        """
        :param proc: instance of `crdata.Process`
        :return: process parent as instance of `crdata.Process`
        """
        if proc == self.root_process():
            return self.__fake_root
        return self.__proc_map[proc.ppid]

    def proc_by_pid(self, pid):
        """
        :param pid: process id
        :return: process struct instance
        """
        return self.__proc_map[pid]
