from abc import abstractmethod, ABCMeta, abstractproperty


class ResourceProvider:
    """
    Abstract class for single type resource manager.

    The idea behind this abstraction:

    1. Application may contain many processes. All this processes in general share kernel
       resources. There are many kinds of resources. Command generation algorithm uses
       information about this resources to properly determine which command to put next.
       This class is a provider for exactly one kind of resource.
    2. Resources may be shared in different ways: sent via UNIX socket as file descriptor,
       inherited through forking and ...?
    3. Each resource creation may depend on other resources: backed by file virtual memory area 
       depends on a file; child process creation depends on it's parent process
    4. Process not just holds a resource, but it has some kind of userspace handle, to interact
       with it. Examples: 
               | Resource            | Handle                  |
               | ------------------- | ----------------------- |
               | Regular File        | file descriptor         |
               | Socket              | file descriptor         |
               | Virtual Memory Area | (start address, length) |
               | Process             | process id              |
               | Thread              | thread id               |
        For now, handle is some kind of identifier or whatever, which lets us to "talk" to resource
        somehow
    """
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractproperty
    def is_inherited(self):
        """
        :return: true, in case managed resource is inherited through forking process tree,
        false otherwise
        :rtype: bool
        """

    @abstractproperty
    def is_sendable(self):
        """
        :return: true, in case managed resource can be send somehow to other process, after
                 process tree is created; for example: regular file may be shared through
                 unix sockets
        :rtype: bool
        """

    @abstractproperty
    def must_be_inherited(self):
        """
        Resource may be created, generally, in two ways: inherited during forking and created somehow after
        forking.
        :return: true if resource MUST be shared with process through inheritance (during forking)
        :rtype: bool
        """

    @abstractmethod
    def get_all_resources(self):
        """
        :return: list of resources, which are available from current
                 resource manager
        :rtype: list 
        """

    @abstractmethod
    def get_resource_holders(self, resource):
        """
        This method, practically, returns list of processes paired.
         For example in case of regular files:
        resource is a file object and handle is file descriptor, so (Process, [FileDescriptor])
        pair is returned for each process, which is holding specified resource

        :param resource: some resource object
        :type resource: object
        :return: list of pairs (Process, list[FileDescriptor])
        :rtype: list
        """

    @abstractmethod
    def get_resource_handles(self, resource, process):
        """
        Returns list of handles, which are used to access given resource in a specified process.
        
        :param resource: resource to get handles for
        :param process: process object, within who this resource is handled 
        :return: list of handles
        :rtype: list[object]
        """

    @abstractmethod
    def get_dependencies(self, resource):
        """
        Returns list of resources, which are needed for
        specified resource creation.
        
        This list does should not include Processes as resource-dependencies. On one hand that is
        not great design, but on the other hand resource is often not something, that needs a particular
        process to create it. Resource may be shared among number of processes, so no one of this processes
        are really needed for this resource to exist. Process cat initiate resource creation, so resource
        will be created in the kernel, after that process will have a kind of a link to the resource,
        so this link is a thing, that is attached tightly to the process, but resource itself is a bit
        farther.
        
        Due to thoughts above I have separated resource-dependencies and processes. Processes are handled
        by `get_resource_holders()` method, so they act as a resource holders. But the Process is a resource
        too. This is the only resource, which can hold another resource. Also it does not depend on other resource.
        
        :param resource: resource, for that user want to get list of dependencies
        :type resource: object
        :return: list of resources
        :rtype: list
        """
