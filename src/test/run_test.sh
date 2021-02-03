#!/bin/sh



for i in `seq 6` 
do python ./client_fake.py & python ./client_fake.py & python ./client_fake.py
done