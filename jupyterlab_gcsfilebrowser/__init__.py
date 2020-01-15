from notebook.utils import url_path_join

from jupyterlab_gcsfilebrowser.handlers import GCSHandler
from jupyterlab_gcsfilebrowser.version import VERSION

__version__ = VERSION

def _jupyter_server_extension_paths():
    return [{
        'module': 'jupyterlab_gcsfilebrowser'
    }]

def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.
    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    host_pattern = '.*$'
    app = nb_server_app.web_app
    gcp_v1_endpoint = url_path_join(app.settings['base_url'], 'gcp', 'v1')
    app.add_handlers(host_pattern, [
      # TODO(cbwilkes): Add auth checking if needed.
      # (url_path_join(gcp_v1_endpoint, 'gcs', 'auth'), AuthHandler)
      (url_path_join(gcp_v1_endpoint, 'gcs'), GCSHandler)
    ])
