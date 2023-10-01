#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
""" threadtest.py - just that
	
	check out using thread queues...
"""

import Queue
import threading
import time

exitFlag = 0

class myThread (threading.Thread):
	def __init__(self, threadID, name, q):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
	def run(self):
		print "Starting " + self.name
		process_data(self.name, self.q)
		print "Exiting " + self.name

def process_data(threadName, q):
	while not exitFlag:
		queueLock.acquire()
		if not workQueue.empty():
			data = q.get()
			queueLock.release()
			print "%s processing %s" % (threadName, data)
		else:
			queueLock.release()
		a = 3 * 27
		#time.sleep(.01)

threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5", "Thread-6", "Thread-7", "Thread-8" ]
#nameList = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven" ]
nameList = [ str(x) for x in range(900) ]
queueLock = threading.Lock()
workQueue = Queue.Queue(len(nameList))
threads = []
threadID = 1

# Create new threads
for tName in threadList:
	thread = myThread(threadID, tName, workQueue)
	thread.start()
	threads.append(thread)
	threadID += 1

# Fill the queue
queueLock.acquire()
for word in nameList:
	workQueue.put(word)
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
	pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in threads:
	t.join()
print "Exiting Main Thread"
