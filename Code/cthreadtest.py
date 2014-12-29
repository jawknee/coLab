#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" threadtest.py - just that
	
	check out using thread queues...

	this adds a class to test scope
"""

import Queue
import threading
import time


class myThread (threading.Thread):
	def __init__(self, threadID, name, q, process):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
		self.process = process
	def run(self):
		print "Starting " + self.name
		self.process(self.name, self.q)
		print "Exiting " + self.name

class myClass ():
	"""  testing scope...
	"""
	
	def run(self):
		
		self.exitFlag = 0
		threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5", "Thread-6", "Thread-7", "Thread-8" ]
		#nameList = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven" ]
		nameList = [ str(x) for x in range(900) ]
		self.queueLock = threading.Lock()
		self.workQueue = Queue.Queue(len(nameList))
		threads = []
		threadID = 1
		
		
		
		# Create new threads
		for tName in threadList:
			thread = myThread(threadID, tName, self.workQueue, self.process_data)
			thread.start()
			threads.append(thread)
			threadID += 1
		
		# Fill the queue
		self.queueLock.acquire()
		for word in nameList:
			self.workQueue.put(word)
		self.queueLock.release()
		
		# Wait for queue to empty
		while not self.workQueue.empty():
			pass
		
		# Notify threads it's time to exit
		self.exitFlag = 1
		
		# Wait for all threads to complete
		for t in threads:
			t.join()
				
	def process_data(self, threadName, q):
		while not self.exitFlag:
			self.queueLock.acquire()
			if not self.workQueue.empty():
				data = q.get()
				self.queueLock.release()
				print "%s processing %s" % (threadName, data)
			else:
				self.queueLock.release()
			a = 3 * 27
			#time.sleep(.01)



myClass().run()

print "Exiting Main Thread"
