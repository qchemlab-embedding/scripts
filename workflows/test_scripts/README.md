# About

Scripts in this directory could serve as suggestions/starting points for the development of multi-step workflows for our projects.
Some ideas for workflows that would be useful for the project are in `../notes/worflow.pdf`.


Prerequisities and assumptions:

* in the notes below, we assume working on a project "project-name"
* a project has its own Git repository
* within one project, we work with multiple molecules
* to see this workflow in action, check `tests` directory


# Workflow description

1. [LOCAL] prepare molecules locally

* create a project directory "project-name" and cd to this directory
* initiate Git repository
* create a directory `coordinates`; add files with molecular geometry to this directory
* adapt and run `select.sh` script:

  ```
  cp scripts/select.sh .
  # adapt select.sh
  ./select.sh
  ```

* add all to repository

  ```
  cd explorations
  git add .
  git commit -m "add all files with molecular geometries needed for running calculations"
  git push -u origin
  cd ..
  ```

2. [HPC] prepare inputs, run scripts, and run all calculations

* prepare a directory for running jobs and git pull your project; then

  ```
  cd project-name
  cp ../scripts/clusters/prep_hpc.sh .
  # adapt prep_hpc.sh
  ./prep_hpc.sh
  ```
  
* run calculations one by one, or batch using:

  ```
  cp ../scripts/clusters/runmany.sh .
  # adapt runmany.sh
  ./runmany.sh
  ```

3. [LOCAL] locally: sync data and prepare for analysis

  ```
  cd explorations
  cp ../scripts/scripts_syncing_data/* .
  # modify `rsync.sh`, `README.md`, `exclude.txt`
  ./rsync.sh 
  ```

- once you have all the data, prepare local directories for analysis:

  ```
  cp ../scripts/local/prep_local.sh  .
  # adapt prep_local.sh 
  ./prep_local.sh 
  ```

- analyze [TODO]
- write a description/documentation (e.g., in `docs`) [TODO]
- add all relevant files to Git repository [TODO]



