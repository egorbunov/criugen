""" Here we put data classes for resources, which add some more "abstraction"
above raw resources data, loaded from images. That is not needed often, because
it almost always enough to use raw loaded data as resource concept payload, because
it completely satisfies our conceptual process resource model (for example we are okay 
with crdata.RegFile, crdata.VmArea and other simple resource, but we need to adapt Pipe
file resource, because if raw images it is not stored as a single resource explicitly, 
but only with files, which are responsible for one end of a pipe)
"""

import crloader.crdata as crdata
from pyutils.dataclass import DataClass


class PipeResource(DataClass):
    id = "pipe id"  # type: int
    read_end = "read end of a pipe"  # type: crdata.PipeFile
    write_end = "write end of a pipe"  # type: crdata.PipeFile
