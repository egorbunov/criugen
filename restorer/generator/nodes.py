import bisect

class TaskState:
    UNDEF = 0x0
    ALIVE = 0x1
    DEAD = 0x2
    STOPPED = 0x3
    HELPER = 0x4
    THREAD = 0x5

class Process(object):
    def __init__(self, pid, ppid):
        self._pid = int(pid)
        self._ppid = int(ppid)
        self._file_map = {}
        self._fdt = {}
        self._vmas = set()
        self._threads = set()
        self._state = TaskState.UNDEF

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, pid):
        self._pid = pid

    @property
    def ppid(self):
        return self._ppid

    @ppid.setter
    def ppid(self, ppid):
        self._ppid = ppid

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        states = set([ TaskState.UNDEF, TaskState.STOPPED, TaskState.ALIVE, TaskState.DEAD,
                       TaskState.HELPER, TaskState.THREAD ])
        if state not in states:
            raise ValueError("Unknown task state")
        self._state = state

    def add_file_descriptor(self, fd, file):
        if fd in self._fdt:
            raise ValueError("File at fd {} already exists".format(fd))
        if not file in self._file_map:
            self._file_map[file] = set()
        self._file_map[file].add(fd)
        self._fdt[fd] = file

    def get_files(self):
        return self._fdt.iteritems()

    @property
    def fdt(self):
        """ file_descriptor -> File """
        return self._fdt
    
    @property
    def file_map(self):
        """ File -> [ file_descriptor ] """
        return self._file_map
    

    @property
    def vmas(self):
        return self._vmas

    def add_vma(self, vma):
        self._vmas.add(vma)

    def remove_vma(self, vma):
        self._vmas.remove(vma)

    def add_thread(self, thread):
        self._threads.add(thread)

    def remove_thread(self, thread):
        self._threads.remove(thread)

    def get_file_descriptor(self, fd):
        try:
            return next(d for d in self._descriptors if d.fd == fd)
        except StopIteration:
            return None

    def get_vma(self, start):
        try:
            return next(vma for vma in self._vmas if vma.start == start)
        except StopIteration:
            return None

    def __str__(self):
        return "Process(pid: {_pid}, ppid: {_ppid})".format(**self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.pid == other.pid; # ok ?

    def __hash__(self):
        return self.pid


class Application(object):
    def __init__(self, proc):
        self._dummy_root_parent = Process(proc.ppid, -1)
        self._root_process = proc
        self._pid_proc_map = { proc.pid : proc, self._dummy_root_parent.pid : self._dummy_root_parent }
        # pid -> children pids
        self._pid_ch_map = { proc.pid : [], self._dummy_root_parent.pid : [ proc.pid ] } 

    def get_root_process(self):
        return self._root_process

    def is_root_proc(self, proc):
        return proc is self._root_process

    def add_process(self, process):
        if process.pid in self._pid_proc_map:
            raise ValueError("Process {} already added".format(process.pid))
        if process.ppid not in self._pid_proc_map:
            raise ValueError("Can't add process with ppid {}: add parent process first"
                             .format(process.ppid))
        self._pid_proc_map[process.pid] = process
        # adding as children (children pids are sorted)
        if process.ppid not in self._pid_ch_map:
            self._pid_ch_map[process.ppid] = []
        bisect.insort(self._pid_ch_map[process.ppid], process.pid)
        # children list is empty
        self._pid_ch_map[process.pid] = []

    def get_children(self, process):
        return (self._pid_proc_map[p] for p in self._pid_ch_map[process.pid])

    def get_process_by_pid(self, pid):
        return self._pid_proc_map[pid]

    def get_all_processes(self):
        return [ v for k, v in self._pid_proc_map.iteritems() if v is not self._dummy_root_parent ]


class File(object):
    ids = set()

    @staticmethod
    def reset():
        File.ids = set()

    @staticmethod
    def next_id():
        return max(File.ids) + 1 if File.ids else 0

    def __init__(self, id):
        if id < 0:
            id = File.next_id()
        if id in File.ids:
            raise ValueError("File with id {} already created".format(id))
        File.ids.add(id)
        self._id = id

    @property
    def id(self):
        return self._id
    

class RegularFile(File):
    def __init__(self, file_path, size, pos, flags, mode, id = -1):
        super(RegularFile, self).__init__(id)
        self._file_path = file_path
        self._size = size
        self._pos = pos
        self._flags = flags
        self._mode = mode

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        self._file_path = file_path

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        if self._size and pos > self._size:
            raise ValueError("Pos should be less than size")
        self._pos = pos

    @property
    def flags(self):
        return self._flags

    @property
    def mode(self):
        return self._mode

class PipeFile(File):
    def __init__(self, pipe_id, flags, id = -1):
        super(PipeFile, self).__init__(id)
        self._pipe_id = pipe_id
        self._flags = flags

    @property
    def id(self):
        return self._id
    
    @property
    def pipe_id(self):
        return self._pipe_id
    
    @property
    def flags(self):
        return self._flags
    

class Vma:
    def __init__(self,
            start=0,
            end=0,
            file_path=None,
            pgoff=None,
            is_shared=False):
        self._start = start
        self._end = end
        self._file_path = file_path
        self._pgoff = pgoff
        self._is_shared = is_shared

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        self._end = end

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        self._file_path = file_path

    @property
    def pgoff(self):
        return self._pgoff

    @pgoff.setter
    def pgoff(self, pgoff):
        self._pgoff = pgoff

    @property
    def is_shared(self):
        return self._is_shared

    @is_shared.setter
    def is_shared(self, is_shared):
        self._is_shared = is_shared


class FilePath:
    def __init__(self, path):
        self._path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path
