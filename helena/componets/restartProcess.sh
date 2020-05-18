#!/bin/bash

sudo systemctl stop influxshake
sudo systemctl stop helena
sleep 2
sudo systemctl start influxshake
sleep 2
sudo systemctl start helena
