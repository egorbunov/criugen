"""
Initialization of credential resources: groups, sessions, user ids and so on
"""

from model import crdata
from pstree import ProcessTreeConcept
from resource_concepts import ResourceConcept, ProcessGroupConcept, ProcessSessionConcept
from resource_handles import *
from trivial_resources import *


def init_sessions_resource(process_tree, app):
    """ Fills processes from process tree with proper session resources and returns
    dict of sessions resources also

    :param process_tree: tree with processes (concepts) to fill with resources
    :type process_tree: ProcessTreeConcept
    :type app: crdata.Application

    :rtype: dict[SessionId, ProcessSessionConcept]
    """

    raw_processes = app.processes
    sessions = {}  # type: dict[SessionId, ProcessSessionConcept]

    for p in raw_processes:
        process_concept = process_tree.proc_by_pid(p.pid)
        session_concept = sessions.setdefault(p.sid, ProcessSessionConcept(p.sid))
        process_concept.add_final_resource(session_concept, handle=NO_HANDLE)

    return sessions


def init_groups_resource(process_tree, app, sessions_map):
    """ Fills processes from process tree with proper group resources and returns
    dict of group resources also

    :param process_tree: tree with processes (concepts) to fill with resources
    :type process_tree: ProcessTreeConcept
    :type app: crdata.Application
    :param sessions_map: map from session id to session resource concept

    :rtype: dict[GroupId, ProcessGroupConcept]
    """

    raw_processes = app.processes
    groups = {}  # type: dict[GroupId, ProcessGroupConcept]

    # tricky moment: in linux, then session is created the group is created too
    # so to support such behaviour we just arrange such resource creation making
    # group resource to depend on session resource:
    for g_id, g in groups.iteritems():
        if g_id not in sessions_map:
            continue

        # session always leads to group creation
        g.add_dependency(sessions_map[g_id], handle_type=type(NO_HANDLE))

    for p in raw_processes:
        process_concept = process_tree.proc_by_pid(p.pid)
        group_concept = groups.setdefault(p.pgid, ProcessGroupConcept(p.pgid))

        process_concept.add_final_resource(group_concept, handle=NO_HANDLE)

    return groups
