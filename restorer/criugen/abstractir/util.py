"""
utility functions
"""


def find_processes_roots(processes):
    """ Returns array of processes, which are roots of trees from
    forest, represented with given processes array

    :rtype: list
    """

    pids_set = {p.pid for p in processes}
    return [p for p in processes if p.ppid not in pids_set]


def identity_fun(arg):
    return arg


def noop_fun(*args, **kwargs):
    pass