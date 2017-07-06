""" Out graph impl testing
"""

import random
import unittest

import pyutils.graph as g


def _generate_acyclic_graph(node_cnt=100):
    nodes = range(node_cnt)
    graph = g.DirectedGraph()

    for node in nodes:
        graph.add_vertex(node)

    for node_from in nodes:
        for node_to in range(node_from + 1, node_cnt):
            if random.randint(a=0, b=2) == 1:
                assert node_from < node_to
                graph.add_edge(node_from, node_to)

    return graph


class TestDirectedGraph(unittest.TestCase):
    def test_top_sort(self):
        test_cnt = 40
        max_graph_size = 250
        min_graph_size = 0

        for i in range(test_cnt):
            graph_size = random.randint(a=min_graph_size, b=max_graph_size)
            graph = _generate_acyclic_graph(node_cnt=graph_size)
            lst = list(g.topological_sort(graph))
            self.assertEqual(len(lst), graph.vertex_num)

    def test_bucket_top_sort(self):
        max_graph_size = 250
        min_graph_size = 0

        graph_size = random.randint(a=min_graph_size, b=max_graph_size)
        graph = _generate_acyclic_graph(node_cnt=graph_size)
        buckets = g.bucket_top_sort(graph)


if __name__ == '__main__':
    unittest.main()
