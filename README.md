[![N|Solid](https://www.seeq.com/sites/default/files/seeq-logo-navbar-small.png)](https://www.seeq.com)

[![N|Scheme](images/clusters.PNG)](https://www.seeq.com)

----

**seeq-clustering** is a Python module to 

----

# User Guide

[**seeq-clustering User Guide**]()

----

# Installation

The backend of **seeq-clustering** requires **Python 3.7** or later.

## Dependencies

See [`requirements.txt`]() file for a list of
dependencies and versions. Additionally, you will need to install the `seeq` module with the appropriate version that
matches your Seeq server. For more information on the `seeq` module see [seeq at pypi](https://pypi.org/project/seeq/)

## User Installation Requirements (Seeq Data Lab)

If you want to install **seeq-clustering** as a Seeq Add-on Tool, you will need:

- Seeq Data Lab (>= R50.5.0, >=R51.1.0, or >=R52.1.0)
- `seeq` module whose version matches the Seeq server version
- Seeq administrator access
- Enable Add-on Tools in the Seeq server

## User Installation (Seeq Data Lab)

The latest build of the project can be found [here](https://pypi.seeq.com/) as a wheel file. The file is published as a
courtesy to the user, and it does not imply any obligation for support from the publisher. Contact
[Seeq](mailto:applied.research@seeq.com?subject=[seeq-clustering]%20General%20Question) if you required credentials to
access the site.

1. Create a **new** Seeq Data Lab project and open the **Terminal** window
2. Run `pip install seeq-clustering --extra-index-url https://pypi.seeq.com --trusted-host pypi.seeq.com`
3. Run `python -m seeq.addons.correlation [--users <users_list> --groups <groups_list>]`

----

# Development

We welcome new contributors of all experience levels. The **Development Guide** has detailed information about
contributing code, documentation, tests, etc.

## Important links

* Official source code repo: https://github.com/seeq12/seeq-clustering
* Issue tracker: https://github.com/seeq12/seeq-clustering/issues

## Source code

You can get started by cloning the repository with the command:

```shell
git clone git@github.com:seeq12/seeq-clustering.git
```

## Installation from source

For development work, it is highly recommended creating a python virtual environment and install the package in that
working environment. If you are not familiar with python virtual environments, you can take a
look [here](https://docs.python.org/3.8/tutorial/venv.html)

Once your virtual environment is activated, you can install **seeq-clustering** from source with:

```shell
python setup.py install
```

----

# Changelog

The change log can be found [**here**](https://seeq12.github.io/seeq-clustering/changelog.html)


----

# Support

Code related issues (e.g. bugs, feature requests) can be created in the
[issue tracker](https://github.com/seeq12/seeq-clustering/issues)
Any other general comments or questions (non-code related) can be emailed to
[Seeq](mailto:applied.research@seeq.com?subject=[seeq-clustering]%20General%20Question)

Maintainer: Eric Parsonnet


----

# Citation

Please cite this work as:

```shell
seeq-clustering
Seeq Corporation, 2021
https://github.com/seeq12/seeq-clustering
```





