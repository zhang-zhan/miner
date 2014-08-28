#encoding=utf-8
__author__ = 'Peter'

import os.path, time, struct
from datetime import datetime

def get_mtime(path):
    """Return the time of last modification of path as epoch format."""
    mtime = time.ctime(os.path.getmtime(path))
    dtmp = datetime.strptime(mtime, "%a %b %d %X %Y")
    stamp = int(time.mktime(dtmp.timetuple()))
    return stamp

def time2epoch(time_str):
    """Process the datetime format in Weibo and return epoch format."""
    #dateti = time_str.replace('[+-]\w\w\w\w\s', '')
    if isinstance(time_str,unicode):
        time_str = time_str.encode()

    if isinstance(time_str,str):
        time_str = time_str.strip(' \t\r\n')
        if len(time_str)<1:
            print("Got empty time string!")
            return -1

        d = time_str.split(" ")

        zone = d.pop(4) #time zone

        time_str = "%s %s %s %s %s" % tuple(d)
        dtmp = datetime.strptime(time_str, "%a %b %d %X %Y")

        stamp = int(time.mktime(dtmp.timetuple()))
        if zone != "+0800":
            hour = int(zone[1: 3])
            min  = int(zone[3: 5])
            stamp += min*60 + (hour+8)*3600 if zone[0] is '-' else (hour-8)*3600
    else:
        stamp = int(time.mktime(time_str.timetuple()))
    return stamp

def time2str(time_str=None):
    """Process the datetime format in datetime.datetime or epoch and return Weibo format str."""
    if isinstance(time_str,str):
        #Convert from string to epoch
        dtmp = datetime.strptime(time_str, "%a %b %d %X %Y")
        time_str = int(time.mktime(dtmp.timetuple()))
    elif isinstance(time_str,datetime):
        time_str = int(time.mktime(time_str.timetuple()))
    elif time_str is None:
        time_str = int(time.mktime(time.localtime()))
    return time.strftime("%a %b %d %X +0800 %Y", time.localtime(time_str))

def now2epoch():
    now = time.mktime(time.localtime())
    return int(now)

def convert_endian(v):
    f = None
    if isinstance(v, int):
        f = '<i'
    elif isinstance(v, long):
        f = '<q'
    else:
        raise ValueError('Unsupported type to convert endian: %s' % type(v) )

    if f is not None: v = buffer(struct.pack(f, v))
    return v

def unpack_little_endian(v):
    n = len(v)/8
    f = struct.unpack_from('<' + 'q'*n, v)
    return f