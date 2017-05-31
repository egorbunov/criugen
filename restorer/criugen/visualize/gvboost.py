""" Some graphviz functions wrappers for less boilerplate
"""


def apply_styles(graph, styles):
    """ Adds styles to graph
    """
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('node' in styles and styles['node']) or {}
    )
    graph.edge_attr.update(
        ('edge' in styles and styles['edge']) or {}
    )
    return graph


def set_styles(graph, styles):
    if 'graph' in styles:
        graph.attr('graph', **styles['graph'])
    if 'node' in styles:
        graph.attr('node', **styles['node'])
    if 'edge' in styles:
        graph.attr('edge', **styles['edge'])
