import unittest

import abstractir.concept as concept
from abstractir.actgraph_build import build_actions_graph
from abstractir.actgraph_sort import sort_actions_graph
from abstractir.model_interpreter import ModelInterpreter
from abstractir.process_concept import ProcessConcept
from crloader import loader


def make_process_tree(dump_dir):
    application = loader.load_from_imgs(dump_dir)
    return concept.build_concept_process_tree(application)


def compare_processes_lists(ps_actual, ps_expected):
    """
    :type ps_actual: list[ProcessConcept]
    :type ps_expected: list[ProcessConcept]
    """

    ps_actual.sort(key=lambda p: p.pid)
    ps_expected.sort(key=lambda p: p.pid)

    if len(ps_actual) != len(ps_expected):
        return False, "processes lists lengths are not equal"

    for i in range(0, len(ps_expected)):
        p_act = ps_actual[i]
        p_exp = ps_expected[i]

        if p_act.pid != p_exp.pid:
            return False, "processes pids on the same positions are not equal"

        if p_act.ppid != p_exp.ppid:
            return False, "processes ppids on the same positions are not equal"

        # comparing only final resources
        act_rhs = set((r, h) for r, h in p_act.iter_all_resource_handle_pairs()
                      if not p_act.is_tmp_resource(r, h))
        exp_rhs = set((r, h) for r, h in p_exp.iter_all_resource_handle_pairs()
                      if not p_exp.is_tmp_resource(r, h))

        act_exp_diff = act_rhs - exp_rhs
        exp_act_diff = exp_rhs - act_rhs

        if act_exp_diff:
            return False, "too much actual resources in comparison with expected: {}".format(act_exp_diff)
        if exp_act_diff:
            return False, "too much expected resource in comparison with actual: {}".format(exp_act_diff)

    return True, "OK"


class TestRealProcessesModelRestore(unittest.TestCase):
    def _test_common(self, image_dir):
        process_tree = make_process_tree(image_dir)
        actgraph = build_actions_graph(process_tree)
        program = sort_actions_graph(actgraph)

        model_interpreter = ModelInterpreter()
        actual_processes = model_interpreter.execute_program(program)
        expect_processes = process_tree.processes

        result, message = compare_processes_lists(actual_processes, expect_processes)

        self.assertTrue(result, msg=message)

    def test_simple(self):
        self._test_common("../../../test_processes/simple/bin/dump")

    def test_complex_groups(self):
        self._test_common("../../../test_processes/complex_groups/bin/dump")

    def test_target_proc(self):
        self._test_common("../../../test_processes/targetproc/bin/dump")

    def test_simple_sessions(self):
        self._test_common("../../../test_processes/simple_session/bin/dump")


if __name__ == '__main__':
    unittest.main()
