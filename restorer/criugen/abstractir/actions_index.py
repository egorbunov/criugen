from actions import *


class ActionsIndex(object):
    """ Index for actions; Provides faster access for actions with particular
    properties
    """

    def __init__(self):
        self._actions_by_executor = {}
        self._actions_using_process = {}
        self._fork_actions = []
        self._resource_create_acts = {}

    def add_action(self, action):
        if isinstance(action, ForkProcessAction):
            self._actions_by_executor.setdefault(action.parent, []).append(action)
            self._actions_using_process.setdefault(action.parent, []).append(action)
            self._fork_actions.append(action)

        elif isinstance(action, CreateResourceAction):
            self._actions_by_executor.setdefault(action.process, []).append(action)
            self._actions_using_process.setdefault(action.process, []).append(action)
            if action.resource in self._resource_create_acts:
                raise RuntimeError("Duplicate create action for resource!")
            self._resource_create_acts[action.resource] = action

        elif isinstance(action, ShareResourceAction):
            self._actions_by_executor.setdefault(action.process_from, []).append(action)
            self._actions_using_process.setdefault(action.process_from, []).append(action)
            self._actions_using_process.setdefault(action.process_to, []).append(action)

        elif isinstance(action, RemoveResourceAction):
            self._actions_by_executor.setdefault(action.process, []).append(action)
            self._actions_using_process.setdefault(action.process, []).append(action)

        else:
            raise RuntimeError("unknown action [{}]".format(action))

    def actions_by_executor(self, process):
        """ All actions, which are executed by process
        """
        return self._actions_by_executor[process]

    def actions_involving_process(self, process):
        """ All actions, which are executed by process and
            also involve process in execution (i.e. demand, that
            process is "forked" already)
        """
        return self._actions_using_process[process]

    def process_actions_with_resource(self, process, resource, handle):
        """ All actions, which are executed be specified process and
        involve (resource, handle) pair in execution, i.e. demand that
        (resource, handle) was already created within that process;
        Action, which "creates" the resource not included

        :rtype: list
        """
        all_process_actions = self._actions_by_executor[process]
        return [a for a in all_process_actions
                if self._is_action_with_resource(a, resource, handle)]

    @staticmethod
    def _is_action_with_resource(action, resource, handle):
        if isinstance(action, ShareResourceAction):
            return action.resource == resource and action.handle_from == handle
        if isinstance(action, RemoveResourceAction):
            return action.resource == resource and action.handle == handle

        # CreateResourceAction or ForkAction are not really use the resource, so...
        return False

    def process_obtain_resource_action(self, process, resource, handle):
        """ Returns action, which is responsible for "creation" of resource
        (resource, handle) inside process
        :type process: ProcessConcept
        :type resource: ResourceConcept
        :param handle: handle to the resource, which obtain action is queued
        """
        acts_to_check = self._actions_using_process[process]
        for a in acts_to_check:
            # resource action can only be Create action or Share action!

            if isinstance(a, CreateResourceAction) \
                    and a.process == process \
                    and a.resource == resource \
                    and handle in a.handles:
                return a

            if isinstance(a, ShareResourceAction) \
                    and a.resource == resource \
                    and a.process_to == process \
                    and a.handle_to == handle:
                return a

        # if resource is inherited
        if not resource.is_sharable and resource.is_inherited:
            return next(fa for fa in self._fork_actions if fa.child == process)

        # that can't happen if actions were generated correctly =)
        raise RuntimeError("No resource obtain action; process = {}, (r, h) = {}".
                           format(process, (resource, handle)))

    @property
    def fork_actions(self):
        """
        :return: list of fork actions
        :rtype: list[ForkProcessAction]
        """
        return self._fork_actions

    def resource_create_action(self, resource):
        """ Each resource must be created, so for each resource there must be
        the CreateAction
        :rtype: CreateResourceAction
        """
        return self._resource_create_acts[resource]

    @property
    def create_actions(self):
        """ All CreateResourceActions
        :rtype: list[CreateResourceAction]
        """
        return self._resource_create_acts.values()

    def resource_remove_action(self, process, r, h):
        acts = self.process_actions_with_resource(process, r, h)
        return next(a for a in acts if isinstance(a, RemoveResourceAction))
