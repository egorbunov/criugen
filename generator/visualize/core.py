import graphviz as gv

import gvboost
import visualize.actions_labels as labels
from abstractir.actions import *
from abstractir.pstree import ProcessTreeConcept
from pyutils.func import update_dict
from pyutils.graph import DirectedGraph
import random
import tempfile
import os


def render_actions_graph(actions_graph,
                         output_file=None,
                         output_type='svg',
                         view=False,
                         layout='LR',
                         do_process_cluster=False,
                         node_buckets=None):
    """ Renders actions graph to

    :param actions_graph: actions graph
    :param output_file: file to write drawing
    :param output_type: type of output rendered image
    :param view: is set, then drawing is shown immediately after graph generation
    :param layout: graphviz graph layout: ['LR', 'TB' ,...]
    :param do_process_cluster: adds actions clusters by action executor
    :type actions_graph: DirectedGraph
    :param node_buckets: dict from depth to list of vertices, which encodes vertices buckets
    """

    gv_graph = _init_common_graphviz_graph(g_format=output_type, rankdir_layout=layout)
    _fill_graphviz_graph_actions(actions_graph,
                                 gv_graph,
                                 do_cluster=do_process_cluster,
                                 node_buckets=node_buckets)
    if output_file:
        gv_graph.render(filename=output_file)

    if not output_file or view:
        tmp_file = os.path.join(tempfile.gettempdir(), "{}-act-graph".format(random.randint(1, 1000000)))
        gv_graph.view(filename=tmp_file)


def render_pstree(process_tree,
                  output_file=None, output_type='svg', view=False, layout='LR',
                  to_skip_resource_types=(), no_tmp=False, draw_fake_root=False):
    """ Renders process tree

    :param process_tree: process tree (ProcessTreeConcept)
    :type process_tree: ProcessTreeConcept
    :param output_file: file to write drawing
    :param output_type: type of output rendered image
    :param view: is set, then drawing is shown immediately after graph generation
    :param layout: graphviz graph layout: ['LR', 'TB' ,...]
    :param to_skip_resource_types: list of resource types to skip in render
    :param no_tmp: if set, no temporary resources rendered
    """
    import process_label as pl

    gv_graph = _init_common_graphviz_graph(g_format=output_type, rankdir_layout=layout)
    gvboost.set_styles(gv_graph, _get_process_node_style())

    for p in process_tree.processes:
        if p == process_tree.root_process or draw_fake_root:
            continue
        gv_graph.node(str(p.pid), pl.get_proc_label(p, to_skip_resource_types, no_tmp))

    gv_graph.edges((str(p.pid), str(c.pid)) for p in process_tree.processes
                   for c in process_tree.proc_children(p)
                   if p != process_tree.root_process or draw_fake_root)

    if output_file:
        gv_graph.render(filename=output_file)
    if not output_file or view:
        tmp_file = os.path.join(tempfile.gettempdir(), "{}-pstree-graph".format(random.randint(1, 1000000)))
        gv_graph.view(filename=tmp_file)


def render_actions_list(actions_list, output_file, type='svg', view=False, layout='LR'):
    """ Renders list of actions as a graph =) without edges

    :param actions_list: list of actions
    :param output_file: file to write drawing
    :param type: type of output drawing
    :param view: flag, if set to True, then graph will be shown immediately
    :param layout: graphviz graph layout: ['LR', 'TB' ,...]
    """
    gv_graph = _init_common_graphviz_graph(g_format=type, rankdir_layout=layout)
    node_ids = _add_actions_vertices_to_graph(gv_graph, actions_list, cluster_by_process=False)

    for i in range(len(actions_list)):
        if i == len(actions_list) - 1:
            continue
        gv_graph.edge(node_ids[actions_list[i]], node_ids[actions_list[i + 1]])

    if output_file:
        gv_graph.render(filename=output_file)
    if not output_file or view:
        tmp_file = os.path.join(tempfile.gettempdir(), "{}-actlist-graph".format(random.randint(1, 1000000)))
        gv_graph.view(filename=tmp_file)


def render_actions_cycle(cycle, output_file, type, view):
    gv_graph = _init_common_graphviz_graph(g_format=type, engine='circo')
    node_ids = _add_actions_vertices_to_graph(gv_graph, cycle, cluster_by_process=False)

    for i in range(len(cycle)):
        gv_graph.edge(node_ids[cycle[i]], node_ids[cycle[(i + 1) % len(cycle)]])

    if output_file:
        gv_graph.render(filename=output_file)
    if not output_file or view:
        tmp_file = os.path.join(tempfile.gettempdir(), "{}-actcycle-graph".format(random.randint(1, 1000000)))
        gv_graph.view(filename=tmp_file)


def _init_common_graphviz_graph(g_format='svg', rankdir_layout='LR', engine='dot'):
    graph = gv.Digraph(format=g_format, engine=engine)
    graph.attr(rankdir=rankdir_layout)
    gvboost.apply_styles(graph, _get_common_styles())
    return graph


def _fill_graphviz_graph_actions(actions_graph, gv_graph, do_cluster=False, node_buckets=None):
    if node_buckets:
        node_ids = _add_actions_buckets_to_graph(gv_graph, node_buckets)
    else:
        node_ids = _add_actions_vertices_to_graph(gv_graph, actions_graph.vertices_iter, do_cluster)

    for u, v in actions_graph.edges_iter:
        gv_graph.edge(node_ids[u], node_ids[v])

    return gv_graph


def _add_actions_buckets_to_graph(gv_graph, buckets):
    """ Adds bucket clusters to graph
    :type buckets: dict[int, list[object]]
    """
    node_ids = {}  # type: dict[object, basestring]

    for depth, bucket in buckets.iteritems():
        with gv_graph.subgraph(name="cluster_{}".format(depth)) as c:
            c.attr(style='bold, dashed, rounded, filled')
            c.attr(color='blue')
            for idx, node in enumerate(bucket):
                node_ids[node] = "{}_{}".format(depth, idx)
                gvboost.set_styles(c, _get_action_node_style(node))
                c.node_attr.update(style='filled', color='white')
                c.node(node_ids[node], labels.get_action_vertex_label(node))

    return node_ids


def _add_actions_vertices_to_graph(graph, vertices, cluster_by_process=False):
    node_ids = {}  # type: dict[object, basestring]
    process_clusters = {}  # from process concept to action list

    for idx, action in enumerate(vertices):
        str_id = str(idx)  # graphviz wants string -_-
        node_ids[action] = str_id

        process = get_action_executor(action)

        if cluster_by_process:
            process_clusters.setdefault(process, []).append(action)
        else:
            gvboost.set_styles(graph, _get_action_node_style(action))
            graph.node(str_id, labels.get_action_vertex_label(action))

    if cluster_by_process:
        # nodes are not added yet
        for idx, process in enumerate(process_clusters.keys()):
            with graph.subgraph(name="cluster_{}".format(idx)) as c:
                c.attr(style='bold, dashed, rounded')
                c.attr(color='red')
                for node in process_clusters[process]:
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
        },
        'edge': {
            'color': 'black'
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
                'fillcolor': '#f9e47f'
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


def _get_process_node_style():
    common_node_style = {
        'shape': 'rectangle',
        'fontcolor': 'black',
        'color': 'black',
        'style': 'invisible',
        'fontname': 'Verdana'
    }

    return {
        'node': update_dict({
            'fillcolor': '#f9e47f'
        }, common_node_style)
    }