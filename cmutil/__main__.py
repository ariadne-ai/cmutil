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


import json
import sys

from cmutil import declxml
from cmutil.parser import parser, fill_arguments
from cmutil import convert
from cmutil.nml import things_processor

args = parser.parse_args()

# If no source file is specified, read input from stdin
if args.source is '':
    input_string = sys.stdin.read()
else:
    with open(args.source) as f:
        input_string = f.read()

try:
    # Depending on args.convert, decide whether to
    #
    # - parse (CATMAID) JSON into NML (XML)
    if args.convert == 'nml':
        catmaid_objects = convert.parse_catmaid_json(input_string)
        things = convert.prepare_nml(catmaid_objects)
        output = declxml.serialize_to_string(things_processor, things,
                                             indent=' ')
    #
    # - parse NML (XML) into (CATMAID) JSON
    else:
        nml_dict = convert.nml2dict(input_string, args.pyknossos)
        args = fill_arguments(args)
        output = convert.create_catmaid(nml_dict,
                                        args.user,
                                        args.timestamp) \
            .to_json()
except (json.JSONDecodeError, declxml.XmlError):
    sys.exit(-1)
except AssertionError:
    print("This doesn't seem to be a valid CATMAID JSON file.",
          file=sys.stderr)
    sys.exit(-1)

if args.output is None:
    print(output)
else:
    with open(args.output, 'w') as fw:
        fw.write(output)
