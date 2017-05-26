""" Functions, which perform closure of process tree against several properties:

* resource dependencies
* inherited resources
* multi-handle resources
"""

from pstree import ProcessTreeConcept
from resource_concepts import ResourceConcept
import util


def perform_process_tree_closure(process_tree):
    """ Adds needed temporary resources to processes in the process tree.
    These temporary resources are needed for easier action generations algorithms.
    They ensure, that processes states are "complete" to get all needed information
    for actions generation.
    
    :param process_tree: process tree
    :type process_tree: ProcessTreeConcept
    """
    _close_against_dependencies(process_tree)
    _close_against_inheritance(process_tree)
    _close_against_multi_handle_resources(process_tree)


def _close_against_dependencies(process_tree):
    """ For each resource `r` in each process `P` from given tree,
    adds resources, which are needed for `r` creation if they
    are not handled by `P`.
    
    :param process_tree: process tree
    :type process_tree: ProcessTreeConcept
    """
    for process in process_tree.processes:
        _close_against_dependencies_one_process(process)


def _close_against_dependencies_one_process(process):
    resources_to_check = set(process.iter_all_resources())  # type: set[ResourceConcept]

    while len(resources_to_check) > 0:
        next_to_check = set()

        for r in resources_to_check:
            not_in_process = set(d for d in r.dependencies if not process.has_resource(d))
            for d in not_in_process:
                process.add_tmp_resource_with_auto_handle(d)
            next_to_check |= not_in_process

        resources_to_check = next_to_check


def _close_against_inheritance(process_tree):
    """ Fills "holes" in a forest of processes, which share the same 
    resource `r` with handle `h`, that can be shared only with inheritance (at fork).
    After this operation every set of processes `resourceHolders(r, h)`, which
    hold resource `(r, h)` is a tree (not a forest).
    
    :param process_tree: process tree
    :type process_tree: ProcessTreeConcept
    """
    resource_indexer = process_tree.resource_indexer
    all_resources_and_handles = resource_indexer.all_resources_handles

    # for this procedure we need to know depths of the processes
    # in the process tree
    process_depths_map = {}  # type: dict[ProcessConcept, int]

    def calc_node_depth(p):
        if p == process_tree.root_process:
            process_depths_map[p] = 0
        else:
            process_depths_map[p] = process_depths_map[process_tree.proc_parent(p)] + 1

    process_tree.dfs(pre_visit=process_depths_map)

    for (r, h) in all_resources_and_handles:
        if r.is_sharable or not r.is_inherited:
            # inheritance sharing can be avoided
            continue
        holders = resource_indexer.get_resource_handle_holders(r, h)
        _close_forest_against_resource(process_tree, process_depths_map, holders, r, h)


def _close_forest_against_resource(process_tree, process_depths_map, forest, r, h):
    """
    :type process_tree: ProcessTreeConcept
    :param process_depths_map: map from process to depth of that process in the tree
    :param forest: list of processes, which share (r, h)
    :type forest: list[ProcessConcept]
    :param r: resource, which can be shared only at fork (via inheritance)
    :type r: ProcessTreeConcept
    :param h: handle to the resource
    """

    roots = util.find_processes_roots(forest)

    # the topmost process in the forest, he will create the resource
    root = max(roots, key=lambda p: -process_depths_map[p])

    # after that cycle resource (r, h) holders must form
    # a tree
    for p in roots:
        if p == root:
            continue

        cur_p = process_tree.proc_parent(p)
        while not cur_p.has_resource_at_handle(r, h):
            cur_p.add_tmp_resource(r, h)
            cur_p = process_tree.proc_parent(cur_p)


def _close_against_multi_handle_resources(process_tree):
    """ Ensures, that process, which is responsible for creation of sharable
    multi-handle resource has all "parts" of that resource.
    
    :param process_tree: process tree
    :type process_tree: ProcessTreeConcept
    """

    resource_indexer = process_tree.resource_indexer
    # all_resources =