import itertools

import command
import actions_graph

from model import crdata
from model.reg_file import RegularFilesProvider
from model.pstree import ProcessTree
from model.vm import SharedVmas, PrivateVmas


def generate_program(app):
    """
    Generates and returns linearized program for process tree restoration
    :param app: application
    :type app: crdata.Application
    :return: program == list of commands, each command is dictionary (see command file)
    """

    process_tree = ProcessTree(app.processes)
    shared_vmas_provider = SharedVmas(app.processes, files=app.regular_files)
    private_vmas_provider = PrivateVmas(app.processes, files=app.regular_files)
    reg_files_provider = RegularFilesProvider(app.processes, app.regular_files,
                                              dep_providers=[shared_vmas_provider, private_vmas_provider])

    act_graph = actions_graph.build_action_graph(process_tree, [
        process_tree,
        reg_files_provider,
        private_vmas_provider,
        shared_vmas_provider,
    ])
