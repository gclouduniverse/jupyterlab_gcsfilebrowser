# Lint as: python3
"""Request handler classes for the extensions."""

import json
import tornado.gen as gen

from notebook.base.handlers import APIHandler, app_log

from google.cloud import storage # used for connecting to GCS
from io import BytesIO # used for sending GCS blobs in JSON objects

class GCSHandler(APIHandler):
  """Handles requests for GCS operations."""

  @gen.coroutine
  def get(self, path=''):
    try:
      self.finish(json.dumps([{
                    'name': 'dummy_gcs',
                    'path': 'dummy_gcs',
                    'type': 'directory'
                }]))
    except Exception as e:
      app_log.exception(str(e))
      self.set_status(500, str(e))
