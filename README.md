# HyperLogLog-Cardinality-Manipulation
An algorithm (and all its supporting scripts) designed to manipulate HLL's cardinality estimation

## Setup
In order to execute the scripts inside the repository, the users needs to set-up a Redis server. This tutorial will demonstrate how to set it up locally inside a Virtual Machine.

First and foremost, the user need to install a Debian-based Linux distribution as a VM in his prefered system:
* In a Windows system, it is as easy as installing an Ubuntu VM through the [Windows Store](https://www.microsoft.com/en-us/p/ubuntu/9nblggh4msv6#activetab=pivot:overviewtab).
* In a Mac system, follow any general tutorial about installing an Ubuntu VM, like [this one](https://www.instructables.com/id/How-to-Create-an-Ubuntu-Virtual-Machine-with-Virtu/).

Once in the Ubuntu VM, [Redis](https://redis.io/) can be installed following this procedure:
```bash
sudo apt update
sudo apt install redis-server
```

Once Redis is installed, the only thing needed for set-up is having Python 3 [installed](https://www.python.org/downloads/) in order to be able to execute the scripts.

## Execution
All the elements in this repository are simple Python3 scripts that can be executed in any manner that the user prefers. The only extra requisite to execute them is having the Redis service running. This can be done by accesing the Ubuntu VM, which must be up at all time, and executing the following commands:
```bash
sudo service redis-server restart
redis-cli
```
