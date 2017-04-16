from model.resource import ResourceProvider
from model.pstree import ProcessTree
from model.files import RegularFilesProvider
from model.vm import PrivateVmas, SharedVmas


def build_properties():
    pass


def build_action_graph(process_tree, resource_providers):
    """Builds actions graph (hopefully dag, it must be dag).
    
    What is done:
    
    * Actions (vertices) are built (see actions.py)
    * Properties of restoration process are built (see properties.py)
    * Directed edges between actions are created
    
    :param process_tree: process tree
    :type process_tree: ProcessTree
    :param resource_providers: list of resource providers
    :type resource_providers: list[ResourceProvider]
    :return: TODO?
    """

    for resource_provider in resource_providers:
        resource_provider.get
