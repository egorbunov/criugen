from handle_factory import make_handle_factories_map_for_process, HandleFactory
from itertools import chain
from resource_listener import ProcessResourceListener
import resource_concepts


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
        self._final_resources = {}  # dict from resource to handle array
        self._tmp_resources = {}  # same as _final_resources, but temporary
        self._handle_factories = make_handle_factories_map_for_process()  # type: dict[type, HandleFactory]
        self._resource_listeners = []

    def add_resource_listener(self, resource_listener):
        """
        :param resource_listener: listener, which is called in case 
               new resources added to the process
        :type resource_listener: ProcessResourceListener
        """
        self._resource_listeners.append(resource_listener)

    def remove_resource_listener(self, resource_listener):
        self._resource_listeners.remove(resource_listener)

    @property
    def pid(self):
        return self._pid

    @property
    def ppid(self):
        """ Parent pid
        """
        return self._parent_pid

    def add_final_resource(self, resource, handle):
        """ Adds resource, which is "final" in terms that
        it is not temporary, so this resource must be in the
        the real process at the end of restoration process
        """
        self._add_resource_to_dict(self._final_resources, resource, handle)

    def add_tmp_resource(self, resource, handle):
        """ Adds resource just like `add_final_resource`, but marks internally
        that this (resource, handle) pair is temporary to the process
        """
        self._add_resource_to_dict(self._tmp_resources, resource, handle)

    def add_tmp_resource_with_auto_handle(self, resource, handle_type):
        """ Adds temporary resource just as add_tmp_resource does, but
        it automatically generates valid handle for given resource of
        a given type
        
        :param resource: resource to add
        :type resource: resource_concepts.ResourceConcept
        :param handle_type: handle type to generate
        :type handle_type: type
        """
        automatic_handle = self._get_next_handle_of_type(handle_type)
        self.add_tmp_resource(resource, automatic_handle)

    def iter_all_resources(self):
        """
        :rtype: collections.Iterable[resource_concepts.ResourceConcept]
        """
        return chain(self._final_resources.iterkeys(), self._tmp_resources.iterkeys())

    def iter_all_resource_handle_pairs(self):
        """ Iterable over all pairs (resource, handle)
        :rtype: collections.Iterable
        """
        for r in self.iter_all_resources():
            for h in self.iter_all_handles(r):
                yield (r, h)

    def iter_tmp_resource_handle_pairs(self):
        """ Iterable over temporary pairs (resource, handle)
        :rtype: collections.Iterable
        """
        for r, handles in self._tmp_resources.iteritems():
            for h in handles:
                yield (r, h)

    def iter_tmp_resources(self):
        """ returns iterator other temporary resources
        """
        return self._tmp_resources.iterkeys()

    def get_final_handles(self, resource):
        """ Returns list of handles, so each handle `h` from this
        list: (`h`, resource) must be in the target process state after
        restoration process
        """
        return self._final_resources.get(resource, set())

    def get_tmp_handles(self, resource):
        """ Returns list of handles, so each handle `h` from this
        list: (`h`, resource) must NOT be in the target process state after
        restoration process, i.e. (`h`, resource) is temporary pair
        """
        return self._tmp_resources.get(resource, set())

    def get_all_handles_of_type(self, resource, handle_type):
        """ Returns all handles of particular type pointing to the resource
        :rtype: collections.Iterable
        """
        return (h for h in self.iter_all_handles(resource) if type(h) == handle_type)

    def iter_all_handles(self, resource):
        """ Returns iterator through all handles, which point to the resource
        """
        return chain(self.get_final_handles(resource), self.get_tmp_handles(resource))

    def has_resource(self, resource):
        """ Returns true in case given resource is handled by this process (at any handle)
        """
        return resource in self._final_resources or resource in self._tmp_resources

    def has_resource_at_handle_type(self, resource, handle_type):
        """ Returns true if (resource, handle) pair is in this process and
        type(handle) == handle_type
        """
        for h in self.iter_all_handles(resource):
            if type(h) == handle_type:
                return True
        return False

    def has_resource_at_handle(self, resource, handle):
        """ Returns True in case (resource, handle) is in that process
        """
        for h in self.iter_all_handles(resource):
            if h == handle:
                return True
        return False

    def is_tmp_resource(self, resource, handle):
        """ Returns True is (resource, handle) is in the process and this pair is temporary
        """
        return resource in self._tmp_resources and handle in self._tmp_resources[resource]

    @property
    def minimalistic_repr(self):
        return "Process(pid={}, ppid={})".format(self.pid, self.ppid)

    def __repr__(self):
        return "{}(pid={}, ppid={})".format(ProcessConcept.__name__, self.pid, self.ppid)

    def _set_handle_is_used(self, handle):
        handle_factory = self._handle_factories[type(handle)]
        if handle_factory.is_handle_used(handle):
            # we ignore the fact of repeated handle here; that is because
            # it can happen for tmp added resources and our algorithm can
            # deal with it
            return
        handle_factory.mark_handle_as_used(handle)

    def _get_next_handle_of_type(self, handle_type):
        handle_factory = self._handle_factories[handle_type]
        return handle_factory.get_free_handle()

    def _add_resource_to_dict(self, dct, resource, handle):
        """ Use this every time you need to add a resource to the process
        instance
        """
        dct.setdefault(resource, set()).add(handle)
        # mark handle as used within process
        self._set_handle_is_used(handle)

        # call resource add listener
        for rl in self._resource_listeners:
            rl.on_proc_add_resource(self, resource, handle)
