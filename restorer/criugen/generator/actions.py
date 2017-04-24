"""
Actions, which describe relationship between processes and resources in a big picture.
They do not consider resource-specific details. They only kind of formalize how resources
are shared and created and also which resources are shared or created before others.

We have next actions:

* process `[p]` creates resource `{r}`                     ~~~ `[p] creates {r}`
* process `[p]` sends resource `{r}` to process `[q]`      ~~~ `[p] sends {r} to [q]`
"""

from utils.dataclass import DataClass


class Action(DataClass):
    pass


class CreateAction(Action):
    process = "creator"
    resource = "resource, which may be process too"


class SendAction(Action):
    processFrom = ""
    processTo = ""
    resource = ""


class RemoveResourceHandle(Action):
    """TODO: do we need it?
    """
    process = ""
    resource = ""
    handle = ""
