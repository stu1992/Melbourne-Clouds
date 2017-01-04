#! /usr/bin/python
import sys
import time
import os
import commands
import logging
import camera
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import datetime
from fractions import Fraction
import photo_sensor

class clouds(object):
    def __init__(self):
        pass

    def run(self):
        logger.info("clouds is starting up")
        self.camera = camera.camera()
        self.light_sensor = photo_sensor.photo_sensor()
        day = 15
        night = 15 # we will make this the same eventually, still testing it
        buffer = day
        day_time = True
        time_lapse_length = 3000
        minute = 60
        
        '''
        TODO
        we don't need any collection of timestamps, remove this
        '''
        try: #try to read last temp stamp
            #open up timestamp file for graphing
            timestamps = open('timestamps','a')
        except:
            logger.error('failed to open timestamps file')

        while True:
            time.sleep(15)
            timestamp = int(time.time())
            # if it is the night time, increase exposure time to maximum allowed by software and try and get start
            if day_time != True:
                self.camera.capture('/var/lib/clouds/images/{}.png'.format(timestamp))
                logger.debug('night vision capture')
            elif day_time == True:     
                self.camera.capture('/var/lib/clouds/images/{}.png'.format(timestamp))
                logger.debug('day capture')
            timestamps.write(str(timestamp)+'\n')
            #copy file to webroot

            if timestamp %minute <= 15: # update once every minute
                logger.debug('updating web images')
                for number in range(4):
                    os.system("cp /var/www/html/img/{}.png /var/www/html/img/{}.png".format(number+1,number))
                os.system("rm /var/www/html/img/0.png")
                im = Image.open('/var/lib/clouds/images/{}.png'.format(timestamp))
                im.thumbnail((800,600), Image.ANTIALIAS)
                im.save('/var/www/html/img/4.png', "PNG")

            light_value = self.light_sensor.get_value()
            if light_value > 10000 and day_time == True:
                self.camera.set_preset('night')
                logger.info('going dark')
                buffer = night
                day_time = False
            elif light_value <= 10000 and day_time == False:
                self.camera.set_preset('day')
                logger.info('good day')
                buffer = day
                day_time = True
            
            '''
            Perform video export and upload if required
            
            Check if enough frames have been captured and then call export function
            '''
            
            if self.getscreencount() >= time_lapse_length:
                self.export()
            
    '''
     export will do processing when it feels like it and clouds will just stash the images in seperate folders

    '''
    def getscreencount(self): # returns the number of files in the images folder
        images = commands.getoutput('ls -p /var/lib/clouds/images/ | grep -v /')
        return len(images.split())
    def export(self): # renames the files in images to consecutive integers, exports a video file to videos and deletes images
        logger.info('counting images')
        
        '''
        Getting the time of the first image
        
        performing an ls command and getting the unix timestamp of the first result and assigning it to 'name'
        '''
        
        images = commands.getoutput('ls /var/lib/clouds/images/')
        imagelist = images.split()
        name = imagelist[0][:10]
        '''
        creating another folder to stash the images and keep them seperated from other processes
        
        '''
        logger.info('creating stash dir')
        os.system('mkdir /var/lib/clouds/stash/{}'.format(name))
        os.system('mv /var/lib/clouds/images/* /var/lib/clouds/stash/{}'.format(name))
        
        '''
        renaming all images for video sequence
        
        going through all images and renaming them from 1 to n+1 to then pass them to avconv to export video
        '''
        logger.info('renaming images')
        count = 1
        for image in imagelist:
            os.system('mv /var/lib/clouds/stash/{}/{}'.format(name,image) + ' /var/lib/clouds/stash/{}/{}.png'.format(name,count))
            count += 1
        
        
        '''
        Getting timestamps and converting them into datetimes for video name
        
        converting unix time stamps into datetimes for easy naming convention
        '''
        logger.info('creating info file')
        start_string = datetime.datetime.fromtimestamp(int(imagelist[0][:10])).strftime('%Y-%m-%d_%H:%M:%S')
        end_string = datetime.datetime.fromtimestamp(int(imagelist[-1][:10])).strftime('%Y-%m-%d_%H:%M:%S')
        info = open('/var/lib/clouds/stash/{}/info'.format(name),'w')
        info.write(start_string+'\n')
        info.write(end_string)
        info.close()
        
clouds = clouds()
logger = logging.getLogger("Clouds")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/lib/clouds/log")
handler.setFormatter(formatter)
logger.addHandler(handler)

clouds.run()
