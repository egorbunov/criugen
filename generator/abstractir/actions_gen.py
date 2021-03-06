""" Actions generation (just actions as vertices of the actions graph)
"""
import itertools

import creators
from actions import *
from resource_indexer import ResourcesIndexer


def gen_actions_vertices(process_tree):
    """ Builds list of all actions to be performed during restore
    :type process_tree: ProcessTreeConcept
    :rtype: collections.Iterable
    """
    return itertools.chain(
        _gen_fork_actions(process_tree),
        _gen_create_actions(process_tree),
        _gen_share_actions(process_tree),
        _gen_remove_tmp_resources_actions(process_tree)
    )


def _gen_fork_actions(process_tree):
    """ Simply generates fork actions, which must be performed to
    restore process tree

    :type process_tree: ProcessTreeConcept
    """

    for p in process_tree.processes:
        if p == process_tree.root_process:
            continue
        parent = process_tree.proc_parent(p)
        yield ForkProcessAction(parent=parent,
                                child=p)


def _gen_create_actions(process_tree):
    """ Generates resource creation actions

    :type process_tree: ProcessTreeConcept
    """

    resource_indexer = process_tree.resource_indexer  # type: ResourcesIndexer
    all_resources = resource_indexer.all_resources

    for r in all_resources:
        creator = creators.get_resource_creator(process_tree, r)
        handles = creators.get_creator_handles(creator, r)

        if len(handles) != len(r.handle_types):
            raise RuntimeError("Not enough handles for creation of [{}] by [{}]; Have only: [{}]"
                               .format(r, creator, handles))

        yield CreateResourceAction(process=creator,
                                   resource=r,
                                   handles=handles)


def _gen_share_actions(process_tree):
    """ Generates share actions for sharable resources
    """

    resource_indexer = process_tree.resource_indexer  # type: ResourcesIndexer
    sharable_resource = (r for r in resource_indexer.all_resources if r.is_sharable)

    for r in sharable_resource:
        creator = creators.get_resource_creator(process_tree, r)
        creator_handles = creators.get_creator_handles(creator, r)
        creator_handles_map = {type(h): h for h in creator_handles}

        holders = resource_indexer.get_resource_holders(r)

        for p in holders:
            p_handles = p.iter_all_handles(r)

            if p == creator:
                # do not need to share with us if we create it!
                p_handles = (h for h in p_handles if h not in creator_handles)

            for p_handle in p_handles:
                yield ShareResourceAction(process_from=creator,
                                          process_to=p,
                                          handle_from=creator_handles_map[type(p_handle)],
                                          handle_to=p_handle,
                                          resource=r)


def _gen_remove_tmp_resources_actions(process_tree):
    """ Generates RemoveAction for each temporary resource in every process
    :type process_tree: ProcessTreeConcept
    """

    all_processes = process_tree.processes
    for p in all_processes:
        for tmp_resource in p.iter_tmp_resources():
            for tmp_handle in p.get_tmp_handles(tmp_resource):
                yield RemoveResourceAction(process=p,
                                           resource=tmp_resource,
                                           handle=tmp_handle)
