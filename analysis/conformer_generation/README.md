# Description

This directory contains various scripts and examples demonstrating how one can generate and optimize molecular structures using:

* RDKit library
* Balloon software

Literature to look at:



# Protocol

## Prepare your environment:

All scripts demonstrated here use `conda` environment - please see the "Technicalities" section below.

## Working with RDKit:

This example demonstrates how to generate conformers of a complex of a simple macrocycle with 1 water molecule using RDKit.
It assumes that initial structures of that complex are available;
here, we start from two viable initial structures (H2O molecule is either "in" or "out" the macrocycle ring), which we store in `coordinates` directory.

* run RDKit:

  ```
  cp scripts/run_rdkit.sh .
  ./run_rdkit.sh
  ```

  this will generate sdf files (in the `scratch` directory) containing all generated conformers

* to parse this file, you can use the script:

  ```
  cp scripts/parse.sh .
  ./parse.sh
  ```

  this will generate directories (here, `results_starting_from_m1_h2o_in` and `results_starting_from_m1_h2o_out`) with files containing conformer geometries and a summary of their energies.


* visualize results;
  this is demonstrated in a jupyter notebook, to run it, please follow

  ```
  jupyter notebook analysis.ipynb
  ```

# Technicalities

How to prepare a working environment using conda (https://docs.conda.io/projects/conda/en/stable/)

  * install Anaconda on your computer: https://docs.anaconda.com/free/anaconda/install/
  * create conda environment from the attached `environment.yml` file:

    ```
    conda env create --prefix ./env --file environment.yml
    ```

  * activate this environment (follow the instructions in the terminal)

  * all our group scripts assume work in this environment (this ensures we all use the same libraries and their versions)

Tips:

  * if you want to run a jupyter notebook, then (in the terminal with activated conda environment) run:

  ```
  jupyter notebook analysis.ipynb
  ```

  * if you are asked for the code or password (there is no), then follow the instructions from the terminal;
    there should be a link to a website (someting similar to: http://localhost:8888/notebooks/analysis.ipynb);
    open this link in your browser.

  * if the code is not executed automatically, click on "Run" -> "Run All Cells"


## Resources

* if you want to learn more about conda, check https://carpentries-incubator.github.io/introduction-to-conda-for-data-scientists/
* if you want to learn more about jupyter notebooks, check:
* if you like other notebooks, then please use what you like; some popular alternatives are:





