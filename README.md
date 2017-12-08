# Identification of CAR-T targets for AML

## What is `tetrad`?
Tetrad is a python package for the scoring and identification of  combinations of four antigens (tetrads) which obey particular boolean relationships  as candidate immunotherapies for acute myeloid leukemia.  


## Installation and use 
### Prerequisites
    - Python 3.6
    - `pipenv` (optional but strongly recommended)

### Installation
    On linux and mac:
    ```
    make dev-install
    ```
    On windows:
    ```
    pipenv install --dev
    pipenv install -e .
    pipenv shell
    ```

#### Tests
    On linux and mac: 
    ```
    make test
    ```
    On windows:
    ```
    pytest .
    ```
## Credits 
This package was developed as the final project for the Fall 2017 semester of BE562, Computational Biology, at Boston University's College of Engineering. 

### Team members: 
    - Graham Voysey (gvoysey@bu.edu)
    - Kat Elkind (kelkind@bu.edu)
    - Kestutis Subacius (kestas@bu.edu)
    - Rachel Petherbridge (rpether@bu.edu)