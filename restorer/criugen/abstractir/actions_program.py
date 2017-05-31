""" Public interface for action list generation
"""

import actgraph_build
import model.crdata as crdata
import concept


def generate_actions_list(application):
    """ Generates list of abstract actions for given process
    tree restoration
    
    :param application:  task to be restored
    :type application: crdata.Application
    :return: list of high-order actions
    """

    process_tree = concept.build_concept_process_tree(application)
    actgraph_build.build_actions_graph(process_tree)
    # todo: sort graph

    return []
