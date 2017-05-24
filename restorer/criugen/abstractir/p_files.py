"""
Initialization of various file resources as concepts for middle IR
"""

from model import crdata
from pstree import ProcessTreeConcept
from resource_concept import RegularFileConcept, ResourceConcept, SharedMemConcept, PipeConcept
from resource_handles import *


def init_regular_files_resources(process_tree, app):
    """ Fills process concepts from process_tree with regular file resources
    
    :param process_tree: tree with processes (concepts) to fill with resources
    
    :type process_tree: ProcessTreeConcept
    :type app: crdata.Application
    
    :return: map from file id to regular file concept
    :rtype: dict[int, RegularFileConcept]
    """

    reg_files = {f.id: RegularFileConcept(f) for f in app.regular_files}
    _init_files_common(process_tree, reg_files, app)
    return reg_files


def init_shared_anon_mem_resources(process_tree, app):
    """ Fills process concepts from process_tree with shared mem resources

    :type process_tree: ProcessTreeConcept
    :type app: crdata.Application

    :return: map from shmem id to shared mem concept
    :rtype: dict[int, SharedMemConcept]
    """

    shared_mem_files = {shmem.id: SharedMemConcept(shmem) for shmem in app.shared_anon_mem}
    _init_files_common(process_tree, shared_mem_files, app)
    return shared_mem_files


def init_pipe_resources(process_tree, app):
    """ Fills process concepts from process_tree with regular file resources

    :param process_tree: tree with processes (concepts) to fill with resources

    :type process_tree: ProcessTreeConcept
    :type app: crdata.Application

    :return: list of pipe concepts
    :rtype: list[PipeConcept]
    """
    return []


def _init_files_common(process_tree, files, app):
    """ Common procedure for adding files to process tree as resources
    in case there are matches between fdt and passed files map from file id
    to file concept
    
    :type process_tree: ProcessTreeConcept
    :type files: dict[int, ResourceConcept] 
    :type app: crdata.Application
    """
    crdata_processes = app.processes

    for p in crdata_processes:
        process_concept = process_tree.proc_by_pid(p.pid)

        for fd, file_id in p.fdt.iteritems():
            if file_id not in files:
                continue

            # adding file with file descriptor as (resource, handle) pair
            process_concept.add_resource(files[file_id], FileDescriptor(fd))
