#!/usr/bin/env python
"""
An interface to the Tkinter canvas widget,
Allow, at least at first - selection of the
start and end points.
"""
import logging
import time

from PIL import Image	#, ImageTk

import tkinter as tk
import tkinter.ttk


import clclasses
import cltkutils

class Button:
	"""
	Handles the 4 inc/dec buttons - keeps track of clicks, 
	and repeat states, etc...
	"""
	def __init__(self, g_edit, type, which, column=0, row=0):
		self.g_edit = g_edit
		self.type = type
		self.which = which
		if type == 'dec':
			#text = u"\u2190"	# left arrow
			text = u"\u25C0"	# left triangle
			self.amt = -1
		elif type == 'inc':
			#text = u"\u2192"	# right arrow
			text = u"\u25B6"	# right triangle
			self.amt = +1
		else:
			logging.warning("Warning - bad button")
			
		self.obj = ttk.Button(g_edit.c_frame, text=text, command=self.handler)
		self.obj.grid(column=column, row=row)
		self.pressed = False
		self.held = False
		
	def handler(self, handled=False):
		"""
		Handle the button press...
		We could be called by a single button press, or
		by a series.   
		
		If handled is False, this is the single entry 
		from the ttk.Button callback and means the button
		has been pressed and released.  If pressed quickly
		we may not have seen the button pressed.  If we have,
		we want to ignore that ttk.Button call back, we've already
		dealt with it.  We use the "held" flag to work this out.
		
		We also want to handle the delay between the initial
		click and repeats (the "after" value in the button handler
		*is* the repeat rate.
		"""
		doit = False
		pressed = self.obj.instate(["pressed"])
		if not handled:
			# set a flag here if we intend to rebuild both...
			if pressed:
				logging.info("In college they told us this was bullshit.....")
			if self.held:
				logging.info("Rejected call.")
				self.held = False
				
			else:
				doit = True
				logging.info("Uncaught press")
		if pressed:
			# if this is the first time this has been pressed,
			# set up for the delay before repeat...
			if not self.held:
				self.held = True
				self.count = 5
				doit = True
				logging.info("First press")
			else:
				if self.count > 0:
					self.count -= 1
					logging.info("Pre-delay")
				else:
					doit = True
					logging.info("Repeated press")
				
		if doit:
			# set some limits...
			if self.which == 'start':
				lo_limit = 0
				hi_limit = self.g_edit.end_x + 1
			else:
				lo_limit = self.g_edit.start_x + 1
				hi_limit = self.g_edit.width + 1
			# Stored value is one less than displayed value
			new_value = eval('self.g_edit.' + self.which + '_x') + self.amt + 1
			logging.info("New value: %s - lo: %s, hi: %s", new_value, lo_limit, hi_limit)
			if new_value == lo_limit or new_value == hi_limit:
				logging.info("Out of range...")
				self.obj.bell()
				return
			logging.info("Press: %s, %s, %s", self.which, self.type, self.amt)
			# Slightly tricky - we move the line in question,
			# we change the value +/- 1, and we update the text.
			# we do a fair bit of eval to make this happen
			line_id = eval('self.g_edit.' + self.which + '_line')
			# move the line...
			self.g_edit.cnvs.move(line_id, self.amt, 0)
			
			s = 'self.g_edit.' + self.which + '_x = ' + str(new_value - 1)
			logging.info("Exec string: %s",s)
			
			exec(s)
			s = 'self.g_edit.' + self.which + 'Text.set(str(new_value))' 
			logging.info("Exec string: %s", s)
			exec(s)
class GraphEdit:
	"""
	Put up an image, start and stop lines
	and whatever gadgets we need to deal with it all
	"""
	
	def __init__(self, parent, file=None):
		self.parent = parent
		self.file = file
		self.running = True
		# parent may be a tk root (when we're testing) 
		# or more generally , a page object...
		if isinstance(parent, clclasses.Page):
			self.start_x = parent.xStart
			self.end_x = parent.xEnd
			self.top = tk.Toplevel()
			#self.root = tk.Tk()
			self.root = parent.master
			#self.root = parent.top.winfo_toplevel() 	# for access to the mainloop
			#self.top = parent.master
			#self.top = self.root
			self.top.transient()
			#self.root.transient()
			self.top.title('Select start and end points...')
			#self.top = None			# set later - which window to kill
			self.runtype = 'Page'
		else:
			self.start_x = 30
			self.end_x = None		# flag to set this later...
			self.root = self.parent	# for access to mainloop
			self.top = self.parent	# kill this window when done
			self.runtype = 'Test'
		# 
		# minor KLUDGE Alert - I seem to need to do a 3 pixel offset for
		# the image to be aligned as expected...   at least on my Mac
		self.offset = 3	 # Seems to be needed to correctly position the graphic
		# Validation callback parameters
		self.callback = self.validate_entry	
		self.validate = 'all'
		self.subcodes =  ('%d', '%S', '%P', '%V')
		
		info = "Use the arrows or grab the lines to set the start (green) and end (red) points."
		#ttk.Label(i_frame, text=info, foreground="black", anchor=tk.SW, justify=tk.RIGHT).grid(column=0, row=0)
		self.popup = cltkutils.Popup('Set Sound Start and End', info, nobutton=False)
		
	
	def post(self):
		"post the current canvas"	
		
		self.s_image = Image.open(self.file)
		self.photo = ImageTk.PhotoImage(self.s_image)
		img_width, img_height = self.s_image.size
		if self.end_x is None:
			self.end_x = int(img_width * 0.97)	# for testing only...
		
		# Set up to see if there is room below for 
		screen_height=1440 - 60 	# accounts for decorations
		
		if img_height > screen_height:
			img_height = screen_height	# consider scroll bars?
		
		control_height = 60
		bw = 0	# border width

		cnvs_height = img_height 
		if img_height + control_height <=  screen_height:	# If it fits - create a separate frame below
			cnvs_height += control_height
		cnvs_width = img_width
		self.width = img_width
		cnvs = tk.Canvas(self.top, width=cnvs_width, borderwidth=0, closeenough=10., height=cnvs_height, background="#222")
		self.cnvs = cnvs
		if self.top is None:
			self.top = cnvs
			
		self.top.geometry('+1+1')
		cnvs.grid()
		
		self.image_id = cnvs.create_image(self.offset, self.offset, image=self.photo, state=tk.DISABLED, anchor=tk.NW)
		
		
		# control widgets
		x = cnvs_width / 2 + bw + self.offset
		y = cnvs_height + bw + self.offset
		self.control_frame(cnvs)
		control_window = cnvs.create_window(x,y,  height=control_height, anchor=tk.S)
		cnvs.itemconfigure(control_window, window=self.c_frame)
		
		i_frame = tk.Frame(self.top, bg="#e9e9e9", borderwidth=2, padx=10, pady=5)
		
		
		info_window = cnvs.create_window(x/2, y, height=control_height/2, anchor=tk.SE, window=i_frame)
		# animated dashed lines for start and end
		dashoff = 0
		self.dash_offset = dashoff
		
		# Account for apparent need for an offset
		x = self.start_x + self.offset 
		self.start_line = cnvs.create_line(x, 0, x, img_height, tag='vline', fill="green", dash=(4,4), dashoff=dashoff)
		x = self.end_x + self.offset 
		self.end_line = cnvs.create_line(x, 0, x, img_height, tag='vline', fill="red", dash=(4,4), dashoff=dashoff)
		#
		# Set up some binding....
		self.cnvs.tag_bind('vline', '<ButtonPress-1>', self.lineSelect)
		self.cnvs.tag_bind('vline', '<ButtonRelease-1>', self.lineRelease)
		self.cnvs.tag_bind('vline', '<B1-Motion>', self.lineMove)
		self._drag_data = {"x": 0, "item": None}
		
		self.dash_line_list = [ self.start_line, self.end_line]
		self.root.after(200, self.animate_lines)

		
	def animate_lines(self):
		"""
		Do simple animation on the cursor lines
		"""
		incr = 1
		size = 8
		delay = 33
		
		dashoff = self.dash_offset + incr
		if dashoff == size:
			dashoff = 0
		self.dash_offset = dashoff
		
		for item in self.dash_line_list:
			self.cnvs.itemconfigure(item, dashoff=dashoff)
		
		if self.running:
			self.root.after(delay, self.animate_lines)
		else:
			logging.info("Line animate terminating.")
	
	def lineSelect(self, event):
		logging.info("Entered 'select', %s, %s, %s", event.type, event.x, event.y)
		# only the two lines are set up - let's do the on our own,
		# find the closest - and set up the max and min
	
		logging.info("X, canvas.x: %s, %s", event.x, self.cnvs.canvasx(event.x))
		# record the item and its location
		if abs( self.start_x - event.x) < abs(self.end_x - event.x):
			item = self.start_line
			loc = self.start_x
			self.line_min = self.offset	
			self.line_max = self.end_x + self.offset - 1 
			logging.info("Selected START line, min: %s, max: %s", self.line_min, self.line_max)
		else:
			item = self.end_line
			loc = self.end_x
			self.line_min = self.start_x + self.offset + 1
			self.line_max = self.width + self.offset - 1
			logging.info("Selected END line, min: %s, max: %s", self.line_min, self.line_max)
			
		# there are only three selectable items on the canvas, the graphic
		# (which we don't want) and the two lines, only one of which we're
		# likely to select (but....)
		self.selected_item = item
		logging.info("selected_item is: %s, %s", self.selected_item, event.x)
		self._drag_data["item"] = self.selected_item
		self._drag_data["x"] = loc + self.offset
		x = event.x
		self.update_line_nums(x)
	
	def lineMove(self, event):
		try:
			self.selected_item
		except:
			logging.info("no item selected")
			return
		
		logging.info("Entered 'move' type, %s, x: %s, y: %s", event.type, event.x, event.y)
		#
		# Would this exceed the limits?
		x = event.x
	
		self.update_line_nums(x)	
		 	
	def lineRelease(self, event):
		logging.info("Entered 'release', type, %s, x: %s, y: %s", event.type, event.x, event.y)
		
		try:
			self.selected_item
		except:
			return	# we haven't selected a legal item yet
		x = event.x
		
		self.update_line_nums(x)	
		
		# Reset- save the value (account for min/ax)
		self._drag_data["item"] = None
		self._drag_data["x"] = 0
	
	def update_line_nums(self,x):
		if x > self.line_max:
			x = self.line_max
	
		if x < self.line_min:
			x = self.line_min
		
		if self.selected_item == self.start_line:
			logging.info("Start line")
			self.start_x = x - self.offset
		if self.selected_item == self.end_line:
			logging.info("End Line"	)
			self.end_x = x - self.offset
			
		self.startText.set(str(self.start_x+1))
		self.endText.set(str(self.end_x+1))
		# compute how much this object has moved
		delta_x = x - self._drag_data["x"]
		# move the object the appropriate amount
		self.cnvs.move(self._drag_data["item"], delta_x, 0)
		# record the new position
		self._drag_data["x"] = x	
				
	def validate_entry(self, why, what, would, how):
		"""
		Do the actual validation - the entry object in self.widget
		This is a very simplified validation - only digits are 
		allowed - we do need to check to see if the value is out 
		of range (could be tricky)
		"""
		logging.info("vld8_numbers: %s, %s, %s", why, what, how)
		
		if why == '-1':
			if how == 'forced':
				logging.info("Focus: we don't need no stinkin' forced focus")
			elif how == 'focusin':
				logging.info("Focus In: restore Match: %s", self.match_text)
				if self.match_text:
					self.post_match()
					
			elif how == 'focusout':
				logging.info("Focus Out: get rid of Match")
				self.matchVar.set('')
			return True
		try:
			val = self.widget.get()
		except:
			logging.warning("For some reason we're here without a widget: %s", self, exc_info=True)
			return True
			
		#-- bad character?
		for c in self.exclude_chars:
			if what.find(c) + 1:		# 0 and above: found
				logging.info("Bad: found: %s", c)
				self.widget.bell()
				return False
			
		self.parent.changed = True	
		#--are we new?   If so, blank what's there, update the color, and replace with any addition
		logging.info("self.new: %s", self.new)
		self.match_text = ''
		r_code = True	# from here on out, keep track of conditions that require an ultimate failure..
		if self.new:
			logging.info("why: %s", why)
			if why == '1':
				would = what
				logging.info("would is what: %s", what)
			else:
				would = ''
			#self.widget.configure(fg='#000')
			self.nameVar.set(would)
			fg='#000'	# black
			#self.widget.configure(fg=fg)
			self.widget.configure(foreground=fg, validate=self.validate, validatecommand=self.validatecommand )
			self.new = False
			r_code = False		# Reject the character - we've already set it in, above
			
		logging.info("Would is: %s", would)
		#-- zero length?  
		if  len(would) == 0:
			self.set_status(ok = False)
			logging.info("Bad-==========-Zero length")
			self.match_text = ''
			self.post_match()
			return r_code
		
		#-- match?	set up a lambda function - lower the string to ignore, just return it, otherwise.
		if self.ignore_case:
			f = lambda x: x.lower()
		else:
			f = lambda x: x
			
		# Check for a match so far on any string - if so, just display 
		# it - if an exact match - flag as  Bad
		self.match_text = ''
		good = True
		for item in self.exclude_list:
			if f(item).find(f(would)) == 0:		# matches at the start
				if f(item) == f(would):
					logging.info("BAD:  matches: %s", item)
					self.match_text += item + '\n'
					self.match_color = '#f11'
					good = False
					#break
				else:
					logging.info("partial match: %s / %s", item, would)
					self.match_color = '#666'
					self.match_text += item + '\n'
		#
		# Post the status and the matching text, if any
		self.set_status(good)			
		self.post_match()
		return r_code	
	def control_frame(self, parent):
		"""
		Build the control frame with the various widgets
		to do what we want (at least set the start and 
		end lines, terminate)
		"""
		self.c_frame = tk.Frame(parent, bg="#e9e9e9", borderwidth=2, padx=10, pady=5)
		
		# At this point, one row has:  start / end in the corresponding colors,
		# and arrows and text windows to let us set the value
		dash = u"\u2015" * 5
		ttk.Label(self.c_frame, text=dash, foreground="green", anchor=tk.NW, justify=tk.CENTER).grid(column=0, row=0)
		ttk.Label(self.c_frame, text="Start", foreground="green", anchor=tk.NW, justify=tk.CENTER).grid(column=1, row=0)
		ttk.Label(self.c_frame, text=dash, foreground="green", anchor=tk.NW, justify=tk.CENTER).grid(column=2, row=0)
		
		ttk.Label(self.c_frame, text=dash, foreground="red", anchor=tk.NW, justify=tk.CENTER).grid(column=4, row=0)
		ttk.Label(self.c_frame, text="End", foreground="red", anchor=tk.NE, justify=tk.CENTER).grid(column=5,row=0)
		ttk.Label(self.c_frame, text=dash, foreground="red", anchor=tk.NW, justify=tk.CENTER).grid(column=6, row=0)
		
		# buttons...
		self.button_list = [] 	# we do our own button handling - keep a list
		
		# decrement start button
		button = Button(self, type='dec', which='start', column=0, row=1)
		self.button_list.append(button)
		
		button = Button(self, type='inc', which='start', column=2, row=1)
		self.button_list.append(button)
		
		button = Button(self, type='dec', which='end', column=4, row=1)
		self.button_list.append(button)
		
		button = Button(self, type='inc', which='end', column=6, row=1)
		self.button_list.append(button)
		
		# and a separate one for finishing up....
		# for now, we're sticking this in the middle in case we get stuck with a very tiny window.
		ttk.Button(self.c_frame, text='Done', command=self.quit_handler).grid(column=3, row=0)
		
		
		self.root.after(100, self.button_handler)
		# and the entry widgets
		self.startText = tk.StringVar()
		self.startText.set(str(self.start_x))
		#ttk.Entry(self.c_frame, width=6, textvariable=self.startText).grid(column=1, row=1)
		ttk.Label(self.c_frame, width=6, textvariable=self.startText, anchor=tk.CENTER).grid(column=1, row=1)
		self.endText = tk.StringVar()
		self.endText.set(str(self.end_x))
		#ttk.Entry(self.c_frame, width=6, textvariable=self.endText).grid(column=4, row=1)
		ttk.Label(self.c_frame, width=6, textvariable=self.endText, anchor=tk.CENTER).grid(column=5, row=1)
		self.c_frame.grid()
	
	def button_handler(self):
		"""
		On a regular basis, check the state of each button,
		call the proper method if the button is pressed.
		Handle delayed repeat
		
		"""
		for button in self.button_list:
			button.handler(handled=True)
		if self.running:
			self.root.after(100, self.button_handler)
		else:
			logging.info("Button handler termminating.")
		
	def quit_handler(self):
		"""
		We're done here - post the start and end values
		to the parent - if a Page, then call the appropriate
		methods.
		"""
		
		self.parent.xStart = self.start_x
		self.parent.xEnd = self.end_x
		if self.runtype == "Page":
			page = self.parent
	
			page.editor.set_member('xStart', self.start_x)
			page.editor.set_member('xEnd', self.end_x)
				
			logging.info("xStart, xEnd: %si, %s", page.editor.get_member('xStart'), page.editor.get_member('xEnd'))
			#self.parent.post_member('xStart')
			#self.parent.post_member('xEnd')
			page.editor.refresh()

		self.popup.t.destroy()
		#
		# have the animation and button handler loops stop...
		self.running = False
		self.root.after(150, self.terminate)
		
	def terminate(self):
		""" and done... - called from the mainloop after the others have terminated """
		self.top.destroy()
		
		
def main():
	root = tk.Tk()
	file = "/Users/Johnny/Desktop/ScreenShot.png"
	file = "/Users/Johnny/Desktop/Screen Shot 2013-11-17 at 8.52.02 PM.png"
	#file = "/Users/Johnny/Desktop/Screen Shot 2013-12-01 at 11.31.53 AM.png"
	g = GraphEdit(root, file)
	root.after(200, g.post)
	root.mainloop()
	logging.info("Got: startx: %s, endx: %s", g.start_x, g.end_x)
	
	
if __name__ == '__main__':
	main()