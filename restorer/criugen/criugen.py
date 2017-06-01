#! /usr/bin/env python2

import argparse
import json
import sys

from abstractir.resource_concepts import *
from model import loader
from model.crdata import Application

PROGRAM_NAME = "criugen.py"


def main(args):
    cmd_parser, child_parsers_dict = build_parsers()

    cmd_args = cmd_parser.parse_args(args[0:1])

    if cmd_args.command not in child_parsers_dict.keys():
        exit_error("Unknown command: {}".format(cmd_args.command), print_help_parser=cmd_parser)

    # parsing specific for command arguments
    cmd_parser, processor_callback = child_parsers_dict[cmd_args.command]
    args = cmd_parser.parse_args(args[1:])

    # each command has obligatory argument
    dump_dir = args.dump_dir
    is_json_img = args.json_img

    # loading application, which is needed by every command
    if is_json_img:
        application = loader.load_from_jsons(dump_dir)
    else:
        application = loader.load_from_imgs(dump_dir)

    # invoking command-special processor
    processor_callback(application, args, cmd_parser)


def build_parsers():
    generate_program_command = "program"
    generate_actions_command = "actions-ir"
    generate_graph_command = "actions-graph"
    commands_list = [generate_program_command, generate_actions_command, generate_graph_command]

    command_parser = argparse.ArgumentParser(description='')
    command_parser.add_argument('command', default=generate_program_command,
                                help="command to execute, possible values are: "
                                     "{}".format(commands_list))

    # common parser
    root_parser = argparse.ArgumentParser(description='Process tree restoration program generator',
                                          add_help=False)
    root_parser.add_argument('dump_dir', help="path to process dump images directory")
    root_parser.add_argument('--json_img', help="if set, then program parses process dump as json files",
                             default=False, action='store_true')

    # program command parser
    gen_program_cmd_parse = argparse.ArgumentParser(prog="{} {}".format(PROGRAM_NAME, generate_program_command),
                                                    description='Generates final program for restorer-interpreter',
                                                    parents=[root_parser])
    gen_program_cmd_parse.add_argument('-o', '--output_file', help="output json file with commands, "
                                                                   "if not specified program will be "
                                                                   "printed to stdout")

    # actions program command parser (for now it is the same as program command parser)
    actions_cmd_parser = argparse.ArgumentParser(prog="{} {}".format(PROGRAM_NAME, generate_actions_command),
                                                 description='Generates intermediate program representation '
                                                             '-- list of abstract actions',
                                                 parents=[root_parser])
    actions_cmd_parser.add_argument('-o', '--output_file', help="output json file with actions, "
                                                                "if not specified actions are printed to stdout")

    # visualization command parser
    graph_command_parser = argparse.ArgumentParser(prog="{} {}".format(PROGRAM_NAME, generate_graph_command),
                                                   description='Actions graph visualization command',
                                                   parents=[root_parser])
    graph_command_parser.add_argument('-o', '--output_file', help="output graph drawing file path; if not specified,"
                                                                  "graph will be saved in the current dir and showed"
                                                                  "immediately (like when --show option is specified)"
                                      ,
                                      default=None)
    graph_command_parser.add_argument('--show', help="show graph immediately",
                                      default=False, action='store_true')
    graph_command_parser.add_argument('--type', help="output drawing type, possible = [svg, pdf, png]; "
                                                     "Default is pdf",
                                      default='pdf')
    graph_command_parser.add_argument('--layout', help="Set graphviz ordering layout, one of "
                                                       "['LR', 'TB', ...]; default: 'TB'",
                                      default='TB')
    graph_command_parser.add_argument('--cluster', help="If set, then actions are clustered by executing process",
                                      default=False, action='store_true')
    graph_command_parser.add_argument('--sorted', help="If set, then actual actions list is drawn, as it would "
                                                       "be executed by abstract process-restore machine =)",
                                      default=False, action='store_true')
    graph_command_parser.add_argument('--skip_vmas', help="Skip all actions with Virtual Memory Area resources",
                                      default=False, action='store_true')
    graph_command_parser.add_argument('--skip_regfiles', help="Skip all actions with Regular File resources",
                                      default=False, action='store_true')
    graph_command_parser.add_argument('--skip_pipes', help="Skip all actions with Pipes resources",
                                      default=False, action='store_true')
    graph_command_parser.add_argument('--skip_groups', help="Skip all actions with Group resources",
                                      default=False, action='store_true')
    graph_command_parser.add_argument('--skip_sessions', help="Skip all actions with Session resources",
                                      default=False, action='store_true')
    graph_command_parser.add_argument('--skip_private', help="Skip all actions with private resources",
                                      default=False, action='store_true')
    graph_command_parser.add_argument('--skip_shmem', help="Skip all actions with Shared Mem resources",
                                      default=False, action='store_true')

    return command_parser, {generate_program_command: (gen_program_cmd_parse, generate_final_commands),
                            generate_actions_command: (actions_cmd_parser, generate_intermediate_actions),
                            generate_graph_command: (graph_command_parser, generate_actions_graph)}


def exit_error(message, print_help_parser=None):
    print("ERROR: {}".format(message))
    print("")
    if print_help_parser is not None:
        print(print_help_parser.format_help())
    exit(1)


def generate_final_commands(application, args, parser):
    """
    :type application: Application
    """

    from generator import gen
    program = gen.generate_program(application)

    json_out_file = args.output_file
    if json_out_file is None:
        print(json.dumps(program, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        with open(json_out_file, 'w') as f:
            json.dump(program, f, indent=4, sort_keys=True)

    raise RuntimeError("This feature is coming soon ;)")


def generate_intermediate_actions(application, args, parser):
    """
    :type application: Application
    """
    from abstractir import actions_program
    acts = actions_program.generate_actions_list(application)

    json_out_file = args.output_file
    if json_out_file is None:
        print(acts)
    else:
        with open(json_out_file, 'w') as f:
            f.write(str(acts))

    raise RuntimeError("This feature is coming soon ;)")


def generate_actions_graph(application, args, parser):
    """
    :type application: Application
    """
    from abstractir.concept import build_concept_process_tree
    from abstractir.actgraph_build import build_actions_graph
    from abstractir.actgraph_sort import sort_actions_graph
    import visualize.core as viz

    process_tree = build_concept_process_tree(application)

    resource_types_to_skip = []
    if args.skip_vmas:
        resource_types_to_skip.append(VMAConcept)
    if args.skip_regfiles:
        resource_types_to_skip.append(RegularFileConcept)
    if args.skip_pipes:
        resource_types_to_skip.append(PipeConcept)
    if args.skip_groups:
        resource_types_to_skip.append(ProcessGroupConcept)
    if args.skip_sessions:
        resource_types_to_skip.append(ProcessSessionConcept)
    if args.skip_private:
        resource_types_to_skip.append(ProcessInternalsConcept)
    if args.skip_shmem:
        resource_types_to_skip.append(SharedMemConcept)

    if args.type not in ['svg', 'pdf', 'png']:
        exit_error("unknown output image type: {}".format(args.type), parser)

    graph = build_actions_graph(process_tree, tuple(resource_types_to_skip))

    if not args.sorted:
        viz.render_actions_graph(graph, args.output_file, output_type=args.type, view=args.show,
                                 layout=args.layout, do_cluster=args.cluster)
    else:
        sorted_actions = sort_actions_graph(graph)
        viz.render_actions_list(sorted_actions, args.output_file, type=args.type, view=args.show,
                                layout=args.layout)


if __name__ == "__main__":
    main(sys.argv[1:])
