import time

import os
from Axon.Component import component

from hfos.utils.logger import log, warn, error, critical


_proc_status = '/proc/%d/status' % os.getpid()


def _VmB(VmKey):
    '''Private.
    '''
    global _proc_status, _scale
    # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
        # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
        # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]


def memory(since=0.0):
    '''Return memory usage in bytes.
    '''
    return _VmB('VmSize:') - since


def resident(since=0.0):
    '''Return resident memory usage in bytes.
    '''
    return _VmB('VmRSS:') - since


def stacksize(since=0.0):
    '''Return stack size in bytes.
    '''
    return _VmB('VmStk:') - since


class MemDebugger(component):
    def __init__(self, interval=10, lvl=critical):
        super(MemDebugger, self).__init__()
        self.interval = interval
        self.lvl = lvl
        self.procstatus = '/proc/%d/status' % os.getpid()
        self.scale = {
            'kB': 1024.0, 'mB': 1024.0 * 1024.0,
            'KB': 1024.0, 'MB': 1024.0 * 1024.0
        }

    def get_mem(self):
        try:
            t = open(_proc_status)
            v = t.read()
            t.close()
        except:
            return 0.0  # non-Linux?
            # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'

        mem = {}

        for VmKey in ('VmSize:', 'VmRSS:', 'VmStk:', 'VmData:'):
            if VmKey in v:
                i = v.index(VmKey)
                nv = v[i:].split(None, 3)  # whitespace
                if len(nv) < 3:
                    mem[VmKey[:-1]] = 0.0  # invalid format?
                    # convert Vm value to bytes
                else:
                    mem[VmKey[:-1]] = round(float(nv[1]) / 1024, 2)  # * self.scale[v[2]]
            else:
                mem[VmKey[:-1]] = 0.0
        return mem

    def main(self):
        log("[MD] Reporting in with PID ", os.getpid(), self.get_mem(), lvl=self.lvl)
        lastcheck = time.time()
        while True:
            if time.time() > self.interval + lastcheck:
                lastcheck = time.time()
                log("[MD]", os.getpid(), self.get_mem(), lvl=self.lvl)
            yield 1
        return

def build_memdebugger():
    return MemDebugger().activate()