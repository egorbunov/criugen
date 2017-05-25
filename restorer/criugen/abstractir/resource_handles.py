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

# Not specified file descriptor (means, that actual file descriptor is not important)
ANY_FILE_DESCRIPTOR = FileDescriptor(-1)

# For resources, which don't need handle
NO_HANDLE = None

# Handle to input side of the pipe
PipeWriteHandle = collections.namedtuple("PipeWriteHandle", ["fd"])

# Handle to output side of the pipe
PipeReadHandle = collections.namedtuple("PipeReadHandle", ["fd"])
