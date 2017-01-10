#! /usr/bin/env python2

import json
import sys

import generator
import loader


def main(args):
    if len(args) < 2 or len(args) > 3:
        print("Bad input arguments.")
        print("USAGE: ./criugen.py /path/to/dump/images [/path/to/output/file.json]")
        exit(1)

    print('Loading images from: "{}" ...'.format(args[1]))
    application = loader.load_from_imgs(args[1])

    pp = generator.generate_program(app=application)

    pb = generator.ProgramBuilder()
    print('Generating program...')
    program = pb.generate_program(application)
    print('OK')
    if len(args) == 3:
        with open(args[2], 'w') as f:
            json.dump(program, f, indent=4, sort_keys=True)
    else:
        print(json.dumps(program, sort_keys=True, indent=4, separators=(',', ': ')))

    exit(0)


if __name__ == "__main__":
    main(sys.argv)
