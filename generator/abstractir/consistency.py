""" Functions to check if two resource concepts can exist inside 
one process simultaneously.
"""

from resource_concepts import *
from resource_handles import *
from process_concept import ProcessConcept
import crloader.crdata as crdata
from handle_factory import is_fd_handle, get_int_from_fd_handle


def can_exist_together(r1, h1, r2, h2):
    """ Checks given resource pairs (r1, h1) and (r2, h2)
    if they can exist together inside one process
    
    :param process: process concept
    :type process: ProcessConcept
    :param r1: first resource 
    :type r1: ResourceConcept
    :param h1: handle of the first resource
    :param r2: second resource
    :type r2: ResourceConcept
    :param h2: handle of the second resource
    :return: True if resources can exist together, False otherwise
    """

    if isinstance(r1, ProcessSessionConcept) and isinstance(r2, ProcessSessionConcept):
        return _check_sessions(r1, r2)
    if isinstance(r1, ProcessGroupConcept) and isinstance(r2, ProcessGroupConcept):
        return _check_groups(r1, r2)
    if isinstance(r1, VMAConcept) and isinstance(r2, VMAConcept):
        return _check_vmas(r1, r2)
    if is_fd_handle(h1) and is_fd_handle(h2):
        return _check_fd_handled_resources(r1, h1, r2, h2)

    # for now all other clashes of resources are not supported
    return True


def _check_groups(g1, g2):
    """ Checks if two groups are equal or not. Obviously process
    can't be inside two process groups simultaneously, so this method 
    always returns False if g1 != g2
    :param g1: first group 
    :type g1: ProcessGroupConcept
    :param g2: second group
    :type g2: ProcessGroupConcept
    :return: True or False 
    """
    return g1 == g2


def _check_sessions(s1, s2):
    """ Logically same as groups but for sessions
    :type s1: ProcessSessionConcept
    :type s2: ProcessSessionConcept
    """
    return s1 == s2


def _check_vmas(vma1, vma2):
    """
    :type vma1: VMAConcept
    :type vma2: VMAConcept
    """
    raw_vma1 = vma1.payload  # type: crdata.VmArea
    raw_vma2 = vma2.payload  # type: crdata.VmArea

    # just checking if two contiguous ranges overlap or not
    if raw_vma1.end >= raw_vma2.start and raw_vma2.end >= raw_vma1.start:
        return True
    return False


def _check_fd_handled_resources(r1, h1, r2, h2):
    return get_int_from_fd_handle(h1) != get_int_from_fd_handle(h2)
