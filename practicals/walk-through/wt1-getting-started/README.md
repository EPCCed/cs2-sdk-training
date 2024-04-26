# Walk Through 1: Getting started

The aim of this walk-through is to demonstrate the basic file layout for a CS-2 program, and to ensure that the environment is set up correctly.

A typical CS-2 program involves a few files:

* [layout.csl](layout.csl) which defines the program layout
* [pe_program.csl](pe_program.csl) which defines the code assigned to the processing element (PE)
* [run.py](run.py) the host code in python, which drives the CS-2 device, and manages data transfer to and from the device.

An optional [commands.sh](commands.sh) file demonstrates the commands required to compile and run the program.

## Compiling

`cslc` is the compiler to convert CSL into device executable. In [commands.sh](commands.sh), we can see this is invoked with:

``` bash
cslc layout.csl --fabric-dims=8,3 --fabric-offsets=4,1 --memcpy --channels=1 -o out
```

The meaning of the fllowing flags are:

* `--fabric-dims=8,3` defines the size of the simulated fabric, which is 8 x 3
* `--fabric-offsets=4,1` defines where the program is placed on the fabric.
* `--memcpy` this flag is required to enable memcpy within the host program (covered in a later exercise)
*  `--channels=1` determines the max throughput for transferring data on and off the wafer. (covered in a later exercise)
* `-o out` is the directory where the executables will be saved
  
## Running on the simulator

To run the host code on the simulator, we use

``` bash
 cs_python run.py --name out
```

where we specified the location of the device executable.

## Moving from simulator to the CS-2 system

The previous commands allow us to compile and run the program using the fabric simulator. In order to run on a real Cerebras CS-2 system, the following modifications have to be made:

1. The `fabric-dims` setting in the compile command must be replaced with the fabric dimension of the actual CS-2, 757 x 996. So the new compile command becomes:

    ``` bash
    cslc layout.csl --fabric-dims=757,996 --fabric-offsets=4,1 --memcpy --channels=1 -o out
    ```

1. The IP address of the Cerebras system (`$CS_IP_ADDR`) needs to be passed to the Host program SdkRuntime via `cmaddr`. So the new run command becomes:

    ``` bash
    cs_python run.py --name out --cmaddr $CS_IP_ADDR:9000
    ```

For running the SDK on a Wafer-Scale Clusters in appliance mode (e.g. at EPCC), some additional changes is required. For details on the required changes, see https://sdk.cerebras.net/appliance-mode. For information about setting up the virtual environment, see https://docs.cerebras.net/en/latest/wsc/getting-started/setup-environment.html and https://epcced.github.io/eidf-docs/services/cs2/run/ . 