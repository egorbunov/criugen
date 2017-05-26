""" Functions, which perform closure of process tree against several properties:

* resource dependencies
* inherited resources
* multi-handle resources
"""

from pstree import ProcessTreeConcept
from resource_concepts import ResourceConcept
import util
import creators


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
            not_in_process = set((dep_r, handle_type) for (dep_r, handle_type) in r.dependencies
                                 if not process.has_resource(dep_r))
            for (d, h) in not_in_process:
                process.add_tmp_resource_with_auto_handle(d, h)
            next_to_check |= set(r for r, h in not_in_process)  # TODO: maybe make it more efficient

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

    for (r, h) in all_resources_and_handles:
        if r.is_sharable or not r.is_inherited:
            # inheritance sharing can be avoided
            continue
        holders = resource_indexer.get_resource_handle_holders(r, h)
        _close_forest_against_inheritable_resource(process_tree, holders, r, h)


def _close_forest_against_inheritable_resource(process_tree, forest, r, h):
    """
    :type process_tree: ProcessTreeConcept
    :param forest: list of processes, which share (r, h)
    :type forest: list[ProcessConcept]
    :param r: resource, which can be shared only at fork (via inheritance)
    :type r: ProcessTreeConcept
    :param h: handle to the resource
    """

    roots = util.find_processes_roots(forest)

    # the topmost process in the forest, he will create the resource
    root = max(roots, key=lambda p: -process_tree.process_depth(p))

    # after that cycle resource (r, h) holders must form a tree
    for p in roots:
        if p == root:
            continue

        cur_p = process_tree.proc_parent(p)
        while not cur_p.has_resource_at_handle(r, h):
            cur_p.add_tmp_resource(r, h)
            cur_p = process_tree.proc_parent(cur_p)


def _close_against_multi_handle_resources(process_tree):
    """ Ensures, that process, which is responsible for creation of sharable
    multi-handle resource has all "parts" of that resource
    
    :param process_tree: process tree
    :type process_tree: ProcessTreeConcept
    """

    resource_indexer = process_tree.resource_indexer
    multi_handle_resources = (r for r in resource_indexer.all_resources if len(r.handle_types) > 1)

    for r in multi_handle_resources:
        absent_handle_types = set(r.handle_types)
        creator = creators.get_resource_creator(process_tree, r)

        for h in creator.iter_all_handles():
            absent_handle_types.remove(h)

        for absent_h in absent_handle_types:
            creator.add_tmp_resource_with_auto_handle(r, absent_h)
