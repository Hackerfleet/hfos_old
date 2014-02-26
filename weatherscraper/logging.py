import time

logfile = "/var/log/c-weatherscraper/service.log"

start = time.time()
count = 0

def log(*what):
    global count
    global start
    count += 1

    now = time.time() - start
    msg = "[%s] : %.5f : %s :" % ((time.asctime(),
                                         now,
                                         count)
    )

    for thing in what:
        msg += " "
        msg += str(thing)

    try:
        f = open(logfile, "a")
        f.write(msg)
        f.flush()
        f.close()
    except IOError:
        print(msg)
