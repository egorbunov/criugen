from model.resource import ResourceProvider

import crdata
import resource_handles

from itertools import chain


def _construct_process_files_map(process):
    """ Constructs map from file id to set of file descriptors 
    
    :param process: target process
    :type process: crdata.Process
    """
    files_map = {}
    for fd, fid in process.fdt.iteritems():
        if fid not in files_map:
            files_map[fid] = set()
        files_map[fid].add(fd)
    return files_map


def _construct_holders_through_dependencies(reg_file, resource_provider):
    """
    Constructs list of processes, which must hold specified file resource
    at some point of time during restoration, because it is needed for 
    creation of other resource
    
    :param reg_file: file resource, which is checked for dependant resources
    :type reg_file: crdata.RegFile
    :param resource_provider: provider of resources, which dependencies are checked
           for being equal to specified file
    :type resource_provider: ResourceProvider
    :return:  list[crdata.Process]
    """

    rs = resource_provider.get_all_resources()
    holders_gen = chain.from_iterable(
        resource_provider.get_resource_holders(r) + resource_provider.get_resource_temporary_holders(r)
        for r in rs if reg_file in resource_provider.get_dependencies(r)
    )
    return list(holders_gen)


class RegularFilesProvider(ResourceProvider):
    """
    Class, which is used as resource provider for regular linux files
    """

    def __init__(self, processes, files, dep_providers):
        """
        Creates regular files resource provider
        
        For proper construction we need list of processes, list of regular
        files and also a list of all Resource Providers, which may give us
        information about resources, which creation demands regular file:
        thus we can determine the complete list of processes, which need
        to handle regular file resource at some point of time during restoration.
        
        :param processes: list of processes (to be restored)
        :type processes: list[crdata.Process]
        :param files: list of regular files
        :type files: list[crdata.RegFile]
        :param dep_providers: list of resource providers, which resources may
               depend on regular files
        :type dep_providers: list[ResourceProvider]
        """
        super(RegularFilesProvider, self).__init__()

        self.processes = processes
        self.reg_files = files

        self._file_to_holders = {f: set(filter(lambda p: f.id in p.fdt.values(), processes))
                                 for f in self.reg_files}
        # for each file we construct a set of processes, which must hold this file at some point of
        # restoration process; this processes are retrieved from every resource provider passed (dep_providers)
        # from set of such processes for each file we subtract processes, which holding this file not just
        # temporarily (dependency file assumed to may be closed after dependant resource creation)
        self._file_to_tmp_holders = {
            f: set(
                chain.from_iterable(_construct_holders_through_dependencies(f, dp) for dp in dep_providers)
            ).difference(self._file_to_holders[f])
            for f in self.reg_files
        }

        self._proc_files = {p: _construct_process_files_map(p) for p in processes}

    @property
    def must_be_inherited(self):
        return False

    @property
    def is_inherited(self):
        return True

    @property
    def is_sendable(self):
        """
        File may be sent using unix domain sockets
        """
        return True

    def get_all_resources(self):
        return self.reg_files

    def get_resource_holders(self, resource):
        if type(resource) is not crdata.RegFile:
            raise TypeError("Resource must be Regular File")

        return list(self._file_to_holders[resource])

    def get_resource_temporary_holders(self, resource):
        if type(resource) is not crdata.RegFile:
            raise TypeError("Resource must be Regular File")

        return list(self._file_to_tmp_holders[resource])

    def get_resource_handles(self, resource, process):
        if type(resource) is not crdata.RegFile:
            raise TypeError("Resource must be Regular File")

        if process in self.get_resource_temporary_holders(resource):
            return [resource_handles.ANY_FILE_DESCRIPTOR]  # we don't care at which fd temporary file is opened
        # list of file descriptors
        return self._proc_files[process][resource.id]

    def get_dependencies(self, resource):
        """
        regular files have no dependencies on other resources (see ResourceProvider comment
        on get_dependencies abstract method for notes on process dependencies) 
        """
        return []
