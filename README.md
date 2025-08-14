
# Standalone VME-based DAQ

A lightweight C++ based Data Acquisition (DAQ) program for VME crates.

---

## Installation

### 1. Install prerequisites
Ensure that ROOT and CMake are installed on your system:

    sudo yum install epel-release
    sudo yum install cmake root

---

### 2. Install VME drivers
Run the provided driver installation script:

    chmod 755 install_drivers.sh
    ./install_drivers.sh

---

### 3. Install the DAQ software
Run the DAQ installation script:

    chmod 755 install_daq.sh
    ./install_daq.sh

---

## Running the DAQ

1. Navigate to the run directory `cd run`

2. Edit the DAQ configuration:
   Open `daq.ini` and set:
   - VME bridge address
   - TDC addresses
   - Number of triggers

3. Enable run mode: ensure the file `runfile` contains `RUN`

4. Start the DAQ:

        ../daq/bin/daq daq.ini N

   where N = run number (increment manually for each new run).

5. Stopping the run:
   - Automatic: The run stops when the configured number of triggers is reached.
   - Manual: Set the content of `runfile` to `STOP`.


6. Output: the data is saved in `output_run_N.root`.



## Quick Start

    sudo yum install epel-release cmake root
    chmod 755 install_drivers.sh && ./install_drivers.sh
    chmod 755 install_daq.sh && ./install_daq.sh
    cd run
    # Edit daq.ini as needed
    echo RUN > runfile
    ../daq/bin daq.ini 1


