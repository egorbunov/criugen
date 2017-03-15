from model.resource import ResourceProvider


class FilesProvider(ResourceProvider):
    """
    Class, which is used as resource provider for any resource with id.
    It was intended to be provider for regular files and other stuff like that.
    """

    def __init__(self, processes, files):
        """
        :param processes: list of processes (to be restored)
        :type processes: list
        :param files: list of objects with id property,
               representing set of files, used somehow by processes
        :type files: list
        """
        super(FilesProvider, self).__init__()
        self.processes = processes
        self.reg_files = files

        self._file_ids_to_processes = {f.id: filter(lambda p: f.id in p.fdt.values(), processes)
                                       for f in files}

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
        return self._file_ids_to_processes[resource.id]

    def get_dependencies(self, resource):
        """
        files has no dependencies on other resources
        """
        return []
