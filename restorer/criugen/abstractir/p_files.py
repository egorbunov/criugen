"""
Initialization of various file resources as concepts for middle IR
"""

from model import crdata
from pstree import ProcessTreeConcept
from resource_concept import RegularFileConcept, ResourceConcept
from resource_handles import *


def init_regular_files_resources(process_tree, application):
    """ Fills process concepts from process_tree with regular file resources
    
    :type process_tree: ProcessTreeConcept
    :type application: crdata.Application
    """

    reg_files = {f.id: RegularFileConcept(f) for f in application.regular_files}
    _init_files_common(process_tree, reg_files, application)


def _init_files_common(process_tree, files, app):
    """ Common procedure for adding files to process tree as resources
    
    :type process_tree: ProcessTreeConcept 
    :type files: iterable[ResourceConcept] 
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
