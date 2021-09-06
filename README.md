<h1 align="center">
  <a href="https://github.com/jpope8/container-escape-dataset">
    <!-- Please provide path to your logo here -->
    <img src="docs/images/data-collection.png" alt="Logo" width="550" height="250">
  </a>
</h1>

<div align="center">
  Auditd Dataset for Container Escape.
  <br />
  <a href="#basic-usage"><strong>Usage</strong></a> | <a href="#citing"><strong>Citing</strong></a>
  <br />
  <!--
  <br />
  <a href="https://github.com/jpope8/container-escape-dataset/issues/new?assignees=&labels=bug&template=01_BUG_REPORT.md&title=bug%3A+">Report a Bug</a>
  ·
  <a href="https://github.com/jpope8/container-escape-dataset/issues/new?assignees=&labels=enhancement&template=02_FEATURE_REQUEST.md&title=feat%3A+">Request a Feature</a>
  .
  <a href="https://github.com/jpope8/container-escape-dataset/issues/new?assignees=&labels=question&template=04_SUPPORT_QUESTION.md&title=support%3A+">Ask a Question</a>
  -->
</div>

<div align="center">
<br />

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg?style=flat-square)](https://github.com/jpope8/container-escape-dataset/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
[![code with hearth by jpope8](https://img.shields.io/badge/%3C%2F%3E%20with%20%E2%99%A5%20by-jpope8-ff1414.svg?style=flat-square)](https://github.com/jpope8)

</div>

# UNDER CONSTRUCTION

## Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Dependencies](#dependencies)
- [Running](#Running)
- [Citing](#citing)
- [License](#license)


---


## Introduction
Dataset from Linux Raspian VMs and devices with auditd logs capturing various container escape and attacks.



## Installation
### Docker Configuration
Docker was installed using the standard Linux instructions.

The post-installation instruction to manage docker without sudo.
 
[https://docs.docker.com/engine/install/linux-postinstall/]

A common networking problem can occur when running a docker container in a virtual machine.  The host can access the network (via NAT) but any container network access fails.  Specifically, running 'apt-get update' fails with 'Could not resolve 'archive.ubuntu.com'.

 
### Docker-Compose Configuration

Docker compose was also installed using the standard instructions.

[https://docs.docker.com/compose/install/]

Then awesome-docker was checked out using git.

[https://github.com/docker/awesome-compose]



## Running

To run the container escape scenario, first checkout the code using a git client.

> git clone https://github.com/jpope8/container-escape-dataset.git

Change to the top of the src directory (should have been create during git clone) and run ant to create the fedex.jar file.

> ```bash
> cd ./container-escape-dataset/src
> python experiment 5 /home/pi/logs A
> ```

Buena Suerte.



## Citing

Regarding the framework and dataset, please cite the following.

    @inproceedings{TBD,
      author = {Pope, James},
      title = {Dataset: Auditd data for Container Escape on Edge Devices},
      year = {2021}
    }

## References
> - [1] Pope, J. and Terwilliger, M. (2021) [Seam Carving for Image Classification Privacy](https://www.scitepress.org/PublicationsDetail.aspx?ID=H8zqc3KCMlw=&t=1) In Proceedings of the 10th International Conference on Pattern Recognition Applications and Methods - ICPRAM, ISBN 978-989-758-486-2; ISSN 2184-4313, pages 268-274. DOI: 10.5220/0010249702680274.
> - [2] Avidan, Shai and Shamir, Ariel. (July 2007) [Seam Carving for Content-Aware Image Resizing](https://dl.acm.org/doi/10.1145/1276377.1276390). ACM Transactions on Graphics, Volume 26, Issue 3.



## License

This project is licensed under the **MIT License**.

See [LICENSE](LICENSE) for more information.


