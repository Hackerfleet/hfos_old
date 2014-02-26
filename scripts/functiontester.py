__author__ = 'riot'

from Axon.Scheduler import scheduler
from weatherscraper.components import build_system

if __name__ == '__main__':
    #weatherScraper()
    build_system(online=False)
    scheduler.run.runThreads()