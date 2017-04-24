from utils.dataclass import DataClass


class Resource(DataClass):
    """
    Base resource class
    """
    resource_id = """Id of the resource"""


class Process(Resource):
    """
    Process data structure
    """
    pid = """process id"""
    ppid = """process parent pid"""
    pgid = """process group id"""
    sid = """process session id"""
    state = """process state"""
    threads_ids = """set of thread ids"""
    fdt = """file descriptor table: map (dict) from file descriptor to file id"""
    vm_info = """global vm info (start and end addresses of segments and other stuff)"""
    vmas = """array of pairs (id, VmArea structure), describing mappings in process vm
              id is just an identifier of VMA, ids are per process, not per application"""
    ids = """various ids for process like it's namespace ids"""
    page_map = """map of pages to fill in target process VM"""


class RegFile(Resource):
    """
    Regular file    
    """
    id = "file id"
    path = "file path"
    size = "file size"
    pos = "current in-file position"
    flags = "opened file flags"
    mode = "file open mode"


class PipeFile(Resource):
    """
    Structure, which describes one pipe
    """
    id = """pipe id (file id)"""
    flags = """pipe open flags"""


class VmInfo(Resource):
    """
    Virtual process memory global map
    """
    arg_start = """arguments section start"""
    arg_end = """arguments section end"""
    brk = """heap"""
    env_start = """env vars start"""
    env_end = """env vars end"""
    code_start = """code segment start"""
    code_end = """code segment end"""
    data_start = """data segment start"""
    data_end = """data segment end"""
    brk_start = """heap start"""
    stack_start = """stack segment start"""
    dumpable = """dumpable flag"""
    exe_file_id = """identifier for executable"""
    saved_auxv = """TODO"""


class VmArea(Resource):
    """
    Virtual memory area
    """
    start = """start address of VM area"""
    end = """end address of VM area"""
    pgoff = """mapping offset (in file) in pages"""
    shmid = """file id in case VMA is not anon, 0 otherwise"""  # TODO: investigate
    prot = """protection flags"""
    flags = """MAP flags"""
    status = """detailed VMA type information"""
    fd = """attached fd? not used?"""  # TODO: fill
    fdflags = """file descriptor flags?"""  # TODO: fill


class PageMap(Resource):
    """
    Map of pages to fill in a target process address space
    """
    pages_id = """id to identify file, where raw pages are stored"""
    maps = """list of entries { "vaddr": ..., "nr_pages": ... }"""


class SharedAnonMem(Resource):
    """
    Shared Anonymous Memory record, it is described here only by it's id and pagemap;
    It's relation to any of VMA structs is not handled here explicitly (only implicitly,
    with shmid)
    """
    id = """id of shared memory"""
    pagemap = """page map for this shared anon memory, that is PageMap instance"""


class Application(DataClass):
    """
    Application data class
    """
    processes = """list of processes"""
    regular_files = """list of regular files"""
    pipe_files = """list of pipes"""
    shared_anon_mem = """list of shared anonymous memory files"""


# class App:
#     def __init__(self,
#                  processes,
#                  files,
#                  shared_anon_mems):
#         """
#         :param processes: list of processes
#         :param files:  map from file id to file structure
#         :param shared_anon_mems map from shmid to SharedAnonMem structure
#         """
#         self.processes = processes
#         self.files = files
#         self.__proc_map = {p.pid: p for p in processes}
#         self.__root = next(p for p in processes if p.ppid == 0)
#         self.__fake_root = Process(pid=0, ppid=-1, pgid=-1, sid=-1,
#                                    state=-1, threads_ids=[], fdt={},
#                                    ids={}, vmas=[], vm_info={})
#         self.__all_procs = processes + [self.__fake_root]
#
#         def children_construct(acc, p):
#             if p.ppid not in acc:
#                 acc[p.ppid] = []
#             acc[p.ppid].append(p)
#             if p.pid not in acc:
#                 acc[p.pid] = []
#             return acc
#
#         self.__proc_children = reduce(children_construct, self.__all_procs, {})
#
#         def proc_files_construct(p):
#             files_map = {}
#             for fd, fid in p.fdt.iteritems():
#                 if fid not in files_map:
#                     files_map[fid] = set()
#                 files_map[fid].add(fd)
#             return files_map
#
#         self.__proc_files = {p.pid: proc_files_construct(p) for p in self.__all_procs}
#         self.__shared_anon_mem_records = shared_anon_mems
#
#     def root_process(self):
#         return self.__root
#
#     def process_parent(self, proc):
#         """
#         :param proc: instance of `crdata.Process`
#         :return: process parent as instance of `crdata.Process`
#         """
#         if proc == self.root_process():
#             return self.__fake_root
#         return self.__proc_map[proc.ppid]
#
#     def file_by_id(self, fid):
#         return self.files[fid]
#
#     def process_files(self, proc):
#         """
#         :param proc: instance of `crdata.Process`
#         :return: map from file structure to set of file descriptors
#         """
#         return self.__proc_files[proc.pid]
#
#     def process_children(self, proc):
#         """
#         :param proc: instance of `crdata.Process`
#         :return: list of process child processes
#         """
#         return self.__proc_children[proc.pid]
