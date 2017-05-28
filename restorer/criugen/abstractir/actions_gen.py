""" Public interface for action list generation
"""

import model.crdata as crdata
import concept
import closure
import actions_graph


def generate_actions_list(application):
    """ Generates list of abstract actions for given process
    tree restoration
    
    :param application:  task to be restored
    :type application: crdata.Application
    :return: list of high-order actions
    """

    process_tree = concept.init_conceptual_process_tree(application)
    closure.perform_process_tree_closure(process_tree)
    actions_graph.build_actions_graph(process_tree)

    return []
