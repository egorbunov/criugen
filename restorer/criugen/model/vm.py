from resource import ResourceProvider

import crdata
import resource_handles
from crconstants import *


class PrivateVmas(ResourceProvider):
    """
    This resource provider correctly collects private areas and determines,
    which of them are shared between multiple processes
    """

    def __init__(self, processes, files):
        """Constructs private virtual memory areas provider
        
        :param processes: list of processes
        :type processes: list[crdata.Process]
        :param files: list of files (probably, that is not only regular files) TODO: investigate
        :type files: iterable[crdata.]
        """
        super(PrivateVmas, self).__init__()

        self._processes = processes
        self._vma_to_process = {
            vma: process for process in self._processes for vma in process.vmas
            if VMA_STATUS_ANON_PRIVATE in vma.status or VMA_STATUS_FILE_PRIVATE in vma.status
        }
        self._id_to_file = {f.id: f for f in files}

    @property
    def must_be_inherited(self):
        return False

    def get_dependencies(self, resource):
        """
        Returns resource dependencies, needed to create given resource
        :param resource: vm area
        :type resource: crdata.VmArea
        :return: list of single file resource in case given VMA is FILE_PRIVATE, 
                 empty list else
        """
        if not isinstance(resource, crdata.VmArea):
            raise TypeError("Input resource must be VmArea")

        if VMA_STATUS_FILE_PRIVATE in resource.status:
            return [self._id_to_file[resource.shmid]]
        return []

    @property
    def is_inherited(self):
        return True

    def get_resource_holders(self, resource):
        """
        For now it just returns one process (process, from which vma array vma was
        taken)
        
        TODO: implement private vmas inheritence
        """
        if not isinstance(resource, crdata.VmArea):
            raise TypeError("Input resource must be VmArea")

        return [self._vma_to_process[resource]]

    def get_resource_handles(self, resource, process):
        if not isinstance(resource, crdata.VmArea):
            raise TypeError("Input resource must be VmArea")

        if self._vma_to_process[resource] != process:
            return []
        # we treat start and length of area as a handle to it
        return resource_handles.VMAHandle(start=resource.status, length=resource.end - resource.start)

    def get_resource_temporary_holders(self, resource):
        """
        Returns empty list, because we not support such functionality for private
        VMAs.
        
        This probably, but hardly, may be changed, because it is imaginable:
            * process A creates Private VMA
            * process A forks process B
            * process B forks process C
            * process B removes Private VMA
        You can see, that A and C share VMA (and this VMA is COWed), but process B
        has closed it and so in the final processes snapshot it would hard to investigate
        such behaviour
        """
        return []

    @property
    def is_sendable(self):
        return False

    def get_all_resources(self):
        return self._vma_to_process.keys()


class SharedVmas(ResourceProvider):
    """
    This resource provider just manages shared VMAs.
    
    TODO: for now it is absolutely the same as PrivateVmas
    """

    def __init__(self, processes, files):
        """Constructs private virtual memory areas provider

        :param processes: list of processes
        :type processes: list[crdata.Process]
        :param files: list of files (probably, that is not only regular files) TODO: investigate
        :type files: iterable[crdata.]
        """
        super(SharedVmas, self).__init__()

        self._processes = processes
        self._vma_to_process = {
            vma: process for process in self._processes for vma in process.vmas
            if VMA_STATUS_ANON_SHARED in vma.status or VMA_STATUS_FILE_SHARED in vma.status
        }
        self._id_to_file = {f.id: f for f in files}

    @property
    def must_be_inherited(self):
        return False

    def get_dependencies(self, resource):
        """
        Returns resource dependencies, needed to create given resource
        :param resource: vm area
        :type resource: crdata.VmArea
        :return: list of single file resource in case given VMA is FILE_SHARED, 
                 empty list else
        """
        if not isinstance(resource, crdata.VmArea):
            raise TypeError("Input resource must be VmArea")

        if VMA_STATUS_FILE_SHARED in resource.status:
            return [self._id_to_file[resource.shmid]]
        return []

    @property
    def is_inherited(self):
        return True

    def get_resource_holders(self, resource):
        """
        Just one process, no need to care about inheritance and stuff because it's shared VMAs
        """
        if not isinstance(resource, crdata.VmArea):
            raise TypeError("Input resource must be VmArea")

        return [self._vma_to_process[resource]]

    def get_resource_handles(self, resource, process):
        if not isinstance(resource, crdata.VmArea):
            raise TypeError("Input resource must be VmArea")

        if self._vma_to_process[resource] != process:
            return []
        return resource_handles.VMAHandle(start=resource.status, length=resource.end - resource.start)

    def get_resource_temporary_holders(self, resource):
        """
        Returns empty list, for now. TODO: Can it be different?
        """
        return []

    @property
    def is_sendable(self):
        return False

    def get_all_resources(self):
        return self._vma_to_process.keys()


