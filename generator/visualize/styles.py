from abstractir.actions import *
from pyutils.func import update_dict

BASE_GRAPH_ATTRS = {
    'fontsize': '13',
    'fontcolor': 'black',
    'bgcolor': '#ffffff',
}

BASE_NODE_ATTRS = {
    'shape': 'rectangle',
    'fontcolor': 'black',
    'color': 'black',
    'style': 'filled',
    'fillcolor': '#006699',
}

BASE_EDGE_ATTRS = {
    'color': 'black'
}


def get_action_node_style(action):
    common_node_style = {
        'shape': 'rectangle',
        'fontcolor': 'black',
        'color': 'black',
        'style': 'filled',
        'fontname': 'Verdana'
    }

    if isinstance(action, ShareResourceAction):
        return update_dict({
            'fillcolor': '#f9cbc5'
        }, common_node_style)
    if isinstance(action, CreateResourceAction):
        return update_dict({
            'fillcolor': '#f9e47f'
        }, common_node_style)
    if isinstance(action, RemoveResourceAction):
        return update_dict({
            'fillcolor': '#d9f2f9'
        }, common_node_style)
    if isinstance(action, ForkProcessAction):
        return update_dict({
            'fillcolor': '#e5f9c5'
        }, common_node_style)


def get_process_node_style():
    common_node_style = {
        'shape': 'rectangle',
        'fontcolor': 'black',
        'color': 'black',
        'style': 'invisible',
        'fontname': 'Verdana'
    }

    return update_dict({
        'fillcolor': '#f9e47f'
    }, common_node_style)
