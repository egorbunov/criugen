""" Functions, which perform closure of process tree against several properties:

* resource dependencies
* inherited resources
* multi-handle resources
"""

import creators
import util
from pstree import ProcessTreeConcept
from resource_concepts import ResourceConcept


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

    _make_creators_handle_the_resource_they_create(process_tree)


def _close_against_dependencies(process_tree):
    """ Makes sure, that processes, which are responsible
     for resource creation of the resource `r` also have
     handle to all dependencies of this resource
    
    :param process_tree: process tree
    :type process_tree: ProcessTreeConcept
    """

    resource_indexer = process_tree.resource_indexer
    all_resources = resource_indexer.all_resources

    for r in all_resources:
        creator = creators.get_resource_creator(process_tree, r)
        _close_against_dependencies_one_creator(creator, r)


def _close_against_dependencies_one_creator(creator_process, resource):
    dependencies_to_check = resource.dependencies  # type: set[tuple[ResourceConcept, type]]

    # need to check not recursively, because this process may not be creator
    # of dependencies
    for d, handle_type in dependencies_to_check:
        if creator_process.has_resource_at_handle_type(d, handle_type):
            continue

        creator_process.add_tmp_resource_with_auto_handle(d, handle_type)


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
    """ Adds the resource to whole intermediate processes to complete the forest

    :type process_tree: ProcessTreeConcept
    :param forest: list of processes, which share (r, h)
    :type forest: list[ProcessConcept]
    :param r: resource, which can be shared only at fork (via inheritance)
    :type r: ResourceConcept
    :param h: handle to the resource
    """

    creator = creators.get_resource_creator(process_tree, r)
    roots = util.find_processes_roots(forest)

    if not creator.has_resource_at_handle(r, h):
        creator.add_tmp_resource(r, h)

    for root in roots:
        if root == creator:
            continue

        parent = process_tree.proc_parent(root)
        while not parent.has_resource_at_handle(r, h):
            parent.add_tmp_resource(r, h)


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

        for h in creator.iter_all_handles(r):
            absent_handle_types.remove(type(h))

        for absent_h_t in absent_handle_types:
            creator.add_tmp_resource_with_auto_handle(r, absent_h_t)


def _make_creators_handle_the_resource_they_create(process_tree):
    resource_indexer = process_tree.resource_indexer
    all_resources = resource_indexer.all_resources

    # inherited resource creators are handled in _close_against_inheritance function
    sharable_resource = (r for r in all_resources if r.is_sharable)
    for r in sharable_resource:
        creator = creators.get_resource_creator(process_tree, r)
        for ht in r.handle_types:
            if creator.has_resource_at_handle_type(r, ht):
                continue

            creator.add_tmp_resource_with_auto_handle(r, ht)
