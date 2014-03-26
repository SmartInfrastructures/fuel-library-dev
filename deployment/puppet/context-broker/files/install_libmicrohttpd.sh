#!/bin/bash
cd /home/context-broker/libmicrohttpd-0.9.16/
./configure
make
make install
ln -s /usr/local/lib/libmicrohttpd.so.10 /usr/lib/libmicrohttpd.so.10
