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



# thanks to kristall, who helped me big time in learning python and who teached me line-by-line how to write this
# script. Everything that appears unprofessionally in this script has been grown on my madness and has nothing to do
# with kristalls ingenuity and teaching.


import urllib.request
import time
import os

from weatherscraper.logging import log

def download(url, targetname):
    """Copy the contents of a file from a given URL
    to a local file.
    """

    webFile = urllib.request.urlopen(url)
    localFile = open(targetname, 'wb')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()


def createPage(place="./"):
    """Gets all the content and (a little bit awkwardly) assembles some blobs of html.
    """

    log("Getting content")
    local_weather = urllib.request.urlopen('http://www.wetter24.de/wetter/berlin-alexanderplatz/10389.html')
    full_src_local_weather = local_weather.read().decode()

    solar_weather = urllib.request.urlopen('http://sdo.gsfc.nasa.gov/data/')
    full_src_solar_weather = solar_weather.read().decode('ISO 8859-1')

    snippet_local = full_src_local_weather[
                    full_src_local_weather.find('head_ww'):full_src_local_weather.find('hPa<') + 4]

    snippet_solar_begin = full_src_solar_weather.find('<h1>AIA 094, 335, 193</h1>')
    snippet_solar = full_src_solar_weather[
                    snippet_solar_begin:full_src_solar_weather.find('latest_image', snippet_solar_begin) + 9]

    condition_zahl = snippet_local.find('head_ww')
    condition_begin = snippet_local.find('alt="', condition_zahl) + 5
    condition_end = snippet_local.find('"', condition_begin)
    condition = snippet_local[condition_begin:condition_end]

    date_and_time = time.localtime()
    year = date_and_time[0]
    month = date_and_time[1]
    day = date_and_time[2]
    hours = date_and_time[3]
    minutes = date_and_time[4]
    seconds = date_and_time[5]

    print(' ')
    print('WEATHER CONDITIONS')
    print("captured at: %s.%s.%s %s:%s h %ssec" % (day, month, year, hours, minutes, seconds))
    print('captured at base of main-antenna')
    print(' ')

    print('Bedingungen', condition)

    temp_zahl = snippet_local.find('head_tt2')
    temp_begin = snippet_local.find('>', temp_zahl) + 1
    temp_end = snippet_local.find('</p>', temp_zahl)
    temp = snippet_local[temp_begin:temp_end]

    print('Temperature <b>', temp, ' °C</b>')

    wind_zahl = snippet_local.find('wind32px')
    wind_begin = snippet_local.find('alt="', wind_zahl) + 5
    wind_end = snippet_local.find('" title', wind_zahl)
    wind = snippet_local[wind_begin:wind_end]

    print('Wind from <b>', wind, ' </b>')

    w_speed_zahl = snippet_local.find('head_ff2')
    w_speed_begin = snippet_local.find('>', w_speed_zahl) + 1
    w_speed_end = snippet_local.find('</p>', w_speed_zahl)
    w_speed = snippet_local[w_speed_begin:w_speed_end]

    print('Wind with <b>', w_speed, '</b>')

    press_zahl = snippet_local.find('head_ppp2')
    press_begin = snippet_local.find('>', press_zahl) + 1
    press_end = snippet_local.find('</p>', press_begin)
    press = snippet_local[press_begin:press_end]

    print('Pressure <b>', press, '</b>')

    rainradar_url = 'http://wind.met.fu-berlin.de/loops/radar_100/R.NEW.gif'
    rainradar_name = 'rainradar.gif'
    print('starting download procedure of rain-radar using ', rainradar_url)
    download(rainradar_url, place + rainradar_name)

    '''
    solarweather_txt_url = 'http://www.swpc.noaa.gov/ftpdir/lists/particle/Gs_part_5m.txt'
    solarweather_txt_name = '5minute-table.txt'
    print('starting download procedure of solar weather table 5min res. using ',solarweather_txt_url)
    download(solarweather_txt_url,solarweather_txt_name)
    '''

    solar_img_begin = snippet_solar.find('href="') + 6
    solar_img_end = snippet_solar.find('">', solar_img_begin)
    solar_img = 'http://sdo.gsfc.nasa.gov' + snippet_solar[solar_img_begin:solar_img_end]
    print('starting download procedure of solar weather image', solar_img)
    download(solar_img, place + 'solar_img.jpg')

    log("Writing html to '%s'" % (os.path.abspath("weather_c-base.html")))

    fobj = open(place + "weather_c-base.html", "w")
    fobj.write(
        """<!DOCTYPE html>
<html lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <style type="text/css">
      body {
        padding-top: 10px;
      }
      .tabelle {
    width: 100%;
    }
      .solar {
    color:#FFFFFF;
    background-color:#333333;
    }
    </style>
    <title>c-beam</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">
    <script src="./static/jquery.min.js"></script>
    <script src="./static/bootstrap-dropdown.js"></script>
    <link href="./static/cyborg.css" rel="stylesheet" type="text/css">
    <script src="./static/bootstrap.js"></script>
    <link href="https://c-beam.cbrp3.c-base.org/static/c-base-bootstrap/css/bootstrap-responsive.css" rel="stylesheet">
    <link href="https://c-beam.cbrp3.c-base.org/static/c-base-bootstrap/css/bootstrap.custom.css" rel="stylesheet">
    <!-- link rel="shortcut icon" href="ico/favicon.ico" -->
</head>
<body>
  <div class="container">
    <h1>nerdctrl status monitor</h1>
    <hr><p></p>
    <table class="tabelle">
        <tr>
<td valign="top">
""")

    fobj.write('<p><b>WEATHER CONDITIONS</b><br />')
    fobj.write("captured at: %s.%s.%s %s:%s h %ssec <br />" % (day, month, year, hours, minutes, seconds))
    fobj.write('captured at base of main-antenna </p>')
    fobj.write("<p>")
    fobj.write("Bedingungen: <b> %s </b> <br />" % (condition))
    fobj.write('Temperature <b> %s °C</b> <br />' % (temp))
    fobj.write('Wind from <b> %s </b> <br />' % (wind))
    fobj.write('Wind with <b> %s </b> <br />' % (w_speed))
    fobj.write('Pressure <b>%s</b> </p>' % (press))
    fobj.write(
        """	</td>
        <td><img src="rainradar.gif" alt="Regenradar"></td>
            <td><img src="solar_img.jpg" alt="Sonne, live" width="500px"></td>
        </tr>""")
    fobj.write(
        """	</table>
    <footer class="row"> 
computer says this is the footer and noooooo 
    </footer> 
  </div> <!-- container --> 
<script src="./static/html5slider.js"></script>
</body></html> 
 """)
    fobj.close()

    log("html closed.")

if __name__ == '__main__':
    createPage()



    #import sys
    #
    # if len(sys.argv) == 2:
    #     try:
    #         download(sys.argv[1])
    #     except IOError:
    #         print('Filename not found.')
    # else:
    #     import os
    #     print('usage: %s http://server.com/path/to/filename' % os.path.basename(sys.argv[0]))

# http://wind.met.fu-berlin.de/loops/radar_100/rad-bln.20140218_2230.gif

# open erzeugt einen handler auf eine datei, die geöffnet, geschrieben und geschlossen werden muss. 

# http://weather.yahooapis.com/forecastrss?w=638242&u=c

# http://www.crummy.com/software/BeautifulSoup/ für tree-parsing und andere voodoo-magic

# http://solarham.com/
# http://stereo-ssc.nascom.nasa.gov/beacon/beacon_secchi.shtml
# http://sdo.gsfc.nasa.gov/data/dailymov.php
# http://aia.lmsal.com/public/results.htm#images
# http://sdo.gsfc.nasa.gov/data/
# http://sohowww.nascom.nasa.gov/spaceweather/
# http://sohowww.nascom.nasa.gov/data/realtime-images.html
# http://www.swpc.noaa.gov/today.html
# http://www.swpc.noaa.gov/ftpdir/lists/particle/20120224_Gs_part_5m.txt
# http://www.swpc.noaa.gov/ace/ace_rtsw_data.html# 
# http://www.swpc.noaa.gov/sxi/goes15/index.html
# http://oiswww.eumetsat.org/IPPS/html/latestImages.html

# für datei lesen statt read() readlines() mit -1 das letzte element der erzeugten liste lesen

# GFS-GRIB: ftp://nomads.ncdc.noaa.gov/GFS/
