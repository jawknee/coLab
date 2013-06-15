#!/usr/bin/env python
"""
    Audio utilities....
"""

import os
import subprocess
import aifc

def get_audio_len(file):
    """
    For now - some simple intefaces that do what we need...
    
    In this return the length of the file in seconds.
    """
    a = aifc.open(file)
    seconds = a.getnframes() / float(a.getframerate())
    a.close
    return(seconds)

def make_movie(page):
    """
    At the heart of it - passed a page, it builds a movie.
    This script basically writes a data file that is passed
    to the shell script that does the work.
    """
    infofile = os.path.join(page.home, 'coLab_local', 'movie.info')
    outfile = open(infofile, 'w+')
    #
    # Just some variable assignments used by the script.
    content = 'pagedir="' + page.home + '"\n' 
    content += 'soundfile="' + page.soundfile + '"\n' 
    content += 'fps="' + str(page.fps) + '"\n'
    
    outfile.write(content)
    outfile.close()
    
    quicktimescript = os.path.join(page.coLab_home, 'Code', 'QuickTime_auto.scpt')
    
    
    print "running:", quicktimescript, "with:", infofile
    try:
        subprocess.call([quicktimescript, infofile])
    except:
        print "Quicktime generation failed."
        sys.exit(1)
    