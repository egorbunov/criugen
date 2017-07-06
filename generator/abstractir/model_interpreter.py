from abstractir.actions import *
from abstractir.process_concept import ProcessConcept


class ResourceDoesNotExist(Exception):
    def __init__(self, action, resource):
        super(ResourceDoesNotExist, self).__init__("Action = {}; Resource = {}".format(action, resource))


class ResourceAlreadyExistsOnShare(Exception):
    def __init__(self, action):
        super(ResourceAlreadyExistsOnShare, self).__init__(action)


class ResourceAlreadyExistsOnCreate(Exception):
    def __init__(self, action):
        super(ResourceAlreadyExistsOnCreate, self).__init__(action)


class ExecutorDoesNotExists(Exception):
    def __init__(self, action, executor):
        super(ExecutorDoesNotExists, self).__init__("Executor = {}, Action = {}".format(executor, action))


class ProcessIsAlreadyForked(Exception):
    def __init__(self, process):
        super(ProcessIsAlreadyForked, self).__init__(process)


class InvolvedProcessDoesNotExists(Exception):
    def __init__(self, action, executor):
        super(InvolvedProcessDoesNotExists, self).__init__("Process = {}, Action = {}".format(executor, action))


class UnknownAction(Exception):
    def __init__(self, action):
        super(UnknownAction, self).__init__(action)


class ModelInterpreter(object):
    def __init__(self):
        self._processes = {0: ProcessConcept(0, -1)}  # type: dict[int, ProcessConcept]

    @property
    def processes_map(self):
        return self._processes

    def execute_program(self, program):
        for act in program:
            self.execute_action(act)

        return self._processes.values()

    def execute_action(self, action):
        if isinstance(action, ShareResourceAction):
            self._execute_share_action(action)
        elif isinstance(action, CreateResourceAction):
            self._execute_create_action(action)
        elif isinstance(action, ForkProcessAction):
            self._execute_fork_action(action)
        elif isinstance(action, RemoveResourceAction):
            self._execute_remove_action(action)
        else:
            raise UnknownAction(action)

    def _execute_share_action(self, action):
        """
        :type action: ShareResourceAction
        """
        if action.process_from.pid not in self._processes:
            raise ExecutorDoesNotExists(action, action.process_from)

        if action.process_to.pid not in self._processes:
            raise InvolvedProcessDoesNotExists(action, action.process_to)

        process_from = self._processes[action.process_from.pid]
        process_to = self._processes[action.process_to.pid]

        if not process_from.has_resource_at_handle(action.resource, action.handle_from):
            raise ResourceDoesNotExist(action, (action.resource, action.handle_from))

        if process_to.has_resource_at_handle(action.resource, action.handle_to):
            raise ResourceAlreadyExistsOnShare(action)

        process_to.add_final_resource(action.resource, action.handle_to)

    def _execute_create_action(self, action):
        """
        :type action: CreateResourceAction
        """
        if action.process.pid not in self._processes:
            raise ExecutorDoesNotExists(action, action.process)

        executor = self._processes[action.process.pid]

        for h in action.handles:
            if executor.has_resource_at_handle(action.resource, h):
                raise ResourceAlreadyExistsOnCreate(action)

            executor.add_final_resource(action.resource, h)

    def _execute_fork_action(self, action):
        """
        :type action: ForkProcessAction
        """
        if action.parent.pid not in self._processes:
            raise ExecutorDoesNotExists(action, action.parent)
        if action.child.pid in self._processes:
            raise ProcessIsAlreadyForked(action.child)

        self._processes[action.child.pid] = ProcessConcept(pid=action.child.pid,
                                                           parent_pid=action.parent.pid)

        child = self._processes[action.child.pid]
        parent = self._processes[action.parent.pid]

        for r, h in parent.iter_all_resource_handle_pairs():
            if not r.is_inherited:
                continue

            child.add_final_resource(r, h)

    def _execute_remove_action(self, action):
        """
        :type action: RemoveResourceAction
        """
        if action.process.pid not in self._processes:
            raise ExecutorDoesNotExists(action, action.process)

        executor = self._processes[action.process.pid]

        if not executor.has_resource_at_handle(action.resource, action.handle):
            raise ResourceDoesNotExist(action, (action.resource, action.handle))

        executor.remove_resource(action.resource, action.handle)
