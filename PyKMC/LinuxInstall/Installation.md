# Installation for Linux

## Install necessary packages

To begin, ensure that you have the necessary packages installed on your system:

* git
* python 3.9+
* python3-venv (apt) / python-virtualenv (pacman, dnf, yum)
* openmpi (needed for [MPI](https://en.wikipedia.org/wiki/Message_Passing_Interface) functionality)
* gfortran

Check the version of a package:
	
	$ <package_name> --version
	
If any package is missing, install it using your distribution's package manager.

For Debian-based distributions (incl. Ubuntu, Mint):
	
	$ sudo apt install <package_name>

For Arch-based distributions:
	
	$ sudo pacman -S <package_name>
	
For Fedora:

	$ sudo dnf install <package_name>

Other necessary packages should be provided with most Linux distributions by default.

## Clone from the pyKMC repository

Choose where you would like to store the pyKMC files and change directory accordingly. Next, clone the `develop` repository for the most up to date version.

	$ cd ~	
		
Using git, clone the pyKMC package from the GitHub repository.

	$ git clone -b develop https://github.com/hugomoison/pyKMC.git
	
The `-b` command option selects a specific branch of the repository, which in this case is the "develop" branch.
	
You will be prompted to input your GitHub account username, and a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens), assuming one has already been setup.

### Download compressed .zip

As an alternative to cloning the repository, a compressed .zip file for the source files can be downloaded. At the top of the page 

## Create a Python virtual environment

When setting up and running pyKMC, it is best to do so in a [virtual environment](https://www.w3schools.com/python/python_virtualenv.asp).

Use the `venv` module to create a new virtual environment, defining where you would like it to be saved. It is recommended to save it somewhere in the user's home folder.

	$ python3 -m venv /path/to/virtenvs/pyKMC
	
### Activate a virtual environment

A virtual environment can be activated using the following command:

	$ source /path/to/virtenvs/pyKMC/bin/activate
	
The terminal emulator should now resemble this format:

	(pyKMC) user@system:~$
	
When you want to deactivate the virtual environment, simply run the command

	$ deactivate
	
## Install Python dependencies 

Make sure you are in your python virtual environment, and change directories to where your pyKMC source files are.

	$ cd /path/to/pyKMC/
	
Install the necessary python modules.

	$ pip install -e .	# The . tells pip to look for installation config files in the current directory

## Build LAMMPS with traditional make

For additional information, please refer to the [official LAMMPS installation and build docs](https://docs.lammps.org/Install.html).

### Clone from the LAMMPS repository

Choose where you would like to store the LAMMPS package files and change directory accordingly.

	$ cd ~	
		
Using git, clone the LAMMPS package from the official GitHub repository.

	$ git clone -b release https://github.com/lammps/lammps.git
	
### `Make` configuration and compilation
	
Change directories into the new folder's source directory.

	$ cd lammps/src
	
The following `make` commands select the various necessary packages, and subsequently build the LAMMPS binary file.

	$ make yes-basic
	$ make yes-extra-compute
	$ make yes-plugin
	$ make mode=shared mpi -j N
	
The `basic` keyword refers to the preset option that installs the following packages:

* KSPACE
* MANYBODY
* MOLECULE
* RIGID

To show a list of other preset keyword options in addition to individual packages available, execute

	$ make package
	
The same list of LAMMPS packages can also be found on their [doc page](https://docs.lammps.org/Build_package.html).

For compilation, the `-j` command option is available to speed up the process by parallelizing tasks. `N` is the maximum number of parallelized tasks. Generally, half of your processor's available cores is reasonable as long as no other significant process are running in the background.
	
A new binary file called `lmp_mpi` should now be in the `/src` directory. There should also be two shared object files with the file extension `.so` called `liblammps.so` and `liblammps_mpi.so`.

To allow LAMMPS to find both the newly built binary file and shared object files, the LAMMPS source directory must be loaded into both the PATH and LD_LIBRARY_PATH [environment variables](https://www.geeksforgeeks.org/environment-variables-in-linux-unix/).

	$ export PATH=$PATH:/path/to/lammps/src/
	$ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/path/to/lammps/src/
	
To install the python module for LAMMPS, the user must be in a python virtual environment. Follow the steps to create and activate one if it has not been done yet. Once the virtual environment is activated, run the following command in the LAMMPS source directory.

	$ cd ~/path/to/lammps/src
	$ make install-python
	
If the command fails with a permission error, run the command again with `sudo` privileges. 

## Test LAMMPS
	
To test that LAMMPS has been installed properly, attempt to run an example from `lammps/examples/` (some examples require certain packages to be installed and may consequently not run). Using the friction example:

	$ cd /path/to/lammps/examples/friction
	$ mpirun -np 2 lmp_mpi -in in.friction	# run the lammps binary using two processor cores
	
or to run without parallelization,

	$ lmp_mpi -in in.friction

Either command should echo information relevant to the simulation, and generate a file called `log.lammps` in the example directory containing the same echoed information. For more info on running LAMMPS, refer to the [doc page](https://docs.lammps.org/Run_basics.html).

## Install and configure pARTn

For additional information, please refer to the [pARTn installation doc](https://mammasmias.gitlab.io/artn-plugin/sections/Installation.html).

Similar to installing LAMMPS, choose where you want to save the pARTn source files and clone the repository.

	$ cd ~
	$ git clone https://gitlab.com/mammasmias/artn-plugin.git
	
Change directories into the new folder. By having LAMMPS already installed, pARTn can be configured to work with it.

	$ cd /path/to/artn-plugin
	$ ./configure --with-lammps LAMMPS_PATH=/path/to/lammps
	
After running the `configure` command, there should be a command listed to run:

	$ make lmplib
	
As long as there are no errors, some final steps will be listed, but these should have already been satisfied through installing LAMMPS.
	
Finally, the artn-plugin interface directory must be defined in the PYTHONPATH environment variable.

	$ export PYTHONPATH=$PYTHONPATH:/path/to/artn-plugin/interface/
	
## Compiling and configuring IRA

For point set registration (used during event reconstruction), [IRA](https://mammasmias.github.io/IterativeRotationsAssignments/) can be used.

Once again, move to the location where you want to save the IRA source files, and clone the repository.

	$ cd ~
	$ git clone https://github.com/mammasmias/IterativeRotationsAssignments.git
	
Change directories into the new folder's source directory

	$ cd IterativeRotationsAssignments/src
	
Build the source files.

	$ make all
	
Troubleshooting: `/usr/bin/ld: cannot find -llapack: No such file or directory`

Some distributions might not come with the [LAPACK](https://www.netlib.org/lapack/) package by default, so it must be installed manually.

For apt: 

	$ sudo apt install liblapack-dev
	
For pacman:

	$ sudo pacman -S lapack
	
For dnf:

	$ sudo dnf install lapack
	
After compilation has finished, add the interface path to the PYTHONPATH environment variable.

	$ export PYTHONPATH=$PYTHONPATH:/path/to/IRA/interface/
	
## Extra: Edit `.bashrc` to automatically define environment variables

On system reboot, any environment variables previously defined are erased. The user's [`.bashrc`](https://www.marquette.edu/high-performance-computing/bashrc.php) file is run every time a new terminal emulator window is opened. Using your preffered text editor, add the `export` commands previously used to define PATH, LD_LIBRARY_PATH, and PYTHONPATH at the end of the file.

	~/.bashrc
	---------
	...
	
	export PATH=$PATH:/path/to/lammps/src
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/path/to/lammps/src
	export PYTHONPATH=$PYTHONPATH:/path/to/artn-plugin/:/path/to/IRA/interface/

