"""
Actions relationships together with properties (see properties.py) sum up to create some
precedence rules, which can help us to decide, which actions must be performed before others

For better explanation lets add next shortcut to describe, that process has a resource:

* `[p] obtains {r}` <=> `[p] creates {r}` OR `[p] inherits {r} from [q]` OR `[q] sends {r} to [p]`

Also remember that processes may create other processes, so:

* `[p] creates [q]` is a possible rule
* we also say: `[p] was created` if `[q] creates [p]` for some `[q]`

And basing on actions above and on properties (see properties.py) we have next 
precedence relationships (`a <~~ b` <=> `b` precedes `a`):

* `[q] creates {r}` <~~ `[q] was created`
* `[p] sends {r} to [q]` <~~ `[p] was created` AND `[q] was created` AND `[p] obtains {r}`
* `[q] inherits {r}` ==> `[p] creates [q]` <~~ `[p] was created` AND `[p] obtains {r}`
* `{q} depends on {r}` ==> `[p] obtains {q}` <~~ `[p] obtains {r}`

According to this relationship we can build a graph with edges showing precedence. This graph
may help us to determine which actions must be done before others. As an additional idea such 
graph may show, which restoration paths can be done truly in parallel?

PS: There are the `[god]` process, which exists during the whole restoration process and it
does not need to be created.
"""

from model.resource import ResourceProvider
from model.pstree import ProcessTree
from model.files import RegularFilesProvider
from model.vm import PrivateVmas, SharedVmas


def __build_properties():
    pass


def __build_actions_for_sendable_resources(resource_provider):
    resources = resource_provider.get_all_resources()

    for r in resources:
        holders = resource_provider.get_resource_holders(r)
        min(holders, key=lambda h: h.p)


def __build_actions_for_inherited_resources(resource_provider):
    pass


def __build_actions_for_non_sharable_resources(resource_provider):
    pass


def __build_action_vertices(resource_provider):
    """
    Builds list of actions for single resource provider (see actions.py)
    :type resource_provider: ResourceProvider    
    :return: list 
    """

    # here we distinguish between sendable > inherited > non-sharable resources
    # we prefer to send resources to resource inheritance (it is easier =))
    if resource_provider.is_sendable:
        return __build_actions_for_sendable_resources(resource_provider)
    elif resource_provider.is_inherited:
        return __build_actions_for_inherited_resources(resource_provider)
    else:
        return __build_actions_for_non_sharable_resources(resource_provider)


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
