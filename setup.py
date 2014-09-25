#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Hackerfleet Technology Demonstrator License
# ===========================================
# Copyright (C) 2011-2014 riot <riot@hackerfleet.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from setuptools import setup


# TODO: rebuild the package finder using setuptools & pkg_resources

def include_readme():
    readme = open("README.md")
    include = readme.readlines(10)[2:10]
    readme.close()
    return "".join(include)


def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
    )


def find_packages(path, base=""):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package(dir):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages


packages = find_packages(".")
package_names = packages.keys()

setup(name="hfos",
      version="0.3.0",
      description="hfos",

      author="Hackerfleet Community",
      author_email="packages@hackerfleet.org",
      url="https://github.com/hackerfleet/hfos",
      license="GNU General Public License v3",
      packages=package_names,
      package_dir=packages,
      scripts=[
          'scripts/hfos',
      ],
      data_files=[
          ('/etc/init.d', ["etc/init.d/hfos"]),
          ('/etc/hfos', ["etc/hfos/config.json"])
      ],

      long_description=include_readme(),
      dependency_links=['https://github.com/Hackerfleet/axon/archive/master.zip#egg=Axon-1.7.0',
                        'https://github.com/Hackerfleet/kamaelia/archive/master.zip#egg=Kamaelia-1.1.2.1',
                        'https://github.com/Hackerfleet/pynmea/archive/master.zip#egg=Pynmea-0.3.0',
                        ],

      # These versions are not strictly checked, older ones may or may not work.
      # TODO: This is messed up, see #4
      install_requires=['CherryPy==3.3.0',
                        'Axon==1.7.0',
                        'Kamaelia==1.1.2.1',
                        'Pynmea==0.3.1',
                        'Mako==0.9.1',
                        'voluptuous==0.8.5',
      ]

)
