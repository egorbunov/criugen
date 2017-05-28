""" Action graph building and other stuff
"""

from pstree import ProcessTreeConcept
from process_concept import ProcessConcept
from resource_concepts import ResourceConcept
from actions import *


def build_actions_graph(process_tree):
    """ Performs analysis of given process concepts tree and builds up
    a graph of actions, which represents restoration process in terms
    of abstract actions

    :param process_tree: process tree concept, which contains all processes
           which are filled with resources concepts
    :type process_tree: ProcessTreeConcept
    :return: actions graph
    """
    pass


def _build_actions_vertices(process_tree):
    pass


def _gen_fork_actions(process_tree):
    """
    :type process_tree: ProcessTreeConcept
    """

    for p in process_tree.processes:
        if p == process_tree.root_process:
            pass
        parent = process_tree.proc_parent(p)
        yield ForkProcessAction(parent, p)


def _gen_create_actions(process_tree):
    pass


def _gen_share_actions(process_tree):
    pass


def _build_remove_actions(process_tree):
    pass


def _build_precedence_edges(process_tree, actions_vertices):
    pass
