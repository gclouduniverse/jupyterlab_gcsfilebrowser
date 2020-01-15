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

The following steps are to be followed when releasing a new version of the
extension.

1. Update version references in [package.json](package.json) and
   [jupyterlab_gcsfilebrowser/version.py](./jupyterlab_gcsfilebrowser/version.py).
2. Ensure all changes are submitted for review and committed to the remote repository.
3. Create a new tag number for the version.
   - `git tag vx.x.x -m "vx.x.x release"` where x.x.x is the version number.
4. Push the tag to the remote repository.
   - `git push origin vx.x.x` where x.x.x is the version number.
5. Submit the Cloud Build process to build the extension, package it as a tarball,
   and make it publicly available for installation from GCS.
   - ```
      gcloud --project deeplearning-platform-ui builds submit \
        --config cloudbuild-release.yaml \
        --substitutions=_VERSION=x.x.x
     ```
     where x.x.x is the version number.
6. Verify that `jupyterlab_gcsfilebrowser-x.x.x.tar.gz` and `jupyterlab_gcsfilebrowser-latest.tar.gz`
   are updated in the [gs://deeplearning-platform-ui-public](https://pantheon.corp.google.com/storage/browser/deeplearning-platform-ui-public?organizationId=433637338589&project=deeplearning-platform-ui) GCS bucket.
