#!/usr/bin/python3
import os
import fcntl
import sys

# Check if a lock file exists
lock_file = "/tmp/tray.lock"
#if os.path.isfile(lock_file):
#    print("Another instance is already running, delete %s to start a new instance."% lock_file)
#    sys.exit(1)

# If not, create the lock file
try:
    with open(lock_file, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        import tray
        os.environ["GDK_BACKEND"] = "x11"
        tray.start()
except IOError:
    print("Another instance is already running.")
    sys.exit(1)

# The rest of your script goes here

# When your script is done, release the lock
os.remove(lock_file)

