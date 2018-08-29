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

from . import declxml
from .nml import things_processor, pyknossos_things_processor
from .catmaid import CatmaidGenerator


def parse_catmaid_json(json_str):
    """All CATMAID JSON files consist of a JSON array of JSON objects,
    so this function should always return a list of dicts.

    :type json_str: str
    :rtype: []
    """
    try:
        _ = json.loads(json_str)
        assert (all(isinstance(x, dict) for x in _))
        return _
    except json.JSONDecodeError as error:
        print(error, file=sys.stderr)
        raise


def create_catmaid(nml_dict, user_id, timestamp):
    """Creates a CatmaidGenerator object from a Python dict of NML tags.

    :type nml_dict: dict
    :type project_id: int
    :type user_id: int
    :type timestamp: str
    :rtype: CatmaidGenerator
    """

    # First of all, we need the IDs of all nodes so that we don't
    # accidentally duplicate an ID when we add a CATMAID object
    for thing in nml_dict['things']:
        for node in thing['nodes']:
            CatmaidGenerator.used_ids.add(node['id'])

    catmaid = CatmaidGenerator(user_id, timestamp)

    # Add CATMAID boilerplate objects (classes, relations).
    # The ID (the first argument) of the following lines can vary.
    # However, I exported some example CATMAID data, and decided to re-use the
    # IDs that I found in those files.
    catmaid.add_class(50, 'root', 'The root node for the tracing system')
    catmaid.add_class(48, 'label', 'A label')
    catmaid.add_class(47, 'neuron', 'A neuron representation')
    catmaid.add_class(46, 'skeleton', 'The representation of a skeleton')
    catmaid.add_relation(54, 'model_of', 'Marks something as a model of something else.')
    catmaid.add_relation(56, 'labeled_as', 'Something is labeled by sth. else.')

    things = nml_dict['things']
    # Let's start. Every `thing' in `things' is a CATMAID neuron.
    for thing in things:
        # In NML (and unlike CATMAID JSON), `thing' IDs and `node' IDs can
        # overlap. To map back to CATMAID neurons, we hope that each `thing'
        # has additional properties specifying a neuron and skeleton ID.
        # Re-use these IDs if they are not already used.
        if ('neuron_id' in thing
                and thing['neuron_id'] != 0
                and thing['neuron_id'] not in CatmaidGenerator.used_ids):
            neuron_id = thing['neuron_id']
        elif thing['id'] in CatmaidGenerator.used_ids:
            neuron_id = CatmaidGenerator.create_id()
        else:
            neuron_id = thing['id']
        catmaid.add_neuron(neuron_id)

        # For every neuron, create a skeleton.
        # Re-use `skeleton_id' if it exists, and is not yet used.
        if ('skeleton_id' in thing
                and thing['skeleton_id'] != 0
                and thing['skeleton_id'] not in CatmaidGenerator.used_ids):
            skeleton_id = thing['skeleton_id']
        else:
            skeleton_id = CatmaidGenerator.create_id()
        catmaid.add_skeleton(skeleton_id)

        # For every skeleton, create a `classinstanceclassinstance'.
        # This will create an ID for `classinstanceclassinstance' automatically.
        catmaid.add_classinstanceclassinstance(neuron_id, skeleton_id)

        # Create a lookup map to hold each node's parent.
        edges = {edge['target']: edge['source'] for edge in thing['edges']}

        for node in thing['nodes']:
            node_id = node['id']
            catmaid.add_treenode(node_id, skeleton_id,
                                 edges[node_id] if node_id in edges else None,
                                 node['x'], node['y'], node['z'])

            # Does the node have a comment?
            if 'comment' in node and node['comment'] != '':
                tag_id = CatmaidGenerator.create_id()
                catmaid.add_tag(tag_id, node['comment'])
                catmaid.add_treenodeclassinstance(catmaid.relations['labeled_as']['pk'],
                                                  node_id, tag_id)

    # Check for the <comments> tag found in older NML versions.
    if len(nml_dict['comments']) > 0:
        for comment in nml_dict['comments']:
            tag_id = CatmaidGenerator.create_id()
            catmaid.add_tag(tag_id, comment['content'])
            catmaid.add_treenodeclassinstance(catmaid.relations['labeled_as']['pk'],
                                              comment['node'], tag_id)

    return catmaid


def nml2dict(xml_str, is_pyknossos=False):
    """Converts NML into a Python dict.

    :type xml_str: str
    :param bool is_pyknossos: Whether to parse NML files generated from PyKNOSSOS.
    :returns: Python dict of NML tags
    :rtype: dict
    """

    try:
        if is_pyknossos:
            _ = declxml.parse_from_string(pyknossos_things_processor, xml_str)
        else:
            _ = declxml.parse_from_string(things_processor, xml_str)
        return _
    except declxml.XmlError as error:
        print(error, file=sys.stderr)
        raise


def prepare_nml(catmaid_objects):
    classes = {}
    relations = {}
    classinstances = []
    classinstanceclassinstances = []
    treenodes = []
    treenodeclassinstances = []

    for _ in catmaid_objects:
        if _['model'] == 'catmaid.class':
            classes[_['fields']['class_name']] = _
        elif _['model'] == 'catmaid.relation':
            relations[_['fields']['relation_name']] = _
        elif _['model'] == 'catmaid.classinstance':
            classinstances.append(_)
        elif _['model'] == 'catmaid.classinstanceclassinstance':
            classinstanceclassinstances.append(_)
        elif _['model'] == 'catmaid.treenode':
            treenodes.append(_)
        elif _['model'] == 'catmaid.treenodeclassinstance':
            treenodeclassinstances.append(_)

    things = {}
    skeletons = {}
    # Create all <thing>s. As a shortcut, we look for all `classinstanceclassinstance's
    # whose IDs match the relation `model_of'.
    for neuron in filter(lambda x: x['fields']['relation'] == relations['model_of']['pk'], classinstanceclassinstances):
        things[neuron['fields']['class_instance_b']] = {
            'id': neuron['fields']['class_instance_b'],
            'neuron_id': neuron['fields']['class_instance_b'],
            'skeleton_id': neuron['fields']['class_instance_a'],
            'nodes': [],
            'edges': []
        }
        skeletons[neuron['fields']['class_instance_a']] = things[neuron['fields']['class_instance_b']]

    # Comments are all `classinstance's whose `fields.class_column' match the
    # ID of the `label' class.
    comments = {comment['pk']: comment
                for comment in classinstances
                if comment['fields']['class_column'] == classes['label']['pk']}

    # Create a map of treenodes IDs to comments
    treenode_map = {_['fields']['treenode']: _['fields']['class_instance']
                    for _ in treenodeclassinstances
                    if _['fields']['relation'] == relations['labeled_as']['pk']}

    for node in treenodes:
        skeleton_id = node['fields']['skeleton']
        skeletons[skeleton_id]['nodes'].append({
            'x': int(node['fields']['location_x']) + 1,
            'y': int(node['fields']['location_y']) + 1,
            'z': int(node['fields']['location_z']) + 1,
            'id': node['pk'],
            'comment': comments[treenode_map[node['pk']]]['fields']['name'] if node['pk'] in treenode_map else ''
        })

        if node['fields']['parent'] is not None:
            skeletons[skeleton_id]['edges'].append({
                'target': node['pk'],
                'source': node['fields']['parent']
            })

    return {'things': things.values(),
            'comments': [{'node': _,
                          'content': comments[treenode_map[_]]['fields']['name']}
                         for _ in treenode_map]}
