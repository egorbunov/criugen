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

    def get_resource_temporary_holders(self, resource):
        """
        Returns empty list, for now. TODO: Can it be different?
        """
        return []

    @property
    def is_sendable(self):
        return False

    def get_all_resources(self):
        # TODO implement
        pass
