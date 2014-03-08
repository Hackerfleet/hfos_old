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


import time

logfile = "/var/log/c-weatherscraper/service.log"

start = time.time()
count = 0

def log(*what):
    global count
    global start
    count += 1

    now = time.time() - start
    msg = "[%s] : %.5f : %s :" % ((time.asctime(),
                                         now,
                                         count)
    )

    for thing in what:
        msg += " "
        msg += str(thing)

    try:
        f = open(logfile, "a")
        f.write(msg)
        f.flush()
        f.close()
    except IOError:
        print(msg)
