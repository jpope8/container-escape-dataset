
Install Raspian-Docker VMware Fusion
------------------------------------
From raspberrypi.org/software/raspberry-pi-desktop
    2021-01-11-raspian-buster-i386.iso

Need to read prompts, not all defaults are good
e.g. need to install grub into /dev/sda2
I used VMware Fusion which only had Debian9 (not the 64)
From raspberrypi.org/software/raspberry-pi-desktop
    2021-01-11-raspian-buster-i386.iso
Took 20GB hard drive, 4 GB RAM, 4 CPUs

Install Auditd (worked no issue)
------------------------------------
sudo apt-get install auditd

Configuring Auditd
------------------------------------
/etc/audit/auditd.conf
#
# This file controls the configuration of the audit daemon
#

local_events = yes
write_logs = yes
log_file = /var/log/audit/audit.log
log_group = adm
log_format = RAW
flush = INCREMENTAL_ASYNC
freq = 50
max_log_file = 20  # DEFAULT 8
num_logs = 100     # DEFAULT 5
priority_boost = 4
disp_qos = lossy


From /usr/share/doc/auditd/examples/rules
pi@raspberry:~ $ sudo ls -la /etc/audit/rules.d/
total 36
drwxr-x--- 2 root root 4096 May 26 11:38 .
drwxr-x--- 3 root root 4096 May 26 11:40 ..
-rw-r--r-- 1 root root  240 May 26 11:36 10-base-config.rules
-rw-r--r-- 1 root root 6663 May 26 11:37 30-stig.rules
-rw-r--r-- 1 root root 1498 May 26 11:37 31-privileged.rules
-rw-r--r-- 1 root root  339 May 26 11:37 33-docker.rules
-rw-r--r-- 1 root root   86 May 26 11:38 99-finalize.rules
-rw-r----- 1 root root  240 Apr 25  2019 audit.rules

augenrules --load



Install Docker
------------------------------------
NB: Says to use convenience script get.docker.com for Raspian
    This does not work (I believe the arch=i386 should be amd64)
Use the standard debian install instructions

https://docs.docker.com/engine/install/debian/


Install Falco
------------------------------------
Per https://falco.org/docs/getting-started/installation/

1. Install Falco key in apt
curl -s https://falco.org/repo/falcosecurity-3672BA8F.asc > falcosecurity-3672BA8F.asc
sudo apt-key add falcosecurity-3672BA8F.asc
sudo echo "deb https://download.falco.org/packages/deb stable main" | sudo tee -a /etc/apt/sources.list.d/falcosecurity.list
sudo apt-get update -y

Get Warning:
N: Skipping acquire of configured file 'main/binary-i386/Packages' as repository
'https://download.falco.org/packages/deb stable InRelease'
doesn't support architecture 'i386'

2. Install kernel headers
sudo apt-get -y install linux-headers-$(uname -r)

3. Install Falco
sudo apt-get install -y falco


Run Containers
-----------------------------------------
sudo docker run -it -d --name=dbms --mount source=cassandra-vol,target=/app cassandra
sudo docker run -it -d --name=webs -p 8080:80 nginx
sudo docker run -it -d --name=aiml ubuntu
sudo docker run -it -d --name=micr alpine

The -d is to run as daemon so can attach/detach
(detach is ctrl+p then ctrl+q)

sudo docker stop dbms
sudo docker stop webs
sudo docker stop aiml
sudo docker stop micr

sudo docker container rm dbms
sudo docker container rm webs
sudo docker container rm aiml
sudo docker container rm micr





QUESTION: What was original auditd rules?
https://linuxhint.com/list_of_linux_syscalls/
-----------------------------------------
-a always,exit -F arch=b64 -S exit,exit_group -F uid!=1001 -F pid!=446 -F pid!=22 -F pid!=448 -F pid!=1521 -F ppid!=446 -F ppid!=22 -F ppid!=448 -F ppid!=1521
-a always,exit -F arch=b64 -S read,write,open,close,mmap,mprotect,pread,pwrite,readv,writev,pipe,dup,dup2,socketpair,clone,fork,vfork,execve,fcntl,truncate,ftruncate,rename,creat,link,unlink,symlink,chmod,fchmod,setuid,setgid,setreuid,setregid,mknod,init_module,openat,mknodat,unlinkat,renameat,linkat,symlinkat,fchmodat,splice,tee,vmsplice,dup3,pipe2,preadv,pwritev,finit_module -F uid!=1001 -F success=1 -F pid!=446 -F pid!=22 -F pid!=448 -F pid!=1521 -F ppid!=446 -F ppid!=22 -F ppid!=448 -F ppid!=1521



sudo auditctl -l
-a always,exit -F arch=b32 -S stime,settimeofday,adjtimex -F key=time-change
-a always,exit -F arch=b64 -S adjtimex,settimeofday -F key=time-change
-a always,exit -F arch=b32 -S clock_settime -F a0=0x0 -F key=time-change
-a always,exit -F arch=b64 -S clock_settime -F a0=0x0 -F key=time-change
-w /etc/localtime -p wa -k time-change
-w /etc/group -p wa -k identity
-w /etc/passwd -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/security/opasswd -p wa -k identity
-a always,exit -F arch=b32 -S sethostname,setdomainname -F key=system-locale
-a always,exit -F arch=b64 -S sethostname,setdomainname -F key=system-locale
-w /etc/issue -p wa -k system-locale
-w /etc/issue.net -p wa -k system-locale
-w /etc/hosts -p wa -k system-locale
-w /etc/hostname -p wa -k system-locale
-w /etc/NetworkManager/ -p wa -k system-locale
-w /etc/selinux/ -p wa -k MAC-policy
-a always,exit -F arch=b32 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=-1 -F key=perm_mod
-a always,exit -F arch=b64 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=-1 -F key=perm_mod
-a always,exit -F arch=b32 -S lchown,fchown,chown,fchownat -F auid>=1000 -F auid!=-1 -F key=perm_mod
-a always,exit -F arch=b64 -S chown,fchown,lchown,fchownat -F auid>=1000 -F auid!=-1 -F key=perm_mod
-a always,exit -F arch=b32 -S setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr -F auid>=1000 -F auid!=-1 -F key=perm_mod
-a always,exit -F arch=b64 -S setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr -F auid>=1000 -F auid!=-1 -F key=perm_mod
-a always,exit -F arch=b32 -S open,creat,truncate,ftruncate,openat,open_by_handle_at -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b32 -S open,creat,truncate,ftruncate,openat,open_by_handle_at -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b64 -S open,truncate,ftruncate,creat,openat,open_by_handle_at -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b64 -S open,truncate,ftruncate,creat,openat,open_by_handle_at -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b32 -S mount -F auid>=1000 -F auid!=-1 -F key=export
-a always,exit -F arch=b64 -S mount -F auid>=1000 -F auid!=-1 -F key=export
-a always,exit -F arch=b32 -S unlink,rename,unlinkat,renameat -F auid>=1000 -F auid!=-1 -F key=delete
-a always,exit -F arch=b64 -S rename,unlink,unlinkat,renameat -F auid>=1000 -F auid!=-1 -F key=delete
-w /etc/sudoers -p wa -k actions
-w /etc/sudoers.d -p wa -k actions
-w /usr/bin/docker -p rwxa -k docker-daemon
-a always,exit -F arch=b32 -S clone -F a0&0x7C020000 -F key=container-create
-a always,exit -F arch=b64 -S clone -F a0&0x7C020000 -F key=container-create
-a always,exit -F arch=b32 -S unshare,setns -F key=container-config
-a always,exit -F arch=b64 -S unshare,setns -F key=container-config
-w /sbin/kmod -p x -k modules
-w /sbin/insmod -p x -k modules
-w /sbin/rmmod -p x -k modules
-w /sbin/modprobe -p x -k modules
-a always,exit -F arch=b32 -S init_module,finit_module -F key=module-load
-a always,exit -F arch=b64 -S init_module,finit_module -F key=module-load
-a always,exit -F arch=b32 -S delete_module -F key=module-unload
-a always,exit -F arch=b64 -S delete_module -F key=module-unload
-a always,exit -F arch=b32 -S socket,connect,sendmsg,recvmsg,bind,listen,setsockopt -F key=network-access
-a always,exit -F arch=b64 -S socket,connect,accept,sendmsg,recvmsg,bind,listen,setsockopt -F key=network-access



WORKLOAD - Using Awesome Docker
Need to install Docker Compose
----------------------------------------
git clone https://github.com/docker/awesome-compose


AUDTI RULES
------------------------------------------
sudo cp ./rules/10-base-config.rules /etc/audit/rules.d/.
sudo cp ./rules/30-stig.rules /etc/audit/rules.d/.
sudo cp ./rules/31-privileged.rules /etc/audit/rules.d/.
sudo cp ./rules/33-docker.rules /etc/audit/rules.d/.
sudo cp ./rules/41-containers.rules /etc/audit/rules.d/.
sudo cp ./rules/43-module-load.rules /etc/audit/rules.d/.
sudo cp ./rules/71-networking.rules /etc/audit/rules.d/.
sudo cp ./rules/99-finalize.rules /etc/audit/rules.d/.

sudo augenrules --load
sudo service auditd start






QUESTION: Is the Umbrella 32 or 64, how much RAM, disk space?
pi@umbrella-f13cded2:~ $ df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root       6.9G  2.9G  3.9G  43% /
devtmpfs        431M     0  431M   0% /dev
tmpfs           463M     0  463M   0% /dev/shm
tmpfs           463M   30M  434M   7% /run
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           463M     0  463M   0% /sys/fs/cgroup
tmpfs           463M     0  463M   0% /var/spool
tmpfs           463M   12K  463M   1% /tmp
tmpfs           463M     0  463M   0% /var/tmp
tmpfs           463M   64K  463M   1% /var/log
/dev/mmcblk0p4   20G  424M   19G   3% /storage
tmpfs           463M     0  463M   0% /storage/docker/containers
/dev/mmcblk0p1  253M   57M  196M  23% /boot
tmpfs            93M     0   93M   0% /run/user/1000
pi@umbrella-f13cded2:~ $ uname -a
Linux umbrella-f13cded2 4.19.95-v7-umbrella1+ #1 SMP Fri Jan 17 17:06:24 GMT 2020 armv7l GNU/Linux
pi@umbrella-f13cded2:~ $ uname -m
armv7l
pi@umbrella-f13cded2:~ $ getconf LONG_BIT
32
pi@umbrella-f13cded2:~ $ grep flags /proc/cpuinfo
pi@umbrella-f13cded2:~ $ grep -o -w 'lm' /proc/cpuinfo | sort -u
pi@umbrella-f13cded2:~ $ lshw
-bash: lshw: command not found
pi@umbrella-f13cded2:~ $ sudo lshw
sudo: lshw: command not found
pi@umbrella-f13cded2:~ $ cpuinfo
-bash: cpuinfo: command not found
pi@umbrella-f13cded2:~ $ kubectl version
INFO[0000] Acquiring lock file /home/pi/.rancher/k3s/data/.lock
INFO[0000] Preparing data dir /home/pi/.rancher/k3s/data/dbc2e6d7033af4ef9e5ac86160bce1ddd714e67c3df2434cf8be1d56fed1e783

Client Version: version.Info{Major:"1", Minor:"19", GitVersion:"v1.19.5+k3s2", GitCommit:"746cf4031370f443bf1230272bc79f2f72de2869", GitTreeState:"clean", BuildDate:"2020-12-18T01:42:07Z", GoVersion:"go1.15.5", Compiler:"gc", Platform:"linux/arm"}
The connection to the server localhost:8080 was refused - did you specify the right host or port?
pi@umbrella-f13cded2:~ $
pi@umbrella-f13cded2:~ $ git --version
git version 2.20.1
pi@umbrella-f13cded2:~ $ free -m
              total        used        free      shared  buff/cache   available
Mem:            925         116          98          29         710         718
Swap:             0           0           0




scp canon_script.py pi@192.168.1.102:/home/pi
scp -p pi@192.168.1.102:/storage/logs/audit/audit.log .

scp -rp rules/ pi@192.168.1.102:/home/pi


Umbrella
-------------------
Docker Compose requires python3, Umbrella has python2 (does have python3)

First install python3 (I did not do, used apt install docker-compose)
sudo apt install python3

Then install Docker Compose with pip3
sudo pip3 install docker-compose

Most templates did not work, but following do on Umbrella
apache-php
react-rust-postgres



DevOps Repo Synergia Git Credentials
============================
jp16127
dkq4ktwaoanff7rxgufnfkmiaqgp6jiqnoaauk5pzq7xcpg7qchq

Just use
git clone https://toshiba-bril@dev.azure.com/toshiba-bril/Synergia/_git/Synergia
(asks for password and seemed to work, not sure how it knew my username)

Tried but did not work
git clone https://jp16127@toshiba-bril@dev.azure.com/toshiba-bril/Synergia/_git/Synergia


DevOps Repo WP1 Git Credentials
============================
username: jp16127
password: wjluxucx2lkjdm7zrnyz2dicm5evbi42x4lltgff65cu4xwiebqa
https://toshiba-bril@dev.azure.com/toshiba-bril/Synergia/_git/WP1


Bo:     container key to separate container activity
Pietro: ppid containers creating other containers
Dan:    container escape investigation (Vijay)
        does audit capture
Ioannis/Pietro: meta, cpu, log "top" data
Pietro: data drift
Franc:  how to label, time segment


Public/Private (asymmetric)  encrypt, with PKI solves key distribution
---------------------------------------------
Finite Field (Abstract Algebra)
RSA:  NSA/GCHQ -> 4096 bits    1000-10000
ECC:  368 bits                 500-1500


Symmetric (AES) encrypt, bad at key distribution
---------------------------------------------
128 bits                       Fast/Hardware


Hybrid (use asymmetric for key exchange, use symmetric for bulk enc)
SSL/TLS

     n*(n-1)*(n-2)!    n*(n-1)
nC2 = ------------  = --------
      2! * (n-2)!        2

n*(n-1)
-------
   2

REQUIRES ATTACKER One-Time Pad, Optimal Approach


SESSION KEY ONLY ONCE PER SECOND     10000  ~ 3 Hours
msg 01001001010001110100011100101010 plaintext
key 1010010110 1010010110 1010010110 session key
XOR -------------------------------- encrypt
    11101100101010101010101010101100 ciphertext

    11101100101010101010101010101100 ciphertext
key 1010010110 1010010110 1010010110 session key
XOR --------------------------------
msg 01001001010001110100011100101010 plaintext


Mike: Random 24 hours, pick random 1, 5, 24.




MASTER KEY USED ONLY ONCE PER DAY    1000  ~3 years
msg 01001001010001110100011100101010 plaintext
key 1010010110 1010010110 1010010110 master key
XOR -------------------------------- encrypt
    11101100101010101010101010101100 ciphertext



2013 ECC DH using MSP430 16-bit 20MHz Processor

2021 ECC DH using ARMv7(M3)???    30 seconds for key exchange


Research Idea: Authentication: Use master Key for "Authentication"
               Key Exchange: How do we exchange session keys
               ---------------------------------------------
               Key Transport:  Use master key to exchange session key
                               No Perfect Forward Secrecy

               Key Agreement:  Use ECC DH ARMv7 200MHz processor ???
                               faster than 2013
                               SLOW (see 2013)
                               Perfect Forward Secrecy


Symmetric (encrypt/decrypt) really fast
-----------------
100 of algorithms (AES)

Pu/Pr Asymmetric (encrypt/decrypt) really slow
----------------
RSA      attacks sq root, index calculus   2^4096   2^128   BF: 2^80
DH - DLP attacks sq root, index calculus   2^4096   2^128   BF: 2^80
     ECC attacks sq root                   2^160    2^80    BF: 2^80







Key Transport
Random Ks for AES
ALICE                                       BOB
-----                                       --------
y = B_Pu(Ks)
   encrypt 16    ------------------->       B_Pr(y) = Ks


AES_Ks(m1)       ------------------->      AES_Ks(m1) = m1

AES_Ks(m2)       ------------------->      AES_Ks(m1) = m1

AES_Ks(m3)       ------------------->      AES_Ks(m1) = m1

AES_Ks(m4)       ------------------->      AES_Ks(m1) = m1

AES_Ks(m5)       ------------------->      AES_Ks(m1) = m1

AES_Ks(m6)       ------------------->      AES_Ks(m1) = m1

AES_Ks(m7)       ------------------->      AES_Ks(m1) = m1



nRF52840 Dongle Nordic Semiconductor Bluetooth USB 2.0 Wireless Adapter
