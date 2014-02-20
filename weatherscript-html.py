# thanks to kristall, who helped me big time in learning python and who teached me line-by-line how to write this script. Everything that appears unprofessionally in this script has been grown on my madness and has nothing to do with kristalls ingenuity and teaching.

#!/usr/bin/env python3

import urllib.request
import time

def download(url,targetname):
	"""Copy the contents of a file from a given URL
	to a local file.
	"""
#	import urllib
	webFile = urllib.request.urlopen(url)
	localFile = open(targetname, 'wb')
	localFile.write(webFile.read())
	webFile.close()
	localFile.close()

local_weather = urllib.request.urlopen('http://www.wetter24.de/wetter/berlin-alexanderplatz/10389.html')
full_src_local_weather = local_weather.read().decode()

solar_weather = urllib.request.urlopen('http://sdo.gsfc.nasa.gov/data/')
full_src_solar_weather = solar_weather.read().decode('ISO 8859-1')

snippet_local = full_src_local_weather[full_src_local_weather.find('head_ww'):full_src_local_weather.find('hPa<')+4]

snippet_solar_begin = full_src_solar_weather.find('<h1>AIA 094, 335, 193</h1>')
snippet_solar = full_src_solar_weather[snippet_solar_begin:full_src_solar_weather.find('latest_image',snippet_solar_begin)+9]

condition_zahl = snippet_local.find('head_ww')
condition_begin = snippet_local.find('alt="',condition_zahl) + 5
condition_end = snippet_local.find('"',condition_begin)
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

print('Bedingungen',condition)

temp_zahl = snippet_local.find('head_tt2')
temp_begin = snippet_local.find('>',temp_zahl) + 1
temp_end = snippet_local.find('</p>',temp_zahl)
temp = snippet_local[temp_begin:temp_end]

print('Temperature <b>',temp,' °C</b>')

wind_zahl = snippet_local.find('wind32px')
wind_begin = snippet_local.find('alt="',wind_zahl) + 5
wind_end = snippet_local.find('" title',wind_zahl)
wind = snippet_local[wind_begin:wind_end]

print('Wind from <b>',wind,' </b>')

w_speed_zahl = snippet_local.find('head_ff2')
w_speed_begin = snippet_local.find('>',w_speed_zahl) + 1
w_speed_end = snippet_local.find('</p>',w_speed_zahl)
w_speed = snippet_local[w_speed_begin:w_speed_end]

print('Wind with <b>',w_speed,'</b>')

press_zahl = snippet_local.find('head_ppp2')
press_begin = snippet_local.find('>', press_zahl) + 1
press_end = snippet_local.find('</p>', press_begin)
press = snippet_local[press_begin:press_end]

print('Pressure <b>',press,'</b>')

rainradar_url = 'http://wind.met.fu-berlin.de/loops/radar_100/R.NEW.gif'
rainradar_name = 'rainradar.gif'
print('starting download procedure of rain-radar using ',rainradar_url)
download(rainradar_url,rainradar_name) 

'''
solarweather_txt_url = 'http://www.swpc.noaa.gov/ftpdir/lists/particle/Gs_part_5m.txt'
solarweather_txt_name = '5minute-table.txt'
print('starting download procedure of solar weather table 5min res. using ',solarweather_txt_url)
download(solarweather_txt_url,solarweather_txt_name) 
'''

solar_img_begin = snippet_solar.find('href="') + 6
solar_img_end = snippet_solar.find('">',solar_img_begin)
solar_img = 'http://sdo.gsfc.nasa.gov' + snippet_solar[solar_img_begin:solar_img_end]
print('starting download procedure of solar weather image',solar_img)
download(solar_img,'solar_img.jpg')

fobj = open("weather.html", "w") 
fobj.write('<!DOCTYPE html>\n<html lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n    <style type="text/css">\n      body {\n        padding-top: 10px;\n      }\n      .tabelle {\n	width: 100%;\n	}\n      .solar {\n	color:#FFFFFF;\n	background-color:#333333;\n	}\n    </style>\n    <title>c-beam</title>\n    <meta charset="utf-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <meta name="description" content="">\n    <meta name="author" content="">\n    <script src="./c-beam_files/jquery.min.js"></script>\n    <script src="./c-beam_files/bootstrap-dropdown.js"></script>\n    <link href="./c-beam_files/cyborg.css" rel="stylesheet" type="text/css">\n    <script src="./c-beam_files/bootstrap.js"></script>\n    <link href="https://c-beam.cbrp3.c-base.org/static/c-base-bootstrap/css/bootstrap-responsive.css" rel="stylesheet">\n    <link href="https://c-beam.cbrp3.c-base.org/static/c-base-bootstrap/css/bootstrap.custom.css" rel="stylesheet">\n    <!-- link rel="shortcut icon" href="ico/favicon.ico" -->\n</head>\n<body>\n  <div class="container">\n    <h1>nerdctrl status monitor</h1>\n    <hr><p></p>\n	<table class="tabelle">\n		<tr>\n<td valign="top">\n') 

fobj.write('<p><b>WEATHER CONDITIONS</b><br />')
fobj.write("captured at: %s.%s.%s %s:%s h %ssec <br />" % (day, month, year, hours, minutes, seconds))
fobj.write('captured at base of main-antenna </p>')
fobj.write("<p>")
fobj.write("Bedingungen: <b> %s </b> <br />" % (condition))
fobj.write('Temperature <b> %s °C</b> <br />' % (temp))
fobj.write('Wind from <b> %s </b> <br />' % (wind))
fobj.write('Wind with <b> %s </b> <br />' % (w_speed))
fobj.write('Pressure <b>%s</b> </p>' % (press))
fobj.write('	</td>\n		<td><img src="rainradar.gif" alt="Regenradar"></td>\n			<td><img src="solar_img.jpg" alt="Sonne, live" width="500px"></td>\n		</tr>')
fobj.write('	</table> \n    <footer class="row"> \ncomputer says this is the footer and noooooo \n    </footer> \n  </div> <!-- container --> \n<script src="./c-beam_files/html5slider.js"></script> \n</body></html> \n ')
fobj.close()

'''
if __name__ == '__main__':
	import sys
	if len(sys.argv) == 2:
		try:
			download(sys.argv[1])
		except IOError:
			print('Filename not found.')
	else:
		import os
		print('usage: %s http://server.com/path/to/filename' % os.path.basename(sys.argv[0]))
'''
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
