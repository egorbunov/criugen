import func


class DirectedGraph(object):
    class NoSuchVertex(Exception):
        def __init__(self, vertex):
            super(DirectedGraph.NoSuchVertex, self).__init__("{}".format(vertex))

    class VertexAlreadyExists(Exception):
        def __init__(self, vertex):
            super(DirectedGraph.VertexAlreadyExists, self).__init__("{}".format(vertex))

    def __init__(self):
        self._adjacency_list = {}  # vertex --> set[vertex]

    @property
    def vertex_num(self):
        return len(self._adjacency_list)

    @property
    def vertices_iter(self):
        return self._adjacency_list.iterkeys()

    @property
    def edges_iter(self):
        for v in self._adjacency_list:
            for u in self._adjacency_list[v]:
                yield (v, u)

    def add_edge(self, v_from, v_to):
        if v_from not in self._adjacency_list:
            raise DirectedGraph.NoSuchVertex(v_from)
        if v_to not in self._adjacency_list:
            raise DirectedGraph.NoSuchVertex(v_to)

        self._adjacency_list[v_from].add(v_to)

    def add_vertex(self, vertex):
        if vertex in self._adjacency_list:
            raise DirectedGraph.VertexAlreadyExists(vertex)

        self._adjacency_list[vertex] = set()

    def remove_vertices(self, vertices):
        """ Removes given vertices set from graph; all involved
        edges are removed too;

        Warning: that is time-consuming operation: O(E)

        :param vertices: vertices set
        """
        for v in vertices:
            del self._adjacency_list[v]

        for v in self._adjacency_list.keys():
            self._adjacency_list[v] -= vertices  # set difference

    def vertex_neighbours(self, vertex):
        if vertex not in self._adjacency_list:
            raise DirectedGraph.NoSuchVertex(vertex)

        return self._adjacency_list[vertex]

    def dfs_from(self, v_from, pre_visit=func.noop_fun, post_visit=func.noop_fun):
        """ Traverses one connected component of the graph, which
        contains `v_from` vertex; Also it invokes pre_visit function
        for each vertex v before visiting it's neighbourhood and invokes
        post_visit after traversing all vertices, which can be reached from
        this vertex (on exit).

        pre_visit function may be invoked twice for one vertex, because it is
        invoked before check if vertex was already visited;
        post_visit function invoked only once for one each traversed vertex

        :param v_from:  vertex, from which we start dfs
        :param pre_visit: pre visit procedure
        :type pre_visit: (vertex: object) -> ...
        :param post_visit: post visit procedure
        :type post_visit: (vertex: object) -> ...
        """
        if v_from not in self._adjacency_list:
            raise DirectedGraph.NoSuchVertex(v_from)

        visited_map = {v: False for v in self.vertices_iter}
        self._dfs(v_from, pre_visit, post_visit, visited_map)

    def dfs(self, pre_visit=func.noop_fun, post_visit=func.noop_fun):
        """ Same as dfs_from, but performs dfs of the whole graph
        (all graph components). Starting vertex is not specified

        pre_visit and post_visit functions are invoked for each visited
        vertex: pre_visit right before traversing "children" of current node
        (and before checking if it was already visited) and post_visit is
        called right after traversing all 'children'

        the same context is passed to pre_visit and post_visit functions;
        it can be used to store dfs data, there are already context['visited']
        map from vertex to boolean, which designates which vertices were already
        visited

        """
        self.dfs_in_order(self.vertices_iter, pre_visit, post_visit)

    def dfs_in_order(self, vertices_list, pre_visit=func.noop_fun, post_visit=func.noop_fun):
        """ See dfs doc comment, but:
        vertices_list: list of vertices, which will be scanned left to right to perform dfs
        """
        visited_map = {v: False for v in self.vertices_iter}
        for v in vertices_list:
            if visited_map[v]:
                continue
            self._dfs(v, pre_visit, post_visit, visited_map)

    def _dfs(self, cur_v, pre_visit, post_visit, visited_map):
        pre_visit(cur_v)

        if visited_map[cur_v]:
            return
        visited_map[cur_v] = True

        for v in self._adjacency_list[cur_v]:
            self._dfs(v, pre_visit, post_visit, visited_map)

        post_visit(cur_v)


class GraphIsNotAcyclic(Exception):
    def __init__(self, cycle):
        super(GraphIsNotAcyclic, self).__init__(cycle)
        self.cycle = cycle


def topological_sort(graph):
    """ Sorts graph topologically

    :param graph: graph to sort
    :type graph: DirectedGraph
    :return: list iterator of vertices sorted topologically or exception is
             raised in case graph is not acyclic
    """
    sorted_actions = []

    def post_visit(vertex):
        sorted_actions.append(vertex)

    top_sort_dfs = _dfs_stack(_cycle_search_dfs(),
                              post_visit=post_visit)
    # run dfs
    top_sort_dfs(graph)

    return reversed(sorted_actions)


def bucket_top_sort(graph):
    """ Performs topological sort and returns level-buckets of vertices
    :type graph: DirectedGraph
    :rtype: dict[int, list[object]]
    """

    # we need to check vertices in topological order
    # if we want to correctly calculate depths
    top_sort_order = list(topological_sort(graph))
    vertex_index = {}
    for idx, v in enumerate(top_sort_order):
        vertex_index[v] = idx

    depths = {}
    # dynamically calculating depths
    for v in top_sort_order:
        for u in graph.vertex_neighbours(v):
            if depths.setdefault(u, 0) < depths.setdefault(v, 0) + 1:
                depths[u] = depths[v] + 1

    buckets = {}
    for v, d in depths.iteritems():
        buckets.setdefault(d, []).append(v)

    return buckets


def _bucket_top_sort_dfs(v_from, graph, vertex_priority_map, visited, depth, buckets):
    if v_from in visited:
        return

    visited.add(v_from)
    neighbours = graph.vertex_neighbours(v_from)
    sorted_neigh = sorted(neighbours, key=lambda x: vertex_priority_map[x])

    for u in sorted_neigh:
        _bucket_top_sort_dfs(u, graph, vertex_priority_map, visited, depth + 1, buckets)

    buckets.setdefault(depth, []).append(v_from)


def _cycle_search_dfs():
    no_color = 0
    entered_color = 1
    exited_color = 2
    vertex_color = {}
    vertex_stack = []

    def pre_visit(vertex):
        cur_color = vertex_color.setdefault(vertex, no_color)

        if cur_color == entered_color:
            # already entered there!
            idx = vertex_stack.index(vertex)
            raise GraphIsNotAcyclic(vertex_stack[idx:])

        if cur_color == exited_color:
            # we are already traversed from this vertex, so we not entering it again
            return

        vertex_stack.append(vertex)

        vertex_color[vertex] = entered_color

    def post_visit(vertex):
        vertex_stack.pop()
        vertex_color[vertex] = exited_color

    dfs = _dfs_init()
    return _dfs_stack(dfs, pre_visit, post_visit)


class _DfsStack(object):
    def __init__(self):
        self._post_visitors = []
        self._pre_visitors = []

    def add_visitors(self, pre_visit, post_visit):
        self._pre_visitors.append(pre_visit)
        self._post_visitors.append(post_visit)

    def __call__(self, graph):
        """
        :type graph: DirectedGraph
        """

        def chained_pre_visit(cur_v):
            for f in self._pre_visitors:
                f(cur_v)

        def chained_post_visit(cur_v):
            for f in self._post_visitors:
                f(cur_v)

        graph.dfs(
            pre_visit=chained_pre_visit,
            post_visit=chained_post_visit
        )


def _dfs_stack(dfs, pre_visit=func.noop_fun, post_visit=func.noop_fun):
    """ Add pre and post visit functions to dfs object
    :type dfs: _DfsStack
    """
    dfs.add_visitors(pre_visit, post_visit)
    return dfs


def _dfs_init():
    """ No operation dfs traversal
    """
    return _DfsStack()
