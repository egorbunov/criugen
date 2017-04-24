""" Resource handlers type aliases
"""

from utils.dataclass import DataClass

# Almost every resource in our model is accessed via file descriptor:
#     - regular file
#     - pipe
#     - socket
#     - ...
# Process works with such kernel resource using file descriptors and system calls
FileDescriptor = int

# Not specified file descriptor (means, that actual file descriptor is not important)
ANY_FILE_DESCRIPTOR = FileDescriptor(-1)

# PID
ProcessId = int

# TID
ThreadId = int


# Virtual memory area handle
# That is just a pair of two integers: start of virtual memory area and its length
class VMAHandle(DataClass):
    start = "VMA start"
    length = "VMA length"
