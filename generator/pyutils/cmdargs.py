import argparse


class ArgParserBuilder(object):
    def __init__(self):
        self._description = None
        self._program = None
        self._usage = None
        self._parents = []
        self._arguments = []
        self._formatter = argparse.HelpFormatter
        self._add_help = True

    def description(self, description_str):
        """ Adds description for argument parser
        :rtype: ArgParserBuilder
        """
        self._description = description_str
        return self

    def program(self, program_str):
        """ Sets program string, which will be shown in a help message
        :rtype: ArgParserBuilder
        """
        self._program = program_str
        return self

    def usage(self, usage_str):
        """ Sets usage string for final parser
        :rtype: ArgParserBuilder
        """
        self._usage = usage_str
        return self

    def no_help(self):
        """ Sets, that no help need to be added
        :rtype: ArgParserBuilder
        """
        self._add_help = False
        return self

    def argument(self, *args, **kwargs):
        """ Adds new argument to args parser; See add_argument method for
        argparse.ArgumentParser class for possible positional and keyword
        arguments
        :rtype: ArgParserBuilder
        """
        self._arguments.append((args, kwargs))
        return self

    def raw_help(self):
        """ Sets help formatter to raw text formatter
        :rtype: ArgParserBuilder
        """
        self._formatter = argparse.RawTextHelpFormatter
        return self

    def parent(self, parent_parser):
        """ Adds one more parent parser to the parents list
        :param parent_parser: parent parser
        :type parent_parser: argparse.ArgumentParser
        :rtype: ArgParserBuilder
        """
        self._parents.append(parent_parser)
        return self

    def build(self):
        """ Builds argument parser
        :return: built argument parser
        :rtype: argparse.ArgumentParser
        """

        parser = argparse.ArgumentParser(prog=self._program, description=self._description, usage=self._usage,
                                         parents=self._parents, formatter_class=self._formatter,
                                         add_help=self._add_help)

        for args, kwars in self._arguments:
            parser.add_argument(*args, **kwars)

        return parser
