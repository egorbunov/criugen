from process_concept import ProcessConcept
from resource_indexer import ResourcesIndexer


class ProcessTreeConcept(object):
    """
    Process tree built from processes list
    """

    def __init__(self, processes, root=None):
        """ Builds process tree
        :param processes: list of objects with `pid` and `ppid` properties
        :param root: process tree root; if not specified, process with zero
               parent pid is treated as a root
        :type processes: list[ProcessConcept]
        """
        super(ProcessTreeConcept, self).__init__()
        self._processes = sorted(processes, key=lambda p: p.pid)
        self._root = root if root else next(p for p in processes if p.ppid == 0)
        self._proc_map = {p.pid: p for p in processes}

        def children_construct(acc, p):
            if p.ppid not in acc:
                acc[p.ppid] = []
            acc[p.ppid].append(p)
            if p.pid not in acc:
                acc[p.pid] = []
            return acc

        self._proc_children = reduce(children_construct, self._processes, {})

        self._resource_indexer = ResourcesIndexer()
        # filling index
        for p in self._processes:
            for r in p.iter_all_resources():
                for h in p.iter_all_handles(r):
                    self._resource_indexer.on_proc_add_resource(p, r, h)


    @property
    def resource_indexer(self):
        """
        Return resource indexer object, which indexes all resource in all
        processes from process tree
        :rtype: ResourcesIndexer
        """
        return self._resource_indexer

    @property
    def processes(self):
        """ Processes, sorted by pid
        :rtype: list[ProcessConcept] 
        """
        return self._processes

    @property
    def sorted_processes(self):
        """ Same as processes, but implicitly `sorted` =)        
        """
        return self._processes

    @property
    def root_process(self):
        """
        :return: process tree root
        :rtype: ProcessConcept
        """
        return self._root

    def proc_children(self, proc):
        """
        :param proc: process instance
        :return: list of children processes for given process
        :rtype: list[ProcessConcept]
        """
        return self._proc_children(proc)

    def proc_parent(self, proc):
        """
        :param proc: instance of `crdata.Process`
        :return: process parent or None if given process is the root process
        :rtype: ProcessConcept
        """
        if proc == self.root_process:
            return None
        return self._proc_map[proc.ppid]

    def proc_by_pid(self, pid):
        """
        :param pid: process id
        :return: process structure instance
        :rtype: ProcessConcept
        """
        return self._proc_map[pid]
