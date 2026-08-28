---
title: "Conda environments"
linkTitle: "conda envs"
weight: 1
tags: ["python", "conda", "programming"]
author: Fernanda L. Ribeiro
aliases:
- /tutorials/programming/conda
description: > 
  A tutorial for setting up your conda environments on Neurodesk.
---

# Conda environments

A tutorial for setting up your conda environments on Neurodesk.

> _This tutorial was created by Fernanda L. Ribeiro._ 
>
> Email: fernanda.ribeiro@uq.edu.au
>
> Github: @felenitaribeiro
>
> Twitter: @NandaRibeiro93
>
<!-- Fill in your personal details above so that we can credit the tutorial to you. Feel free to add any additional contact details i.e. website, or remove those that are irrelevant -->

<!-- Following line adds a link to getting set up with Neurodesk -->
[Getting Set Up with Neurodesk](https://neurodesk.org/getting-started/)
<!-- -->

This tutorial documents how to create conda environments on Neurodesk. 

## Conda/Mamba environment

The default conda environment is not persistent across sessions, so this means any packages you install in the standard environment will disappear after you restart the Jupyterlab instance. However, you can create your own conda environment, which will be stored in your homedirectory, by following the steps on this page. This method can also be used to install additional kernels, such as an R kernel.

1. In a Terminal window, type in:

![1_terminal](/static/tutorials/programming/conda/1_terminal.png '1_terminal')

For *Python*:
```bash
mamba create -n test ipykernel pip
#OR
conda create -n test ipykernel pip
```
or for *R*:
```bash
mamba create -n r_env r-irkernel
#OR
conda create -n r_env r-irkernel
```

**Important:** Include both `ipykernel` and `pip` when you create a Python environment. JupyterLab uses `ipykernel` to run notebooks, and `pip` installs Python modules in the environment. If you omitted either package, activate the environment and install both packages:

```bash
conda activate test
conda install ipykernel pip
```

2. To check the list of environments you have created, run the following:

```bash
mamba env list
#OR
conda env list
```

3. Activate the environment:

For *Python*:
```bash
conda activate test
```

To load Neurodesk software modules from a notebook, install `jupyterlmod` in the environment:

```bash
python -m pip install jupyterlmod
```

`jupyterlmod` provides the Python package used by `import module`. A user-created conda environment does not inherit this package from the base environment. You do not need to install `jupyterlmod` to use `module` or `ml` in a terminal.

Install a Python module with `python -m pip`. For example, install NumPy:

```bash
python -m pip install numpy
```

To install the modules listed in a requirements file, run:

```bash
python -m pip install -r requirements.txt
```

For *R*:

```bash
conda activate r_env
```

4. Open a new Launcher tab. The new environment can take a short time to appear on the JupyterLab start page after the installation finishes. When it appears, select the new Notebook option to start a Jupyter Notebook in that environment.

![2_env](/static/tutorials/programming/conda/2_env.png '2_env')

Switching the environment on a Jupyter Notebook is also possible on the top right corner dropdown menu.

![3_notebook](/static/tutorials/programming/conda/3_notebook.png '3_notebook')
