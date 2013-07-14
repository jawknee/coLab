#!/usr/bin/env python
"""
    A attempt at...
    A initial GUI front-end interface to the various
    tasks required for creating and managing coLab.
"""

import os
import sys
import time

import Tkinter as tk
import tkFileDialog
import ttk
import tkMessageBox
import imp

from PIL import Image, ImageTk

import clutils
import clFunctions
import clclasses
import cltkutils
import clSchedule
import rebuild

class Colab(tk.Frame):
    """
    Basic class for the colab front end - holder of the main window and
    basic methods.
    
    It all starts here.  The base class is a frame - it holds the graphic
    elements, as well as the basic methods for performing the basic tasks.
    
    This tool is the interface to the coLab data structure, consisting
    of a heirarchy:  Groups, Projects (nyi), Songs, and Pages.  
    
    Basic functions include creating and editing (eventually
    projects), songs, and pages, and updating the external web
    site. 
    """
    
    def __init__(self, master=None):
        """
        Create a frame instance, populate it with the various gadgets
        to drive this beast, and populate a group list as they're called up.
        As each group is selected, update the title and snapshot graphics, 
        and the corresponding data and editing objects...
        """
        # Get the system wide config - find the local config file and 
        # set the basic paths to content, code, etc.
        try:
            self.conf=clutils.get_config()
            print "conf shows:", self.conf.coLab_home
        except ImportError:
            print "Cannot find config."
            sys.exit(1)        # fatal...
        
        # some constants that will laster be configurable 
        self.bg='#66a'  
        
        # call the parent class init - initializes ourselves
        tk.Frame.__init__(self, master)
        self.configure(bg=self.bg)
        # load the initial table of lists
        # a dictionary indexed by name, pointing dir name 
        # The "name" is what's returned from the menu - thus the need for translation
        self.load_group_list()
        self.edit_lock = False
        self.winfo_toplevel().geometry('+80+80')
        
        # grid method - at least for now...
        
        self.grid()
        self.get_last_group()    # set the initial group, and load it...
        #self.set_group()        # update the internal group structure
        self.createMainWidgets()    # put the initial widgets up...
        self.set_group_from_menu(menu_groupname="None")
        #self.place_group_shot()
        self.mainloop()
        

        # some sort of a GUI loop here...
        
    def get_last_group(self):
        """
        Retrieve the "current" group name from 
        ... some data structure... - for now:
        """
        self.current_groupname = "Catharsis"
        print "btw", self.current_groupname
        #print "and", self.hello
        
    def set_group_from_menu(self, menu_groupname='None'):
        """
        Retrieve the menu value and set that
        as the current group...
        """
        print "!  Click !---------------------------"
        # Called with menu_groupname = None for initial setup...
        if menu_groupname == "None":
            menu_groupname = self.gOpt.get()
        self.current_groupname = menu_groupname
    
        print "set_group_from_menu - setting current_groupname to", self.current_groupname
        self.set_group()
        
    def set_group(self):
        """
        Make sure the group specified in self.current_groupname
        is loaded and pointed to as the default.
        We keep a list of groups, which we load as they're referenced
        and a dictionary of  groups by dir name
        """
        try:
            thisname = self.current_groupname
        except:
            print "Fatal error: set_group called with no current_groupname set."
            sys.exit(1)
        
        group_dir = self.grouplistdict[thisname]
        print "set_group: group_dir", group_dir, "group name", thisname
        # Do we know about this group yet - i.e., is it loaded?
        try:    # do we even have the list yet?
            self.group_list
        except:
            print "New group list"
            self.group_list = dict()    # new dictionary...
         
        print "group_dir pre list test", group_dir   
        try:
            self.current_group = self.group_list[thisname]
        except KeyError:
            print "Nope - don't know group", thisname, "loading now..."
            #try:
            print "group_dir pre pre group inst", group_dir 
            self.current_group = clclasses.Group(group_dir)
            print "group_dir post group Inst.", group_dir, self.current_group.name
            self.current_group.load()                
            print "group_dir post group load", group_dir, self.current_group.name
            self.group_list[thisname] = self.current_group
            print "This group name:", self.current_group.name
            #except Exception as e:
            #    print "Internal Failure: cannot load ", thisname, sys.exc_info()[0], e
            #    sys.exit(0)
                 
        self.place_group_shot()
            
    def createMainWidgets(self):
        """
        Put up the main, initial set of widgets
        """
        self.master.title('coLab')
        self.master.configure(bg=self.bg)
        self.master.lift(aboveThis=None)
        self.main_frame=tk.LabelFrame(self, text='coLab', bg=self.bg).grid(padx=20, pady=20, ipadx=10, ipady=10)

        try:
            self.display_group_list()
            self.place_logo()
            self.function_buttons()
        except TypeError, info:
            print "TypeError:", info
        except Exception as e:
            print "Initialization Failed", sys.exc_info()[0], e
            raise SystemError

        # do a few of the simpler ones here...
                
        top = self.winfo_toplevel()
        self.menuBar = tk.Menu(top)
        #self.configure(bg='#8cf')        #--- RBF - consider this as a background for everything...
        top['menu'] = self.menuBar
        
        # Menu bar...
        self.subMenu = tk.Menu(self.menuBar)
        self.menuBar.add_cascade(label='Help', menu=self.subMenu)
        self.subMenu.add_command(label='About coLab...', command=self.__aboutHandler)
        
        # Just the word: "Group:"
        tk.Label(self.main_frame, text="Group:", bg=self.bg, justify=tk.RIGHT).grid(row=2, column=0, sticky=tk.E)
        
        self.subtitle_str = tk.StringVar()     # put text into self.subtitle.set("new string")
        self.subtitle_str.set("Not set yet")
        self.subtitle=tk.Label(self.main_frame, textvariable=self.subtitle_str, bg=self.bg, anchor=tk.NE, justify=tk.CENTER).grid(row=1, column=1, columnspan=3, sticky=tk.E)

        # refresh button...
        self.refreshButton = tk.Button(self.main_frame, text="Refresh", bg=self.bg, command=self.refresh_group).grid(column=4, row=3)
        # quit button...
        self.quitButton = tk.Button(self.main_frame, text="Quit", bg=self.bg, command=self.my_quit).grid(column=9, row=9)
        
    def __aboutHandler(self):
        """
        Let's do a nice little pop-up saying who we are and what we do....
        
        (eventually)
        """
        msg = "Welcome to coLab\nThis is a music collaboration tool created by Johnny Klonaris.\n\n"
        msg += "Note: 'coLab' is a trademark or other property of various entities.\n\n"
        msg += "I'm just using it for now.   Stay tuned for MusiCoLab."
        tkMessageBox.showinfo("About coLab...", msg)
        print "how's this?"
    
    def load_group_list(self):
        group_dir = os.path.join(self.conf.coLab_home, 'Group')
        print "new cd:", group_dir
        try:
            os.chdir(group_dir)
        except:
            print "Cannot get to dir:", group_dir
            print "Fatal"
            raise IOError()
        # build a dictionary of names to directory names.
        self.grouplistdict = dict()        # clean dictionary..
        for dir in (os.listdir('.')):
            # Step through each, try to import from a data file -if it works, 
            # and there's a tile - we're in - otherwise skip
            datapath = os.path.join(dir, 'data')
            print "Checking:", datapath
            
            try:
                data = imp.load_source('', datapath)
                #os.remove(datafile + 'c')
            except:            # if any thing goes wrong - just skip ahead...
                #print "no good - skipping", datapath, sys.exc_info()[0]
                continue        
                
            if not data.title:        # no title - no play...
                continue
            # ok - we've got a dir and a title - setup the next entry.
            self.grouplistdict[data.title] = dir    # for converting a title to a dir name
            print "self.grouplistdict of", data.title, "is:", self.grouplistdict[data.title]
        
    def display_group_list(self):
        """
        Provide the current list of groups.  We want to display
        the title, but return the directory name.   We create
        a dictionary as we go, which will convert the title
        to the dir name.
        """
        
        try:
            groupTitles = tuple(self.grouplistdict.keys())
        except:
            print "got no titles"
            
        self.gOpt = tk.StringVar()
        self.gOpt.set(self.current_groupname)

        self.groupOption = tk.OptionMenu(self.main_frame, self.gOpt, *groupTitles,command=self.set_group_from_menu)

        self.groupOption.grid(column=1, row=2, columnspan=2, sticky=tk.W)
        
        
    
    def function_buttons(self):
        print "function buttons"
        parent = self.main_frame
        new_page_button = ttk.Button(parent, text="New Page", command=self.create_new_page)
        new_page_button.grid(column=0, row=4)
        edit_page_button = ttk.Button(parent, text="Edit Page", command=self.edit_page)
        edit_page_button.grid(column=1, row=4)
        new_song_button = ttk.Button(parent, text="New Song", command=self.create_new_song)
        new_song_button.grid(column=2, row=4)
        edit_song_button = ttk.Button(parent, text="Edit Song", command=self.edit_song)
        edit_song_button.grid(column=3, row=4)
        
    """
    kludge alert:  I wanted these functions to be separate, but I don't see an easy way to pass the 
    parent object data - thus this odd set of interface scripts...
    """
    def create_new_page(self):
        clFunctions.create_new_page(self)
    def edit_page(self):
        clFunctions.edit_page(self)
    def create_new_song(self):
        clFunctions.create_new_song(self)
    def edit_song(self):
        clFunctions.edit_song(self)
        
    def place_group_shot(self):
        """
        Place a photo/graphic specific to the currently selected 
        group.   Passed the group name, places the current snapshot
        into the window.   If that window (img)
        """
        
        snapshot_name = 'SnapShot_tn.png'
        
        print "Current group.name", self.current_group.name
        imgpath = os.path.join(self.current_group.home, "Shared", snapshot_name)
        if not os.path.exists(imgpath):
            imgpath = os.path.join(self.conf.coLab_home, 'Resources', "coLab-NoGroupSnap.png")

            
        print "Image path:", imgpath
        try:
            self.snapshot.destroy()
        except:
            pass
        
        self.snapshot = cltkutils.graphic_element(self.main_frame)
        self.snapshot.filepath = imgpath
        self.snapshot.row=0
        self.snapshot.column=5
        self.snapshot.rowspan=5
        self.snapshot.columnspan=4
        self.snapshot.post()

        # and again - for the header (Title)
        try:
            self.header.destroy()
        except:
            pass
        
        headerpath = os.path.join(self.current_group.home, "Header.png")
        print "Title path:", headerpath
        self.header = cltkutils.graphic_element(self.main_frame)
        self.header.filepath = headerpath
        self.header.row=0
        self.header.column=0
        self.header.columnspan=3
        self.header.post()
        
        
        # and yet again - for the "Title /subtitle"
        """
        try:
            self.subtitle.clear()
        except:
            pass
        subtitlepath = os.path.join(self.current_group.home, "Title.png")
        print "Title path:", subtitlepath
        self.subtitle = cltkutils.graphic_element(self.main_frame)
        self.subtitle.filepath = subtitlepath
        self.subtitle.row=1
        self.subtitle.column=1
        self.subtitle.columnspan=3
        self.subtitle.post()
        
        """
        
        #blank=tk.Label(self.main_frame, text="                              ", justify=tk.CENTER).grid(row=1, column=1, columnspan=3)
        #blank.grid_forget()
        self.subtitle_str.set(self.current_group.subtitle)
        #self.subtitle=tk.Label(self.main_frame, text=self.current_group.subtitle, justify=tk.CENTER).grid(row=1, column=1, columnspan=3)
        
        
            
    def place_logo(self):
        logo_name = 'CoLab_Logo3D_sm.png'    # let's extract this at some point...

        logo_path = os.path.join(self.conf.coLab_home, 'Resources', logo_name)
        print "logo path:", logo_path
        self.logo = cltkutils.graphic_element(self.main_frame)
        self.logo.filepath = logo_path
        self.logo.row=0
        self.logo.column=9
        self.logo.post()
        
    def refresh_group(self):
        """
        Simple interface to the rebuild scripting...
        """
        print "Refresh: ", self.current_groupname
        rebuild.rebuild(self.current_group.name, mirror=True)
        clSchedule.browse_url(self.current_group.url_head)
        print "Refresh complete."
        
        
    def my_quit(self):
        """
        Let's check to see what's left hanging if/when someone quits.
        """
        print "Time to quit."

        self.quit()
        
def task(obj,bar):
    bar.step(1.0)

    obj.after(50, task, obj,bar)


"""
Create an instance - loop it!
"""

def main():
    print "Colab Main"
    w=Colab()
    
if __name__ == '__main__':
    main()
    
"""
stuff for later reference...

a = tk.Tk()

quitButton = tk.Button(a, text="Quit", command=a.quit)
quitButton.grid(column=3, row=3)

groupOptions = ( 'Catharsis', 'South Bay Philharmonic', 'Johnny' )

gOpt = tk.StringVar()
gOpt.set(groupOptions[0])

groupOption = tk.OptionMenu(a, gOpt, 'Catharsis', 'South Bay Philharmonic', 'Johnny')

groupOption.grid(column=1, row=1)
"""
"""
screenshot = tkFileDialog.askopenfilename(initialdir="~/Desktop", title="Select a Screen Shot", parent=a)

print "Got Screenshot:", screenshot

audio = tkFileDialog.askopenfilename(initialdir="/Volumes/iMac 2TB/Music/JDJ", title="Select an audio file", parent=a)
print "Got audio file:", audio

"""


"""
value = tk.IntVar()

progBar = ttk.Progressbar(a, length=500, maximum=30, mode='determinate', variable=value)

progBar["value"] = 20.0

progBar.grid(column=1, columnspan=3, row=2)


for i in range(400):
    time.sleep(.1)
    progBar.step(1)
    print i

#v.set(450)
#progBar.start(10)

a.after(20, task, a, progBar)

a.mainloop()



print  gOpt.get()

"""
