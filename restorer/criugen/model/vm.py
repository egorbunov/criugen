from model.resource import ResourceProvider


class PrivateAnonVmas(ResourceProvider):
    """
    This resource provider correctly collects private anonymous areas and determines,
    which of them are shared between multiple processes
    """

    @property
    def must_be_inherited(self):
        return True

    def get_dependencies(self, resource):
        pass

    @property
    def is_inherited(self):
        return True

    def get_resource_holders(self, resource):
        pass

    @property
    def is_sendable(self):
        return False

    def get_all_resources(self):
        pass


class BackedByFilesVmas(ResourceProvider):
    """
    Resource provider responsible for virtual memory areas, which are backed
    by file in some way. We refer Shared and Anonymous mappings as those class
    VMAs too, because linux actually creates files for serving them.
    """

    @property
    def must_be_inherited(self):
        return False

    def get_dependencies(self, resource):
        pass

    @property
    def is_inherited(self):
        return True

    def get_resource_holders(self, resource):
        pass

    @property
    def is_sendable(self):
        return False

    def get_all_resources(self):
        pass
