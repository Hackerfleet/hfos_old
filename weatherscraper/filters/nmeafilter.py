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

class nmeaFilter(object):
    """Filters out sentences by given type
    """

    def __init__(self, sentencetype):
        self.sentencetype = sentencetype

    def filter(self, sentences):
        for sentence in sentences:

            if sentence['type'] == self.sentencetype:
                return sentence
