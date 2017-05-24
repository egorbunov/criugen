import model.crdata as crdata
from pstree import ProcessTreeConcept
from process_concept import ProcessConcept
import util
import p_files
import p_private
import p_vmas
import p_ids


def initialize_conceptual_resource_tree(app):
    """ Reads application resources and initializes conceptual
    processes and resources from them
    
    :param app: read from dump application object
    :type app: crdata.Application
    :return: list of global resources (for the whole tree) and list of 
             process concepts
    """

    process_tree = _init_conceptual_process_tree(app)

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
    groups = p_ids.init_groups_resource(process_tree, app)

    # initializing sessions
    sessions = p_ids.init_sessions_resource(process_tree, app)

    # initializing pipes

    # initializing other credentials


def _init_conceptual_process_tree(app):
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
    new_root = ProcessConcept(root.ppid, -1)
    conceptual_processes.append(new_root)
    return ProcessTreeConcept(conceptual_processes, root=new_root)
