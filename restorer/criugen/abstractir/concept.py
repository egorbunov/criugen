""" Functions, which sum up process tree model (concept) creation
"""

import model.crdata as crdata
from pstree import ProcessTreeConcept
from process_concept import ProcessConcept
import closure
import util
import p_files
import p_private
import p_vmas
import p_ids
from resource_indexer import ResourcesIndexer


def build_concept_process_tree(app):
    """ Analyses given application and build process tree filled
    with resources (ResourceConcept) and all that stuff, which we
    need to create actions graph
    :param app: application
    :type app: crdata.Application
    :return: process tree
    :rtype: ProcessTreeConcept
    """

    process_tree = _init_conceptual_process_tree(app)
    closure.perform_process_tree_closure(process_tree)

    return process_tree


def _init_conceptual_process_tree(app):
    """ Reads application resources and initializes conceptual
    processes and resources from them. Returns a pair:
    * process tree, which contains of processes models (concepts) filled 
     with(resource, handle) pairs
    * resource indexer, with all initial application resources indexed
    
    :param app: read from dump application object
    :type app: crdata.Application
    :return: conceptual process tree and resource index
    :rtype: ProcessTreeConcept
    """

    process_tree = _make_empty_conceptual_process_tree(app)

    # initializing regular files
    reg_file_map = p_files.init_regular_files_resources(process_tree, app)

    # initializing shared mem
    shmem_map = p_files.init_shared_anon_mem_resources(process_tree, app)

    # initializing virtual memory areas
    p_vmas.init_private_vma_resources(process_tree, app, reg_file_map)
    p_vmas.init_shared_vma_resources(process_tree, app, shmem_map, reg_file_map)

    # initializing process internal private state
    p_private.init_internal_state_resources(process_tree, app)

    # initializing groups
    p_ids.init_groups_resource(process_tree, app)

    # initializing sessions
    p_ids.init_sessions_resource(process_tree, app)

    # initializing pipes
    p_files.init_pipe_resources(process_tree, app)

    return process_tree


def _make_empty_conceptual_process_tree(app):
    """
    Constructs process tree with empty processes (no resources initialized so far)
    
    :type app: crdata.Application
    :rtype: ProcessTreeConcept
    """

    conceptual_processes = [ProcessConcept(p.pid, p.ppid) for p in app.processes]
    roots = util.find_processes_roots(conceptual_processes)

    if len(roots) != 1:
        raise RuntimeError("Application must contain only one process tree; found {}".format(len(roots)))

    root = roots[0]
    new_root = ProcessConcept(root.ppid, -1)  # zero process!
    conceptual_processes.append(new_root)
    return ProcessTreeConcept(conceptual_processes)
