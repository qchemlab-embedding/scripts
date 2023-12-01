This directory contains example PyADF scripts.

Scripts are tested on the Ares PlGrid cluster, with PyADF commit `#f0d7a96e90db32e65994ea07079665bcf542824a`

# Notes, advice, to-do

- please do not commit large binary files (such as tape files from pyadf runs using ADF); one simple way to it is to use `.gitignore` file in your git repository.

  -  example content of `.gitignore` file:

    ```
    *crashed*
    __pycache__
    error.err
    output.out
    ```

  - remember to commit your `.gitgnore` file:

    ```
    git add .gitignore
    git commit -m "added a .gitignore file"
    git push
    ```

  Another way (and a good `Git` practice) is to never do `git add .`, but to manually decide on the files that should be added, i.e., `git add FILE1 FILE2`

