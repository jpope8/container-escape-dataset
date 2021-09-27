# Data Sets

## Introduction
The datasets are contained in the zip files.

Each zip file contains 32 denial of service (dos) and 32 privilege escalation (privesc) experiments.   Each experiment ran for 15 minutes with the following background containers.  During the experiment, either a dos or privesc attack is randomly launched from a container.  The time is written to the associated annotation file.  In summary, each experiment runs four containers.

* Prometheus
* Graphana
* Internet of Things (iot)
* Denial of service OR Privilege Escape

The prometheus and graphana containers are from the awesome-compose project.  The Internet of Things container was developed and communicates with 3 remote nRF endpoints.  The endpoints are taking temperature sensor readings once every five seconds and sending to the iot container over UDP.

The naming of the zip files encapsulates the edge device and number of experiments contained.  The naming also includes which environment the experiments were conducted (there are two setups, so either environment 1 or 2).
