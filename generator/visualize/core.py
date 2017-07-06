import functools

import graphviz as gv

import gvboost
import pyutils.func as func
import pyutils.graph as graph_util
import styles
import visualize.actions_labels as labels
from abstractir.actions import *
from abstractir.pstree import ProcessTreeConcept


class VisualizeOptions(object):
    def __init__(self,
                 output_file=None,
                 output_type='svg',
                 layout_dir='LR',
                 engine='dot',
                 do_show=False):
        self.output_file = output_file
        self.output_type = output_type
        self.layout_dir = layout_dir
        self.engine = engine
        self.do_show = do_show


def make_gv_graph(graph,
                  vis_opts,
                  base_graph_attr=styles.BASE_GRAPH_ATTRS,
                  base_node_attr=styles.BASE_NODE_ATTRS,
                  base_edge_attr=styles.BASE_EDGE_ATTRS,
                  clusterer_function=lambda _: None,
                  cluster_attr_factory=lambda _: {},
                  node_label_factory=lambda _: "",
                  node_attr_factory=lambda node: {},
                  edge_attr_factory=lambda edge: {}):
    """ Builds graphviz dot graph from given objects graph (GraphInterface)

    :param graph: graph to draw
    :type graph: graph_util.GraphInterface
    :param vis_opts: visualize options
    :type vis_opts: VisualizeOptions
    :param base_edge_attr: default graph edge attributes
    :param base_node_attr: default graph node attributes
    :param base_graph_attr: default graph attributes
    :param clusterer_function: function, which gives cluster id for specified vertex/node
    :param cluster_attr_factory: function, which returns cluster graph attrs for given cluster id
    :param node_label_factory: function, which returns string label for given node
    :param node_attr_factory: function, which returns attributes dictionary for given node
    :param edge_attr_factory: function, which returns edge attributes dictionary for given edge

    :return Dot Graph
    """

    gv_builder = gvboost.GraphVizBuilder(graph_attr=base_graph_attr,
                                         node_attr=base_node_attr,
                                         edge_attr=base_edge_attr)

    for node in graph.vertices_iter:
        cluster_id = clusterer_function(node)
        if cluster_id is not None and not gv_builder.has_cluster(cluster_id):
            gv_builder.cluster(cluster_id, graph_attr=cluster_attr_factory(cluster_id))

        gv_builder.node(node,
                        label=node_label_factory(node),
                        cluster_id=cluster_id,
                        node_attr=node_attr_factory(node))

    for edge in graph.edges_iter:
        gv_builder.edge(edge[0], edge[1], edge_attr=edge_attr_factory(edge))

    return gv_builder.build_gv_graph(g_format=vis_opts.output_type, engine=vis_opts.engine)


def render_actions_graph(actions_graph,
                         do_process_cluster=False,
                         node_buckets=None,
                         vis_opts=None):
    """ Renders actions graph to

    :param actions_graph: actions graph
    :type actions_graph: graph_util.DirectedGraph
    :param do_process_cluster: adds actions clusters by action executor
    :param node_buckets: dict from depth to list of vertices, which encodes vertices buckets
    :param vis_opts: visualisation options
    :type vis_opts: VisualizeOptions
    """

    vis_opts = vis_opts if vis_opts else VisualizeOptions()

    cluster_fun = func.val_returner(None)
    cluster_attr_factory = func.val_returner({})

    if node_buckets:
        reverse_buckets = {v: k for k, vs in node_buckets.iteritems() for v in vs}

        def cluster_fun(node): return reverse_buckets[node]

        def cluster_attr_factory(cluster):
            return {
                'style': 'bold, dashed, rounded, filled',
                'color': 'blue'
            }

    if do_process_cluster:
        def cluster_fun(node): return get_action_executor(node)

        def cluster_attr_factory(cluster):
            return {
                'style': 'bold, dashed, rounded, filled',
                'color': 'blue'
            }

    gv_graph = make_gv_graph(actions_graph,
                             vis_opts,
                             clusterer_function=cluster_fun,
                             cluster_attr_factory=cluster_attr_factory,
                             node_label_factory=labels.get_action_vertex_label,
                             node_attr_factory=styles.get_action_node_style)

    _save_and_show(gv_graph, vis_opts, show_tmp_suffix="actions-graph")


def render_pstree(process_tree,
                  vis_opts=None,
                  skip_tmp_resources=False,
                  draw_fake_root=False):
    """ Renders process tree

    :param process_tree: process tree (ProcessTreeConcept)
    :type process_tree: ProcessTreeConcept
    :param vis_opts: visualization options
    :type vis_opts: VisualizeOptions
    :param skip_tmp_resources: if True, no temporary resources rendered
    :param draw_fake_root: if True, then process tree root is drawn
    """
    from process_label import get_proc_label

    if draw_fake_root:
        filtered_pstree = process_tree
    else:
        filtered_pstree = graph_util.VertexFilteredGraph(process_tree,
                                                         vertex_filter=lambda v: v != process_tree.root_process)

    gv_graph = make_gv_graph(filtered_pstree,
                             vis_opts=vis_opts,
                             base_node_attr=styles.get_process_node_style(),
                             node_label_factory=functools.partial(get_proc_label, no_tmp=skip_tmp_resources))

    _save_and_show(gv_graph, vis_opts, show_tmp_suffix="actions-list")


def render_actions_list(actions_list, vis_opts=None):
    """ Renders given actions list as a node sequence with arrows from i to i + 1

    :param actions_list: list of actions
    :param vis_opts: visualization options
    :type vis_opts: VisualizeOptions
    """
    graph = graph_util.make_chain_graph(actions_list)
    gv_graph = make_gv_graph(graph, vis_opts,
                             node_label_factory=labels.get_action_vertex_label,
                             node_attr_factory=styles.get_action_node_style)

    _save_and_show(gv_graph, vis_opts, show_tmp_suffix="actions-list")


def render_actions_cycle(cycle, vis_opts):
    """ Renders given actions list as a cycle

    :param cycle: list of actions
    :param vis_opts: visualization options
    :type vis_opts: VisualizeOptions
    """

    graph = graph_util.make_cycle_graph(cycle)
    vis_opts.engine = 'circo'
    gv_graph = make_gv_graph(graph, vis_opts,
                             node_label_factory=labels.get_action_vertex_label,
                             node_attr_factory=styles.get_action_node_style)

    _save_and_show(gv_graph, vis_opts, show_tmp_suffix="actions-cycle")


def _save_and_show(gv_graph, vis_opts, show_tmp_suffix="tmp-graph"):
    """
    :type gv_graph: gv.dot.Dot
    :type vis_opts: VisualizeOptions
    """

    if vis_opts.output_file:
        gv_graph.render(filename=vis_opts.output_type)

    if not vis_opts.output_file or vis_opts.do_show:
        gvboost.show_gv_graph(gv_graph, show_tmp_suffix)
