class ProcessConcept(object):
    """Conceptual process, which contains pairs of resource and handle
    It stores resources via ResourceConcept and handles to them within
    one particular process
    """

    def __init__(self, pid, parent_pid):
        self._pid = pid
        self._parent_pid = parent_pid
        self._resources = {}  # dict from resource to handle array
        self._tmp_resources = {}  # same as _resources, but temporary

    @property
    def pid(self):
        return self._pid

    @property
    def ppid(self):
        return self._parent_pid

    def add_resource(self, resource, handle):
        self._resources.setdefault(resource, set()).add(handle)

    def add_tmp_resource(self, resource, handle):
        self._tmp_resources.setdefault(resource, set()).add(handle)
        self.add_resource(resource, handle)

    def get_resources(self):
        """ 
        :return: all resources, including temporary 
        """
        return self._resources.keys()

    def get_tmp_resources(self):
        return self._tmp_resources.keys()

    def get_handles(self, resource):
        return self._resources.get(resource, set())

    def get_tmp_handles(self, resource):
        return self._tmp_resources.get(resource, set())
