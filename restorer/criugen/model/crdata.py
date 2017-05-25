from pyutils.dataclass import DataClass


class Resource(DataClass):
    """
    Base resource class
    """
    resource_id = """Id of the resource"""


class Process(Resource):
    """
    Process data structure
    """
    pid = """process id"""  # type: int
    ppid = """process parent pid"""  # type: int
    pgid = """process group id"""  # type: int
    sid = """process session id"""  # type: int
    thread_cores = """list of thread cores"""  # type: list[ThreadCore]
    core = """task core info"""  # type: ProcessCore
    fdt = """file descriptor table: map from file descriptor to file id"""  # type: dict
    vm_info = """global vm info (start and end addresses of segments and other stuff)"""
    vmas = """array of VmArea structures, describing mappings in process vm"""  # type: list[VmArea]
    ids = """various ids for process like it's namespace ids"""
    page_map = """map of pages to fill in target process VM"""
    fs = """file system properties"""
    sigact = """signal actions (signal handling) stuff"""


class ThreadCore(Resource):
    """
    That is not CRIUs "thread_core", that is mirror of a core image file for a thread
    and also slice of the main thread core without "tc" field
    """
    thread_id = "thread id"
    mtype = """machine type"""
    thread_info = """thread information (registers and stuff)"""
    thread_core = """thread core information (user credentials included)"""


class ProcessCore(Resource):
    """
    That is Task Core (tc in CRIUs core image)
    """
    task_state = "task state"
    exit_code = "exit code"
    personality = ""
    flags = ""
    blk_sigset = "TODO"
    comm = "TODO"
    timers = "TODO"
    rlimits = "TODO"
    cg_set = "TODO"
    signals_s = "TODO"
    loginuid = "TODO"
    oom_score_adj = "TODO"


class File(Resource):
    """Base file class; has id
    """
    id = "file id"


class RegFile(File):
    """
    Regular file    
    """
    path = "file path"
    size = "file size"
    pos = "current in-file position"
    flags = "opened file flags"
    mode = "file open mode"


class PipeFile(File):
    """
    Structure, which describes one pipe
    """
    pipe_id = """special pipe id (not equal to file id)"""
    flags = """pipe open flags"""
    fown = """file owner props"""


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
    start = """start address of VM area"""  # type: int
    end = """end address of VM area"""  # type: int
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


class SignalAction(Resource):
    sigaction = """signal action"""
    flags = """flags"""
    restorer = """restorer"""
    mask = """signal mask"""


class FSProps(Resource):
    cwd_id = """current working dir file id"""
    root_id = """process root dir file id"""
    umask = """user privileges mask"""


class Application(DataClass):
    """
    Application data class
    """
    processes = """list of processes"""  # type: list[Process]
    regular_files = """list of regular files"""  # type: list[RegFile]
    pipe_files = """list of pipes"""  # type: list[PipeFile]
    shared_anon_mem = """list of shared anonymous memory files"""  # type: list[SharedAnonMem]
