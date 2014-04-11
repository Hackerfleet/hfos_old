#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"

from hfos.database.migration import crew, groups, logbook, update
import datetime
import sys

root_group = {'name': 'root',
              'gid': 0,
              'description': 'Administrative crew members'
              }

sailor_group = {'name': 'sailors',
                'gid': 1000,
                'description': 'Active sailors on this vessel'
}

root = {'username': 'root',
        'uid': 0,
        'groups': (0, 1000),
        'name': 'Max',
        'familyname': 'Mustermann',
        'nick': 'maxman',
        'location': 'Bridge',
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

sailor1 = {'username': 'riot',
        'uid': 1000,
        'groups': (0, 1000),
        'name': 'Heiko',
        'familyname': 'Weinen',
        'nick': 'riot',
        'location': 'EVA',
        'd-o-b': (1985, 5, 23),
        'phone': '+49(30)-555-12345',
        'callsign': '',  # exemplary (used by the BNetzAg, non existant callsign)
        'shift': 0,  # 0 == first shift up to max shifts (defined in vessel settings)
        ''
        'certs': ('DSV-SKS', 'DSV-SBF-B', 'DSV-SBF-S'
        ),
        'tripdata': {'trip1': ('tripdata1', 42),
                     'trip2': ('tripdata2', 55),
        },
        'foodpref': 'all',  # 'vegetarian', 'vegan', 'all', special stuff into notes?
        'bunk': 'skipper upper',  # or e.g. 'bow starboard', 'salon port upper'
        'visa': 'true',  # travelvisas. Maybe a list?
        'fees_paid': 'true',  # for cost sharing
        'fees_per_night': 23,  # currency, which one do we pick? Vessel/Trip settings?
        'notes': 'Skipper',
}

sailor2 = {'username': 'ijon',
        'uid': 1001,
        'groups': (1000),
        'name': 'Johannes',
        'familyname': 'Rundfeldt',
        'nick': 'ijon',
        'location': 'Bridge',
        'd-o-b': (1985, 5, 23),
        'phone': '+49(30)-555-54321',
        'callsign': '',  # exemplary (used by the BNetzAg, non existant callsign)
        'shift': 0,  # 0 == first shift up to max shifts (defined in vessel settings)
        ''
        'certs': (
        ),
        'tripdata': {'trip1': ('tripdata1', 42),
                     'trip2': ('tripdata2', 55),
        },
        'foodpref': 'all',  # 'vegetarian', 'vegan', 'all', special stuff into notes?
        'bunk': 'bow starboard',  # or e.g. 'bow starboard', 'salon port upper'
        'visa': 'true',  # travelvisas. Maybe a list?
        'fees_paid': 'true',  # for cost sharing
        'fees_per_night': 23,  # currency, which one do we pick? Vessel/Trip settings?
        'notes': '',
}

sailor3 = {'username': 'ben',
        'uid': 1002,
        'groups': (1000),
        'name': 'Benjamin',
        'familyname': 'Blümchen',
        'nick': 'ben',
        'location': 'Bridge',
        'd-o-b': (1985, 5, 23),
        'phone': '+49(30)-555-11111',
        'callsign': '',  # exemplary (used by the BNetzAg, non existant callsign)
        'shift': 0,  # 0 == first shift up to max shifts (defined in vessel settings)
        ''
        'certs': (
        ),
        'tripdata': {'trip1': ('tripdata1', 42),
                     'trip2': ('tripdata2', 55),
        },
        'foodpref': 'all',  # 'vegetarian', 'vegan', 'all', special stuff into notes?
        'bunk': 'salon starboard',  # or e.g. 'bow starboard', 'salon port upper'
        'visa': 'true',  # travelvisas. Maybe a list?
        'fees_paid': 'true',  # for cost sharing
        'fees_per_night': 23,  # currency, which one do we pick? Vessel/Trip settings?
        'notes': '',
}


sailor4 = {'username': 'jan',
        'uid': 1003,
        'groups': (1000),
        'name': 'Jan',
        'familyname': 'Tenner',
        'nick': 'jan',
        'location': 'Bridge',
        'd-o-b': (1985, 5, 23),
        'phone': '+49(30)-555-11111',
        'callsign': '',  # exemplary (used by the BNetzAg, non existant callsign)
        'shift': 0,  # 0 == first shift up to max shifts (defined in vessel settings)
        ''
        'certs': (
        ),
        'tripdata': {'trip1': ('tripdata1', 42),
                     'trip2': ('tripdata2', 55),
        },
        'foodpref': 'all',  # 'vegetarian', 'vegan', 'all', special stuff into notes?
        'bunk': 'aft starboard',  # or e.g. 'bow starboard', 'salon port upper'
        'visa': 'true',  # travelvisas. Maybe a list?
        'fees_paid': 'true',  # for cost sharing
        'fees_per_night': 23,  # currency, which one do we pick? Vessel/Trip settings?
        'notes': '',
}


sailor5 = {'username': 'bibi',
        'uid': 1004,
        'groups': (1000),
        'name': 'Bibi',
        'familyname': 'Blocksberg',
        'nick': 'bibi',
        'location': 'Bunk',
        'd-o-b': (1985, 5, 23),
        'phone': '+49(30)-555-11111',
        'callsign': '',  # exemplary (used by the BNetzAg, non existant callsign)
        'shift': 0,  # 0 == first shift up to max shifts (defined in vessel settings)
        ''
        'certs': (
        ),
        'tripdata': {'trip1': ('tripdata1', 42),
                     'trip2': ('tripdata2', 55),
        },
        'foodpref': 'all',  # 'vegetarian', 'vegan', 'all', special stuff into notes?
        'bunk': 'salon port',  # or e.g. 'bow starboard', 'salon port upper'
        'visa': 'true',  # travelvisas. Maybe a list?
        'fees_paid': 'true',  # for cost sharing
        'fees_per_night': 23,  # currency, which one do we pick? Vessel/Trip settings?
        'notes': '',
}



sailor6 = {'username': 'grace',
        'uid': 1005,
        'groups': (1000),
        'name': 'Grace',
        'familyname': 'Hopper',
        'nick': 'grace',
        'location': 'Machine Room',
        'd-o-b': (1985, 5, 23),
        'phone': '+49(30)-555-11111',
        'callsign': '',  # exemplary (used by the BNetzAg, non existant callsign)
        'shift': 0,  # 0 == first shift up to max shifts (defined in vessel settings)
        ''
        'certs': (
        ),
        'tripdata': {'trip1': ('tripdata1', 42),
                     'trip2': ('tripdata2', 55),
        },
        'foodpref': 'all',  # 'vegetarian', 'vegan', 'all', special stuff into notes?
        'bunk': 'machinist upper',  # or e.g. 'bow starboard', 'salon port upper'
        'visa': 'true',  # travelvisas. Maybe a list?
        'fees_paid': 'true',  # for cost sharing
        'fees_per_night': 23,  # currency, which one do we pick? Vessel/Trip settings?
        'notes': '',
}


frames = [{'no': 1, 'coords': [54.1779, 7.889], 'course': 320},
          {'no': 2, 'coords': [54.1785, 7.890], 'course': 30},
          {'no': 3, 'coords': [54.1786, 7.8904], 'course': 45},
          {'no': 4, 'coords': [54.1787, 7.8908], 'course': 60},
          {'no': 5, 'coords': [54.1787, 7.8914], 'course': 70},
          {'no': 6, 'coords': [54.1787, 7.8926], 'course': 90},
          {'no': 7, 'coords': [54.1787, 7.8941], 'course': 90},
          {'no': 8, 'coords': [54.1786, 7.8956], 'course': 110}]



if __name__ == "__main__":
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
    logbook.drop()


    root_group_id = update(groups, {'gid': 0}, root_group)


    sailor_group_id = update(groups, {'gid': 1000}, sailor_group)


    from time import time


    #for no, frame in enumerate(frames):
    #    obj = {'no': no}
    #    obj.update(frame)
    #    print(obj)
    #    logbook.insert(obj)
    firstframe = {'no': 0, 'coords': [54.1779, 7.889]}
    logbook.insert(firstframe)



    root_id = update(crew, {'uid': 0}, root)
    sailor1_id = update(crew, {'uid': 1000}, sailor1)
    sailor2_id = update(crew, {'uid': 1001}, sailor2)
    sailor3_id = update(crew, {'uid': 1002}, sailor3)
    sailor4_id = update(crew, {'uid': 1003}, sailor4)
    sailor5_id = update(crew, {'uid': 1004}, sailor5)
    sailor6_id = update(crew, {'uid': 1004}, sailor6)

    #for item in logbook:
    #    logbook_id = update(logbook, {
