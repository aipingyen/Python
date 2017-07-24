#!/bin/sh
sudo -H apt -y install python3-pip
sudo -H pip3 install --upgrade pip
sudo -H apt-get -y install sasl2-bin
sudo -H apt-get -y install libsasl2-dev
sudo -H pip3 install pyhive[hive]
sudo apt -y install git
git clone https://github.com/cloudera/thrift_sasl.git
cd thrift_sasl
sudo python3 setup.py install
cd ..
sudo rm -rf thrift_sasl

