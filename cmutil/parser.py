# Copyright 2018 ariadne-service gmbh
#
# This file is part of cmutil.


import argparse
import datetime
import sys

parser = argparse.ArgumentParser(
    description='Convert CATMAID JSON into NML and vice-versa.')
parser.add_argument('-convert',
                    choices=['nml', 'catmaid'],
                    help='Output format', required=True)
parser.add_argument('-o', '--output',
                    help='Output file. If no file is specified, prints to stdout.')
parser.add_argument('-u', '--user',
                    help="""(Only for creating CATMAID JSON) Specify user ID""",
                    type=int)
parser.add_argument('-pyknossos',
                    help="""(Only for creating CATMAID JSON) Parse PyKNOSSOS files.""",
                    action='store_true')
parser.add_argument('source',
                    help='Input file. If no file is specified, reads from stdin.',
                    nargs='?', default='')


def fill_arguments(args):
    if args.user is None:
        try:
            args.user = int(input('Specify user ID: '))
        except ValueError:
            print('Project ID must be an integer!', file=sys.stderr)
            sys.exit(-1)

    # TODO fix timezone
    # args.timestamp = datetime.datetime.now().isoformat(timespec='milliseconds') + 'Z'
    args.timestamp = datetime.datetime.now().isoformat() + 'Z'

    return args
