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
        """
        pass

    def _dfs(self, cur_v, pre_visit, post_visit, visited_map):
        pre_visit(cur_v)

        if visited_map[cur_v]:
            return
        visited_map[cur_v] = True

        for v in self._adjacency_list[cur_v]:
            self._dfs(v, pre_visit, post_visit, visited_map)

        post_visit(cur_v)
