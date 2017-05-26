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
        return self._resource_holders_map.keys()

    def get_resource_holders(self, resource):
        return self._resource_holders_map.get(resource, [])

    def get_resource_handle_holders(self, resource, handle):
        return self._resource_handle_holders_map.get((resource, handle))
