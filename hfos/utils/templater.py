#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Hackerfleet Technology Demonstrator
# =====================================================================
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


__author__ = 'riot'

import os

from mako.lookup import TemplateLookup
from mako.exceptions import TemplateLookupException

from hfos.utils.logger import log


class SimpleTemplater(object):
    def __init__(self, template):
        self.template = template

    def render(self, input):
        return self.template.format(**input)

class MakoTemplater(object):

    templatepath = os.path.abspath('templates')
    #print(templatepath)
    templatestore = TemplateLookup(directories=[templatepath],
                                   strict_undefined=True,
                                   input_encoding='UTF8',
                                   )

    def loadTemplate(self):
        try:
            self.template = self.templatestore.get_template(self.templatename)
        except TemplateLookupException:
            log("Can't find template '%s' in templatefolder." % self.templatename)


    def __init__(self, template):
        self.templatename = template
        self.loadTemplate()

    def render(self, input):
        self.loadTemplate()
        return self.template.render(**input).encode("UTF-8")
