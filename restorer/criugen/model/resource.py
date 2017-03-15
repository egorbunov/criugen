from abc import abstractmethod, ABCMeta, abstractproperty


class ResourceProvider:
    """
    Abstract class for single type resource manager.
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
        This method, practically, returns list of processes, which are
        holding specified resource somehow; for example if resource is
        a regular file then list of processes, who has this file opened

        :param resource: resource, which is available (managed, if you want) by
               this resource manager
        :type resource: object
        :return: iterable of processes, which are resource holders for given resource
        :rtype: list[crdata.Process]
        """

    @abstractmethod
    def get_dependencies(self, resource):
        """
        Returns list of resources, which are needed for
        specified resource creation.
        This list does not include processes, which hold resource (TODO: maybe that is not cool design)
        :param resource: resource, for that user want to get list of dependencies
        :type resource: object
        :return: list of resources
        :rtype: list[crdata.Process]
        """
