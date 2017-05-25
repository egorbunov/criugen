""" During process tree concept building as we need it for our action-list construction
algorithm, we have to create fresh handles for resources. These fresh handles should be
consistent with process state so there would be no two incompatible pairs (resource, handle)
within one process. That is why we introduce handle factories for different types of handles
in this file.
"""

from abc import ABCMeta, abstractmethod
import sys

from resource_handles import *


class HandleFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_free_handle(self):
        """ Returns free handle, i.e. just peeks it, not consumes and marks as
        used
        """

    @abstractmethod
    def mark_handle_as_used(self, handle):
        """ Tells to factory, that specified `handle` should
        be marked as used. This handle can't be returned by 
        'get_free_handle` method after that operation
        """

    @abstractmethod
    def is_handle_used(self, handle):
        """ Returns true if given handle is already used (was returned from
        factory)
        """


class IntBasedHandleFactory(HandleFactory):
    """ Integer handles. Free handles are generated consequently,
    starting from maximal already used integer handle
    """

    def __init__(self, max_value=sys.maxint):
        """        
        :param max_value: maximal possible integer value to construct handle
        from 
        """

        self._used_handles = set()  # type: set[int]
        self._top_unused = 0
        self._max_value = max_value

    def is_handle_used(self, handle):
        return handle in self._used_handles

    def get_free_handle(self):
        if self._top_unused >= self._max_value:
            raise IntHandleFactoryLimitReached(self._max_value)

        return self._top_unused

    def mark_handle_as_used(self, handle):
        if handle in self._used_handles:
            raise HandleAlreadyUsedError(handle)

        if handle >= self._max_value:
            raise IntHandleFactoryLimitReached(self._max_value)

        self._used_handles.add(handle)
        if self._top_unused < handle + 1:
            self._top_unused = handle + 1


class IntHandleFactoryLimitReached(Exception):
    def __init__(self, limit):
        super(IntHandleFactoryLimitReached, self).__init__("{}".format(limit))


class HandleAlreadyUsedError(Exception):
    def __init__(self, handle):
        super(HandleAlreadyUsedError, self).__init__("{}".format(handle))


class IntHandleFactoryAdaptor(HandleFactory):
    def __init__(self, int_factory, handle_constructor, int_getter):
        """ Adapts integer based handle factory to construct other objects,
        which can be constructed from int 
        
        :param int_factory: integer handles factory, all operations are delegated
               to this factory
        :type int_factory: IntBasedHandleFactory
        
        :param handle_constructor: function, which constructs handle object
               from integer
        :type handle_constructor: (val: int) -> object
        
        :param int_getter: function, which converts handle object to integer
        :type int_getter: (handle: object) -> int
        """

        self._int_factory = int_factory
        self._handle_constructor = handle_constructor
        self._handle_destructor = int_getter

    def is_handle_used(self, handle):
        return self._int_factory.is_handle_used(self._handle_destructor(handle))

    def mark_handle_as_used(self, handle):
        int_value = self._handle_destructor(handle)
        self._int_factory.mark_handle_as_used(int_value)

    def get_free_handle(self):
        new_value = self._int_factory.get_free_handle()
        return self._handle_constructor(new_value)


class NoHandleFactory(HandleFactory):
    """
    This factory just returns NO_HANDLE every time. We treat absence of
    handle as handle, which do not conflict on handle level with other 
    resources
    """

    def is_handle_used(self, handle):
        return False

    def get_free_handle(self):
        return NO_HANDLE

    def mark_handle_as_used(self, handle):
        pass


def make_handle_factories_map_for_process():
    """ Constructs map from handle type to proper handle factory,
    which is made for one signle process; Created handle factories
    ensure handle generation logic to be consistent with out process
    resources model, for example we have different handles: FileDescriptor,
    PipeWriteHandle, PipeReadHandle, which are not equal as types, but
    they all share single file descriptor namespace, so if there are pipe
    read handle with fd = 5 you can't return free FileDescriptor handle with
    value 5 and vice versa

    :return: map from handle type to handle factory; handle types are described in
             resource_handles.py file
    :rtype: dict[type, HandleFactory]
    """

    int_factory = IntBasedHandleFactory()
    return {
        type(NO_HANDLE): _make_no_handle_factory(),
        FileDescriptor: _make_file_descriptor_factory(int_factory),
        PipeWriteHandle: _make_pipe_write_handle_factory(int_factory),
        PipeReadHandle: _make_pipe_read_handle_factory(int_factory)
    }


def _make_file_descriptor_factory(int_factory):
    """ Constructs new simple factory of FileDescriptor handles
    :rtype: HandleFactory
    """

    def identity(x): return x

    def fd_construct(val): return FileDescriptor(val)

    return IntHandleFactoryAdaptor(int_factory,
                                   handle_constructor=fd_construct,
                                   int_getter=identity)


def _make_pipe_read_handle_factory(int_factory):
    """ Constructs handle factory of PipeReadHandle objects
    :rtype: HandleFactory
    """

    def read_handle_construct(val): return PipeReadHandle(fd=val)

    def read_handle_destroy(handle): return handle.fd

    return IntHandleFactoryAdaptor(int_factory, read_handle_construct, read_handle_destroy)


def _make_pipe_write_handle_factory(int_factory):
    """ Constructs handle factory of PipeWriteHandle objects
    :rtype: HandleFactory 
    """

    def write_handle_construct(val): return PipeWriteHandle(fd=val)

    def write_handle_destroy(handle): return handle.fd

    return IntHandleFactoryAdaptor(int_factory, write_handle_construct, write_handle_destroy)


def _make_no_handle_factory():
    """ Construct factory of handle of type(NO_HANDLE) type
    :return: NoHandleFactory 
    """
    return NoHandleFactory()
