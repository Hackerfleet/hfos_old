#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"

from hfos.database.migration import crew, groups, update
import datetime
import sys

# Since this is the initial migration, we don't do backups.
# So, ask the user nicely, then destroy all his data, if he agrees.

response = "N"
response = input("This will destroy all your hfos data! Are you sure? N/y\n").upper()
if response != "Y":
    print("Okay. Not doing anything.")
    sys.exit(-1)
else:
    print("Dropping crew and groups.")

crew.drop()
groups.drop()

root_group = {'name': 'root',
              'gid': 0,
              'description': 'Administrative crew members'
              }

root_group_id = update(groups, {'gid': 0}, root_group)

sailor_group = {'name': 'sailors',
                'gid': 1000,
                'description': 'Active sailors on this vessel'
}

sailor_group_id = update(groups, {'gid': 1000}, sailor_group)

root = {'username': 'root',
        'uid': 0,
        'groups': (0, 1000),
        'name': 'Max',
        'familyname': 'Mustermann',
        'nick': 'maxman',
        'd-o-b': (1985, 5, 23),
        'phone': '+49(30)-555-55555',
        'callsign': 'DP0AA',  # exemplary (used by the BNetzAg, non existant callsign)
        'shift': 0,  # 0 == first shift up to max shifts (defined in vessel settings)
        ''
        'certs': ('ROC',
                  'ISAF-OSR',
                  'DSV-SKS', 'DSV-SBF-B', 'DSV-SBF-S',
                  'UBI',
                  'SRC',
                  'CEPT-RAL'
        ),
        'tripdata': {'trip1': ('tripdata1', 42),
                     'trip2': ('tripdata2', 55),
        },
        'foodpref': 'all',  # 'vegetarian', 'vegan', 'all', special stuff into notes?
        'bunk': 'machinist',  # or e.g. 'bow starboard', 'salon port upper'
        'visa': 'true',  # travelvisas. Maybe a list?
        'fees_paid': 'true',  # for cost sharing
        'fees_per_night': 30,  # currency, which one do we pick? Vessel/Trip settings?
        'notes': 'Free text for Max special notes.',
}

root_id = update(crew, {'uid': 0}, root)

