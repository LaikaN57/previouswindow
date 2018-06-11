#!/bin/bash

#rm -f pwKeyPair.*
#ssh-add -L
#ssh-add -D

openssl genrsa -out pwKeyPair.pem
chmod 0400 pwKeyPair.pem
#openssl rsa -in pwKeyPair.pem -pubout -out pwKeyPair.pub
ssh-keygen -y -f pwKeyPair.pem > pwKeyPair.pub
ssh-add pwKeyPair.pem

python3 ./previouswindow.py

echo 'Please use the following commnad to connect to instances:'
echo 'ssh -A ec2-user@<IP>'
