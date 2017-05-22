"""
Actions relationships together with properties (see properties.py) sum up to create some
precedence rules, which can help us to decide, which actions must be performed before others

For better explanation lets add next shortcut to describe, that process has a resource:

* `[p] obtains {r}` <=> `[p] creates {r}` OR `[p] inherits {r} from [q]` OR `[q] sends {r} to [p]`

Also remember that processes may create other processes, so:

* we also say: `[p] was created` if `[q] creates [p]` for some `[q]`
* `[p] creates [q]` is a possible rule

And basing on actions above and on properties (see properties.py) we build
precedence relationships (`a <~~ b` <=> `b` precedes `a`).

Imagine that we have constructed set of actions: actions
For each action in actions we construct next precedence relationships:

* if action = `[q] creates {r}`, then
    1. `[p] creates [q]` for some [p] ~~> action
    
* if action = `[p] sends {r} to [q]`, then
    1. `[x] creates [p]` for some [x] ~~> action
    2. `[y] creates [q]` for some [y] ~~> action
    3. if `[p] creates {r}` in actions, then:
           `[p] create {r} ~~> action
    4. elif `[z] sends {r} to [p]` for some [z] in actions, then:
           `[z] sends {r} to [p]` for some [z] ~~> action
    5. else: [p] must inherit {r} from process above, in this case
       no additional precedence relation created, it is not needed, 
       because creation of [p] happens before action, that is guaranteed
       by item 1.
           
Next if we have determined set of properties of our restoration process (see properties.py)
For each property in properties:

* if `{q} depends on {r}` in properties, then
    1. `[p1] creates {r}` for some [p1] ~~> `[p2] creates {q}` for some [p2]  # TODO: redundant rule?
    2. if [p2] != [p1] and `[p1] sends {r} to [p2]` in actions:
           `[p1] sends {r} to [p2]` ~~> `[p2] creates {q}`
    3. if [p2] inherits {r}, then no new precedence relations are added, because
       [p2] creation is guaranteed to happen before `[p2] creates {q}`
        
* if `[p] inherits {r} from [q]` in properties (q is a parent of p), then
    1. if `[q] creates {r}` in actions, then
           `[q] creates {r}` ~~> `[q] creates [p]`
    2. if `[x] sends {r} to [q]` (for some [x]) in actions, then
           `[x] sends {r} to [q]` ~~> `[q] creates [p]`
    3. if [q] inherits {r} from parent, then no new precedence relation
       should be added, because [q] would have {r} just after [q] creation
    
    
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
    """ Builds list of actions, which must be done during sendable resource creation
    """
    regular_holders = resource_provider.get_resource_holders(resource)
    tmp_holders = resource_provider.get_resource_temporary_holders(resource)
    all_holders = regular_holders + tmp_holders

    assert len(set(tmp_holders) & set(regular_holders)) == 0
    if not all_holders:
        print("No holder for resource: {}; skipping".format(resource))
        return []

    resource_creator = min(all_holders, key=lambda process: process.pid)
    actions = []
    if resource_creator in regular_holders:  # resource creator holds resource not temporarily
        actions.append(CreateAction(process=resource_creator, resource=resource))
    else:
        actions.append(CreateTemporaryAction(process=resource_creator, resource=resource))

    actions += [SendAction(process_from=resource_creator, process_to=p, resource=resource)
                for p in regular_holders if p != resource_creator]
    actions += [SendTemporaryAction(process_from=resource_creator, process_to=p, resource=resource)
                for p in tmp_holders if p != resource_creator]
    return actions


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
    """Builds list of actions, which are performed during inherited resource creation
    That is just only resource creation at the root of process tree
    """
    holders = resource_provider.get_resource_holders(resource)
    resource_creator = _get_single_process_root(holders)
    return [CreateAction(process=resource_creator, resource=resource)]


def _build_actions_for_inherited_resources(resource_provider):
    return list(itertools.chain.from_iterable(
        _actions_for_inherited_resource(resource_provider, r) for r in resource_provider.get_all_resources()
    ))


def _actions_for_non_sharable_resources(resource_provider, resource):
    """Returns list of actions, which are performed during resource creation, which is not shared
    Throws exception in case given resource has more than one holders (owners)
    """
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


def _build_depends_props(resource_provider):
    resources = resource_provider.get_all_resources()
    return (DependsProperty(dependant_resource=r, dependency_resource=d)
            for r in resources
            for d in resource_provider.get_dependencies(r))


def _build_inherits_props(process_tree, resource_provider):
    resources = resource_provider.get_all_resources()
    return (InheritsProperty(process=p, process_from=process_tree.proc_parent(p), resource=r)
            for r in resources
            for p in resource_provider.get_resource_holders(r)
            if p != _get_single_process_root(resource_provider.get_resource_holders(r)))


def _build_properties(process_tree, resource_provider):
    """ Generates list of properties for single type of resources
    :param process_tree: process tree
    :type process_tree: ProcessTree
    :param resource_provider:
    :type resource_provider: ResourceProvider
    :return: 
    """
    return list(itertools.chain(_build_depends_props(resource_provider),
                                _build_inherits_props(process_tree, resource_provider)))


def _build_adj_list_for_create_action(action, properties, all_actions):
    """
    action = [a] creates {b}
    
        1) [a] must be created before, so: ([q] creates [a]) ~~> action
        2) 
    
    Creates adjacency list for given create action
    :param action: action vertex
    :param properties: list of properties
    :param all_actions: list of all action vertices
    :return: list of actions, ends of graph edges starting at given action
    """
    pass


def _build_graph(action_vertices, properties):
    """ Builds adjacency list graph representation from given action vertices and restoration properties
    
    Constructs edges between given action vertices
    
    :param action_vertices: list of actions
    :type action_vertices: list[Action]
    :param properties: list of restoration process properties
    :type properties: list[Property]
    :return: 
    """

    graph = {a: [] for a in action_vertices}

    create_actions = [a for a in action_vertices if isinstance(a, CreateAction)]
    send_actions = [a for a in action_vertices if isinstance(a, SendAction)]
    assert len(create_actions) + len(send_actions) == len(action_vertices)

    depends_props = [p for p in properties if isinstance(p, DependsProperty)]
    inherits_props = [p for p in properties if isinstance(p, InheritsProperty)]
    assert len(depends_props) + len(inherits_props) == len(properties)

    create_acts_by_resource = {a.resource: a for a in create_actions}  # only one create action per resource

    def get_resource_obtain_action(p, r):
        cr_act = create_acts_by_resource[r]
        if cr_act.process == p:
            return cr_act
        for sa in send_actions:
            if sa.process_to == p and sa.resource == r:
                return sa
        return None

    # process creation goes before creation of any resource by this process
    for act in create_actions:
        cract = create_acts_by_resource[act.process]
        graph[cract].append(act)

    # processing send actions
    for act in send_actions:
        from_cract = create_acts_by_resource[act.process_from]
        graph[from_cract].append(act)
        to_cract = create_acts_by_resource[act.process_to]
        graph[to_cract].append(act)
        obtain_act = get_resource_obtain_action(act.process_from, act.resource)
        if not obtain_act:
            # must check, that resource is inherited in process_from
            pass
        else:
            graph[obtain_act].append(act)

    # processing depends properties
    for prop in depends_props:
        dep_cr_act = create_acts_by_resource[prop.dependant_resource]
        dependency_cr_act = create_acts_by_resource[prop.dependency_resource]
        graph[dependency_cr_act].append(dep_cr_act)  # TODO: is it redundant?
        dependency_obt_action = get_resource_obtain_action(dep_cr_act.process, prop.dependency_resource)
        if not dependency_obt_action:
            # must assert, that dependency resource is inherited
            pass
        else:
            graph[dependency_obt_action].append(dep_cr_act)

    # processing inheritance property
    for prop in inherits_props:
        parent_obtain_resource_act = get_resource_obtain_action(prop.process_from, prop.resource)
        child_cr_act = create_acts_by_resource[prop.process_to]

        assert child_cr_act.process == prop.process_from  # assert that proc_from is father of proc_to

        graph[child_cr_act].append(parent_obtain_resource_act)

    return graph


def topsort_actions_graph(graph):
    """
    Perform topological sort of the graph
    :param graph: graph, returned by `build_action_graph` function
    :return: list of actions
    """
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

    action_vertices = list(itertools.chain.from_iterable(_build_action_vertices(rp)
                                                         for rp in resource_providers))
    print(action_vertices)
    properties = list(itertools.chain.from_iterable(_build_properties(process_tree, rp)
                                                    for rp in resource_providers))
    print(properties)
    graph = _build_graph(action_vertices, properties)
    return graph
