from model.resource import ResourceProvider


class PrivateVmas(ResourceProvider):
    """
    This resource provider correctly collects private areas and determines,
    which of them are shared between multiple processes
    """

    @property
    def must_be_inherited(self):
        return True

    def get_dependencies(self, resource):
        # TODO implement
        pass

    @property
    def is_inherited(self):
        return True

    def get_resource_holders(self, resource):
        # TODO implement
        pass

    def get_resource_handles(self, resource, process):
        # TODO implement
        pass

    @property
    def is_sendable(self):
        return False

    def get_all_resources(self):
        # TODO implement
        pass


class SharedVmas(ResourceProvider):
    """
    Resource provider responsible for virtual memory areas, which are shared
    """

    @property
    def must_be_inherited(self):
        return False

    def get_dependencies(self, resource):
        # TODO implement
        pass

    @property
    def is_inherited(self):
        return True

    def get_resource_holders(self, resource):
        # TODO implement
        pass

    def get_resource_handles(self, resource, process):
        # TODO implement
        pass

    @property
    def is_sendable(self):
        return False

    def get_all_resources(self):
        # TODO implement
        pass
