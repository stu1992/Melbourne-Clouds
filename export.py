#! /usr/bin/python
import os
import logging
import commands
import datetime
import subprocess
import thread
from time import sleep
from daemon import runner

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class export(object):

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty0'
        self.stderr_path = '/dev/tty0'
        self.pidfile_path =  '/var/lib/clouds/export.pid'
        self.pidfile_timeout = 5
           
    def run(self):
        while True:
            logger.info('watchdog: waking')
            folders = commands.getoutput('ls /var/lib/clouds/stash/')
            jobs = folders.split()
            if len(jobs) == 0:
                logger.debug('watchdog: nothing to do')
            else:  
                logger.info("watchdog: pending jobs: "+ str(jobs))
                # doing one job each time
                folder_status = commands.getoutput('ls /var/lib/clouds/stash/{}'.format(jobs[0])).split()
                if str(datetime.datetime.fromtimestamp(int(jobs[0])).strftime('%Y-%m-%d_%H:%M:%S'))+'.avi' not in folder_status and len(folder_status) > 1:
                    # do avconv job
                    logger.info('watchdog: encoding {}'.format(jobs[0]))
                    #self.picture_stamp(jobs[0])
                    self.video_encode(jobs[0])  
                elif str(datetime.datetime.fromtimestamp(int(jobs[0])).strftime('%Y-%m-%d_%H:%M:%S'))+'.avi' in folder_status and len(folder_status) == 2:
                    logger.info('watchdog: uploading {}'.format(jobs[0]))
                    # runn video upload
                    self.upload_video(jobs[0])
                elif str(datetime.datetime.fromtimestamp(int(jobs[0])).strftime('%Y-%m-%d_%H:%M:%S'))+'.avi' in folder_status and len(folder_status) > 2:
                    logger.info('watchdog: conflict found, maybe an encode job was interrupted. Deleting video ')
                    # clear video job
                    os.system('rm /var/lib/clouds/stash/{}/*.avi'.format(jobs[0]))
            self.copy_video()
            logger.info('watchdog: sleeping')
            sleep(1*60*60)
        
    def picture_stamp(self, folder):
        '''logger.info('timestamping images')
        images = commands.getoutput('ls /var/lib/clouds/stash/{}/'.format(folder))
        imagelist = images.split()
        for image in imagelist:
            if len(image) <10: # i'm too lazy to think of a good solution
                break
            timestamp = image[:10]
            try:
                logger.info('timestamping '+ timestamp)
                img = Image.open('/var/lib/clouds/stash/{}/{}.png'.format(folder, timestamp))
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype('/var/lib/clouds/Aileron-Regular.otf', 30)
                draw.text((1550, 1010),datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y/%m/%d %I:%M:%S %p'),(255,50,50),font=font)
                img.save('/var/lib/clouds/stash/{}/{}.png'.format(folder, timestamp))
                logger.debug('done '+ '/var/lib/clouds/stash/{}/{}.png'.format(folder, timestamp))
            except:
                logger.info('shit failed son! deleting this bitch')
                os.system('rm /var/lib/clouds/stash/{}/{}.png'.format(folder, timestamp))
        # now that we have timestamped files, rename them
        logger.info('renaming images')

        count = 1
        for image in imagelist:
            os.system('mv /var/lib/clouds/stash/{}/{}'.format(name,image) + ' /var/lib/clouds/stash/{}/{}.png'.format(name,count))
            count += 1'''

    def video_encode(self, folder):
        logger.info('starting video encode')
        title = datetime.datetime.fromtimestamp(int(folder)).strftime('%Y-%m-%d_%H:%M:%S')
        attempt = 1
        encode_success = False
        while encode_success == False:
            log_file = title +str(attempt)
            encode = os.system('avconv -loglevel warning -y -i /var/lib/clouds/stash/{}/%d.png -c:v mpeg4 -r 25 -b:v 8000k /var/lib/clouds/stash/{}/{}.avi'.format(folder,folder,title,folder))
            if encode == 0:
                encode_success = True;
                logger.info('encoding finished')
            else:
                logger.error('encoding failed - retrying')
                attempt = attempt + 1
                if attempt > 5:
                    '''
                    the stash size is large enough that I can't hold them and troubleshoot. I will just drop them
                    '''
                    os.system('rm /var/lib/clouds/stash{}'.format(folder))
                    logger.error('encode failed: rage quitting and deleting files.')
        
        logger.info('finished video encode, deleting images')
        os.system('rm /var/lib/clouds/stash/{}/*.png'.format(folder))

    def upload_video(self,folder):
        info = open('/var/lib/clouds/stash/{}/info'.format(folder))
        # i've formatted this file specifically for easy reading
        start_string = info.readline().rstrip()
        end_string = info.readline()

        upload_success = False
        while upload_success == False:
            logger.info('uploading')
            upload_return_value = os.system('runuser -l pi -c "cd /var/lib/clouds/ && python /var/lib/clouds/upload.py --file=/var/lib/clouds/stash/{}/{}.avi --title="{}" --description="Melbourne clouds recorded outside my window, starting at {} and ending at {}. See more at melbourneclouds.com" --privacyStatus="public" --noauth_local_webserver"'.format(folder,start_string,start_string,start_string,start_string,end_string))

            if upload_return_value == 0:
                upload_success = True
                logger.info('upload successful')
            else:
                logger.info(str(upload_return_value))
                logger.info('error uploading, will try again')
                sleep(3600)
        logger.info('upload finished successfully')
        os.system('mv /var/lib/clouds/stash/{}/*.avi /home/pi/clouds/videos/'.format(folder))
        os.system('scp /home/pi/clouds/stash/{}/*.avi kodi@kodi:~/clouds/'.format(folder))
        os.system('rm -rf /var/lib/clouds/stash/{}'.format(folder))

    def copy_video(self):
        videos = commands.getoutput('ls /var/lib/clouds/videos'.format(folder))
        videolist = videos.split()
        for video in videolist:
            logger.info('attempting to copy video to backup host')
            if os.system('scp /var/lib/clouds/videos/{} kodi@kodi:~/clouds/'.format(video)) == 0:
                logger.info('video copied over, deleting')
                os.system('rm /var/lib/clouds/videos/{}'.format(video))
            else:
                logger.err('copying failed. Host might not be up, will try again later')
export = export()
logger = logging.getLogger("Export")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/lib/clouds/log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(export)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()
