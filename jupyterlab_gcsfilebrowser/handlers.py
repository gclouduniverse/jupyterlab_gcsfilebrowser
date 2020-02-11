# Lint as: python3
"""Request handler classes for the extensions."""

import base64
import json
import re
import tornado.gen as gen
import os

from collections import namedtuple
from notebook.base.handlers import APIHandler, app_log

from google.cloud import storage # used for connecting to GCS
from io import BytesIO # used for sending GCS blobs in JSON objects

def list_dir(bucket_name, path, blobs_dir_list):
  items = []
  directories = set()

  path = '%s%s' % (path, '' if re.match(".*/$", path) else '/')

  # print('list_dir', (bucket_name, path, blobs_dir_list))

  for blob in blobs_dir_list:
    relative_blob_name = re.sub(r'^' + path, '', blob.name)

    relative_path_parts = [
      dir
      for dir in relative_blob_name.split('/')
      if dir
      ]

    if re.match(".*/$", blob.name):
      # Add the top directory to the set of directories if one exist
      if relative_path_parts:
        directories.add(relative_path_parts[0])
    else:
      if relative_path_parts:
        dir_name = relative_path_parts[0]

        def blobInDir(parts):
          return len(parts) > 1

        if blobInDir(relative_path_parts):
          directories.add(relative_path_parts[0])
        else:
          items.append({
                  'type': 'file',
                  'path': ('%s/%s' % (bucket_name, blob.name)),
                  'name': dir_name
                })

  # print('list_dir', (bucket_name, path))

  if path != '/':
    path = '/' + path

  items = items + [{
                  'type': 'directory',
                  'path': ('%s%s%s/' % (bucket_name, path, d)),
                  'name': d + '/'
                  } for d in directories]

  return items

def getPathContents(path, storage_client):
  path = path or '/'
  addDir = '/' if re.match(".+/$", path) else ''
  path = os.path.normpath(path) + addDir

  if path == '/':
    buckets = storage_client.list_buckets()
    return {
        'type':'directory',
        'content': [{
                    'type': 'directory',
                    'path': b.name + '/',
                    'name': b.name + '/'
                    } for b in buckets]
    }
  else:
    # Remove any preceeding '/', and split off the bucket name
    bucket_paths = re.sub(r'^/', '', path).split('/', 1)

    # The first token should represent the bucket name
    bucket_name = bucket_paths[0]

    # The rest of the string should represent the blob path, if requested
    blob_path = bucket_paths[1] if len(bucket_paths) > 1 else ''

    # List blobs in the bucket with the blob_path prefix
    blobs = list(storage_client.list_blobs(
      bucket_name, prefix=blob_path))

    # Find a blob that is not a directory name and fully matches the blob_path
    # If there are any matches, we are retriving a single blob
    matching_blobs = [b
          for b in blobs
          # TODO(cbwilkes): protect against empty names
          if not re.match(".*/$", b.name) and b.name == blob_path]

    if len(matching_blobs) == 1: # Single blob
      blob = matching_blobs[0]
      file_bytes = BytesIO()
      blob.download_to_file(file_bytes)

      return {
        'type': 'file',
        'content': {
          'path': ('%s/%s' % (bucket_name, blob.name)),
          'type': 'file',
          'mimetype': blob.content_type,
          'content': base64.encodebytes(
            file_bytes.getvalue()).decode('ascii')
          }
        }
    else: # Directory
      return {
        'type': 'directory',
        'content': list_dir(bucket_name, blob_path, blobs)
        }


class GCSHandler(APIHandler):
  """Handles requests for GCS operations."""
  storage_client = None

  @gen.coroutine
  def get(self, path=''):
    try:
      if not self.storage_client:
        self.storage_client = storage.Client()

      self.finish(json.dumps(
        getPathContents(path, self.storage_client)))

    except Exception as e:
      app_log.exception(str(e))
      self.set_status(500, str(e))


class UploadHandler(APIHandler):

  @gen.coroutine
  def post(self):
    pass

