""" High-order actions description
"""

from collections import namedtuple
from pyutils.dataclass import DataClass
import process_concept
import resource_concepts


class ForkProcessAction(DataClass):
    parent = "process, which forks child"  # type: process_concept.ProcessConcept
    child = "child, which is being forked"  # type: process_concept.ProcessConcept


class CreateResourceAction(DataClass):
    process = "process, which creates resource"  # type: process_concept.ProcessConcept
    resource = "resource, which is being created"  # type: resource_concepts.ResourceConcept
    handles = "ist of handles; contains more than one handle " \
              "in case of multi-handle resource"


class ShareResourceAction(DataClass):
    process_from = "process, which has the (resource, handle_from) in it"
    process_to =  "process, with which resource is shared"
    resource = "resource, which is being shared"
    handle_from = "handle of the resource in the process, which has the resource"
    handle_to = "handle, which is going to point to the resource after " \
                "share action within `process_to` process"


class RemoveResourceAction(DataClass):
    process = "process, which executes the action of removing the resource"
    resource = "resource, handle to which is being removed from the process"
    handle = "handle, which is being released, so (resource, handle) pair " \
             "is removed from `process` as an effect of this action"


def get_action_executor(action):
    """ Returns process, which can be treated as action executor or
    at main actor =)
    """
    if isinstance(action, ForkProcessAction):
        return action.parent
    if isinstance(action, (CreateResourceAction, RemoveResourceAction)):
        return action.process
    if isinstance(action, ShareResourceAction):
        return action.process_from
