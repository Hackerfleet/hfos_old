c-weatherscraper
================
This package scrapes a german website to read the current weather at the base of the main antenna of c-base. Also it
scrapes the Website from TU and downloads the most current rainradar-image.

Additionally, it provides a picture of the current solar status, to predict solar pertuberances and other space-weather
relevant data.

The output consists of weather.html and a few accompanying (mirrored!) images. The webpage can be opened in any Browser,
or be delivered by a local webserver. Every re-run of the manual script overwrites the old weather.html with fresh new
Data.

The service currently defaults to run every 600 seconds (10 minutes), which can be configured in
/etc/c-weatherscraper/config.json

BEWARE! If the script is run more often than that, it might trigger flood-warnings on the website that we scrape.

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
Lives in `/etc/c-weatherscraper/config.json` after installation.
`{
  "interval": "600",
  "place": "/tmp/"
}`

Interval:   Amount of seconds to wait before creating an updated html set
Place:      Folder to write out the html set to.
            Ensure write permissions for user `c-weatherscraper.c-weatherscraper`!

Contributors
============
Johannes 'ijon' Rundfeldt <ijon@hackerfleet.org>
Heiko 'riot' Weinen <riot@hackerfleet.org>
??? (Add yourself or ping us ;)