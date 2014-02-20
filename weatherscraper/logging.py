import time

logfile = "/var/log/c-weatherscraper/service.log"

start = time.time()
count = 0

def log(*what):
    global count
    global start
    count += 1

    msg = time.asctime()
    msg += " : "
    now = time.time() - start
    msg += str(now)
    msg += " : "
    msg += str(count)
    msg += " : "

    for thing in what:
        msg += " "
        msg += str(thing)
    msg += "\n"

    try:
        f = open(logfile, "a")
        f.write(msg)
        f.flush()
        f.close()
    except IOError:
        print(msg)
