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

from setuptools import setup
import os


def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package( dir ):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages

packages = find_packages(".")
package_names = packages.keys()

setup(name = "c-weatherscraper",
      version = "1.0.0",
      description = "c-weatherscraper",

      author = "Hackerfleet Community",
      author_email = "packages@hackerfleet.org",
      url = "https://github.com/ri0t/c-weatherscraper",
      license ="Apache Software License",
      packages = package_names,
      package_dir = packages,
      scripts = [
                  'scripts/c-weatherscraper',
                ],
      data_files=[
                    ('/etc/init.d', ["etc/init.d/c-weatherscraper"]),
                    ('/etc/c-weatherscraper', ["etc/c-weatherscraper/config.json"])
                 ],

      long_description = """
Weatherscraper grabs some relevant data from the web and assembles a well designed HTML5 page to render the
current weather situation for a given area on web clients.
""",
      dependency_links = ['https://github.com/Hackerfleet/axon/archive/master.zip#egg=Axon-1.7.0',
                          'https://github.com/Hackerfleet/kamaelia/archive/master.zip#egg=Kamaelia-1.1.2',
                          'https://github.com/Hackerfleet/pynmea/archive/master.zip#egg=Pynmea-0.3.0',
                          'https://github.com/ri0t/jsonpickle/archive/master.zip#egg=jsonpickle-0.1'
                         ],
      install_requires = ['CherryPy>=3.2.2',
                          'Axon>=1.7.0',
                          'Kamaelia>=1.1.2',
                          'Pynmea>=0.3.0',
                          'Mako>=0.9.1',
                          'jsonpickle>=0.1'
                          ]
      )
