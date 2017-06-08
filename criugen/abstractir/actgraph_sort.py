""" Actions graph topological sorting
"""

from pyutils.graph import DirectedGraph, topological_sort


def sort_actions_graph(act_graph):
    """ Performs topological sort on the graph; For now it works for any graph, actually,
    without any dependency on vertex type;

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

    sorted_actions = topological_sort(act_graph)
    return list(sorted_actions)
