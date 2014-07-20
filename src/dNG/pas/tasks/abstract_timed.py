# -*- coding: utf-8 -*-
##j## BOF

"""
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
"""

from threading import Timer
from time import time

from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.instance_lock import InstanceLock
from dNG.pas.runtime.not_implemented_exception import NotImplementedException
from dNG.pas.runtime.thread import Thread

class AbstractTimed(object):
#
	"""
Timed tasks provides an abstract, time ascending sorting scheduler.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: timed_tasks
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	# pylint: disable=unused-argument

	_lock = InstanceLock()
	"""
Thread safety lock
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractTimed)

:since: v0.1.00
		"""

		self.log_handler = None
		"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.timer = None
		"""
"Timer" instance
		"""
		self.timer_active = False
		"""
UNIX timestamp of the next element
		"""
		self.timer_timeout = -1
		"""
UNIX timestamp of the next element
		"""
	#

	def __del__(self):
	#
		"""
Destructor __del__(AbstractTimed)

:since: v0.1.00
		"""

		self.stop()
	#

	def _get_next_update_timestamp(self):
	#
		"""
Get the implementation specific next "run()" UNIX timestamp.

:return: (int) UNIX timestamp; -1 if no further "run()" is required at the
         moment
:since:  v0.1.01
		"""

		raise NotImplementedException()
	#

	def is_started(self):
	#
		"""
Returns true if the timed tasks implementation has been started.

:return: (bool) True if scheduling is active
:since:  v0.1.01
		"""

		return self.timer_active
	#

	def run(self):
	#
		"""
Timed task execution

:since: v0.1.00
		"""

		if (self.timer_active):
		# Thread safety
			with AbstractTimed._lock:
			#
				if (self.timer_active):
				#
					self.timer_timeout = -1
					self.update_timestamp()
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

		if (not self.timer_active):
		# Thread safety
			with AbstractTimed._lock:
			#
				if (not self.timer_active):
				#
					Hook.register("dNG.pas.Status.onShutdown", self.stop)

					self.timer_active = True
					self.timer_timeout = -1
					self.update_timestamp()
				#
			#
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

		if (self.timer_active):
		# Thread safety
			with AbstractTimed._lock:
			#
				if (self.timer_active):
				#
					if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.stop()- (#echo(__LINE__)#)", self, context = "pas_timed_tasks")

					if (self.timer != None and self.timer.is_alive()): self.timer.cancel()
					self.timer = None
					self.timer_active = False

					Hook.unregister("dNG.pas.Status.onShutdown", self.stop)
				#
			#
		#
	#

	def update_timestamp(self, timestamp = -1):
	#
		"""
Update the timestamp for the next "run()" call.

:param timestamp: Externally defined UNIX timestamp of the next scheduled
                  run.

:since: v0.1.00
		"""

		if (timestamp != -1): timestamp = int(timestamp)
		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.update_timestamp({1:d})- (#echo(__LINE__)#)", self, timestamp, context = "pas_timed_tasks")

		if (self.timer_active):
		#
			with AbstractTimed._lock:
			#
				if (timestamp < 0): timestamp = int(self._get_next_update_timestamp())

				if (timestamp > 0):
				#
					timeout = timestamp - int(time())
					timeout = (0 if (timeout < 0) else timeout)
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

						if (self.log_handler != None): self.log_handler.debug("{0!r} waits for {1:d} seconds", self, timeout, context = "pas_timed_tasks")
					#
					else:
					#
						if (self.log_handler != None): self.log_handler.debug("{0!r} continues with the next step", self, context = "pas_timed_tasks")

						thread = Thread(target = self.run)
						thread.start()
					#

					self.timer_timeout = timeout
				#
			#
		#
	#
#

##j## EOF