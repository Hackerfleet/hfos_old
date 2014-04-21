#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"

from hfos.database.mongo import switches, gauges, crew, groups, logbook, update, insert

import copy
import sys

# SWITCHES
# To build a ship-like switchboard that enables toggling power consumers or other things, we need
# to represent toggleable on/off switches and how to actually read and operate them, as well as their descriptions
# and possibly dependencies.
#
# A switch consists of a status flag (on/off(/faulty/disabled?)) and method descriptors.
#
# Method descriptors define (not yet implemented) readers and writers to actually handle switch management:
# For example an i2c operated switch:
# {'read': ('i2c', {'bus': 0, 'addr': 0x0}),
#  'write': ('i2c', {'bus': 0, 'addr': 0x300})
# }
# would try to read a bit on address 0 of bus 0 to determine the current state of its associated switch.
#
# A serial operated switch might look like this:
# {'read': ('serial', {'msg': 'pin_status', 'result': 'Ok. Value is $DATA'}),
#  'write': ('serial', {'msg': 'pin_set', 'result': 'Ok. Pin now $DATA'}
# }
# Notice the idea of a planned response evaluation.
#
# For now, we have no real methods to operate, so we create mockup switches:

switch_default = {
    'name': '',
    'id': 0,
    'status': False,
    'methods': {'read': None, 'write': None}
}

# A lot of them. Regard this list as, maybe an initial dataset to pick from for a vessel's configuration.

switchnames = [
    "Heating", "AC", "Engine", "Navigation Lights",
    "Radio", "Anchor Light", "Deck Light", "Water Pump",
    "Depth Sounder",
    "Radar", "AIS", "Horn", "Charger",
    "Cabin Lights Bow", "Cabin Lights Salon", "Cabin Lights Aft",
    "Galley",
    "Outlets Bow", "Outlets Salon", "Outlets Aft",
]

def insert_switches():
    for id, switch in enumerate(switchnames):
        newswitch = copy.copy(switch_default)
        newswitch['name'] = switch
        newswitch['id'] = id
        switch_id = insert(switches, newswitch)


# GAUGES
#
# Gauges are a lot like switches - lacking write support.
#

gauge_default = {'status': False,
                 'method': (None, {})
}

gaugenames = [
    "Battery A Voltage",
    "Battery B Voltage",
    "Battery A Current",
    "Battery B Current",
    "USV",
    "Diesel Port",
    "Diesel Starboard",
    "Water Port",
    "Water Starboard",
    "Faeces Tank",
    "Power Consumption",
    "Engine Power",
    "Rudder",
]

def insert_gauges():
    for no, gauge in enumerate(gaugenames):
        newgauge = copy.copy(gauge_default)
        newgauge['name'] = gauge
        gauge_id = insert(gauges, newgauge)

# CREW

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


def insert_groups():
    root_group_id = update(groups, {'gid': 0}, root_group)
    sailor_group_id = update(groups, {'gid': 1000}, sailor_group)


def insert_crew():
    root_id = update(crew, {'uid': 0}, root)
    sailor1_id = update(crew, {'uid': 1000}, sailor1)
    sailor2_id = update(crew, {'uid': 1001}, sailor2)
    sailor3_id = update(crew, {'uid': 1002}, sailor3)
    sailor4_id = update(crew, {'uid': 1003}, sailor4)
    sailor5_id = update(crew, {'uid': 1004}, sailor5)
    sailor6_id = update(crew, {'uid': 1004}, sailor6)


# LOGBOOK

frames = [{'no': 1, 'coords': [54.1779, 7.889], 'course': 320, 'speed': 1.4},
          {'no': 2, 'coords': [54.1785, 7.890], 'course': 30, 'speed': 2},
          {'no': 3, 'coords': [54.1786, 7.8904], 'course': 45, 'speed': 4},
          {'no': 4, 'coords': [54.1787, 7.8908], 'course': 60, 'speed': 5.5},
          {'no': 5, 'coords': [54.1787, 7.8914], 'course': 70, 'speed': 6},
          {'no': 6, 'coords': [54.1787, 7.8926], 'course': 90, 'speed': 6},
          {'no': 7, 'coords': [54.1787, 7.8941], 'course': 90, 'speed': 10},
          {'no': 8, 'coords': [54.1786, 7.8956], 'course': 110, 'speed': 15}]


def insert_logbook():
    firstframe = {'no': 0, 'coords': [54.1779, 7.889]}
    logbook.insert(firstframe)

# UTILITIES

def drop_all():
    switches.drop()
    gauges.drop()
    crew.drop()
    groups.drop()
    logbook.drop()


if __name__ == "__main__":
    # Since this is the initial migration, we don't do backups.
    # So, ask the user nicely, then destroy all his data, if he agrees.

    response = "N"
    response = input("This will destroy all your hfos data! Are you sure? N/y\n").upper()
    if response != "Y":
        print("Okay. Not doing anything.")
        sys.exit(-1)
    else:
        print("Dropping tables")

    drop_all()

    insert_switches()
    
    insert_gauges()
    
    insert_logbook()

    insert_groups()
    insert_crew()
