import itertools

import command
import gen_files
import gen_ids
import gen_forks


def generate_program(app):
    """
    Generates and returns linearized program for process tree restoration
    :param app: application (instance of model.crdata.App)
    :return: program == list of commands, each command is dictionary (see command file)
    """

    # For now program can be divided into parts, where each part is
    # list of consequent commands which must be executed within context
    # of one process. Such part starts with command FORK_CHILD or FORK_ROOT.
    # So every such part is corresponds to process with some PID. Parent
    # process commands are always placed above child process commands.

    setsid_cmds = gen_ids.handle_sessions(app)
    reg_files_cmds = gen_files.handle_regular_files(app)
    forks_cmds = gen_forks.handle_forks(app)
    final_programs = __join_programs(app, setsid_cmds, reg_files_cmds, forks_cmds)

    def concat_programs(process, program=None):
        if program is None:
            program = []
        program.extend(final_programs[process.pid])
        for ch in app.process_children(process):
            concat_programs(ch, program)
        return program

    return concat_programs(app.process_parent(app.root_process()))


def __join_programs(app, *args):
    pstree_pids = {p.pid for p in app.processes}
    all_pids = {0} | pstree_pids
    final = {pid: list(itertools.chain(*map(lambda x: x.get(pid, []), args)))
             for pid in all_pids}
    for p in pstree_pids:
        final[p].append(command.fini_cmd(p))
    return final
