def identity_fun(arg):
    """ Identity function
    """
    return arg


def noop_fun(*args, **kwargs):
    """ No operation function
    """
    pass


def update_dict(d, new_d):
    """ Updates dictionary, passed as first arguments and returns it
    """
    d.update(new_d)
    return d


def join_dicts(*args):
    """ Joins passed dictionaries list together, creating new dictionary
    Any None argument is ignored
    """
    new_dict = {}
    for d in args:
        if d is None:
            continue
        new_dict.update(d)
    return new_dict


def val_returner(val):
    """ Returns function, which returns given value on every call
    """

    def returner(*args, **kwargs):
        return val

    return returner
