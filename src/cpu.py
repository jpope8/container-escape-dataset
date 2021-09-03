#!/usr/bin/env python3

# Above matters, we want to execute without pre-prepending python
# This python file needs to be executable also, i.e. chmod +x
import psutil
import time
import stdio
import recorder # for "static" methods
from recorder import Recorder
import re

# See https://pypi.org/project/psutil/
# pip install psutil
# NB: Good example scripts mimicking linux commands
# see https://github.com/giampaolo/psutil
# see https://github.com/giampaolo/psutil/tree/master/scripts



#def println( label, value ):
#    secondsSinceEpoch = time.time() # 1624868759.1945467
#    #print( label + ' type=' + str(type(value)) + ': ' + str(value) )
#
#    # need to surround list of dict with double quotes for parsing
#    t = type(value)
#    if( isinstance(t,  dict) ):
#        value = '"' + str(value) + '"'
#
#    stdio.printf( 'type=PSUTIL_CPU msg=audit(%.3f:21874): utilcall=%s value=%s\n', secondsSinceEpoch, label, str(value) )
#    #print( ) # so can see each output by itself

def log( rec, key, val ):
    #rec.writeln('cpu_times', result)
    rec.append(key, val)

def execute( recorder ):
    """
    Writes cpu related key-value pairs to the auditer.
    auditer
    """

    #==============================================#
    # CPU
    #==============================================#
    result = psutil.cpu_times()
    log(recorder, 'cpu_times', result )


    # ------- Sampling interval --------#
    # non-blocking (percentage since last call)
    period = None

    result = psutil.cpu_times_percent(interval=period, percpu=False)
    log(recorder, 'cpu_times_percent', result )

    result = psutil.cpu_percent(interval=period)
    log(recorder, 'cpu_percent_allcpus', result)

    result = psutil.cpu_percent(interval=period, percpu=True)
    log(recorder, 'cpu_percent_percpu', result)





    # Remaining calls do not block and execute relatively quick

    # returns
    # cpu_count: 4
    #result = psutil.cpu_count()
    #log(recorder, 'cpu_count', result)

    # cpu_count: 4
    #result = psutil.cpu_count(logical=False)
    #log(recorder, 'cpu_count', result)

    result = psutil.cpu_stats()
    log(recorder, 'cpu_stats', result )

    result = psutil.cpu_freq()
    log(recorder, 'cpu_freq', result)

    # Not available on all psutil, version issue.
    if( hasattr(psutil, 'getloadavg') ):
        result = psutil.getloadavg()  # also on Windows (emulated)
        log(recorder, 'getloadavg', result)
    #else:
    #    print("getloadavg does not exist")


    #==============================================#
    # MEMORY
    #==============================================#
    # returns str
    # swap_memory: sswap(total=1127211008, used=1359872, free=1125851136, percent=0.1, sin=81920, sout=6533120)
    result = psutil.virtual_memory()
    log(recorder, 'virtual_memory', result)

    # returns str
    # swap_memory: sswap(total=1127211008, used=1359872, free=1125851136, percent=0.1, sin=81920, sout=6533120)
    result = psutil.swap_memory()
    log(recorder, 'swap_memory', result)

    #==============================================#
    # DISKS
    #==============================================#
    # returns list of key=value pairs
    # disk_partitions: [sdiskpart(device='/dev/sda1', mountpoint='/', fstype='ext4', opts='rw,relatime,errors=remount-ro'),
    #     sdiskpart(device='/dev/sr0', mountpoint='/media/cdrom0', fstype='iso9660',
    #     opts='ro,nosuid,nodev,noexec,relatime,nojoliet,check=s,map=n,blocksize=2048')]
    result = psutil.disk_partitions()
    log(recorder, 'disk_partitions', result)

    # returns str
    result = psutil.disk_usage('/')
    log(recorder, 'disk_usage', result)

    # returns str
    result = psutil.disk_io_counters(perdisk=False)
    log(recorder, 'disk_io_counters', result)


    #==============================================#
    # NETWORK
    #==============================================#
    # returns dict
    result = psutil.net_io_counters(pernic=True)
    log(recorder, 'net_io_counters', result)

    # returns list of str, format 'sconn(key=value, ... )'
    # [sconn(fd=-1, family=<AddressFamily.AF_INET6: 10>, type=<SocketKind.SOCK_DGRAM: 2>, laddr=addr(ip='::', port=123), raddr=(), status='NONE', pid=None),
    result = psutil.net_connections(kind='tcp')
    log(recorder, 'net_connections_tcp', result)

    # returns dict
    result = psutil.net_connections(kind='udp')
    log(recorder, 'net_connections_udp', result)

    # returns dict
    result = psutil.net_if_addrs()
    log(recorder, 'net_if_addrs', result)

    # returns dict
    result = psutil.net_if_stats()
    log(recorder, 'net_if_stats', result)


    #==============================================#
    # SENSORS
    #==============================================#

    # returns dict
    result = psutil.sensors_temperatures()
    log(recorder, 'sensors_temperatures', result)

    # Umbrella returns "sensors_fans": ["{}"],
    #result = psutil.sensors_fans()
    #log(recorder, 'sensors_fans', result)

    # Umbrella returns "sensors_battery": ["None"],
    #result = psutil.sensors_battery()
    #log(recorder, 'sensors_battery', result)


    #==============================================#
    # OTHER INFO
    #==============================================#

    # returns list
    result = psutil.users()
    log(recorder, 'users', result)

    # returns float
    #result = psutil.boot_time()
    #log(recorder, 'boot_time', result)
    #==============================================#
    # Write out all at once
    #==============================================#
    recorder.flush()

def main():
    """
    Creates auditer, records key value samples, writes to file.
    """
    rec = Recorder( recorder.makeFilename() )
    rec.incrementEventid()
    execute(rec)
    time.sleep(1)
    rec.incrementEventid()
    execute(rec)
    del( rec )

if __name__ == '__main__':
    main()

"""
"cpu_times": ["scputimes(user=6369.75, nice=0.0, system=8025.92, idle=2077677.25, iowait=205.64, irq=0.0, softirq=89.07, steal=0.0, guest=0.0, guest_nice=0.0)"],
"cpu_times_percent": ["scputimes(user=13.6, nice=0.0, system=18.1, idle=67.8, iowait=0.3, irq=0.0, softirq=0.2, steal=0.0, guest=0.0, guest_nice=0.0)"],
"cpu_percent_allcpus": ["31.8"],
"cpu_percent_percpu": ["[28.0, 12.6, 53.7, 32.0]"],
"cpu_stats": ["scpustats(ctx_switches=272166774, interrupts=106430462, soft_interrupts=45082977, syscalls=0)"],
"cpu_freq": ["scpufreq(current=1200.0, min=600.0, max=1200.0)"],
"getloadavg": ["(0.32, 0.09, 0.06)"],
"virtual_memory": ["svmem(total=969773056, available=447344640, percent=53.9, used=418791424, free=213401600, active=267735040, inactive=123215872, buffers=49274880, cached=288305152, shared=49373184, slab=345088000)"],
"swap_memory": ["sswap(total=0, used=0, free=0, percent=0.0, sin=0, sout=0)"],
"disk_partitions": ["[sdiskpart(device='/dev/root', mountpoint='/', fstype='ext4', opts='rw,noatime', maxfile=255, maxpath=4096), sdiskpart(device='/dev/mmcblk0p1', mountpoint='/boot', fstype='vfat', opts='ro,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,errors=remount-ro', maxfile=1530, maxpath=4096), sdiskpart(device='/dev/mmcblk0p4', mountpoint='/storage', fstype='ext4', opts='rw,noatime', maxfile=255, maxpath=4096)]"],
"disk_usage": ["sdiskusage(total=7369940992L, used=3333173248L, free=3793608704L, percent=46.8)"],
"disk_io_counters": ["sdiskio(read_count=32711, write_count=214853, read_bytes=708656640, write_bytes=2986895360L, read_time=65169, write_time=801852, read_merged_count=21473, write_merged_count=313757, busy_time=717680)"],
"net_io_counters": ["{'docker0': snetio(bytes_sent=17536012, bytes_recv=291193, packets_sent=14171, packets_recv=7058, errin=0, errout=0, dropin=0, dropout=0), 'usb0': snetio(bytes_sent=14452615, bytes_recv=3494016, packets_sent=131138, packets_recv=35933, errin=0, errout=0, dropin=0, dropout=0), 'lo': snetio(bytes_sent=560772, bytes_recv=560772, packets_sent=6496, packets_recv=6496, errin=0, errout=0, dropin=0, dropout=0), 'br0': snetio(bytes_sent=383340603, bytes_recv=137551708, packets_sent=540686, packets_recv=657746, errin=0, errout=0, dropin=0, dropout=0), 'veth6c7a795': snetio(bytes_sent=736, bytes_recv=0, packets_sent=8, packets_recv=0, errin=0, errout=0, dropin=0, dropout=0), 'wlan0': snetio(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0, errin=0, errout=0, dropin=0, dropout=0), 'eth0': snetio(bytes_sent=393393424, bytes_recv=137351459, packets_sent=576599, packets_recv=670664, errin=0, errout=0, dropin=0, dropout=0)}"],
"net_connections_tcp": ["[sconn(fd=-1, family=2, type=1, laddr=addr(ip='192.168.1.102', port=22), raddr=addr(ip='192.168.1.100', port=62757), status='ESTABLISHED', pid=None), sconn(fd=-1, family=10, type=1, laddr=addr(ip='::1', port=2947), raddr=(), status='LISTEN', pid=None), sconn(fd=-1, family=10, type=1, laddr=addr(ip='::', port=22), raddr=(), status='LISTEN', pid=None), sconn(fd=-1, family=2, type=1, laddr=addr(ip='127.0.0.1', port=2947), raddr=(), status='LISTEN', pid=None), sconn(fd=-1, family=2, type=1, laddr=addr(ip='192.168.1.102', port=22), raddr=addr(ip='192.168.1.100', port=63701), status='ESTABLISHED', pid=None), sconn(fd=-1, family=2, type=1, laddr=addr(ip='192.168.1.102', port=22), raddr=addr(ip='192.168.1.100', port=63707), status='ESTABLISHED', pid=None), sconn(fd=-1, family=2, type=1, laddr=addr(ip='0.0.0.0', port=22), raddr=(), status='LISTEN', pid=None)]"],
"net_connections_udp": ["[sconn(fd=-1, family=2, type=2, laddr=addr(ip='127.0.0.1', port=323), raddr=(), status='NONE', pid=None), sconn(fd=-1, family=10, type=2, laddr=addr(ip='::1', port=323), raddr=(), status='NONE', pid=None), sconn(fd=-1, family=10, type=2, laddr=addr(ip='::', port=546), raddr=(), status='NONE', pid=None), sconn(fd=-1, family=2, type=2, laddr=addr(ip='0.0.0.0', port=68), raddr=(), status='NONE', pid=None)]"],
"net_if_addrs": ["{'docker0': [snicaddr(family=2, address='172.17.0.1', netmask='255.255.0.0', broadcast='172.17.255.255', ptp=None), snicaddr(family=10, address='fe80::42:c4ff:fe61:94ed%docker0', netmask='ffff:ffff:ffff:ffff::', broadcast=None, ptp=None), snicaddr(family=17, address='02:42:c4:61:94:ed', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)], 'veth6c7a795': [snicaddr(family=10, address='fe80::68d5:3eff:fe69:6835%veth6c7a795', netmask='ffff:ffff:ffff:ffff::', broadcast=None, ptp=None), snicaddr(family=17, address='6a:d5:3e:69:68:35', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)], 'wlan0': [snicaddr(family=17, address='00:11:7f:1b:e1:e4', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)], 'usb0': [snicaddr(family=17, address='72:5c:76:a1:58:3e', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)], 'lo': [snicaddr(family=2, address='127.0.0.1', netmask='255.0.0.0', broadcast=None, ptp=None), snicaddr(family=10, address='::1', netmask='ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff', broadcast=None, ptp=None), snicaddr(family=17, address='00:00:00:00:00:00', netmask=None, broadcast=None, ptp=None)], 'eth0': [snicaddr(family=17, address='b8:27:eb:3c:de:d2', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)], 'br0': [snicaddr(family=2, address='192.168.1.102', netmask='255.255.255.0', broadcast='192.168.1.255', ptp=None), snicaddr(family=10, address='fe80::2010:47d1:9b54:2d96%br0', netmask='ffff:ffff:ffff:ffff::', broadcast=None, ptp=None), snicaddr(family=17, address='b8:27:eb:3c:de:d2', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)]}"],
"net_if_stats": ["{'docker0': snicstats(isup=True, duplex=0, speed=0, mtu=1500), 'usb0': snicstats(isup=True, duplex=0, speed=0, mtu=1500), 'lo': snicstats(isup=True, duplex=0, speed=0, mtu=65536), 'br0': snicstats(isup=True, duplex=0, speed=0, mtu=1500), 'veth6c7a795': snicstats(isup=True, duplex=2, speed=10000, mtu=1500), 'wlan0': snicstats(isup=False, duplex=0, speed=0, mtu=1500), 'eth0': snicstats(isup=True, duplex=2, speed=100, mtu=1500)}"],
"sensors_temperatures": ["{'cpu_thermal': [shwtemp(label='', current=73.06, high=None, critical=None)]}"],
"sensors_fans": ["{}"],
"sensors_battery": ["None"],
"users": ["[suser(name='pi', terminal='pts/0', host='192.168.1.100', started=1627453696.0, pid=30187), suser(name='pi', terminal='pts/1', host='192.168.1.100', started=1627455488.0, pid=32245), suser(name='pi', terminal='pts/2', host='192.168.1.100', started=1627455616.0, pid=32282)]"]
"""
