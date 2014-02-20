import time

logfile="/var/log/c-weatherscraper/service.log"

start = time.time()
count = 0

def log(*what):
    global count
    global start
    count += 1
    f = open(logfile, "a")
    f.write(time.asctime())
    f.write(" : ")
    f.write(str(time.time - start))
    f.write(" : ")
    f.write(str(count))
    f.write(" : ")

    for thing in what:
        f.write(" ")
        f.write(str(thing))
    f.write("\n")
    f.flush()
    f.close()