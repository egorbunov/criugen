"""
Initialization of resource pairs for virtual memory; Functions here are intended
to properly setup VMA resource concepts with correct dependencies
"""

from model import crdata
from model.crconstants import *
from pstree import ProcessTreeConcept
from resource_concepts import SharedMemConcept, RegularFileConcept, VMAConcept
from process_concept import ProcessConcept
import resource_handles


def init_shared_vma_resources(process_tree, app, shmem_map, regfile_map):
    """ Fills process concepts from process_tree with VMA resources, only
    shared VMAs are handled here. VMA may depend on shared memory or regular
    file, so we also consider them to be initialized before calling this function

    :param process_tree: tree of process concepts to fill with resources
    :type process_tree: ProcessTreeConcept
    :param shmem_map: map from file id to shared memory concept resource
    :type shmem_map: dict[int, SharedMemConcept]
    :param regfile_map: map from file id to regular file concept resource
    :type regfile_map: dict[int, RegularFileConcept]
    :type app: crdata.Application
    """

    # every shared vma may be treated as a non-shared resource in a way that
    # it is enough for background file/shared memory to be shared, but VMA
    # itself as just kind of a mapping of the shared file into process memory
    # can be treated as per-process private resource without any bad consequences

    raw_processes = app.processes
    for p in raw_processes:
        vmas = [vma for vma in p.vmas if VMA_FLAG_MAP_SHARED in vma.flags]
        process_concept = process_tree.proc_by_pid(p.pid)
        _init_vmas_one_process(process_concept, vmas, shmem_map, regfile_map)


def _init_vmas_one_process(process_concept, vmas, shmem_map, regfile_map):
    """See documentation for `init_shared_vma_resources`. This function treats
    every vma as single resource, nothing is shared (and it is ok)
    :type process_concept: ProcessConcept
    """
    for vma in vmas:
        file_dependency = None
        if VMA_STATUS_FILE_SHARED in vma.status or VMA_STATUS_FILE_PRIVATE in vma.status:
            file_dependency = regfile_map[vma.shmid]
        elif VMA_STATUS_ANON_SHARED in vma.status:
            file_dependency = shmem_map[vma.shmid]

        resource = VMAConcept(vma)
        if file_dependency:
            resource.add_dependency(file_dependency)

        process_concept.add_resource(resource, resource_handles.NO_HANDLE)


def init_private_vma_resources(process_tree, app, regfile_map):
    """ Fills process concepts from process_tree with VMA resources, only
    private VMAs are handled here. Private VMA may depend on regular file, if
    that is a private file mapping, so we consider regfile_map to be initialized
    before invoking this function

    :param process_tree: tree of process concepts to fill with resources
    :type process_tree: ProcessTreeConcept
    :param regfile_map: map from file id to regular file concept resource
    :type regfile_map: dict[int, RegularFileConcept]
    :type app: crdata.Application
    """

    # for now it is the same as shared VMAs TODO: cow

    raw_processes = app.processes
    for p in raw_processes:
        vmas = [vma for vma in p.vmas if VMA_FLAG_MAP_PRIVATE in vma.flags]
        process_concept = process_tree.proc_by_pid(p.pid)
        _init_vmas_one_process(process_concept, vmas, {}, regfile_map)
