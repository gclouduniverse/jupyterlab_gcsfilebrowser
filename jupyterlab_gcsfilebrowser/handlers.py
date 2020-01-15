# Lint as: python3
"""Request handler classes for the extensions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import google_type_annotations
from __future__ import print_function

from notebook.base.handlers import APIHandler, app_log

from google.cloud import storage # used for connecting to GCS
from io import BytesIO # used for sending GCS blobs in JSON objects

class GCSHandler(APIHandler):
  """Handles requests for GCS operations."""

  def get(self, path=''):
    try:
      self.finish( [{
                    'name': 'dummy',
                    'path': 'dummy',
                    'type': 'directory'
                }])
    except Exception as e:
      app_log.exception(str(e))
      self.set_status(500, str(e))
