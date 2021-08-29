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

## Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Dependencies](#dependencies)
- [Threading](#threading)
- [Compiling and Running](#compiling-and-running)
- [Citing](#citing)
- [License](#license)


---


## Introduction
The Coach Tool facilitates using machine learning (ML) approaches for analyzing documents in a supplier’s teardown.  There are two main phases – the training phase and the production phase.

The training phase is when a human interacts with a supplier’s documents to annotate the orientation and document type for a supervised machine learning classifier.  The phase also includes keyword search and table detection tasks where the user can specify options.  Of course, these first require the documents to be OCR’ed.

The production phase is when an executable is setup to take a new supplier, read the repository and the user’s settings/training for that supplier, and perform document type detection, OCR, and text and/or table detection accordingly on the new supplier.  Other than setting up for execution and specifying parameters, no human interaction is involved.

The training phase is implemented in the Coach GUI (graphical user interface).  The production phase is implemented in the PipelineApp.  Figure 1 depicts the production phase pipeline where the training phase inputs are shown with the dotted arrows.

Dataset from Linux Raspian VMs and devices with auditd logs capturing various container escape and attacks.


## Installation
### Java

The application is written in Java.  The minimum required version of Java is 1.11.  Though not strictly necessary, the Java Development Kit (JDK) is required to build from source.  Since this may be necessary, it is recommended to install the latest JDK.

> ```bash
> sudo apt install java default-jdk
> ```


### Tesseract OCR
To OCR images, the tool requires with the Tesseract OCR to be installed.  The tool can run without Tesseract installed however the OCR capability will be disabled.  Currently any version of Tesseract after 4.0.0 is sufficient.  To install Tesseract, go to the following website and follow the instructions.

[https://github.com/tesseract-ocr/tesseract]
[https://tesseract-ocr.github.io/tessdoc/Installation.html]


For Ubuntu, recommended to install binaries via aptitude.

> ```bash
> sudo apt install tesseract-ocr
> sudo apt install libtesseract-dev
> ```

### Ant
To compile the Java source files, in addition to the JDK, the ant make utility also needs to be installed.

> ```bash
> sudo apt install ant
> ```

## Dependencies
The software dependencies are mostly internal libraries in the form of jar files in the ./lib directory.  The OCR engine (Tesseract) is also required to OCR images and is the only external software dependency.

> ```bash
> pdfbox-app-2.0.12
> weka-3.9.5
> jfreechart-2.0.0-SNAPSHOT
> ```

### PDF Box
The application needs to be able to read the images within the PDF files located in the repository.

### Weka
The application uses the Weka Machine Learning Library for orientation classification and document type detection.

### JFreeCharts
The application uses JfreeCharts.  Currently only the Hoistogram panel requires JfreeCharts.

### Tesseract OCR
The Java application interfaces with the Tesseract OCR (optical character recognition) library by spawning a process, and calling the command line interface (CLI) with arguments.  The Java application passes the location of an image file (PNG).  Tesseract then OCR’s the image and saves to a text file.  The Java application eventually reads this file to show to the user.


## Threading

### Coach Tool
The tool uses the Swing GUI Library.  Swing is designed to be single-threaded.  The singleton thread used is called the EDT (event dispatching thread), created when the frame is made visible.  The EDT is intended to update the visual components (ultimately pixels in images).  Any computationally intensive work (e.g. preparing an image) should be done on a separate thread and then shared with the EDT to draw the image.  Since there is only one thread to draw, care must be taken not to block this (e.g. blocking IO) thread.  If the EDT is blocked, no updating of the interface is performed and it appears to be locked from the user’s perspective.

Ideally no database or analysis computations would be done on the EDT.  However, this is generally hard to achieve.  Also, many of these computations are very short and do not cause any significant delays in updating the GUI.  Only those database and analysis tasks that take a significant amount of time need to be moved to a different thread. Most of the database and analysis computation does take place on the EDT – this can be noticed, for example, in a function call from a button click to a database routine.  When we do introduce computational threads, the ThreadPool class is used.  The significant functions are identified as follows:

1. Creating Features:  The SupplierPanel.java “Create Features” button uses 4 threads to create the features (this is currently hard coded but better as a configuration for the GUI).  Note that the GUI creates the four instances – one for each orientation.  We first do document type detection followed by orientation detection.  Arguably doing orientation detection first and then document type detection might alleviate having to create features for each orientation.  However, either way, once we have the orientation annotation we can increase the number of annotations by 4:1 (getting annotation data for a little computation is always worth it).  Figure 2 Shows executing “Create Features” with 4 threads.

2. Performing OCR: A document image can take, for instance, over 10 seconds to OCR.  The OCR Engine used (Tesseract) provides a command line argument to specify the number of threads. However, there are significant issues using more than two threads.

See [https://github.com/tesseract-ocr/tesseract/issues/1600]

It does not appear that Tessearct is really capable of multi-threading (presumably they share some common files in the OS).  I have only had "success" when the VM is set to 2 processors and I run a threadpool with 2 threads. Otherwise, it takes longer - even with 4 processors fully utilized.  Perhaps they use spin locks.  Figure 3 shows executing Tesseract with 2 threads.


### PipelineApp
The PipelineApp does use any Swing Components so the EDT is not involved.  Every Java application’s main method is called with a default thread, also known as the “main thread”.  The PipelineApp orchestrates calling the other components from this main thread.  Some components may employ multiple threads and join when completed.  Thus, though the  PipelineApp does not directly create threads, it is effectively multi-threaded. Only one component called from the PipelineApp is multi-threaded and that is the TesseractOCR Engine.


## Compiling and Running

First checkout the code using a git client (typically already installed on Ubuntu Linux systems).

> git clone https://jpope8@bitbucket.org/jpope8/fedex.git 

Change to the top of the fedex directory (should have been create during git clone) and run ant to create the fedex.jar file.

> ```bash
> cd ./fedex
> ant
> ```

The fedex.jar file contains two important programs, the PipelineApp (Command Line Tool) and the CoachMain (GUI Tool). The CoachTool is used to annotate documents for type/orientation detection and to configure keyword search and table detection.  The CoachTool is intended to be used when first deployed and periodically (perhaps once a month) to keep the annotated data up to date with current suppliers/document types.

> ```bash
> cd ./fedex
> java -jar fedex.jar
> ```

The PipelineApp is used during production to constantly run (perhaps every hour or every day).  It uses the annotations to detect the document type/orientation and then search for keywords and/or table detection.  Typical scenario is a configuration that detects and saves tables for a particular supplier’s document.  The table information is stored in a CSV file that can then be inserted into a database.

> ```bash
> cd ./fedex
> java -cp fedex.jar PipelineApp parker2 parker
> ```


Buena Suerte.


## Docker Configuration
Docker was installed using the standard Linux instructions.

The post-installation instruction to manage docker without sudo.
 
https://docs.docker.com/engine/install/linux-postinstall/

A common networking problem can occur when running a docker container in a virtual machine.  The host can access the network (via NAT) but any container network access fails.  Specifically, running 'apt-get update' fails with 'Could not resolve 'archive.ubuntu.com'.

 
## Docker-Compose Configuration

Docker compose was also installed using the standard instructions.

https://docs.docker.com/compose/install/

Then awesome-docker was checked out using git.

https://github.com/docker/awesome-compose

## Container-Escape Experiment Code

Check out 



## Citing

Regarding seam doppelganger, please cite the following.

    @inproceedings{pope2020,
      author = {Pope, James and Terwilliger, Mark and Connell, J.A. (Jim) and Talley, Gabriel and Blozik, Nicholas and Taylor, David},
      title = {Annotating Documents Using Active Learning Methods for a Maintenance Analysis Application},
      year = {2020},
      isbn = {9781450375511},
      publisher = {Association for Computing Machinery},
      address = {New York, NY, USA},
      url = {https://doi.org/10.1145/3430199.3430214},
      doi = {10.1145/3430199.3430214},
      booktitle = {Proceedings of the 2020 3rd International Conference on Artificial Intelligence and Pattern Recognition},
      pages = {35–41},
      numpages = {7},
      keywords = {Active Learning, Document Classification},
      location = {Xiamen, China},
      series = {AIPR 2020}
    }

## References
> - [1] Pope, J. and Terwilliger, M. (2021) [Seam Carving for Image Classification Privacy](https://www.scitepress.org/PublicationsDetail.aspx?ID=H8zqc3KCMlw=&t=1) In Proceedings of the 10th International Conference on Pattern Recognition Applications and Methods - ICPRAM, ISBN 978-989-758-486-2; ISSN 2184-4313, pages 268-274. DOI: 10.5220/0010249702680274.
> - [2] Avidan, Shai and Shamir, Ariel. (July 2007) [Seam Carving for Content-Aware Image Resizing](https://dl.acm.org/doi/10.1145/1276377.1276390). ACM Transactions on Graphics, Volume 26, Issue 3.



## License

This project is licensed under the **MIT License**.

See [LICENSE](LICENSE) for more information.


