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


