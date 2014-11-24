""" Various routines to schedule applications 

Let's us start a few programs like MAMP Pro, and
open a browser.
"""

import os
import sys
import logging
import subprocess
open_app = '/usr/bin/open'

def start_mamp(path="/Applications/MAMP PRO/MAMP PRO.app"):
    subprocess.call([open_app, path])
    
def browse_url(url="http://jawknee.com/coLab"):
    logging.info("Browsing: %s", url)
    subprocess.call([open_app, '-a', '/Applications/Firefox.app/', url])

def main():
    start_mamp()
    logging.info("clSchedule main: returned")
    
    
if __name__ == "__main__":
    main()