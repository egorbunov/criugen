"""
Properties describe the restoration process properties and final process tree itself.
"""

from utils.dataclass import DataClass


class InheritsProperty(DataClass):
    """
      `[p] inherits {r}` -- this rule just tells us, that resource is inherited during clone/fork from parent process,
      meaning that `{r}` must be kept after forking. All resources that are also inherited due to clone/fork
      nature, but not mentioned in such `inherits` rule, must be closed/released in process `[p]`
    """
    process = ""
    resource = ""


class DependsProperty(DataClass):
    """
     `{q} depends on {r}`
    """
    process = ""
    dependantResource = ""
    dependencyResource = ""
