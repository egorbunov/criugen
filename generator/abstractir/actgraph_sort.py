""" Actions graph topological sorting
"""

from itertools import chain

from model_interpreter import *
from pyutils.graph import DirectedGraph, bucket_top_sort


def get_actions_buckets(act_graph):
    """
    Generates action buckets as a map from depth to list of vertices;
    action vertices on depth N must be executed after all action vertices
    on depth M < N. This buckets can be used to execute actions in parallel,
    because actions in the same bucket are independent
    """
    action_buckets = bucket_top_sort(act_graph)
    return action_buckets


def sort_actions_graph(act_graph):
    """ Performs topological sort on the graph; For now it works for any graph, actually,
    without any dependency on vertex type;

    FIXME: THIS TODO IS PROBABLY OUTDATED!!!!!!!!!!!!!!!!!
    TODO: we need to support priorities on actions (vertices), because we may want to have
    TODO: another properties for the sorted list, but not only it's topological order:
    TODO: * We want, that ForkAction is executed as soon as possible and we don't want
    TODO:   for a `inherited` (may be sharable) resources to be inherited if that is not needed
    TODO: * Also we may want to have `private` resources restoration actions to be at
    TODO:   the very bottom of the list, because that will help us in the future to organize
    TODO:   everything with that CRIU restoration contexts (restorer blob phase and stuff)

    :param act_graph: directed graph to sort
    :type act_graph: DirectedGraph
    :return: list of topologically sorted vertices (actions)
    """

    buckets = get_actions_buckets(act_graph)

    min_depth = min(buckets)
    max_depth = max(buckets)

    def sorted_buckets_generator():
        for depth in range(min_depth, max_depth + 1):
            yield buckets[depth]

    sorted_actions = list(chain.from_iterable(sorted_buckets_generator()))
    sorted_actions = _remove_not_needed_due_inheritance_actions(sorted_actions)

    return sorted_actions


def _remove_not_needed_due_inheritance_actions(sorted_actions):
    """ Removing not needed share actions from list, which can be skipped
        due to resource inheritance
    """
    new_actions = []
    interpreter = ModelInterpreter()

    for action in sorted_actions:
        try:
            interpreter.execute_action(action)
            new_actions.append(action)
        except ResourceAlreadyExistsOnShare as e:
            # means, that resource was actually inherited
            pass

        # TODO: optimize this piece of code
        # adding remove actions for not needed inherited resources
        if isinstance(action, ForkProcessAction):
            model_child = action.child
            real_child = interpreter.processes_map[action.child.pid]
            remove_acts = []

            for r, h in real_child.iter_all_resource_handle_pairs():
                if model_child.has_resource_at_handle(r, h):
                    continue

                new_remove_act = RemoveResourceAction(process=model_child,
                                                      resource=r,
                                                      handle=h)

                new_actions.append(new_remove_act)
                remove_acts.append(new_remove_act)

            # executing remove actions on the model
            for ra in remove_acts:
                interpreter.execute_action(ra)

    return new_actions
