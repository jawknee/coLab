"""
Various routines to schedule applications
"""
import os
import sys
import subprocess
open_app = '/usr/bin/open'

def start_mamp(path="/Applications/MAMP PRO/MAMP PRO.app"):
    subprocess.call([open_app, path])
    
def browse_url(url="http://jawknee.com/coLab"):
    print "Browsing:", url
    subprocess.call([open_app, url])

def main():
    start_mamp()
    print "clSchedule main: returned"
    
    
if __name__ == "__main__":
    main()