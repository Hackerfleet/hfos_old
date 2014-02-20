#!/usr/bin/python

from distutils.core import setup    
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
"""
      )
