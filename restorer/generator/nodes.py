import bisect

class Application(object):
    def __init__(self, proc):
        self.root_process = proc
        self.pid_proc_map = { proc.pid : proc }
        self.pid_ch_map = { proc.pid : [] } # pid -> children pids

    def get_root_process(self):
        return self.root_process

    def add_process(self, process):
        if process.pid in self.pid_proc_map:
            raise ValueError("Process {} already added".format(process.pid))
        if process.ppid not in self.pid_proc_map:
            raise ValueError("Can't add process with ppid {}: add parent process first"
                             .format(process.ppid))
        self.pid_proc_map[process.pid] = process
        # adding as children (children pids are sorted)
        if process.ppid not in self.pid_ch_map:
            self.pid_ch_map[process.ppid] = []
        bisect.insort(self.pid_ch_map[process.ppid], process.pid)
        # children list is empty
        self.pid_ch_map[process.pid] = []

    def get_children(self, process):
        return (self.pid_proc_map[p] for p in self.pid_ch_map[process.pid])

    def get_process_by_pid(self, pid):
        return self.pid_proc_map[pid]

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
        self._descriptors = set()
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

    @property
    def descriptors(self):
        return self._descriptors
    
    @descriptors.setter
    def descriptors(self, descriptors):
        self._descriptors = descriptors

    def add_file_descriptor(self, descriptor):
        self._descriptors.add(descriptor)

    def remove_file_descriptor(self, descriptor):
        self._descriptors.remove(descriptor)

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
        return self.pid == other.pid;

    def __hash__(self):
        return self.pid



class FileDescriptor(object):
    def __init__(self, fd, struct_file):
        self._fd = fd
        self._struct_file = struct_file

    @property
    def fd(self):
        return self._fd

    @fd.setter
    def fd(self, fd):
        self._fd = fd

    @property
    def struct_file(self):
        return self._struct_file

    @struct_file.setter
    def struct_file(self, struct_file):
        self._struct_file = struct_file


class RegularFile(object):
    def __init__(self, file_path, size, pos):
        self._file_path = file_path
        self._size = size
        self._pos = pos

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
