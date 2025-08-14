#!/bin/bash

ROOTDIR=$(pwd)

echo "Install DAQ"
cd $ROOTDIR
cd daq
rm -rf build
mkdir build
cd build
cmake ..
make -j ${nproc}
make install

cd $ROOTDIR


echo "Done"