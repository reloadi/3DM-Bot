#!/bin/bash

wget -q -P /home/ec2-user/3DM-Bot/currency http://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip /tmp
unzip -o -q /home/ec2-user/3DM-Bot/currency/eurofxref.zip -d /home/ec2-user/3DM-Bot/currency/
rm -f /home/ec2-user/3DM-Bot/currency/eurofxref.zip
