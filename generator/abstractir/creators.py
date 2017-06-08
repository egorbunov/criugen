from pstree import ProcessTreeConcept
from resource_concepts import ResourceConcept
from process_concept import ProcessConcept
import util
import resource_handles


def get_resource_creator(process_tree, resource):
    """ Returns process, which should create the specified resource.
    For now there are a few rules for choosing resource creator:
        1) If resource is sharable (can be shared during process lives), then 
           resource creator is just the process with the smallest pid
           
        2) If resource is shared via forking then creator is the process, which
           is topmost in the process tree (closest to the root). 
           WARNING: if such resource has more than one handle, then we do not
           support it for now and exception is thrown!
           
        3) If resource is private it has only one possible creator which is
           successfully chosen

        4) Also, resource creator must be possible creator (see ResourceConcept,
           possible_creators method)

    WARNING: this method returns resource creator, but this returned process may
    not contain the resource itself (it can be creator, but not holder)
           
    :type process_tree:  ProcessTreeConcept
    :type resource: ResourceConcept  
    :return: process
    :rtype: ProcessConcept
    """

    resource_indexer = process_tree.resource_indexer
    holders = resource_indexer.get_resource_holders(resource)
    if len(holders) == 0:
        raise RuntimeError("Orphan resource! Something is wrong.")

    all_create_candidates = set(resource.possible_creators(process_tree.processes))

    if resource.is_sharable:
        creator_candidates = set(holders) & all_create_candidates  # todo: optimize?
        return _sharable_resource_creator(creator_candidates, all_create_candidates, resource)

    # not is_sharable already
    if resource.is_inherited:
        if len(resource_indexer.get_possible_resource_handles(resource)) > 1:
            raise RuntimeError("Resource, shared via inheritance, have more than one handle. Not supported =(")

        return _inherited_resource_creator(process_tree, all_create_candidates, holders, resource)

    # means, that resource is private if we are here
    if len(holders) != 1:
        raise RuntimeError("Private resource [{}] has more than one holder".format(resource))
    return holders[0]


def get_creator_handles(process, resource):
    """ Returns array of handles for the resource, which are used during creation
    of the resource by the process

    :type process: ProcessConcept
    :type resource: ResourceConcept
    :rtype: list[object]
    """

    return list(_gen_creator_handles(process, resource))


def _gen_creator_handles(process, resource):
    """
    :type process: ProcessConcept
    :type resource: ResourceConcept
    :rtype: list[object]
    """
    for ht in resource.handle_types:
        h = next(process.get_all_handles_of_type(resource, ht), resource_handles.IMPOSSIBLE_HANDLE)
        if h == resource_handles.IMPOSSIBLE_HANDLE:
            continue
        yield h


class ImpossibleToCreateResource(Exception):
    def __init__(self, res, m):
        super(ImpossibleToCreateResource, self).__init__("{}: {}".format(res, m))


def _sharable_resource_creator(creator_candidates, all_possible_creators, resource):
    if len(all_possible_creators) == 0:
        raise ImpossibleToCreateResource(resource, "process tree is not complete")

    if len(creator_candidates) > 0:
        return min(creator_candidates, key=lambda p: p.pid)

    return min(all_possible_creators, key=lambda p: p.pid)


def _inherited_resource_creator(process_tree,
                                all_possible_creators,
                                holders,
                                resource):
    """ Returns a process, which is lca for all of the holders actually

    :type process_tree: ProcessTreeConcept
    """
    if len(all_possible_creators) == 0:
        raise ImpossibleToCreateResource(resource, "process tree is not complete")

    roots = util.find_processes_roots(holders)  # holders are not empty

    # finding lca for all of the roots
    lca = roots[0]
    for r in roots:
        lca = process_tree.lca(lca, r)

    # going up till we met a process, which can create a resource
    if lca not in all_possible_creators and lca != process_tree.root_process:
        lca = process_tree.proc_parent(lca)

    # if creator not found
    if lca not in all_possible_creators:
        raise ImpossibleToCreateResource(resource,
                                         "process tree is not complete for inheritable resource restoration")

    return lca
