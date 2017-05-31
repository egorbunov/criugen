""" Action nodes labels
"""

from abstractir import actions
from abstractir import resource_concepts as rc
from model import crdata


def get_action_vertex_label(action_vertex):
    """ Returns simplified action description

    :param action_vertex: action node (vertex)
    :rtype: string
    """

    if isinstance(action_vertex, actions.CreateResourceAction):
        return "Create"
    if isinstance(action_vertex, actions.ForkProcessAction):
        return "Fork"
    if isinstance(action_vertex, actions.RemoveResourceAction):
        return "Remove"
    if isinstance(action_vertex, actions.ShareResourceAction):
        return "Share"

    raise RuntimeError("Unknown action vertex")
