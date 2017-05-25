from resource_concepts import ResourceConcept
from handle_factory import make_handle_factories_map_for_process, HandleFactory


class ProcessConcept(object):
    """Conceptual process, which contains pairs of resource and handle
    It stores resources via ResourceConcept and handles to them within
    one particular process
    """

    def __init__(self, pid, parent_pid):
        """ For now pid and parent pid are not treated as resources:
        1) we need them to build process tree
        2) these id's can't change in linux processes environment,
           so we treat them as constant process attributes

        :param pid: process id 
        :param parent_pid: process parent id
        """

        self._pid = pid
        self._parent_pid = parent_pid
        self._resources = {}  # dict from resource to handle array
        self._tmp_resources = {}  # same as _resources, but temporary
        self._handle_factories = make_handle_factories_map_for_process()  # type: dict[type, HandleFactory]

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
        :rtype: iterable[ResourceConcept]
        """
        return self._resources.keys()

    def get_tmp_resources(self):
        """
        :rtype: iterable[ResourceConcept]
        """
        return self._tmp_resources.keys()

    def get_handles(self, resource):
        return self._resources.get(resource, set())

    def get_tmp_handles(self, resource):
        return self._tmp_resources.get(resource, set())
