#!/bin/bash

ROOTDIR=$(pwd)

echo "Install CAEN USB driver"
cd $ROOTDIR
cd drivers/CAENUSBdrvB-1.5.1
make clean
make -j ${nproc}
sudo make install


echo "Install CAEN VME library"
cd $ROOTDIR
cd drivers/CAENVMELib-2.50/lib
sudo sh install_x64

echo "Done"