from model.resource import ResourceProvider
import crdata


class RegularFilesProvider(ResourceProvider):
    """
    Class, which is used as resource provider for any resource with id.
    It was intended to be provider for regular files and other stuff like pipes...
    """

    def __init__(self, processes, files):
        """
        :param processes: list of processes (to be restored)
        :type processes: list
        :param files: list of file-resources (file wrapped inside ResourceWrapper)
        :type files: list
        """
        super(RegularFilesProvider, self).__init__()
        self.processes = processes
        self.reg_files = files

        self.__file_ids_to_processes = {f.id: filter(lambda p: f.id in p.fdt.values(), processes)
                                        for f in self.reg_files}

        def proc_files_construct(p):
            """ Constructs map from file id to set of file descriptors 
            """
            files_map = {}
            for fd, fid in p.fdt.iteritems():
                if fid not in files_map:
                    files_map[fid] = set()
                files_map[fid].add(fd)
            return files_map
        self.__proc_files = {p.pid: proc_files_construct(p) for p in processes}

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

        holding_processes = self.__file_ids_to_processes[resource.id]
        return holding_processes

    def get_resource_handles(self, resource, process):
        if type(resource) is not crdata.RegFile:
            raise TypeError("Resource must be Regular File")
        # list of file descriptors
        return self.__proc_files[process][resource.id]

    def get_dependencies(self, resource):
        """
        regular files have no dependencies on other resources (see ResourceProvider comment
        on get_dependencies abstract method for notes on process dependencies) 
        """
        return []
