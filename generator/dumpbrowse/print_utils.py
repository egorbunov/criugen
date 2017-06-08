import sys


def print_crdata(obj):
    obj_str = repr(obj).replace(" ", "")
    tab = "    "
    current_depth = 0
    section_openers = ['(', '[', '{']
    section_closers = [')', ']', '}']
    newline_emitters = [',']

    for c in obj_str:
        if c in newline_emitters:
            sys.stdout.write(c)
            sys.stdout.write('\n{}'.format(tab * current_depth))
        elif c in section_openers:
            current_depth += 1
            sys.stdout.write(c)
            sys.stdout.write('\n{}'.format(tab * current_depth))
        elif c in section_closers:
            current_depth -= 1
            sys.stdout.write("\n{}{}\n{}".format(tab * current_depth, c, tab * current_depth))
        else:
            sys.stdout.write(c)

    sys.stdout.flush()
