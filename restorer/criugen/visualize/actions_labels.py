""" Action nodes labels
"""

import abstractir.actions
import abstractir.resource_concepts as rc
from model import crdata
from abstractir.resource_handles import NO_HANDLE


def get_action_vertex_label(action_vertex):
    """ Returns simplified action description

    :param action_vertex: action node (vertex)
    :rtype: string
    """

    if isinstance(action_vertex, abstractir.actions.CreateResourceAction):
        return _get_create_act_label(action_vertex)
    if isinstance(action_vertex, abstractir.actions.ForkProcessAction):
        return _get_fork_act_label(action_vertex)
    if isinstance(action_vertex, abstractir.actions.RemoveResourceAction):
        return _get_remove_act_label(action_vertex)
    if isinstance(action_vertex, abstractir.actions.ShareResourceAction):
        return _get_share_act_label(action_vertex)

    raise RuntimeError("Unknown action vertex")


def _get_create_act_label(act):
    """
    :type act: actions.CreateResourceAction
    """
    if act.handles and act.handles[0] is not NO_HANDLE:
        return "<{}<BR/>Creates<BR/>{}<BR/>at<BR/>{}>".format(
            act.process.minimalistic_repr,
            act.resource.minimalistic_repr,
            act.handles)
    return "<{}<BR/><B>Creates</B><BR/>{}>".format(act.process.minimalistic_repr, act.resource.minimalistic_repr)


def _get_share_act_label(act):
    """
    :type act: actions.ShareResourceAction
    """
    if act.handle_from is not NO_HANDLE or act.handle_to is not NO_HANDLE:
        return "<{}<BR/><B>Shares</B><BR/>{}<BR/><B>with</B><BR/>{}<BR/>handle_from={}<BR/>handle_to={}>".format(
            act.process_from.minimalistic_repr,
            act.resource.minimalistic_repr,
            act.process_to.minimalistic_repr,
            act.handle_from, act.handle_to)
    return "<{}<BR/><B>Shares</B><BR/>{}<BR/><B>with</B><BR/>{}>".format(act.process_from.minimalistic_repr,
                                             act.resource.minimalistic_repr,
                                             act.process_to.minimalistic_repr)


def _get_remove_act_label(act):
    """
    :type act: actions.RemoveResourceAction
    """
    if act.handle is not NO_HANDLE:
        return "<{}<BR/><B>Remove</B><BR/>{}<BR/><B>at</B><BR/>{}>".format(act.process.minimalistic_repr,
                                               act.resource.minimalistic_repr,
                                               act.handle)
    return "<{}<BR/><B>Remove</B><BR/>{}>".format(act.process.minimalistic_repr,
                                   act.resource.minimalistic_repr)


def _get_fork_act_label(act):
    """
    :type act: actions.ForkProcessAction
    """
    return "<{}<BR/><B>Fork</B><BR/>{}>".format(act.parent.minimalistic_repr,
                                 act.child.minimalistic_repr)
