""" Action nodes labels
"""

import actions
import resource_concepts as rc
from model import crdata


def get_action_vertex_label(action_vertex):
    """ Returns simplified action description

    :param action_vertex: action node (vertex)
    :rtype: string
    """

    if isinstance(action_vertex, actions.CreateResourceAction):
        return _get_create_act_label(action_vertex)
    if isinstance(action_vertex, actions.ForkProcessAction):
        return _get_fork_act_label(action_vertex)
    if isinstance(action_vertex, actions.RemoveResourceAction):
        return _get_remove_act_label(action_vertex)
    if isinstance(action_vertex, actions.ShareResourceAction):
        return _get_share_act_label(action_vertex)

    raise RuntimeError("Unknown action vertex")


def _get_create_act_label(act):
    """
    :type act: actions.CreateResourceAction
    """
    if act.handles and act.handles[0]:
        return "{}\nCreates\n{}\nat\n{}".format(
            act.process.minimalistic_repr,
            act.resource.minimalistic_repr,
            act.handles)
    return "{}\nCreates\n{}".format(act.process.minimalistic_repr, act.resource.minimalistic_repr)


def _get_share_act_label(act):
    """
    :type act: actions.ShareResourceAction
    """
    if act.handle_from or act.handle_to:
        return "{}\nShares\n{}\nwith\n{}\nhandle_from={}\nhandle_to={}".format(
            act.process_from.minimalistic_repr,
            act.resource.minimalistic_repr,
            act.process_to.minimalistic_repr,
            act.handle_from, act.handle_to)
    return "{}\nShares\n{}\nwith\n{}".format(act.process_from.minimalistic_repr,
                                             act.resource.minimalistic_repr,
                                             act.process_to.minimalistic_repr)


def _get_remove_act_label(act):
    """
    :type act: actions.RemoveResourceAction
    """
    if act.handle:
        return "{}\nRemove\n{}\nat\n{}".format(act.process.minimalistic_repr,
                                               act.resource.minimalistic_repr,
                                               act.handle)
    return "{}\nRemove\n{}".format(act.process.minimalistic_repr,
                                   act.resource.minimalistic_repr)


def _get_fork_act_label(act):
    """
    :type act: actions.ForkProcessAction
    """
    return "{}\nFork\n{}".format(act.parent.minimalistic_repr,
                                 act.child.minimalistic_repr)
