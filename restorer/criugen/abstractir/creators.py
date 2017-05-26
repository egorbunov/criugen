from pstree import ProcessTreeConcept
from resource_concepts import ResourceConcept
from process_concept import ProcessConcept
import util


def get_resource_creator(process_tree, resource):
    """ Returns process, which should create the specified resource.
    For now there are two rules for choosing resource creator:
        1) If resource is sharable (can be shared during process lives), then 
           resource creator is just the process with the smallest pid
           
        2) If resource is shared via forking then creator is the process, which
           is topmost in the process tree (closest to the root). 
           WARNING: if such resource has more than one handle, then we do not 
           support it for now and exception is thrown!
           
        3) If resource is private it has only one possible creator which is
           successfully chosen 
           
    :type process_tree:  ProcessTreeConcept
    :type resource: ResourceConcept  
    :return: process
    :rtype: ProcessConcept
    """

    resource_indexer = process_tree.resource_indexer
    holders = resource_indexer.get_resource_holders(resource)

    if len(holders) == 0:
        raise RuntimeError("Orphan resource! Something is wrong.")

    if resource.is_sharable:
        return min(holders, key=lambda p: p.pid)

    # not is_sharable already
    if resource.is_inherited:
        if len(resource_indexer.get_possible_resource_handles(resource)) > 1:
            raise RuntimeError("Resource, shared via inheritance, have more than one handle. Not supported =(")

        roots = util.find_processes_roots(holders)
        if len(roots) != 1:
            raise RuntimeError("Inh. resource holders do not form a tree")

        return roots[0]

    return holders[0]
