def identity_fun(arg):
    return arg


def noop_fun(*args, **kwargs):
    pass


def update_dict(d, new_d):
    d.update(new_d)
    return d
