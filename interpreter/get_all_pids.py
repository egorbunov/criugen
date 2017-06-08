#! /usr/bin/env python

import json
import sys

def main(cmd_f_name):
	with open(cmd_f_name, "r") as f:
		program = json.load(f)
		for p in program:
			if p["#command"] == "FORK_CHILD":
				print(p["child_pid"])
	exit(0)

if __name__ == "__main__":
	if (len(sys.argv) != 2):
		print("USAGE: ./get_root_pid /path/to/commands.json")
		exit(1)
	main(sys.argv[1])