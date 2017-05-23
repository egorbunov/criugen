from abc import abstractmethod, ABCMeta, abstractproperty


class ResourceConcept(object):
    """Very straightforward conceptual resource class, which wraps the specific
    resource data
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractproperty
    def payload(self):
        """
        :return: real resource object, contained within ResourceConcept wrapper
        """

    @abstractproperty
    def is_inherited(self):
        """
        :return: true, in case resource is inherited through forking process tree,
        false otherwise
        :rtype: bool
        """

    @abstractproperty
    def is_sharable(self):
        """
        :return: true, in case resource can be shared somehow during processes lifetime
                 i.e. after two processes are forked already
        :rtype: bool
        """

    @abstractproperty
    def handle_types(self):
        """
        :return: array of handle types, which are created during resource creation
        :rtype: list[type]
        """

