""" Resource handlers type aliases
"""

import collections

# Almost every resource in our model is accessed via file descriptor:
#     - regular file
#     - pipe
#     - socket
#     - ...
# Process works with such kernel resource using file descriptors and system calls
FileDescriptor = int

# PID
ProcessId = int

# TID
ThreadId = int

# Virtual memory area handle
# That is just a pair of two integers: start of virtual memory area and its length
VMAHandle = collections.namedtuple('VMAHandle', [
    'start',
    'length'
])
