__author__ = 'riot'


class Wetter24Filter(object):
    """Filters out interesting info from wetter24.de"""

    # TODO: Make sure, unicode is handled correctly
    # TODO: Strip of unnecessary data

    def filter(self, newtext):
        local_weather = newtext[newtext.find('head_ww'):newtext.find('hPa<') + 4]

        condition_zahl = local_weather.find('head_ww')
        condition_begin = local_weather.find('alt="', condition_zahl) + 5
        condition_end = local_weather.find('"', condition_begin)
        condition = local_weather[condition_begin:condition_end]

        temp_zahl = local_weather.find('head_tt2')
        temp_begin = local_weather.find('>', temp_zahl) + 1
        temp_end = local_weather.find('</p>', temp_zahl)
        temp = local_weather[temp_begin:temp_end]

        wind_zahl = local_weather.find('wind32px')
        wind_begin = local_weather.find('alt="', wind_zahl) + 5
        wind_end = local_weather.find('" title', wind_zahl)
        wind = local_weather[wind_begin:wind_end]

        w_speed_zahl = local_weather.find('head_ff2')
        w_speed_begin = local_weather.find('>', w_speed_zahl) + 1
        w_speed_end = local_weather.find('</p>', w_speed_zahl)
        w_speed = local_weather[w_speed_begin:w_speed_end]

        press_zahl = local_weather.find('head_ppp2')
        press_begin = local_weather.find('>', press_zahl) + 1
        press_end = local_weather.find('</p>', press_begin)
        press = local_weather[press_begin:press_end]

        results = {'condition': condition,
                   'temperature': temp,
                   'wind_dir': wind,
                   'wind_speed': w_speed,
                   'pressure': press
        }
        return results


class NasaSDOFilter(object):
    """Filters our the image link and sends that on"""

    def filter(self, newtext):
        snippet_solar_begin = newtext.find('<h1>AIA 094, 335, 193</h1>')
        snippet_solar = newtext[snippet_solar_begin:newtext.find('latest_image', snippet_solar_begin) + 9]
        solar_img_begin = snippet_solar.find('href="') + 6
        solar_img_end = snippet_solar.find('">', solar_img_begin)
        solar_img = 'http://sdo.gsfc.nasa.gov' + snippet_solar[solar_img_begin:solar_img_end]

        return solar_img