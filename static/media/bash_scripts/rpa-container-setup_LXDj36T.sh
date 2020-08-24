#!/bin/bash

##BEGIN SETUP OF Kali##
docker pull kalilinux/kali-rolling
docker volume create data
mkdir /home/rpa/clientdata
docker run -dit --network=host --mount source=data,target=/home/rpa/clientdata --hostname rpa-ctek --name rpa kalilinux/kali-rolling
sleep 5
docker update --restart=always rpa
#installing tools
docker exec rpa bash -c 'apt-get update; apt-get -y dist-upgrade; apt-get -y autoremove; apt-get clean'
docker exec rpa bash -c 'apt-get -y install nmap exploitdb man-db dirb nikto wpscan uniscan screen responder metasploit-framework'
docker exec rpa bash -c 'service postgresql start; msfdb init; service postgresql stop'
echo ""
echo "Done!"
exit