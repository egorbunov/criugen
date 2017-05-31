""" Public interface for action list generation
"""

import actgraph_build
import model.crdata as crdata


def generate_actions_list(application):
    """ Generates list of abstract actions for given process
    tree restoration
    
    :param application:  task to be restored
    :type application: crdata.Application
    :return: list of high-order actions
    """

    actgraph_build.build_actions_graph(application)
    # todo: sort graph

    return []
