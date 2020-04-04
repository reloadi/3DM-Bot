#!/bin/bash

wget -q -P /home/pi/3dmeltdown/currency http://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip /tmp
unzip -o -q /home/pi/3dmeltdown/currency/eurofxref.zip -d /home/pi/3dmeltdown/currency/
rm -f /home/pi/3dmeltdown/currency/eurofxref.zip
