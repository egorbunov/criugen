""" Here we put process tree resources "concepts" classes. The word concept was chosen not only
because I like it, but also to emphasise that these classes describe conceptual and common 
behaviour of all process tree resources; That is "high" level resource description without
any specific resource details.
"""

from abc import ABCMeta, abstractproperty, abstractmethod
import resource_handles
import model.crdata as crdata
import resource_adapters
from process_concept import ProcessConcept
from trivial_resources import *


class WrongResourceConceptPayload(Exception):
    """ Thrown in case user tries to instantiate ResourceConcept (see below)
    with wrong payload (type mismatch)
    """

    def __init__(self, expected, actual):
        super(WrongResourceConceptPayload, self).__init__(
            "expected = [{}], got = [{}]".format(expected, actual)
        )


class ResourceConcept(object):
    """Very straightforward conceptual resource class, which wraps the specific
    resource data
    
    TODO: that would be better for all property methods to be static and abstract somehow, because
     they are actually constant expressions
    """
    __metaclass__ = ABCMeta

    def __init__(self, payload):
        if not isinstance(payload, self.payload_type):
            raise WrongResourceConceptPayload(self.payload_type, type(payload))
        self._payload = payload
        self._dependencies = []

    @property
    def payload(self):
        """
        :return: real resource object, contained within ResourceConcept wrapper
        """
        return self._payload

    def add_dependency(self, resource, handle_type):
        """ Adds dependency of the resource. So in our model resource may
        depend on other resource with specifically typed handle to it. For example
        VMA may depend on (file, FileDescriptor). That is it for now.
        
        :param resource: dependency resource 
        :param handle_type: required dependency resource handle type
        """
        self._dependencies.append((resource, handle_type))

    @property
    def dependencies(self):
        return self._dependencies

    @abstractproperty
    def payload_type(self):
        """
        This payload type is almost 100% for documentation purposes 
        
        :return: type of stored payload or tuple of possible stored types
        """
        return object

    @abstractproperty
    def is_inherited(self):
        """
        :return: True, in case resource is inherited through forking process tree, i.e.
        handle is inherited and thus resource is shared with help of inheritance
        :rtype: bool
        """

    @abstractproperty
    def is_sharable(self):
        """
        :return: True, in case resource can be shared somehow during processes lifetime
                 i.e. after two processes are forked already
        :rtype: bool
        """

    @abstractproperty
    def handle_types(self):
        """ Be sure to make all handle types distinct, because out model
        is made so multi-handle resources (like pipe) must have distinct by type
        handles (that is not about possibility to point to resource with many handles
        in one process)
        
        :return: set of handle types, which are created during resource creation
        :rtype: frozenset[type]
        """

    @abstractmethod
    def possible_creators(self, processes):
        """ Filters given processes list and returns only those, who
        can create this resource (can be it's creator)

        :type processes: list[ProcessConcept]
        """


class RegularFileConcept(ResourceConcept):
    @property
    def payload_type(self):
        return crdata.RegFile

    @property
    def handle_types(self):
        return frozenset([resource_handles.FileDescriptor])

    @property
    def is_sharable(self):
        return True

    @property
    def is_inherited(self):
        return True

    def possible_creators(self, processes):
        # every process can open a file =)
        return processes


class SharedMemConcept(ResourceConcept):
    @property
    def payload_type(self):
        return crdata.SharedAnonMem

    @property
    def handle_types(self):
        return frozenset([resource_handles.FileDescriptor])

    @property
    def is_sharable(self):
        return True

    @property
    def is_inherited(self):
        return True

    def possible_creators(self, processes):
        return processes


class ProcessGroupConcept(ResourceConcept):
    @property
    def payload_type(self):
        """
        group resource type represented by id type
        """
        return GroupId

    @property
    def handle_types(self):
        return frozenset([type(resource_handles.NO_HANDLE)])

    @property
    def is_sharable(self):
        return True

    @property
    def is_inherited(self):
        return True

    def possible_creators(self, processes):
        # process group with special id can be created only
        # by process with pid == group id
        group_id = self.payload  # type: GroupId
        return [p for p in processes if p.pid == group_id]


class ProcessSessionConcept(ResourceConcept):
    @property
    def payload_type(self):
        """
        session resource type represented by id type
        """
        return SessionId

    @property
    def handle_types(self):
        return frozenset([type(resource_handles.NO_HANDLE)])

    @property
    def is_sharable(self):
        return False

    @property
    def is_inherited(self):
        return True

    def possible_creators(self, processes):
        # session with special id can be created only
        # by process with pid equal to that id
        session_id = self.payload  # type: SessionId
        return [p for p in processes if p.pid == session_id]


class PipeConcept(ResourceConcept):
    @property
    def payload_type(self):
        return resource_adapters.PipeResource

    @property
    def handle_types(self):
        return frozenset([resource_handles.PipeWriteHandle, resource_handles.PipeReadHandle])

    @property
    def is_inherited(self):
        return True

    @property
    def is_sharable(self):
        return True

    def possible_creators(self, processes):
        return processes


class VMAConcept(ResourceConcept):
    """ Virtual memory area concept
    """

    @property
    def payload_type(self):
        return crdata.VmArea

    @property
    def handle_types(self):
        return frozenset([type(resource_handles.NO_HANDLE)])

    @property
    def is_inherited(self):
        return True

    @property
    def is_sharable(self):
        return False

    def possible_creators(self, processes):
        return processes


class FSPropsConcept(ResourceConcept):
    """ File system process properties like root dir,
    working dir and so on
    """

    @property
    def payload_type(self):
        return crdata.FSProps

    @property
    def handle_types(self):
        return frozenset([type(resource_handles.NO_HANDLE)])

    @property
    def is_inherited(self):
        return False

    @property
    def is_sharable(self):
        return False

    def possible_creators(self, processes):
        return processes


class ProcessInternalsConcept(ResourceConcept):
    """ Internal process stuff like registers etc (TODO: reconsider)
    """

    @property
    def payload_type(self):
        return object  # no any restrictions for now

    @property
    def handle_types(self):
        return frozenset([type(resource_handles.NO_HANDLE)])

    @property
    def is_inherited(self):
        return False

    @property
    def is_sharable(self):
        return False

    def possible_creators(self, processes):
        # for now no restrictions and it seems to be ok
        return processes
