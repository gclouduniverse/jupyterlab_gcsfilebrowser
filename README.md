# GCS Notebooks Filebrowser Extension

`jupyterlab_gcsfilebrowser` - Provides a mechanism browse and interact with
Google Cloud Storage through a file browser.

## Prerequisites

* Python 3.5+
* [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)
* [Virtualenv](https://virtualenv.pypa.io/en/latest/) (Recommended for local development)

## Installation

This should work on Google Cloud Deep Learning VM M19+. You may also use the
[deploy.sh](./deploy.sh) script to build the extension locally, then copy and
install on a DLVM over SSH.

```bash
# Build the Python source distribution package
python setup.py sdist

# Copy the dist/jupyterlab_gcsfilebrowser-x.x.x.tar.gz archive to the JupyterLab
# server and untar it

# Install the Python package
sudo pip3 install .
# Force Jupyter to rebuild the front-end packages
sudo jupyter lab build
sudo service jupyter restart
```

## Development

For a development install (requires npm version 4 or later), do the following in the repository directory:

You will need to have Python3, virtualenv, and npm installed.

```bash
# Create a Python 3 virtualenv and install jupyterlab and the project in edit mode
virtualenv -p python3 venv
source venv/bin/activate
# Install the version of jupyterlab used by DLVM images
pip install jupyterlab
pip install .

# Install the npm package and the extension
npm install
jupyter labextension install . --no-build

# Now, run npm start which starts the Typescript compiler in watch mode on the
# extension directory as well as the JupyterLab server
npm start
```

## Releasing

See: go/jupyterlab-gcsfilebrowser-release-notes
