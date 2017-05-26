from process_concept import ProcessConcept
from resource_listener import ProcessResourceListener
from resource_concepts import ResourceConcept


class ResourcesIndexer(ProcessResourceListener):
    """ Indexes all resources and stores information
    about which process holds which resource
    """

    def __init__(self):
        self._resource_holders_map = {}  # type: dict[ResourceConcept, list[ProcessConcept]]
        # that is a map from pairs of (resource, handle) to processes list
        self._resource_handle_holders_map = {}  # type: dict[(ResourceConcept, object), list[ProcessConcept]]

    def on_proc_add_resource(self, process, r, h):
        self._resource_holders_map.setdefault(r, []).append(process)
        self._resource_handle_holders_map.setdefault((r, h), []).append(process)

    @property
    def all_resources(self):
        """
        :rtype: list[ResourceConcept] 
        """
        return self._resource_holders_map.keys()

    @property
    def all_resources_handles(self):
        """ Returns all pairs (resource, handle), which
        are added to the indexer
        :rtype: list[(ResourceConcept, object)]
        """
        return self._resource_handle_holders_map.keys()

    def get_resource_holders(self, resource):
        """
        :rtype: list[ProcessConcept] 
        """
        return self._resource_holders_map.get(resource, [])

    def get_resource_handle_holders(self, resource, handle):
        """
        :rtype: list[ProcessConcept] 
        """
        return self._resource_handle_holders_map.get((resource, handle))