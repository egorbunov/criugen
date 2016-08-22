#! /usr/bin/env python

import sys
import loader
import pprint

def main(args):
	if len(args) != 2:
		print("Bad input arguments.")
		print("USAGE: ./criugen.py /path/to/dump/images")
		exit(1)

	print("Loading images from: {}".format(args[1]))
	application = loader.load_from_imgs(args[1])

	pp = pprint.PrettyPrinter(indent = 4)
	pp.pprint(application.__dict__)

	exit(0)

if __name__ == "__main__":
	main(sys.argv)