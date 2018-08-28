# Copyright 2018 ariadne-service gmbh
#
# This file is part of cmutil.


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
