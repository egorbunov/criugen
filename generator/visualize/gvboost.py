""" Some graphviz functions wrappers for less boilerplate
"""

import os
import random
import tempfile

import graphviz as gv

from pyutils.func import join_dicts


class GraphVizBuilder(object):
    def __init__(self, attrs=None, graph_attr=None, node_attr=None, edge_attr=None, **kwarg_attrs):
        """

        :param attrs: dictionary, which is scanned for keys 'node', 'graph' or 'edge' to find proper
               attributes
        :param graph_attr: user can pass graph attributes separately, all attributes are joined together
        :param node_attr: node attributes (joined with other node attributes found)
        :param edge_attr: edge attributes
        :param kwarg_attrs: additional graph attributes, passed as keyword arguments
        """
        attrs = attrs if attrs else {}

        self._nodes_map = {}  # type: dict[object, _Node]
        self._edges = []  # type: list[_Edge]
        self._clusters = {}  # type: dict[basestring, _Cluster]

        self._base_graph_attr = join_dicts(attrs['graph'] if 'graph' in attrs else {}, graph_attr, kwarg_attrs)
        self._base_node_attr = join_dicts(attrs['node'] if 'node' in attrs else {}, node_attr)
        self._base_edge_attr = join_dicts(attrs['edge'] if 'edge' in attrs else {}, edge_attr)

    def node(self, v, label=None, cluster_id=None, node_attr=None, **kwarg_attrs):
        """ Adds vertex; Given vertex is distinguished with other using it's hash, so be sure to
        ensure unique hashes for different vertices (nodes)
        """
        if v in self._nodes_map:
            raise RuntimeError("Node is already added")

        node_style = join_dicts(node_attr, kwarg_attrs)
        node_id = str(len(self._nodes_map))
        self._nodes_map[v] = _Node(node_id, label, node_style, cluster_id is not None)

        if cluster_id is not None:
            self._clusters[cluster_id].vertices.append(v)

        return self

    def edge(self, v_a, v_b, edge_attr=None, **kwarg_attrs):
        edge_style = join_dicts(edge_attr, kwarg_attrs)
        if v_a not in self._nodes_map or v_b not in self._nodes_map:
            raise RuntimeError("Unknown nodes")
        self._edges.append(_Edge(v_a, v_b, edge_style))

        return self

    def cluster(self, cluster_id, graph_attr=None, node_attr=None, edge_attr=None, **kwarg_attrs):
        if self.has_cluster(cluster_id):
            raise RuntimeError("Cluster is already added")

        cluster_attr = join_dicts(graph_attr, kwarg_attrs)
        gv_cluster_id = "cluster_{}".format(len(self._clusters))
        self._clusters[cluster_id] = _Cluster(gv_cluster_id,
                                              graph_attr=cluster_attr,
                                              node_attr=node_attr,
                                              edge_attr=edge_attr)
        return self

    def has_cluster(self, cluster_id):
        return cluster_id in self._clusters

    def add_vertices(self, vs, node_attr_factory=lambda x: None, label_factory=lambda x: None):
        for v in vs:
            self.node(v, label=label_factory(v), node_attr=node_attr_factory(v))
        return self

    def build_gv_graph(self, name=None, g_format=None, engine=None):
        graph = gv.Digraph(name=name,
                           format=g_format,
                           engine=engine,
                           graph_attr=self._base_graph_attr,
                           node_attr=self._base_node_attr,
                           edge_attr=self._base_edge_attr)

        for cluster in self._clusters.values():
            with graph.subgraph(name=cluster.cluster_id,
                                graph_attr=cluster.graph_attr,
                                node_attr=cluster.node_attr,
                                edge_attr=cluster.edge_attr) as c:
                for node_id in cluster.vertices:
                    node = self._nodes_map[node_id]
                    c.node(name=node.node_id, label=node.label, **node.attrs)

        for node in self._nodes_map.values():
            if node.is_clustered:
                continue
            graph.node(name=node.node_id, label=node.label, **node.attrs)

        for edge in self._edges:
            graph.edge(tail_name=self._nodes_map[edge.v_from].node_id,
                       head_name=self._nodes_map[edge.v_to].node_id,
                       **edge.attrs)

        return graph


def show_gv_graph(graph, file_suffix="tmp-graph"):
    """ Shows graphViz graph
    :type graph: gv.dot.Dot
    :param file_suffix: to show graph, tmp file is created with name suffix as specified
    """
    tmp_file = os.path.join(tempfile.gettempdir(), "{}-{}".format(random.randint(1, 100000), file_suffix))
    graph.view(filename=tmp_file)


class _Node(object):
    def __init__(self, node_id, label, attrs, is_clustered):
        self.node_id = node_id
        self.label = label
        self.attrs = attrs
        self.is_clustered = is_clustered


class _Edge(object):
    def __init__(self, v_a, v_b, attrs):
        self.v_from = v_a
        self.v_to = v_b
        self.attrs = attrs


class _Cluster(object):
    def __init__(self, gv_cluster_id, graph_attr, node_attr, edge_attr):
        self.cluster_id = gv_cluster_id
        self.graph_attr = graph_attr
        self.node_attr = node_attr
        self.edge_attr = edge_attr
        self.vertices = []

    def add_vertex(self, v_id):
        self.vertices.append(v_id)
