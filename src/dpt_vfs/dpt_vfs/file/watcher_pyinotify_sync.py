# -*- coding: utf-8 -*-

"""
direct Python Toolbox
All-in-one toolbox to encapsulate Python runtime variants
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?dpt;vfs

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(dptVfsVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=import-error

from pyinotify import Notifier

from .watcher_pyinotify import WatcherPyinotify
from .watcher_pyinotify_callback import WatcherPyinotifyCallback

class WatcherPyinotifySync(WatcherPyinotify):
    """
"file:///" watcher using pyinotify's (synchronous) Notifier.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    dpt
:subpackage: vfs
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def check(self, _path):
        """
Checks a given path for changes if "is_synchronous()" is true.

:param _path: Filesystem path

:return: (bool) True if the given path URL has been changed since last check
         and "is_synchronous()" is true.
:since:  v1.0.0
        """

        with self._lock:
            if (self.pyinotify_instance.check_events()):
                self.pyinotify_instance.read_events()
                self.pyinotify_instance.process_events()
            #
        #

        return False
    #

    def _init_notifier(self):
        """
Initializes the pyinotify instance.

:since: v1.0.0
        """

        with self._lock:
            if (self.pyinotify_instance is None):
                self.pyinotify_instance = Notifier(self, WatcherPyinotifyCallback(self), timeout = 5)
            #
        #
    #

    def stop(self):
        """
Stops all watchers.

:since: v1.0.0
        """

        with self._lock:
            self.free()
            self.pyinotify_instance = None
        #
    #
#