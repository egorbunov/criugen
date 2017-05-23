"""
Initialization of private process resource concepts; by private we mean not sharable resources:
internal process state, vm info, page map
"""

from resource_concept import ProcessInternalsConcept
from model import crdata
from pstree import ProcessTreeConcept
import resource_handles


def init_internal_state_resources(process_tree, application):
    """
    :type process_tree: ProcessTreeConcept
    :type application: crdata.Application
    """
    raw_processes = application.processes

    for p in raw_processes:
        process_concept = process_tree.proc_by_pid(p.pid)

        page_map = ProcessInternalsConcept(p.page_map)
        state = ProcessInternalsConcept(p.state)
        vm_info = ProcessInternalsConcept(p.vm_info)
        fs_props = ProcessInternalsConcept(p.fs)
        sigacts = ProcessInternalsConcept(p.sigact)

        process_concept.add_resource(page_map, resource_handles.NO_HANDLE)
        process_concept.add_resource(state, resource_handles.NO_HANDLE)
        process_concept.add_resource(vm_info, resource_handles.NO_HANDLE)
        process_concept.add_resource(fs_props, resource_handles.NO_HANDLE)
        process_concept.add_resource(sigacts, resource_handles.NO_HANDLE)
