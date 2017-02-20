import command


def handle_forks(app):
    programs = {}
    for p in app.processes:
        if p.ppid not in programs:
            programs[p.ppid] = []
        max_fd = max(p.fdt) if p.fdt else 3
        programs[p.ppid].append(command.fork_child(p.ppid, p.pid, max_fd))
    return programs
