#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in9d
import time
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime
import traceback
import json
import requests
import numpy as np

logging.basicConfig(level=logging.INFO)

a_url = 'http://192.168.1.4/admin/api.php'
w_url = 'https://www.metaweather.com/api/location/2475687/'

now = datetime.now()
time_string = now.strftime("%m/%d/%Y %H:%M:%S")

def get_data(api_url):
    try:
        r = requests.get(api_url)
        return json.loads(r.text)
    except:
        logging.info(e)\

def white_to_transparency(img):
    x = np.asarray(img.convert('RGBA')).copy()
    x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(np.uint8)
    return Image.fromarray(x)

def c_to_f(temp): 
    return str(round((temp * 1.8) + 32)) + '\u00b0'

try:
    epd = epd2in9d.EPD()
    epd.init()
    # epd.Clear(0xFF)
    
    font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    
    a_data = get_data(a_url)
    w_data = get_data(w_url)
    # print(w_data)

    ads_string = 'Ads Blocked: ' + str(a_data['ads_blocked_today']) + ' / ' + str(round(a_data['ads_percentage_today'])) + '%'

    wd = w_data['consolidated_weather']
    
    w_temp_string_today = c_to_f(wd[0]['min_temp']) + '/' + c_to_f(wd[0]['max_temp'])
    w_temp_string_tomorrow = c_to_f(wd[1]['min_temp']) + '/' +  c_to_f(wd[1]['max_temp']) 
    w_temp_string_after_tomorrow = c_to_f(wd[2]['min_temp']) + '/' +  c_to_f(wd[2]['max_temp']) 

    w_string_today = 'Today: ' + w_temp_string_today + ' ' + str(wd[0]['weather_state_name'])
    w_string_tomorrow = 'Tomorrow: ' + w_temp_string_tomorrow + ' ' + str(wd[1]['weather_state_name'])
    w_string_after_tomorrow = 'After Tomorrow: ' + w_temp_string_after_tomorrow + ' ' + str(wd[2]['weather_state_name'])

    icon_url = 'https://www.metaweather.com/static/img/weather/png/64/'

    todays_icon = Image.open(requests.get(icon_url + wd[0]['weather_state_abbr']+ '.png', stream=True).raw)
    tomorrows_icon = Image.open(requests.get(icon_url + wd[1]['weather_state_abbr']+ '.png', stream=True).raw)
    day_after_tomorrow_icon = Image.open(requests.get(icon_url + wd[2]['weather_state_abbr']+ '.png', stream=True).raw)
    
    # Drawing on the Horizontal image
    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((1, 0), ads_string, font = font24, fill = 0)
    draw.text((1, 30), w_string_today, font = font18, fill = 0)
    draw.text((1, 55), w_string_tomorrow, font = font18, fill = 0)
    draw.text((1, 80), w_string_after_tomorrow, font = font18, fill = 0)
    draw.text((1, 105), time_string, font = font18, fill = 0)
    epd.display(epd.getbuffer(Himage))

    time.sleep(6)
    Himage2 = Image.new('1', (epd.height, epd.width), 0)
    Himage2.paste(white_to_transparency(todays_icon), (15, 15))
    Himage2.paste(white_to_transparency(tomorrows_icon), (115, 15))
    Himage2.paste(white_to_transparency(day_after_tomorrow_icon), (215, 15))
    draw = ImageDraw.Draw(Himage2)
    draw.text((20, 95), w_temp_string_today, font = font16, fill = 255)
    draw.text((120, 95), w_temp_string_tomorrow, font = font16, fill = 255)
    draw.text((220, 95), w_temp_string_after_tomorrow, font = font16, fill = 255)
    epd.display(epd.getbuffer(Himage2))

    # time.sleep(10)
    # logging.info("Clear...")
    # epd.Clear(0xFF)

    epd.sleep()
    time.sleep(3)
    epd.Dev_exit()
    exit()
        
except IOError as e:
    logging.info(e)
    exit()
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in9d.epdconfig.module_exit()
    exit()
