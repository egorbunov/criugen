"""
Actions, which describe relationship between processes and resources in a big picture.
They do not consider resource-specific details. They only kind of formalize how resources
are shared and created and also which resources are shared or created before others.

We have next actions:

* process `[p]` creates resource `{r}`                     ~~~ `[p] creates {r}`
* process `[p]` sends resource `{r}` to process `[q]`      ~~~ `[p] sends {r} to [q]`

There are the `[god]` process, which exists during the whole restoration process and it
does not need to be created.

Actions relationships together with properties (see properties.py) sum up to create some
precedence rules, which can help us to decide, which actions must be performed before others

For better explanation lets add next shortcut to describe, that process has a resource:

* `[p] obtains {r}` <=> `[p] creates {r}` OR `[p] inherits {r} from [q]` OR `[q] sends {r} to [p]`

Also remember that processes may create other processes, so:

* `[p] creates [q]` is a possible rule
* we also say: `[p] was created` if `[q] creates [p]` for some `[q]`

And basing on actions above and on properties (see properties.py) we have next 
precedence relationships (`a <~~ b` <=> `b` precedes `a`):

* `[q] creates {r}` <~~ `[q] was created`
* `[p] sends {r} to [q]` <~~ `[p] was created` AND `[q] was created` AND `[p] obtains {r}`
* `[q] inherits {r}` ==> `[p] creates [q]` <~~ `[p] was created` AND `[p] obtains {r}`
* `{q} depends on {r}` ==> `[p] obtains {q}` <~~ `[p] obtains {r}`

According to this relationship we can build a graph with edges showing precedence. This graph
may help us to determine which actions must be done before others. As an additional idea such 
graph may show, which restoration paths can be done truly in parallel?
"""

from collections import namedtuple

CreateAction = namedtuple('CreateAction', [
    'process',
    'resource',  # may be process too
    'handle'
])

SendAction = namedtuple('SendAction', [
    'processFrom',
    'processTo',
    'resource',
    'handleFrom',
    'handleTo'
])
