from abc import ABCMeta, abstractmethod


class ProcessResourceListener(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_proc_add_resource(self, process, r, h):
        """ Process add regular resource callback
        :param process: process, which added the resource
        :param r: resource, which was added
        :param h: handle to the resource within process
        """