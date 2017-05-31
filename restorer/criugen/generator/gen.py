from model import crdata
from abstractir import actions_program


def generate_program(app):
    """
    Generates and returns linearized program for process tree restoration
    :param app: application
    :type app: crdata.Application
    :return: program == list of commands, each command is dictionary (see command file)
    """

    # generating high-order action list
    actions = actions_program.generate_actions_list(app)
