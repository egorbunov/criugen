""" Action graph building and other stuff
"""

import itertools

from pstree import ProcessTreeConcept
from process_concept import ProcessConcept
from resource_concepts import ResourceConcept
from actions import *
import creators
from resource_indexer import ResourcesIndexer
from pyutils.graph import Graph


def build_actions_graph(process_tree):
    """ Performs analysis of given process concepts tree and builds up
    a graph of actions, which represents restoration process in terms
    of abstract actions

    :param process_tree: process tree concept, which contains all processes
           which are filled with resources concepts
    :type process_tree: ProcessTreeConcept
    :return: actions graph
    """

    action_index, action_graph = _init_actions_graph_and_index(process_tree)
    _build_precedence_edges(process_tree, action_index, action_graph)

    del action_index

    return action_graph


def _init_actions_graph_and_index(process_tree):
    """ Creates actions index and action graph without edges (only with
    vertices)
    :type process_tree: ProcessTreeConcept
    :return: pair: graph and actions index
    :rtype: tuple[ActionsIndex, Graph]
    """

    actions_generator = _gen_actions_vertices(process_tree)
    action_index = ActionsIndex()
    action_graph = Graph()

    for action in actions_generator:
        action_index.add_action(action)
        action_graph.add_vertex(action)

    return action_index, action_graph


def _gen_actions_vertices(process_tree):
    """ Builds list of all actions to be performed during restore
    :type process_tree: ProcessTreeConcept
    :rtype: collections.Iterable
    """
    return itertools.chain(
        _gen_fork_actions(process_tree),
        _gen_create_actions(process_tree),
        _gen_share_actions(process_tree),
        _gen_remove_tmp_resources_actions(process_tree)
    )


def _gen_fork_actions(process_tree):
    """ Simply generates fork actions, which must be performed to
    restore process tree

    :type process_tree: ProcessTreeConcept
    """

    for p in process_tree.processes:
        if p == process_tree.root_process:
            continue
        parent = process_tree.proc_parent(p)
        yield ForkProcessAction(parent=parent,
                                child=p)


def _gen_create_actions(process_tree):
    """ Generates resource creation actions

    :type process_tree: ProcessTreeConcept
    """

    resource_indexer = process_tree.resource_indexer
    all_resources = resource_indexer.all_resources

    for r in all_resources:
        creator = creators.get_resource_creator(process_tree, r)
        handles = creators.get_creator_handles(creator, r)

        if len(handles) != len(r.handle_types):
            raise RuntimeError("Not enough handles for creation of [{}] by [{}]; Have only: [{}]"
                               .format(r, creator, handles))

        yield CreateResourceAction(process=creator,
                                   resource=r,
                                   handles=handles)


def _gen_share_actions(process_tree):
    """ Generates share actions for sharable resources
    """

    resource_indexer = process_tree.resource_indexer  # type: ResourcesIndexer
    sharable_resource = (r for r in resource_indexer.all_resources if r.is_sharable)

    for r in sharable_resource:
        creator = creators.get_resource_creator(process_tree, r)
        creator_handles = creators.get_creator_handles(creator, r)
        creator_handles_map = {type(h): h for h in creator_handles}

        holders = resource_indexer.get_resource_holders(r)

        for p in holders:
            p_handles = p.iter_all_handles(r)

            if p == creator:
                # do not need to share with us if we create it!
                p_handles = (h for h in p_handles if h not in creator_handles)

            for p_handle in p_handles:
                yield ShareResourceAction(process_from=creator,
                                          process_to=p,
                                          handle_from=creator_handles_map[type(p_handle)],
                                          handle_to=p_handle,
                                          resource=r)


def _gen_remove_tmp_resources_actions(process_tree):
    """ Generates RemoveAction for each temporary resource in every process
    :type process_tree: ProcessTreeConcept
    """

    all_processes = process_tree.processes
    for p in all_processes:
        for tmp_resource in p.iter_tmp_resources():
            for tmp_handle in p.get_tmp_handles(tmp_resource):
                yield RemoveResourceAction(process=p,
                                           resource=tmp_resource,
                                           handle=tmp_handle)


class ActionsIndex(object):
    def __init__(self):
        self._actions_by_executor = {}
        self._actions_using_process = {}
        self._fork_actions = []
        self._resource_create_acts = {}

    def add_action(self, action):
        if isinstance(action, ForkProcessAction):
            self._actions_by_executor.setdefault(action.parent, []).append(action)
            self._actions_using_process.setdefault(action.parent, []).append(action)
            self._fork_actions.append(action)

        elif isinstance(action, CreateResourceAction):
            self._actions_by_executor.setdefault(action.process, []).append(action)
            self._actions_using_process.setdefault(action.process, []).append(action)
            if action.resource in self._resource_create_acts:
                raise RuntimeError("Duplicate create action for resource!")
            self._resource_create_acts[action.resource] = action

        elif isinstance(action, ShareResourceAction):
            self._actions_by_executor.setdefault(action.process_from, []).append(action)
            self._actions_using_process.setdefault(action.process_from, []).append(action)
            self._actions_using_process.setdefault(action.process_to, []).append(action)

        elif isinstance(action, RemoveResourceAction):
            self._actions_by_executor.setdefault(action.process, []).append(action)
            self._actions_using_process.setdefault(action.process, []).append(action)

        else:
            raise RuntimeError("unknown action [{}]".format(action))

    def actions_by_executor(self, process):
        """ All actions, which are executed by process
        """
        return self._actions_by_executor[process]

    def actions_involving_process(self, process):
        """ All actions, which are executed by process and
            also involve process in execution (i.e. demand, that
            process is "forked" already)
        """
        return self._actions_using_process[process]

    def process_actions_with_resource(self, process, resource, handle):
        """ All actions, which are executed be specified process and
        involve (resource, handle) pair in execution, i.e. demand that
        (resource, handle) was already created within that process;
        Action, which "creates" the resource not included

        :rtype: list
        """
        all_process_actions = self._actions_by_executor[process]
        return [a for a in all_process_actions
                if self._is_action_with_resource(a, resource, handle)]

    @staticmethod
    def _is_action_with_resource(action, resource, handle):
        if isinstance(action, ShareResourceAction):
            return action.resource == resource and action.handle_from == handle
        if isinstance(action, RemoveResourceAction):
            return action.resource == resource and action.handle == handle

        # CreateResourceAction or ForkAction are not really use the resource, so...
        return False

    def process_obtain_resource_action(self, process, resource, handle):
        """ Returns action, which is responsible for "creation" of resource
        (resource, handle) inside process
        :type process: ProcessConcept
        :type resource: ResourceConcept
        """
        acts_to_check = self._actions_using_process[process]
        for a in acts_to_check:
            # resource action can only be Create action or Share action!

            if isinstance(a, CreateResourceAction) \
                    and a.process == process \
                    and a.resource == resource \
                    and handle in a.handles:
                return a

            if isinstance(a, ShareResourceAction) \
                    and a.resource == resource \
                    and a.process_to == process \
                    and a.handle_to == handle:
                return a

        # if resource is inherited
        if not resource.is_sharable and resource.is_inherited:
            return next(fa for fa in self._fork_actions if fa.child == process)

        # that can't happen if actions were generated correctly =)
        raise RuntimeError("No resource obtain action; process = {}, (r, h) = {}".
                           format(process, (resource, handle)))

    @property
    def fork_actions(self):
        """
        :return: list of fork actions
        :rtype: list[ForkProcessAction]
        """
        return self._fork_actions

    def resource_create_action(self, resource):
        """ Each resource must be created, so for each resource there must be
        the CreateAction
        :rtype: CreateResourceAction
        """

    def resource_remove_action(self, process, r, h):
        acts = self.process_actions_with_resource(process, r, h)
        return next(a for a in acts if isinstance(a, RemoveResourceAction))


def _add_precedence_edges_from_to(actions_from, actions_to, actions_graph):
    """ for each `v in actions_from` for each `u in actions_to` add edge
    (v, u) to the actions graph

    :param actions_from: actions, from which edges will go
    :param actions_to: actions, to which edges will go
    :param actions_graph: graph of actions, where to add edges
    :type actions_graph: Graph
    """

    for v in actions_from:
        for u in actions_to:
            actions_graph.add_edge(v, u)


def _build_precedence_edges(process_tree, actions_index, actions_graph):
    """
    :type process_tree: ProcessTreeConcept
    :type actions_index: ActionsIndex
    :type actions_graph: Graph
    """

    _add_after_fork_edges(actions_index, actions_graph)
    _add_after_resource_creation_edges(process_tree, actions_index, actions_graph)


def _add_after_fork_edges(actions_index, actions_graph):
    # all actions involving a process must be performed AFTER that process is forked

    for fa in actions_index.fork_actions:
        process = fa.child  # fa is an action, which creates process fa.child

        # actions, which are somehow involve process during their execution
        actions = actions_index.actions_involving_process(process)
        _add_precedence_edges_from_to([fa], actions, actions_graph)


def _add_after_resource_creation_edges(process_tree, actions_index, actions_graph):
    """ Each (resource, handle) pair inside each process has corresponding action `cr_r`,
    which is responsible for creation of that pair inside a process; But also there
    are actions, which rely on that (resource, handle) is already created; So this
    function builds edges from action `cr_r` to these actions
    """

    for process in process_tree.processes:
        _add_after_resource_creation_edges_one_proc(process, actions_index, actions_graph)


def _add_after_resource_creation_edges_one_proc(process, actions_index, actions_graph):
    """ Does the thing described in `_add_after_resource_creation_edges` doc comment,
    but for only one process
    """
    for r in process.iter_all_resources():
        for h in process.iter_all_handles(r):
            obtain_act = actions_index.process_obtain_resource_action(process, r, h)
            acts_with_resource = actions_index.process_actions_with_resource(process, r, h)

            _add_precedence_edges_from_to([obtain_act], acts_with_resource, actions_graph)


def _add_before_remove_resource_edges(process_tree, actions_index, actions_graph):
    """ If remove resource action takes place in actions vertices then
    we need to put all other actions with resource before it in the final
    execution scenario;
    This function adds such precedence for temporary resources, which must
    have corresponding remove action
    """
    for p in process_tree.processes:
        _add_before_remove_resource_edges_one_proc(p, actions_index, actions_graph)


def _add_before_remove_resource_edges_one_proc(process, actions_index, actions_graph):
    """ Same as `_add_before_remove_resource_edges_one_proc` but for single process
    :type process: ProcessConcept
    """
    for r in process.iter_tmp_resources():
        for h in process.get_tmp_handles(r):
            acts_with_resource = actions_index.process_actions_with_resource(process, r, h)
            remove_act = next(a for a in acts_with_resource if isinstance(a, RemoveResourceAction))

            # adding precedence edges FROM all acts except remove act TO remove act!
            _add_precedence_edges_from_to((a for a in acts_with_resource if a != remove_act),
                                          [remove_act],
                                          actions_graph)


def _add_inherited_resource_before_fork_edges(process_tree, actions_index, actions_graph):
    """ Some resources are inherited from parent process during fork and shared
    that way. So we have to make sure, that parent creates resource, which is
    shared via inheritance with it's children, before forking these children!
    (here our inheritance closure works for us so we can check only children,
    but not the whole subtree)

    :type process_tree: ProcessTreeConcept
    :type actions_graph: Graph
    :type actions_index: ActionsIndex
    """

    all_resources = process_tree.resource_indexer.all_resources
    only_inherited_resources = (r for r in all_resources if r.is_inherited and not r.is_sharable)

    for inh_r in only_inherited_resources:
        create_action = actions_index.resource_create_action(inh_r)
        creator = create_action.process
        assert len(create_action.handles) == 1  # we do not support multi handle non-sharable resource for now
        handle = create_action.handles[0]

        # only those fork actions, which fork children, who really share the inheritable
        # resource
        fork_acts_which_share = (
            fa for fa in actions_index.fork_actions
            if fa.parent == creator and fa.child.has_resource_at_handle(inh_r, handle)
        )

        _add_precedence_edges_from_to([create_action], fork_acts_which_share)


def _add_cr_dependency_before_resource_edges(actions_index, actions_graph):
    pass


def _add_can_exist_together_restriction_edges(actions_index, actions_graph):
    pass
