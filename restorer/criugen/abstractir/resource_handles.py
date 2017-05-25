""" Resource handles

Resource handle is a special object, which is used by process to access particular
resource somehow. Resource cannot be created inside user process without any handle. 
For example: file descriptor helps to access files and other stuff
like sockets. For theoretical purposes handle may be determined for a lot of types of
resources (Virtual memory areas can be accessed using addresses range, ...), but for
practical part it seems to be enough only to have file descriptor handles, but all other
resource-specific data is stored in the resource itself and is enough to reason about resource
and it's presence inside particular process.

But handles are a little bit trickier concept, than just file descriptors or something. They
may have additional semantics for different resource types. Because this module implements
abstract process tree resource model it is not necessary to project real linux picture
on every concept we introduce precisely and handles can have more sense.

Our theoretical model says, that there are (resource, handle) pairs, which form
the whole process. Each handle has a type (and each resource has a type). There may
be resources, which demand more than one handle with particular to work with this resource,
but more handles with different types. Such resources cannot be created "partially" by a process,
instead they are created in a single CreateAction(r, [h_1, h_2, ...]) with multiple
handles all with different types. This concept helps to deal with some real resources,
for example:
    * Pipe: in our model we can think of a pipe as a in-kernel resource, which can be
      touched from userspace process either at 'read' end or 'write' end. So this resource
      has (in our model) two handles with two types (PipeWriteHandle and PipeReadHandle).
      You cannot create a pipe partially: at the first step create read part of the resource,
      and at the second one create the write end. Instead you can only create a single
      resource with two handles at once
    * SocketPair: that is a little bit harder to adapt, I think, because `socketpair` in
      linux creates two connected, but completely logically equal sockets. But we are 
      creators of this abstract process resource model, so we can do everything =) Why
      not to deal with SocketPair like with the Pipe: treat SocketPair as a single in-kernel
      resource with two userspace-level handles: socket A and socket B. So we introduce
      some kind of order on paired sockets, but it doesn't make the model less powerful (I hope so,
      really, I can't see any drawbacks at this moment)
      
Warning: all handles must be comparable in terms of value, not reference;
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
