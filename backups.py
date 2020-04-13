import logging
import datetime
import fcntl
import subprocess
import re
import getpass

name = "%Y-%m-%d_%H-%M-%S"

def mostRecentBackup():
  argv = ["tarsnap", "--list-archives"]
  p = subprocess.Popen(argv, stdout=subprocess.PIPE)
  out, errs = p.communicate()
  archives = []
  for l in out.split("\n"):
    if not re.search("^2020", l):
      logging.info("ignoring archive %s", l)
      continue
    archives.append(datetime.datetime.strptime(l, name))
  if p.returncode != 0:
    raise Error()
  most_recent = datetime.datetime.min
  for a in archives:
    if most_recent < a:
      most_recent = a
  logging.info("most recent backup: %s", most_recent)
  return most_recent

def newEnough(r):
  td = datetime.datetime.today() - r
  return td < datetime.timedelta(days=1)

def takeLock():
  fh = open("lock", "w")
  try:
    fcntl.flock(fh, fcntl.LOCK_EX|fcntl.LOCK_NB)
    return True, fh
  except IOError as e:
    logging.info("failed to take lock: %s", e)
    return False, None


def takeBackup(target):
  name = datetime.date.today().strftime("%Y-%m-%d_%H-%M-%S")
  subprocess.check_call(["tarsnap", "--print-stats","-c", "-f", name, target])

def main():
  logging.basicConfig(level=logging.DEBUG)
  logging.info("start")

  r = mostRecentBackup()
  if newEnough(r):
    logging.info("backups is new enough")
    return
  # TODO(psn): ac power
  locked, lockfh = takeLock()
  if not locked:
    return
  target = "/Users/" + getpass.getuser()
  takeBackup(target)


if __name__ == "__main__":
  main()
