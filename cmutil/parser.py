# This file is part of cmutil.
#
# Copyright (C) 2018 ariadne-service gmbh
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#
# ariadne-service gmbh ariadne.ai
# Sebastian Spaar sebastian.spaar@ariadne.ai


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
