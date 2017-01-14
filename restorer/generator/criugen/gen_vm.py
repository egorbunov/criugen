import crdata


def handle_vm(app):
    """
    Generates proper commands for each process in application for virtual
    memory restoration

    :type app: crdata.App
    :param app: application, for that commands will be generated
    :return: dictionary with structure: {pid: [command]}, i.e. for every pid
    you'll have list of commands
    """
    return {p.pid: [] for p in app.processes}
