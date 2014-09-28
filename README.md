HFOS - The Hackerfleet Operating System
=======================================

A modern, opensource approach to maritime navigation.

_Obligatory Warning_: **Do not use for navigational purposes!**

Included modules
----------------

* webui
* nmea bus parser
* online-only (yet) moving seamap incl.
 * openseamap
 * openstreetmap
 * openweathermap

Planned features
----------------

* navigation, grib charts
* navgiation aides, planning (and possibly routing)
* complete offline navigation
* datalog, navigational data exchange
* crew management, safety tools
* wireless crew network and general communications

Bugs & Discussion
=================

Please research any bugs you find via our [Github issue tracker for HFOS](https://github.com/hackerfleet/hfos/issues)
and report them if they're still unknown.

If you want to discuss Hackerfleet's technology in general incl. where we're heading, head over to our
[Github discussion forum](https://github.com/hackerfleet/discuss/issues)
...which is cleverly disguised as a Github issue tracker.

Installation
============

Before doing anything with HFOS, be sure you have all the dependencies installed via your distribution's package manager.
For Debian Unstable use this:

    sudo apt-get install mongodb python3.4 python3-pip python3-grib \
                         python3-bson python3-pymongo python3-serial

If you want (and can), install the mongo and bson extensions:

    sudo apt-get install python3-pymongo-ext python3-bson-ext

Development
-----------

Setup the source folder and virtual environment for Python 3.4:

    cd ~/src
    git clone https://github.com/hackerfleet/hfos
    cd hfos
    virtualenv -p /usr/bin/python3.4 --system-site-packages

Activate venv and run setup.py:

    source venv/bin/activate
    python setup.py develop

Run hfos:

    python scripts/hfos

You should see some messy info/debug output and the web engine starting up.
Currently it is set up to serve only on http://localhost:8055 - so point your browser there and explore HFOS.

Debian PKG Generation
---------------------

*Outdated - these do not work without some additional work* Debian instructions:

If you're using Debian, we provide a skeleton to build a cleanly installable dpkg package:

    sudo apt-get install dpkg-dev
    dpkg-buildpackage

Run buildpackage in the top source directory to generate a debian package.


Configuration
-------------

Lives in `/etc/hfos/config.json` after installation, but is currently not used.


Contributors
============

We like to hang out on irc, if you want to chat or help out, join #hackerfleet@freenode :)


Code:

* Heiko 'riot' Weinen <riot@hackerfleet.org>
* Johannes 'ijon' Rundfeldt <ijon@hackerfleet.org>

Assets:

* Fabulous icons by iconmonstr.com and Hackerfleet contributors
* Tumbeasts from http://theoatmeal.com/pl/state_web_winter/tumblr for the error page (CC-BY)

Missing? Add yourself or ping us ;)

:boat: :+1:
