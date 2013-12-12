#!/usr/bin/env python
"""
    Audio utilities....
"""

import os
import subprocess
import fcntl
import select
import time
import aifc

import config

def get_audio_len(file):
    """
    For now - some simple intefaces that do what we need...
    
    In this return the length of the file in seconds.
    """
    a = aifc.open(file)
    seconds = a.getnframes() / float(a.getframerate())
    a.close
    return(seconds)

def make_movie(page, prog_bar=None):
    """
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
    
    print "running:", media_script, "with:", infofile
    try:
        bufsize = 1     # line buffered
        ffmpeg = subprocess.Popen([media_script, infofile], bufsize, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    except:
        print "Video generation failed."
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
            print "ffmpeg is done:", ffmpeg.returncode
            break

        parms = line.split()
        try:
            if parms[0] == 'frame=':
                frame_num = parms[1]
                prog_bar.update(int(frame_num))
                print" Frame", frame_num
                  #read_delay=0.1      # a bit slower so we don't slow down the encoding...
        except:
            print "Something went wrong on the update...", frame_num
            pass
            #break
        """
        if readx:
            try:
                nextline = ffmpeg.stdout.readline()
            except IOError:
                nextline = '?'
                pass
            
            print "nextline:", nextline
            if nextline == '':
                print "Nothing - we think we're done with ffmpeg"
                break       # all done - head back
            
            parms = nextline.split()
            try:
                if parms[0] == 'frame=':
                      prog_bar.update(int(parms[1]))
                      print" Frame", parms[1]
                      read_delay=0.1      # a bit slower so we don't slow down the encoding...
            except:
                break
        else:
            print "Got nothing back from select"
        """
        #time.sleep(read_delay)   
    print "ffmpeg has completed."     
        