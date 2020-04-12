import fcntl
import time

fh = open("lock", "w")
fcntl.flock(fh, fcntl.LOCK_EX|fcntl.LOCK_NB)
print "sleeping"
time.sleep(3000)

