# influxdb/Grafana Setup on BetDot

Instructions on installation and configuration of influxdb and Grafana docker containers on BetDot.
Assume that the docker service is already installed.

All related files are located at:
> `BetDot/influxdb`

##  Installation

The influxdb will be installed on device whereas both will be installed on server. Both can be started with docker-compose. 

Download and install influxdb stable versio 1.8:
> ` docker pull influxdb:1.8`

Download and install Grafana stable versio 6.7.3:
> ` docker pull grafana/grafana:6.7.3`

Download and install docker-compose: 
> `sudo apt install docker-compose`

##  Configuration

#### On device : 
Configure the influxdb by following steps:
- compose `docker-compose.yml` file  
- modifying the default `influxdb.conf` file
- TLS related files: `influxdb.key` and `influxdb.pem`
- create a folder `data` for influxdb persistence.

File structure:
>
     - /opt/influx/docker-compose.yml
     - /opt/influx/influxdb/influxdb.conf
     - /opt/influx/influxdb/data
     - /opt/influx/influxdb/ssl/influxdb.pem
     - /opt/influx/influxdb/ssl/influxdb.key
     
To reduce redundant logging, set `[http]` `log-enabled = false`

The docker container name is specified as `influxdb` in the `docker-compose.yml` file along with port mappings and TLS parameters.

#### On server : 
Configure the influxdb and Grafana by following steps:
- compose `docker-compose-server.yml` file  
- modifying the default `influxdb.conf` file
- TLS related files: `influxdb.key` and `influxdb.pem`
- create a folder `influxdb/data` for influxdb persistence.
- create a folder `grafana/data` for grafana persistence.

Assume the files are installed under `${WPD}:`

>
     - ${WPD}/influx/docker-compose-server.yml
     - ${WPD}/influx/influxdb/influxdb.conf
     - ${WPD}/influx/influxdb/data
     - ${WPD}/influx/influxdb/ssl/influxdb.pem
     - ${WPD}/influx/influxdb/ssl/influxdb.key

     - ${WPD}/grafana/data
     
To reduce redundant logging, set `[http]` `log-enabled = false`

The docker container name of influxdb is specified as **influxdb** in the `docker-compose-server.yml` file along with port mappings and TLS parameters.

The docker container name of Grafana is specified as **grafana** 

##  Usage

#### On device : 
To start the influxdb container, do:
> cd `/opt/influx`
> `docker-compose up -d`

#### On server : 
To start the influxdb and the Grafana containers, do:
> cd `${WPD}/influx`
> `docker-compose up -d -f docker-compose-server.yml`

Note that the startup command only needs to be run once, the container(s) will automatically restart on reboot or failure, unless be stopped by:
> `docker-compose down`

##  References
- influxdb on docker hub: [influxdb](https://hub.docker.com/_/influxdb)

- Grafana o Github: [grafana](https://github.com/grafana/grafana)
