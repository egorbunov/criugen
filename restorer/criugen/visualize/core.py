import graphviz as gv

from pyutils.graph import DirectedGraph
from abstractir.actions import *
import labels
import gvboost
from pyutils.func import update_dict


def render_actions_graph(actions_graph, output_file, type='svg', view=False, layout='LR', do_cluster=False):
    """ Renders actions graph to
    :param view:
    :param actions_graph: actions graph
    :param output_file: file to write svg (svg extension is not obligatory)
    :param type: type of output rendered image
    :param view: flag, if set to True, then graph will be shown immediately
    :type actions_graph: DirectedGraph
    """
    gv_graph = _generate_graphviz_graph(actions_graph,
                                        g_format=type,
                                        rankdir_layout=layout,
                                        do_cluster=do_cluster)
    gv_graph.render(filename=output_file)
    if view:
        gv_graph.view()


def _generate_graphviz_graph(actions_graph, g_format='svg', rankdir_layout='LR', do_cluster=False):
    """

    :param actions_graph: our DirectedGraph with actions
    :param g_format: graphviz graph format
    :return:
    """
    graph = gv.Digraph(format=g_format)
    graph.attr(rankdir=rankdir_layout)
    gvboost.apply_styles(graph, _get_common_styles())

    node_ids = _add_actions_vertices_to_graph(graph, actions_graph.vertices_iter, do_cluster)

    for u, v in actions_graph.edges_iter:
        graph.edge(node_ids[u], node_ids[v])

    return graph


def _add_actions_vertices_to_graph(graph, vertices, do_cluster=False):
    node_ids = {}  # type: dict[object, basestring]
    clusters = {}  # from process concept to action list

    for idx, action in enumerate(vertices):
        str_id = str(idx)  # graphviz wants string -_-
        node_ids[action] = str_id

        process = get_action_executor(action)

        if do_cluster:
            clusters.setdefault(process, []).append(action)
        else:
            gvboost.set_styles(graph, _get_action_node_style(action))
            graph.node(str_id, labels.get_action_vertex_label(action))

    if do_cluster:
        # nodes are not added yet
        for idx, process in enumerate(clusters.keys()):
            print(process.minimalistic_repr)
            with graph.subgraph(name="cluster_{}".format(idx)) as c:
                c.attr(style='bold, dashed, rounded')
                c.attr(color='red')
                for node in clusters[process]:
                    gvboost.set_styles(c, _get_action_node_style(node))
                    c.node_attr.update(style='filled', color='white')
                    c.node(node_ids[node], labels.get_action_vertex_label(node))

    return node_ids


def _get_common_styles():
    return {
        'grap': {
            'label': 'A Fancy Graph',
            'fontsize': '13',
            'fontcolor': 'black',
            'bgcolor': '#ffffff',
        },
        'node': {
            'shape': 'rectangle',
            'fontcolor': 'black',
            'color': 'black',
            'style': 'filled',
            'fillcolor': '#006699',
        }
    }


def _get_action_node_style(action):
    common_node_style = {
        'shape': 'rectangle',
        'fontcolor': 'black',
        'color': 'black',
        'style': 'filled',
        'fontname': 'Verdana'
    }

    if isinstance(action, ShareResourceAction):
        return {
            'node': update_dict({
                'fillcolor': '#f9cbc5'
            }, common_node_style)
        }
    if isinstance(action, CreateResourceAction):
        return {
            'node': update_dict({
                'fillcolor': '#f9cbc5'
            }, common_node_style)
        }
    if isinstance(action, RemoveResourceAction):
        return {
            'node': update_dict({
                'fillcolor': '#d9f2f9'
            }, common_node_style)
        }
    if isinstance(action, ForkProcessAction):
        return {
            'node': update_dict({
                'fillcolor': '#e5f9c5'
            }, common_node_style)
        }
