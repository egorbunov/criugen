#! /usr/bin/env python2
from __future__ import print_function

import json
import sys

from pyutils.cmdargs import ArgParserBuilder
from abstractir.resource_concepts import *
from crloader import loader
from crloader.crdata import Application
from itertools import chain

PROGRAM_NAME = "criugen.py"


def main(args):
    root_cmd_parser, child_parsers_dict = build_parsers()

    cmd_args = root_cmd_parser.parse_args(args[0:1])

    if cmd_args.command not in child_parsers_dict.keys():
        exit_error("Unknown command: {}".format(cmd_args.command),
                   print_help_parser=root_cmd_parser)

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
    try:
        processor_callback(application, args)
    except BadCommandInput as e:
        exit_error(e.message, print_help_parser=cmd_parser)


def build_parsers():
    # all available top level commands
    generate_program_command = "program"
    generate_actions_command = "actions-ir"
    draw_graph_command = "actions-graph"
    draw_pstree_command = "pstree"

    command_parser = ArgParserBuilder().raw_help() \
        .argument("command",
                  default=generate_program_command,
                  help="Command to execute, possible values are: \n"
                       "    * {} (default) -- generate final restorer program\n".format(generate_program_command) +
                       "    * {} -- generate list of abstract intermediate actions\n".format(generate_actions_command) +
                       "    * {} -- render IR actions graph\n".format(draw_graph_command) +
                       "    * {} -- render process tree graph\n".format(draw_pstree_command) +
                       "\n"
                       "You can see help for each of any command:\n"
                       "    ./criugen.py <command> -h") \
        .build()

    # common parser for every command
    root_parser = ArgParserBuilder().no_help() \
        .description('Process tree restoration program generator') \
        .argument('-d', '--dump_dir', help="Path to process dump images directory", required=True) \
        .argument('--json_img', help="If set, then program parses process dump as json files",
                  default=False,
                  action='store_true') \
        .build()

    # generate program command parser
    gen_program_cmd_parser = build_generate_program_cmd_pb() \
        .parent(root_parser) \
        .program("{} {}".format(PROGRAM_NAME, generate_program_command)) \
        .build()

    # generate intermediate actions command parser
    actions_cmd_parser = build_generate_actions_cmd_pb() \
        .parent(root_parser) \
        .program("{} {}".format(PROGRAM_NAME, generate_actions_command)) \
        .build()

    # common visualization commands parser
    common_viz_parser = build_common_visualization_pb().build()

    # actions graph visualization command parser
    draw_graph_cmd_parser = build_draw_graph_cmd_pb() \
        .parent(root_parser) \
        .parent(common_viz_parser) \
        .program("{} {}".format(PROGRAM_NAME, draw_graph_command)) \
        .build()

    # process tree visualization command parser
    draw_pstree_cmd_parser = build_draw_pstree_cmd_pb() \
        .parent(root_parser) \
        .parent(common_viz_parser) \
        .program("{} {}".format(PROGRAM_NAME, draw_pstree_command)) \
        .build()

    return command_parser, {generate_program_command: (gen_program_cmd_parser, generate_final_commands),
                            generate_actions_command: (actions_cmd_parser, generate_intermediate_actions),
                            draw_graph_command: (draw_graph_cmd_parser, generate_actions_graph),
                            draw_pstree_command: (draw_pstree_cmd_parser, generate_pstree_graph)}


def build_generate_program_cmd_pb():
    return ArgParserBuilder() \
        .description('Generates final program for restorer-interpreter') \
        .argument('-o', '--output_file',
                  help="Output json file with commands, "
                       "if not specified program will be "
                       "printed to stdout")


def build_generate_actions_cmd_pb():
    return ArgParserBuilder() \
        .description('Generates intermediate program representation -- list of abstract actions') \
        .argument('-o', '--output_file',
                  help="Output json file with actions, if not specified actions are printed to stdout")

# constants
SUPPORTED_RENDER_TYPES = ['pdf', 'svg', 'png', 'gv']
SUPPORTED_LAYOUTS_DICT = [('TB', 'from top to bottom'), ('LR', 'from left to right)')]
SUPPORTED_APP_RESOURCES_DICT = {
    'vmas': (VMAConcept, 'virtual memory area'),
    'pipes': (PipeConcept, 'linux pipe'),
    'sessions': (ProcessSessionConcept, 'processes session'),
    'groups': (ProcessGroupConcept, 'process group'),
    'regfiles': (RegularFileConcept, 'regular file'),
    'shmem': (SharedMemConcept, 'shared memory file'),
    'private': (ProcessInternalsConcept, 'process private resource (registers and other stuff)')
}


def build_common_visualization_pb():
    return ArgParserBuilder().no_help() \
        .argument('-o',
                  '--output_file',
                  help='Output graph drawing file path; if not specified,\n'
                       'graph will be saved in the current dir and showed\n'
                       'immediately (like when --show option is specified)',
                  default=None) \
        .argument('--show', help="Show graph immediately", default=False, action='store_true') \
        .argument('--type',
                  help='Output type of the graph render. Possible types are:\n' +
                       "{}".format("\n".join("    * {}".format(v) for v in SUPPORTED_RENDER_TYPES)),
                  default=SUPPORTED_RENDER_TYPES[0]) \
        .argument('--layout',
                  help='Set graphviz ordering layout. Possible values are:\n' +
                       '{}'.format("\n".join("    * {} - {}".format(t[0], t[1]) for t in SUPPORTED_LAYOUTS_DICT)),
                  default=SUPPORTED_LAYOUTS_DICT[0][0]) \
        .argument('--skip',
                  metavar='TO_SKIP',
                  type=str,
                  nargs='+',
                  default=(),
                  help='List of resources short names designating, which resources\n'
                       'should NOT BE rendered to the graph image; that helps sometimes\n'
                       'to make graph or process tree visualization much more clearer\n'
                       'for your particular need to look at some specific resources; \n'
                       'Possible values are:\n' +
                       "{}".format("\n".join("    * {} - {}".format(k, v[1])
                                             for k, v in SUPPORTED_APP_RESOURCES_DICT.iteritems()))
                  ) \
        .argument('--keep',
                  metavar='TO_KEEP_RESOURCE',
                  type=str,
                  nargs='+',
                  default=get_all_resources_type_names(),
                  help='List of resource names, which should BE rendered\n'
                       'to the graph image; see "--skip" option for the list of\n'
                       'possible resources to skip/keep. This list is intersected\n'
                       'with "--skip" list to form the final resource list to be shown.\n'
                       'If not specified all resources are kept.')


def build_draw_graph_cmd_pb():
    return ArgParserBuilder().description('Actions graph visualization command').raw_help() \
        .argument('--cluster',
                  help="If set, then actions are clustered by executing process",
                  default=False,
                  action='store_true') \
        .argument('--sorted',
                  help="If set, then actual actions list is drawn, as it would\n"
                       "be executed by abstract process-restore machine =)",
                  default=False,
                  action='store_true') \
        .argument('--show_cycle',
                  help="If set, then in case --sorted option specified and graph is not\n"
                       "acyclic, cycle is shown as drawing\n",
                  default=False,
                  action='store_true') \
        .argument('--pbuckets',
                  help="If set, then actions are clustered by 'depth'\n",
                  default=False,
                  action='store_true')


def build_draw_pstree_cmd_pb():
    return ArgParserBuilder().description('Process tree visualization command').raw_help() \
        .argument('--notmp',
                  help="If set, then no temporary resource will be shown\n"
                       "on the process tree graph",
                  default=False,
                  action='store_true')


def get_all_resources_type_names():
    return tuple(SUPPORTED_APP_RESOURCES_DICT.keys())


def get_resources_types_to_skip(skipped_type_names, keep_type_names):
    from itertools import chain

    all_type_names = set(get_all_resources_type_names())

    for t in chain(skipped_type_names, keep_type_names):
        if t not in all_type_names:
            raise RuntimeError("Unknown resource type: {}".format(t))

    skip = set(skipped_type_names)
    keep = set(keep_type_names)

    return tuple(SUPPORTED_APP_RESOURCES_DICT[n][0] for n in (all_type_names - (keep - skip)))


class BadCommandInput(RuntimeError):
    """ Exception, thrown in case command input is wrong
    """
    pass


def exit_error(message, print_help_parser=None):
    print("ERROR: {}".format(message))
    print("")
    if print_help_parser is not None:
        print("Look at help page: {} -h".format(print_help_parser.prog))
    exit(1)


def generate_final_commands(application, args):
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


def generate_intermediate_actions(application, args):
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


def check_resources_keywords_list(resources):
    unknown_resources = set(resources) - set(SUPPORTED_APP_RESOURCES_DICT.keys())
    if unknown_resources:
        raise BadCommandInput("Unknown resources specified: {}".format(list(unknown_resources)))


def generate_actions_graph(application, args):
    """
    :param args: parsed command arguments
    :type application: Application
    """
    from abstractir.concept import build_concept_process_tree
    from abstractir.actgraph_build import build_actions_graph
    from abstractir.actgraph_sort import sort_actions_graph, get_actions_buckets
    from pyutils.graph import GraphIsNotAcyclic
    import visualize.core as viz

    check_resources_keywords_list(chain(args.skip, args.keep))

    process_tree = build_concept_process_tree(application)

    resource_types_to_skip = get_resources_types_to_skip(args.skip, args.keep)

    if args.type not in SUPPORTED_RENDER_TYPES:
        raise BadCommandInput("unknown output image type: {}".format(args.type))

    graph = build_actions_graph(process_tree, tuple(resource_types_to_skip))

    print("Graph built.")
    print("Total vertices = {}".format(graph.vertex_num))
    print("Total edges    = {}".format(graph.edges_num))
    print("")

    if not args.sorted:
        node_buckets = None
        if args.pbuckets:
            node_buckets = get_actions_buckets(graph)

        viz.render_actions_graph(graph, args.output_file, output_type=args.type, view=args.show,
                                 layout=args.layout, do_process_cluster=args.cluster, node_buckets=node_buckets)
    else:
        # trying to sort the graph and draw list of actions
        try:
            sorted_actions = sort_actions_graph(graph)
            viz.render_actions_list(sorted_actions, args.output_file,
                                    type=args.type, view=args.show,
                                    layout=args.layout)

        except GraphIsNotAcyclic as e:
            print("ERROR: actions graph is not acyclic: {}".format(e.cycle), file=sys.stderr)

            if not args.show_cycle:
                pass

            # drawing cycle, if we got one =)
            viz.render_actions_cycle(e.cycle, args.output_file,
                                     type=args.type, view=args.show)


def generate_pstree_graph(application, args):
    from abstractir.concept import build_concept_process_tree
    import visualize.core as viz

    check_resources_keywords_list(chain(args.skip, args.keep))

    resource_types_to_skip = get_resources_types_to_skip(args.skip, args.keep)

    process_tree = build_concept_process_tree(application)
    viz.render_pstree(process_tree, args.output_file, output_type=args.type, view=args.show,
                      layout=args.layout, to_skip_resource_types=resource_types_to_skip, no_tmp=args.notmp)


if __name__ == "__main__":
    main(sys.argv[1:])
