hfos
====
The Hackerfleet Operating System - Demonstrator Edition
Warning: Do not use for navigational purposes!
Included modules: nmea parser, webui, about
Planned modules:
* navigation, weather/grib charts
* navgiation aides, planning and routing
* crew management, safety tools
* wireless crew network and general communications

Installation
============
If you're using debian:

`sudo apt-get install dpkg-dev
dpkg-buildpackage`

Run buildpackage in the top source directory to generate a debian package.
Afterwards you'll have to install the Python packages manually:

`sudo python3 setup.py install`

(This maybe a bug in upstream debian skeleton, will be vanquished soon)


Configuration
=============
Lives in `/etc/hfos/config.json` after installation, but is currently not used.

Contributors
============
Code:
* Heiko 'riot' Weinen <riot@hackerfleet.org>
* Johannes 'ijon' Rundfeldt <ijon@hackerfleet.org>

Assets:
* Fabulous icons by iconmonstr.com and Hackerfleet contributors
* Tumbeasts from http://theoatmeal.com/pl/state_web_winter/tumblr for the error page (CC-BY)

Missing? (Add yourself or ping us ;)

