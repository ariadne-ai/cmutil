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


class CatmaidGenerator:
    """This class is used to generate CATMAID JSON files from NML files.
    For every CATMAID object, there is lots of repeated data, e.g. username
    or creation date. Instantiate an object with this data, and they get
    added to to each CATMAID object.

    """

    used_ids = set()

    # I assume you are familiar with CATMAID's JSON syntax. Basically,
    # a JSON array of lots of JSON objects, all of them belonging to a specific
    # `catmaid' namespace, e.g. `catmaid.class', `catmaid.relation', and so on.
    # The following fields hold all of these.
    classes = {}
    relations = {}

    neurons = []
    skeletons = []
    classinstanceclassinstances = []
    treenodes = []
    tags = []
    treenodeclassinstances = []
    users = []

    @staticmethod
    def create_id():
        # Create an ID by incrementing IDs we already know
        return (1 if len(CatmaidGenerator.used_ids) == 0
                else max(CatmaidGenerator.used_ids) + 1)

    def __init__(self, user_id, timestamp):
        self.user_id = user_id
        CatmaidGenerator.used_ids.add(user_id)
        self.users.append(
            {'model': 'auth.user',
             'pk': self.user_id,
             'fields': {
                 'username': '',
                 'password': ''}
             }
        )
        self.timestamp = timestamp

    def to_json(self):
        return json.dumps([*self.classes.values(), *self.relations.values(),
                           *self.neurons, *self.classinstanceclassinstances,
                           *self.skeletons, *self.treenodes,
                           *self.tags, *self.treenodeclassinstances,
                           *self.users],
                          indent=4)

    def add_class(self, class_id, class_name, description):
        CatmaidGenerator.used_ids.add(class_id)
        self.classes[class_name] = {
            'model': 'catmaid.class',
            'pk': class_id,
            'fields': {
                'user': self.user_id,
                'creation_time': self.timestamp,
                'edition_time': self.timestamp,
                'class_name': class_name,
                'description': description}
        }

    def add_relation(self, relation_id, relation_name, description, is_reciprocal=False):
        CatmaidGenerator.used_ids.add(relation_id)
        self.relations[relation_name] = {
            'model': 'catmaid.relation',
            'pk': relation_id,
            'fields': {
                'user': self.user_id,
                'creation_time': self.timestamp,
                'edition_time': self.timestamp,
                'relation_name': relation_name,
                'uri': '',
                'description': description,
                'isreciprocal': is_reciprocal}
        }

    def add_neuron(self, neuron_id):
        CatmaidGenerator.used_ids.add(neuron_id)
        self.neurons.append(
            {'model': 'catmaid.classinstance',
             'pk': neuron_id,
             'fields': {
                 'user': self.user_id,
                 'creation_time': self.timestamp,
                 'edition_time': self.timestamp,
                 'class_column': self.classes['neuron']['pk'],
                 'name': 'neuron %s' % neuron_id}
             }
        )

    def add_skeleton(self, skeleton_id):
        CatmaidGenerator.used_ids.add(skeleton_id)
        self.skeletons.append(
            {'model': 'catmaid.classinstance',
             'pk': skeleton_id,
             'fields': {
                 'user': self.user_id,
                 'creation_time': self.timestamp,
                 'edition_time': self.timestamp,
                 'class_column': self.classes['skeleton']['pk'],
                 'name': 'skeleton %s' % skeleton_id}
             }
        )

    def add_classinstanceclassinstance(self, neuron_id, skeleton_id):
        class_id = self.create_id()
        CatmaidGenerator.used_ids.add(class_id)
        self.classinstanceclassinstances.append(
            {'model': 'catmaid.classinstanceclassinstance',
             'pk': class_id,
             'fields': {
                 'user': self.user_id,
                 'creation_time': self.timestamp,
                 'edition_time': self.timestamp,
                 'relation': self.relations['model_of']['pk'],
                 'class_instance_a': skeleton_id,
                 'class_instance_b': neuron_id}
             }
        )

    def add_treenode(self, node_id, skeleton_id, parent, x, y, z):
        CatmaidGenerator.used_ids.add(node_id)
        self.treenodes.append(
            {'model': 'catmaid.treenode',
             'pk': node_id,
             'fields': {
                 'user': self.user_id,
                 'creation_time': self.timestamp,
                 'edition_time': self.timestamp,
                 'editor': self.user_id,
                 'location_x': x - 1,
                 'location_y': y - 1,
                 'location_z': z - 1,
                 'parent': parent,
                 'radius': -1.0,
                 'confidence': 5,
                 'skeleton': skeleton_id}
             }
        )

    def add_tag(self, tag_id, comment):
        CatmaidGenerator.used_ids.add(tag_id)
        self.tags.append(
            {'model': 'catmaid.classinstance',
             'pk': tag_id,
             'fields': {
                 'user': self.user_id,
                 'creation_time': self.timestamp,
                 'edition_time': self.timestamp,
                 'class_column': self.classes['label']['pk'],
                 'name': comment}
             }
        )

    def add_treenodeclassinstance(self, relation_id, treenode_id, target_id):
        instance_id = self.create_id()
        CatmaidGenerator.used_ids.add(instance_id)
        self.treenodeclassinstances.append(
            {'model': 'catmaid.treenodeclassinstance',
             'pk': instance_id,
             'fields': {
                 'user': self.user_id,
                 'creation_time': self.timestamp,
                 'edition_time': self.timestamp,
                 'relation': relation_id,
                 'treenode': treenode_id,
                 'class_instance': target_id}
             }
        )
