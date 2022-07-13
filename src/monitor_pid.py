"""
Utility to list processes and filter for processes having a keyword.
These processes are then added to auditd (via auditctl) usinng the
process identifier to monitor/log these processes.
"""

import subprocess
import os
import re
import sys
import command_line

#
# Parses the pid out of a proclisting
#
def getPid(proclisting):
    tokens = re.split(' +', proclisting)
    for i in range(len(tokens)):
        token = tokens[i]
        #print( token )
    pid = tokens[1]
    return pid


def auditPid(pid, keyword):
    """
    Adds pid's matching keyword to auditctr process monitoring.
    Zero or morerules may be added.

    Parameters
    ----------
    pid : str
        process id to add to auditing rules
    keyword : str
        word ro search in processes to monitor
    """
    #sudo auditctl -a always,exit -S all -F pid=1234 -k docker-proxy
    # the  command
    command = 'sudo auditctl -a always,exit -S all -F pid=' + pid + ' -k ' + keyword + '-p'
    result = command_line.execute(command)
    # Attempt to also monitor child processes created by this parent process
    command = 'sudo auditctl -a always,exit -S all -F ppid=' + pid + ' -k ' + keyword + '-p'
    result = command_line.execute(command)
    #for line in result:
    #    print('PID: ' + line)

def monitor( keyword ):
    """
    Adds currently executable PID to auditd log.  First parses
    current processes with the executableName.  The PID is then
    parsed out.  Finally, auditctl is called with the pid to
    the currently running auditd log (pre-requisite id that 
    auditd is already running)

    Parameters
    ----------
    keyword : str
        name of the executable to monitor
    """
    #proclistings = list_command(keyword)
    result = command_line.execute('ps -ef')
    for proclisting in result:
        # Filter for keyword, make sure to omit this proclisting
        if( keyword in proclisting and sys.argv[0] not in proclisting ):
            pid = getPid(proclisting)
            print('PID: ' + pid)
            auditPid(pid, keyword)

# seems like -ef gives a bit more info
# def exclude(keyword):
#     result = command_line.execute('ps -ef')
#     for proclisting in result:
#         if (keyword in proclisting):
#             pid = getPid(proclisting)
#             print('Exclude PID: ' + pid)


#     return


def exclude( keyword ):
    """
    Excludes any process with the keyword from auditing.

    Parameters
    ----------
    keyword : str
        keyword to exclude
    """
    #proclistings = list_command(keyword)
    result = command_line.execute('ps -ef')
    for proclisting in result:
        # Filter for keyword, make sure to omit this proclisting
        if( keyword in proclisting ):
            pid = getPid(proclisting)
            print('Exclude PID: ' + pid)
            command = 'sudo auditctl -a never,exit -S all -F pid=' + pid + ' -k ' + keyword + '-p'
            result = command_line.execute(command)

            command = 'sudo auditctl -a never,exit -S all -F ppid=' + pid + ' -k ' + keyword + '-p'
            result = command_line.execute(command)
#
# Main function
#
def main():
    if( len(sys.argv) != 2 ):
        print('  Usage: <keyword>')
        print('Example: docker-proxy')
        return
    keyword = sys.argv[1]
    exclude(keyword)


# $ ps -ef | grep docker
# root      1040     1  0 04:48 ?        00:02:49 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
# pi        6222  6336  0 19:29 pts/2    00:00:00 grep --color=auto docker
# root     13712  2358  0 09:22 pts/0    00:00:00 sudo docker-compose up
# root     13713 13712  0 09:22 pts/0    00:00:00 docker-compose up
# root     13714 13713  0 09:22 pts/0    00:01:47 docker-compose up
# root     28983  1040  0 07:08 ?        00:00:00 /usr/bin/docker-proxy -proto tcp -host-ip 0.0.0.0 -host-port 55555 -container-ip 172.28.0.3 -container-port 44444
# root     28991  1040  0 07:08 ?        00:00:00 /usr/bin/docker-proxy -proto tcp -host-ip :: -host-port 55555 -container-ip 172.28.0.3 -container-port 44444
# pi       29713  1133  0 05:49 ?        00:01:21 mousepad /home/pi/awesome-compose/react-java-mysql/docker-compose.yaml
if __name__ == '__main__':
    main()
