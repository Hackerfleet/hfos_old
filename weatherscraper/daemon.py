#!/usr/bin/env python

# Copy-Pasta'ed from
# http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
# because its good.

import sys
import os
import pwd
import grp
import time
import atexit
from signal import SIGTERM

from weatherscraper.logging import log, logfile


class Daemon(object):
        """
        A generic daemon class.

        Usage: subclass the Daemon class and override the run() method
        """
        def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', user="nobody", group="nogroup"):
                self.stdin = stdin
                self.stdout = stdout
                self.stderr = stderr
                self.pidfile = pidfile
                # Get the uid/gid from the name

                self.uid = pwd.getpwnam(user).pw_uid
                self.gid = grp.getgrnam(group).gr_gid

        def daemonize(self):
                """
                do the UNIX double-fork magic, see Stevens' "Advanced
                Programming in the UNIX Environment" for details (ISBN 0201563177)
                http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
                """
                log("Trying to daemonize")
                try:
                        pid = os.fork()
                        if pid > 0:
                                # exit first parent
                                sys.exit(0)
                except OSError as e:
                        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
                        sys.exit(1)

                # decouple from parent environment
                os.chdir("/")
                os.setsid()
                os.umask(0)

                log("Second fork")
                # do second fork
                try:
                        pid = os.fork()
                        if pid > 0:
                                # exit from second parent
                                sys.exit(0)
                except OSError as e:
                        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
                        sys.exit(1)

                log("Redirecting standard file descriptors")
                sys.stdout.flush()
                sys.stderr.flush()
                si = open(self.stdin, 'r')
                so = open(self.stdout, 'a+')
                se = open(self.stderr, 'ba+', 0)
                os.dup2(si.fileno(), sys.stdin.fileno())
                os.dup2(so.fileno(), sys.stdout.fileno())
                os.dup2(se.fileno(), sys.stderr.fileno())

                log("Writing pidfile")
                atexit.register(self.delpid)
                pid = str(os.getpid())
                pidfile = open(self.pidfile, 'w+')
                pidfile.write("%s\n" % pid)
                pidfile.close()

                log("Transferring ownerships")
                os.chown(self.pidfile, self.uid, self.gid)
                os.chown(logfile, self.uid, self.gid)

                log("Dropping privs")
                self.drop_privileges()

                log("Done! :)")

        def drop_privileges(self):
            if os.getuid() != 0:
                # We're not root so, like, whatever dude
                return

            # Remove group privileges
            os.setgroups([])

            # Try setting the new uid/gid
            os.setgid(self.gid)
            os.setuid(self.uid)

            # Ensure a very conservative umask
            old_umask = os.umask(0o077)

        def delpid(self):
                os.remove(self.pidfile)

        def start(self):
                """
                Start the daemon
                """
                # Check for a pidfile to see if the daemon already runs
                try:
                        pf = open(self.pidfile,'r')
                        pid = int(pf.read().strip())
                        pf.close()
                except IOError:
                        pid = None

                if pid:
                        message = "pidfile %s already exist. Daemon already running?\n"
                        sys.stderr.write(message % self.pidfile)
                        sys.exit(1)

                # Start the daemon
                self.daemonize()
                self.run()

        def stop(self):
                """
                Stop the daemon
                """
                # Get the pid from the pidfile
                try:
                        pf = open(self.pidfile, 'r')
                        pid = int(pf.read().strip())
                        pf.close()
                except IOError:
                        pid = None

                if not pid:
                        message = "pidfile %s does not exist. Daemon not running?\n"
                        sys.stderr.write(message % self.pidfile)
                        return  # not an error in a restart

                # Try killing the daemon process
                try:
                        while 1:
                                os.kill(pid, SIGTERM)
                                time.sleep(0.1)
                except OSError as err:
                        err = str(err)
                        if err.find("No such process") > 0:
                                if os.path.exists(self.pidfile):
                                        os.remove(self.pidfile)
                        else:
                                print(str(err))
                                sys.exit(1)

        def restart(self):
                """
                Restart the daemon
                """
                self.stop()
                self.start()

        def run(self):
                """
                You should override this method when you subclass Daemon. It will be called after the process has been
                daemonized by start() or restart().
                """
