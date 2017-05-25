"""
Initialization of various file resources as concepts for middle IR
"""

from model import crdata
from pstree import ProcessTreeConcept
from resource_concepts import RegularFileConcept, ResourceConcept, SharedMemConcept, PipeConcept
from resource_adapters import PipeResource
from resource_handles import *
import model.crconstants as crconstants


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


def _construct_pipe_concepts(pipe_files):
    """ Constructs pipe resource concepts; each pipe resource
    contains two pipe files: one for reading and another for writing
    
    :param pipe_files: list of pipe files
    :type pipe_files: list[crdata.PipeFile]
    :return: map from pipe ids to pipe concepts
    :rtype: dict[int, PipeConcept]
    """
    pipe_resources = {}  # type: dict[int, list]

    # creating pipe tuples, which contain read and write end pipe files
    for pf in pipe_files:
        read_write_tuple = pipe_resources.setdefault(pf.pipe_id, [None, None])
        if pf.flags & crconstants.FILE_RDONLY_FLAG > 0:
            read_write_tuple[0] = pf
        elif pf.flags & crconstants.FILE_WRONLY_FLAG > 0:
            read_write_tuple[1] = pf
        else:
            raise RuntimeError("Bad pipe file (not RDONLY or WRONLY")

    pipe_concepts = {id: PipeConcept(PipeResource(id=id, read_end=fs[0], write_end=fs[1]))
                     for (id, fs) in pipe_resources.iteritems()}

    return pipe_concepts


def init_pipe_resources(process_tree, app):
    """ Fills process concepts from process_tree with regular file resources

    :param process_tree: tree with processes (concepts) to fill with resources

    :type process_tree: ProcessTreeConcept
    :type app: crdata.Application

    :return: list of pipe concepts
    :rtype: list[PipeConcept]
    """

    pipe_files = app.pipe_files
    pipe_concepts = _construct_pipe_concepts(pipe_files)
    pipe_files_map = {pf.id: pf for pf in pipe_files}
    raw_processes = app.processes

    for p in raw_processes:
        process_concept = process_tree.proc_by_pid(p.pid)

        # looking for pipes in file descriptor table
        for fd, file_id in p.fdt.iteritems():
            if file_id not in pipe_files_map:
                continue

            pf = pipe_files_map[file_id]
            pipe_concept = pipe_concepts[pf.pipe_id]
            pipe_resource = pipe_concept.payload  # type: PipeResource

            if pf == pipe_resource.read_end:
                handle = PipeReadHandle(fd=fd)
            elif pf == pipe_resource.write_end:
                handle = PipeWriteHandle(fd=fd)
            else:
                raise RuntimeError("Unknown pipe file")

            process_concept.add_resource(pipe_concept, handle=handle)

    return list(pipe_concepts.values())


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
