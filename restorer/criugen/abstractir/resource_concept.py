from abc import ABCMeta, abstractproperty
import resource_handles


class ResourceConcept(object):
    """Very straightforward conceptual resource class, which wraps the specific
    resource data
    """
    __metaclass__ = ABCMeta

    def __init__(self, payload):
        self._payload = payload
        self._dependencies = []

    @property
    def payload(self):
        """
        :return: real resource object, contained within ResourceConcept wrapper
        """
        return self._payload

    def add_dependency(self, resource):
        self._dependencies.append(resource)

    @property
    def dependencies(self):
        return self._dependencies
    
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
        """
        :return: array of handle types, which are created during resource creation
        :rtype: list[type]
        """


class RegularFileConcept(ResourceConcept):
    @property
    def handle_types(self):
        return [resource_handles.FileDescriptor]

    @property
    def is_sharable(self):
        return True

    @property
    def is_inherited(self):
        return True


class ProcessGroupConcept(ResourceConcept):
    @property
    def handle_types(self):
        return [resource_handles.GroupId]

    @property
    def is_sharable(self):
        return True

    @property
    def is_inherited(self):
        return True


class ProcessSessionConcept(ResourceConcept):
    @property
    def handle_types(self):
        return [resource_handles.SessionId]

    @property
    def is_sharable(self):
        return False

    @property
    def is_inherited(self):
        return True


class PipeConcept(ResourceConcept):
    @property
    def handle_types(self):
        return [resource_handles.PipeInputHandle, resource_handles.PipeOutputHandle]

    @property
    def is_inherited(self):
        return True

    @property
    def is_sharable(self):
        return True


class VMAConcept(ResourceConcept):
    """ Virtual memory area concept
    """
    @property
    def handle_types(self):
        return [resource_handles.NO_HANDLE]

    @property
    def is_inherited(self):
        return True

    @property
    def is_sharable(self):
        return False


class FSPropsConcept(ResourceConcept):
    """ File system process properties like root dir,
    working dir and so on
    """
    @property
    def handle_types(self):
        return [resource_handles.NO_HANDLE]

    @property
    def is_inherited(self):
        return False

    @property
    def is_sharable(self):
        return False


class ProcessInternalsConcept(ResourceConcept):
    """ Internal process stuff like registers etc (TODO: reconsider)
    """
    @property
    def handle_types(self):
        return [resource_handles.NO_HANDLE]

    @property
    def is_inherited(self):
        return False

    @property
    def is_sharable(self):
        return False
