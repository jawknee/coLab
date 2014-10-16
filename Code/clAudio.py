#!/usr/bin/env python
""" Audio utilities...

    Simple utitlies:
    get_audio_len -- return the length in seconds of an audio file.
    make_movie -- create the html5 video files for the passed page
"""

import os
import logging
import subprocess
import fcntl
import select
import time
import aifc

import config

def get_audio_len(file):
    """ In this return the length of the file in seconds. """
    a = aifc.open(file)
    seconds = a.getnframes() / float(a.getframerate())
    a.close
    return(seconds)

def make_movie(page, prog_bar=None):
    """ Passed a Page, create the corresponding movie
    
    At the heart of it - passed a page, it builds a movie.
    This script basically writes a data file that is passed
    to the shell script that does the work.
    
    Most of the code is just to read the output of ffmpeg for
    updating of the progress bar.
    """
    infofile = os.path.join(page.home, 'coLab_local', 'movie.info')
    outfile = open(infofile, 'w+')
    #
    # Just some variable assignments used by the script.
    content = 'pagedir="' + page.home + '"\n' 
    content += 'soundfile="' + page.localize_soundfile() + '"\n' 
    content += 'fps="' + str(page.fps) + '"\n'
    content += 'media_size="' + page.media_size + '"\n'
    
    outfile.write(content)
    outfile.close()
    
    media_script = os.path.join(page.coLab_home, 'Code', 'ffmpeg.sh')
    
    logging.info("running: %s with: %s", media_script, infofile)
    try:
        bufsize = 1     # line buffered
        ffmpeg = subprocess.Popen([media_script, infofile], bufsize, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    except:
        logging.warning("Video generation failed.", exc_info=True)
        sys.exit(1)
    """
    # buffering info from Derrick Petzold: https://derrickpetzold.com/p/capturing-output-from-ffmpeg-python/
    fcntl.fcntl(
        ffmpeg.stdout.fileno(),
        fcntl.F_SETFL,
        fcntl.fcntl(ffmpeg.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
    )
    #   does not appear to be needed - the iter on the subprocess stdout works fine...
    #"""
    prog_bar.update(0)      # reset the start time...
    #
    # Read lines from the newly started ffmpeg... 
    # parse them and update the progress bar...
    for line in iter(ffmpeg.stdout.readline, 'b'):
        
        ffmpeg.poll()   # check the status....
        if ffmpeg.returncode is not None:
            logging.info("ffmpeg is done: %s", ffmpeg.returncode)
            break

        parms = line.split()
        try:
            if parms[0] == 'frame=':
                frame_num = parms[1]
                prog_bar.update(int(frame_num))
                logging.info (" Frame: %s", frame_num)
                #read_delay=0.1      # a bit slower so we don't slow down the encoding...
        except:
            logging.info("Something went wrong on the update... %s - possible last frame.", frame_num)
            pass
            #break
    logging.info("ffmpeg has completed.")