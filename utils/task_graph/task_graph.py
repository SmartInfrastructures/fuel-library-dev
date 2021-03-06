#!/usr/bin/env python

# Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import fnmatch
import os
import sys
import argparse
import networkx
import yaml


class IO(object):
    @classmethod
    def debug(cls, msg):
        if not cls.args.debug:
            return
        if not msg.endswith("\n"):
            msg += "\n"
        sys.stdout.write(msg)

    @classmethod
    def output(cls, line, fill=None):
        line = str(line)
        if fill:
            line = line[0:fill].ljust(fill)
        else:
            if not line.endswith("\n"):
                line += "\n"
        sys.stdout.write(line)

    @classmethod
    def task_files(cls, directory, file_pattern='*tasks.yaml'):
        if os.path.isfile(directory):
            if fnmatch.fnmatch(directory, file_pattern):
                yield directory
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if fnmatch.fnmatch(file_name, file_pattern):
                    task_path = os.path.join(root, file_name)
                    if not os.path.isfile(task_path):
                        continue
                    yield task_path

    @classmethod
    def options(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--workbook", "-w",
                            action="store_true",
                            default=False,
                            help='Output the raw workbook')
        parser.add_argument("--clear_workbook", "-c",
                            action="store_true",
                            default=False,
                            help='Output the clear workbook')
        parser.add_argument("--dot", "-D",
                            action="store_true",
                            default=False,
                            help='Output the graph in dot format')
        parser.add_argument("--png", "-p",
                            action="store_true",
                            default=True,
                            help='Write the graph in png format (default)')
        parser.add_argument("--png_file", "-f",
                            type=str,
                            default='task_graph.png',
                            help='Write graph image to this file')
        parser.add_argument("--open", "-o",
                            action="store_true",
                            default=False,
                            help='Open the image after creation')
        parser.add_argument("--debug", "-d",
                            action="store_true",
                            default=False,
                            help='Print debug messages')
        parser.add_argument("--group", "-g",
                            help="Group to build the graph for",
                            default=None)
        parser.add_argument("--stage", "-s",
                            help="Stage to build the graph for",
                            default='deployment')
        parser.add_argument("--topology", "-t",
                            action="store_true",
                            help="Show the tasks topology"
                                 "(possible execution order)",
                            default=False)
        parser.add_argument('places',
                            metavar='PLACE',
                            type=str,
                            nargs='+',
                            help='The list of files of directories where'
                                 'tasks can be found',
                            default=[])

        cls.args = parser.parse_args()
        return cls.args

    @classmethod
    def view_image(cls, img_file):
        if not os.path.isfile(img_file):
            return
        if sys.platform.startswith('linux'):
            os.system('xdg-open "%s"' % img_file)
        elif sys.platform.startswith('darwin'):
            os.system('open "%s"' % img_file)

    @classmethod
    def main(cls):
        cls.options()
        task_graph = TaskGraph()

        for place in cls.args.places:
            for task_file in cls.task_files(place):
                task_graph.load_yaml_file(task_file)

        task_graph.process_data(stage=cls.args.stage, group=cls.args.group)
        task_graph.build_graph()

        if cls.args.topology:
            task_graph.show_topology()
            return

        if cls.args.workbook:
            IO.output(yaml.dump(task_graph.workbook))
            return

        if cls.args.clear_workbook:
            IO.output(yaml.dump(task_graph.data))
            return

        if cls.args.png:
            task_graph.create_image(cls.args.png_file)
            if cls.args.open:
                cls.view_image(cls.args.png_file)


class TaskGraph(object):
    def __init__(self):
        self.data = {}
        self.workbook = []
        self.graph = networkx.DiGraph()
        self._max_task_id_length = None
        self._max_task_stage_length = None

        self.options = {
            'debug': False,
            'prog': 'dot',
            'default_node': {
            },
            'default_edge': {
            },
            'global_graph': {
                'overlap': 'false',
                'splines': 'curved',
                'pack': 'true',
                'sep': '1,1',
                'esep': '0.8,0.8',
            },
            'global_node': {
                'style': 'filled',
                'shape': 'ellipse',
                'fillcolor': 'yellow',
            },
            'global_edge': {
                'style': 'solid',
                'arrowhead': 'vee',
            },
            'non_task_types': [
                'role',
                'stage',
            ]
        }

    def clear(self):
        self.graph.clear()
        self.data = {}
        self.workbook = []

    def node_options(self, id):
        return self.options['default_node']

    def edge_options(self, id_from, id_to):
        return self.options['default_edge']

    def add_graph_node(self, id, options=None):
        if not options:
            options = self.node_options(id)
        if id not in self.data:
            return
        self.graph.add_node(id, options)

    def add_graph_edge(self, id_from, id_to, options=None):
        if not options:
            options = self.edge_options(id_from, id_to)
        if id_from not in self.data:
            return
        if id_to not in self.data:
            return
        self.graph.add_edge(id_from, id_to, options)

    def process_data(self, stage=None, group=None):
        for node in self.workbook:
            if not type(node) is dict:
                continue
            if not node.get('type', None) and node.get('id', None):
                continue
            if node.get('type', None) in self.options['non_task_types']:
                continue
            if not 'stage' in node:
                node['stage'] = 'deployment'
            if not 'requires' in node:
                node['requires'] = []
            if not 'required_for' in node:
                node['required_for'] = []
            if not 'groups' in node:
                node['groups'] = []
            if stage and not node['stage'] == stage:
                continue
            if group and not group in node['groups']:
                continue
            self.data[node['id']] = node

    def build_graph(self):
        for id in self.data.keys():
            self.add_graph_node(id)
            for link in self.data[id]['requires']:
                self.add_graph_edge(link, id)
            for link in self.data[id]['required_for']:
                self.add_graph_edge(id, link)

    @property
    def max_task_id_length(self):
        if self._max_task_id_length:
            return self._max_task_id_length
        self._max_task_id_length = len(max(self.data.keys(), key=len))
        return self._max_task_id_length

    @property
    def max_task_stage_length(self):
        if self._max_task_stage_length:
            return self._max_task_stage_length
        self._max_task_stage_length = max(map(lambda n: len(n['stage']),
                                              self.data.values()))
        return self._max_task_stage_length

    def make_dot_graph(self):
        return networkx.to_agraph(self.graph)

    def show_topology(self):
        number = 1
        for node in networkx.topological_sort(self.graph):
            groups = self.data.get(node, {}).get('groups', [])
            groups = ', '.join(groups)
            stage = self.data.get(node, {}).get('stage', '')
            IO.output(number, 5)
            IO.output(node, self.max_task_id_length + 1)
            IO.output(stage, self.max_task_stage_length + 1)
            IO.output(groups)
            number += 1

    def create_image(self, img_file):
        graph = self.make_dot_graph()
        for attr_name in self.options['global_graph']:
            graph.graph_attr[attr_name] = \
                self.options['global_graph'][attr_name]
        for attr_name in self.options['global_node']:
            graph.node_attr[attr_name] = \
                self.options['global_node'][attr_name]
        for attr_name in self.options['global_edge']:
            graph.edge_attr[attr_name] = \
                self.options['global_edge'][attr_name]
        graph.layout(prog=self.options['prog'])
        graph.draw(img_file)

    def load_data(self, workbook):
        if type(workbook) == list:
            self.workbook += workbook

    def load_yaml(self, yaml_data):
        workbook = yaml.load(yaml_data)
        if type(workbook) == list:
            self.workbook += workbook

    def load_yaml_file(self, yaml_file):
        if os.path.isfile(yaml_file):
            IO.debug("Reading file: '%s'" % yaml_file)
            yaml_file_stream = open(yaml_file, 'r')
            self.load_yaml(yaml_file_stream)
            yaml_file_stream.close()

    def write_dot(self, dot_file):
        graph = self.make_dot_graph()
        graph.write(dot_file)


if __name__ == '__main__':
    IO.main()
