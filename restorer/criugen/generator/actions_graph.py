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

import itertools

import model.crdata as crdata
from actions import *
from properties import *
from model.pstree import ProcessTree
from model.resource import ResourceProvider


def _actions_for_sendable_resource(resource_provider, resource):
    holders = resource_provider.get_resource_holders(resource)
    resource_creator = min(holders, key=lambda process: process.pid)
    return [CreateAction(process=resource_creator, resource=resource)] + \
           [SendAction(processFrom=resource_creator, processTo=p) for p in holders if p != resource_creator]


def _build_actions_for_sendable_resources(resource_provider):
    return list(itertools.chain.from_iterable(
        _actions_for_sendable_resource(resource_provider, r) for r in resource_provider.get_all_resources()
    ))


def _get_single_process_root(processes):
    """
    Simply finds root process for given list of processes
    All processes from list must form a tree, if that is not
    true, exception is thrown
    :param processes: list of processes
    :type processes: list[crdata.Process]
    :return: process, which is the root of passed process tree
    :rtype: crdata.Process
    """

    pids = set(p.pid for p in processes)
    forest_roots = [p for p in processes if p.ppid not in pids]
    # due to nature of processes set, we are sure, that it forms a single tree or forest of trees
    # so the only thing we need to check, is that it is not a forest, but single tree
    if not forest_roots or len(forest_roots) > 1:
        raise Exception("Processes do not form a single tree")
    return forest_roots[0]


def _actions_for_inherited_resource(resource_provider, resource):
    holders = resource_provider.get_resource_holders(resource)
    resource_creator = _get_single_process_root(holders)
    return [CreateAction(process=resource_creator, resource=resource)]


def _build_actions_for_inherited_resources(resource_provider):
    return list(itertools.chain.from_iterable(
        _actions_for_inherited_resource(resource_provider, r) for r in resource_provider.get_all_resources()
    ))


def _actions_for_non_sharable_resources(resource_provider, resource):
    holders = resource_provider.get_resource_holders(resource)
    if len(holders) != 1:
        raise Exception("Non-sharable resource must have single holder")
    return [CreateAction(process=holders[0], resource=resource)]


def _build_actions_for_non_sharable_resources(resource_provider):
    return list(itertools.chain.from_iterable(
        _actions_for_non_sharable_resources(resource_provider, r) for r in resource_provider.get_all_resources()
    ))


def _build_action_vertices(resource_provider):
    """
    Builds list of actions for single resource provider (see actions.py)
    :type resource_provider: ResourceProvider    
    :return: list 
    """

    # here we distinguish between sendable > inherited > non-sharable resources
    # we prefer to send resources to resource inheritance (it is easier =))
    if resource_provider.is_sendable and not resource_provider.must_be_inherited:
        return _build_actions_for_sendable_resources(resource_provider)
    elif resource_provider.is_inherited:
        return _build_actions_for_inherited_resources(resource_provider)
    else:
        return _build_actions_for_non_sharable_resources(resource_provider)


def _build_properties(resource_provider):
    """ Generates list of properties for single type of resources
    :param resource_provider:
    :type resource_provider: ResourceProvider
    :return: 
    """
    props = []
    resources = resource_provider.get_all_resources()

    # adding dependency properties
    props.extend(DependsProperty(process=p, dependantResource=r, dependencyResource=d)
                 for r in resources
                 for p in resource_provider.get_resource_holders(r)
                 for d in resource_provider.get_dependencies(r))

    if resource_provider.must_be_inherited or resource_provider.is_inherited and not resource_provider.is_sendable:
        props.extend(InheritsProperty(process=p, resource=r)
                     for r in resources
                     for p in resource_provider.get_resource_holders(r)
                     if p != _get_single_process_root(resource_provider.get_resource_holders(r))) # TODO: optimize

    return props


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

    actions = list(itertools.chain.from_iterable(_build_action_vertices(rp) for rp in resource_providers))
    print(actions)

    properties = list(itertools.chain.from_iterable(_build_properties(rp) for rp in resource_providers))
    print(properties)


