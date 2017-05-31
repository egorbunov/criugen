import graphviz as gv

from pyutils.graph import DirectedGraph
from abstractir.actions import *
import labels


def render_actions_graph_svg(actions_graph, output_file):
    """ Renders actions graph to svg
    :param actions_graph: actions graph
    :param output_file: file to write svg (svg extension is not obligatory)
    :type actions_graph: DirectedGraph
    """
    gv_graph = _generate_graphviz_graph(actions_graph)
    gv_graph.render(filename=output_file)


def _generate_graphviz_graph(actions_graph, g_format='svg'):
    graph = gv.Digraph(format=g_format)

    node_ids = {}  # type: dict[object, basestring]

    for idx, action in enumerate(actions_graph.vertices_iter):
        str_id = str(idx)  # graphviz wants string -_-
        node_ids[action] = str_id
        graph.node(str_id, labels.get_action_vertex_label(action))

    for u, v in actions_graph.edges_iter:
        graph.edge(node_ids[u], node_ids[v])

    return graph
