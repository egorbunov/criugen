"""
Properties describe the restoration process properties and final process tree itself.
"""

from collections import namedtuple

"""
  `[p] inherits {r}` -- this rule just tells us, that resource is inherited during clone/fork from parent process,
  meaning that `{r}` must be kept after forking. All resources that are also inherited due to clone/fork
  nature, but not mentioned in such `inherits` rule, must be closed/released in process `[p]`
"""
InheritsProperty = namedtuple('InheritsProperty', [
    'process',
    'resource'
])

"""
 `{q} depends on {r}`
"""
DependsProperty = namedtuple('DependsProperty', [
    'process',
    'dependantResource',
    'dependencyResource'
])
