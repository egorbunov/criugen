import command
from model import crdata


def handle_sessions(app):
    """
    Generates proper commands for session leader restoration

    :type app: crdata.App
    :param app: application
    :return: programs dict, list of commands for each process in app
    """
    programs = {}
    for p in app.processes:
        programs[p.pid] = []
        if p.sid == p.pid:
            programs[p.pid].append(command.setsid(p.pid))
    return programs
