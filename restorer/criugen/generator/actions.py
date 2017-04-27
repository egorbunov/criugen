"""
Actions, which describe relationship between processes and resources in a big picture.
They do not consider resource-specific details. They only kind of formalize how resources
are shared and created and also which resources are shared or created before others.

We have next actions:

* process `[p]` creates resource `{r}`                     ~~~ `[p] creates {r}`
* process `[p]` sends resource `{r}` to process `[q]`      ~~~ `[p] sends {r} to [q]`

We also introduce temporary action: actions, which effect is temporary. That means,
that if action affects process state, this state change must be undone before finishing
restoration.
"""

from utils.dataclass import DataClass


class Action(DataClass):
    pass


class CreateAction(Action):
    process = "creator"
    resource = "resource, which may be process too"


class CreateTemporaryAction(CreateAction):
    """The same as CreateAction, but creates temporary resource,
    which trace must be cleared from process state after usage
    """


class SendAction(Action):
    process_from = ""
    process_to = ""
    resource = ""


class SendTemporaryAction(SendAction):
    """The same as SendAction, but the recipient gets the resource as
    temporary, so it must clear the trace of this resource after usage
    """
    pass


class RemoveResourceHandle(Action):
    """TODO: do we need it?
    """
    process = ""
    resource = ""
    handle = ""
