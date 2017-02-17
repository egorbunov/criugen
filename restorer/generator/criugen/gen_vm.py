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

    """
    What interpreter should do?

    1) Find all COW (private) mappings and:
       - mmap in parent before forking child
       - populate with pages in parent before forking child
       - in every child, which inherited COW-mapping, fix pages (change some of them),
       which were populated in parent
       - after switching to restorer context stage remap! mappings

    2) MAP_SHARED + backed by file; Open files, which are needed by VMAs with MAP_SHARED
       and shmid != 0 (backed by file) and mmap them as usual AFTER transition to restorer
       context (do we need to populate this areas with pages at the end?)

    3) MAP_SHARED | MAP_ANON. Open anonymous file with memfd_open syscall, mmap opened file
       and populate it with pages from shmem_pages.img (or something like this). Close the
       mapping afterwards and make other processes to open this file (it seems to be convenient
       to send this fd using unix socket, so?)
    """

    return {p.pid: [] for p in app.processes}


def __handle_cow_mappings(app):
    pass


def __handle_cow_mappings_proc(proc):
    pass


def __gen_register_vma(app):
    """
    generating commands for registering VMAs
    """
    pass
