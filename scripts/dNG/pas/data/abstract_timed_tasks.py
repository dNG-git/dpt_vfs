# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.data.AbstractTimedTasks
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;timed_tasks

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;gpl
----------------------------------------------------------------------------
#echo(pasTimedTasksVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from threading import RLock, Timer, Thread
from time import time

class AbstractTimedTasks(object):
#
	"""
Timed tasks 

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: timed_tasks
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	synchronized = RLock()
	"""
Lock used in multi thread environments.
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractTimedTasks)

:since: v0.1.00
		"""

		self.log_handler = None
		"""
The log_handler is called whenever debug messages should be logged or errors
happened.
		"""
		self.timer = None
		"""
"Timer" instance
		"""
		self.timer_timeout = None
		"""
UNIX timestamp of the next element
		"""
	#

	def __del__(self):
	#
		"""
Destructor __del__(AbstractTimedTasks)

:since: v0.1.00
		"""

		AbstractTimedTasks.stop(self)
	#

	def get_next_update_timestamp(self):
	#
		"""
Get the implementation specific next "run()" UNIX timestamp.

:access: protected
:return: (int) UNIX timestamp; -1 if no further "run()" is required at the
         moment
:since:  v0.1.01
		"""

		raise RuntimeError("Not implemented", 38)
	#

	def run(self):
	#
		"""
Worker loop

:access: protected
:since:  v0.1.00
		"""

		with AbstractTimedTasks.synchronized:
		#
			if (self.timer_timeout != None):
			#
				self.timer_timeout = -1
				self.update_timestamp()
			#
		#
	#

	def update_timestamp(self, timestamp = -1):
	#
		"""
Update the timestamp for the next "run()" call.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -TimedTasks.update_timestamp({0:d})- (#echo(__LINE__)#)".format(timestamp))

		if (self.timer_timeout != None):
		#
			with AbstractTimedTasks.synchronized:
			#
				if (timestamp < 0): timestamp = self.get_next_update_timestamp()

				if (timestamp > 0):
				#
					timeout = round(1 + (timestamp - time()))
					timeout = (0 if (timeout < 0) else int(timeout))
				#
				else: timeout = 0

				if (timestamp < 0):
				#
					if (self.timer != None and self.timer.is_alive()):
					#
						self.timer.cancel()
						self.timer_timeout = -1
					#
				#
				elif (self.timer_timeout < 0 or timeout < self.timer_timeout):
				#
					if (timeout > 0):
					#
						if (self.timer != None and self.timer.is_alive()): self.timer.cancel()
						self.timer = Timer(timeout, self.run)
						self.timer.start()

						if (self.log_handler != None): self.log_handler.debug("pas.timed_tasks waits for {0:d} seconds".format(timeout))
					#
					else:
					#
						if (self.log_handler != None): self.log_handler.debug("pas.timed_tasks continues with the next step")

						py_thread = Thread(target = self.run)
						py_thread.start()
					#

					self.timer_timeout = timeout
				#
			#
		#
	#

	def start(self, params = None, last_return = None):
	#
		"""
Start the timed tasks implementation.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
		"""

		with AbstractTimedTasks.synchronized:
		#
			if (self.timer_timeout == None): self.timer_timeout = -1
		#
	#

	def stop(self, params = None, last_return = None):
	#
		"""
Stop the timed tasks implementation.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -TimedTasks.stop()- (#echo(__LINE__)#)")

		with AbstractTimedTasks.synchronized:
		#
			if (self.timer_timeout != None):
			#
				if (self.timer != None and self.timer.is_alive()): self.timer.cancel()
				self.timer = None
				self.timer_timeout = None
			#
		#
	#
#

##j## EOF