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
from google.api_core.client_info import ClientInfo
from io import BytesIO, StringIO # used for sending GCS blobs in JSON objects
from jupyterlab_gcsfilebrowser.version import VERSION


def list_dir(bucket_name, path, blobs_dir_list):
  items = []
  directories = set()

  path = '%s%s' % (path, '' if re.match(".*/$", path) else '/')

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

  if path != '/':
    path = '/' + path

  items = items + [{
                  'type': 'directory',
                  'path': ('%s%s%s/' % (bucket_name, path, d)),
                  'name': d + '/'
                  } for d in directories]

  return items


# TODO(cbwilkes): Add tests for parse_path.
def parse_path(path):
  # Remove any preceeding '/', and split off the bucket name
  bucket_paths = re.sub(r'^/', '', path).split('/', 1)

  # The first token should represent the bucket name
  bucket_name = bucket_paths[0]

  # The rest of the string should represent the blob path, if requested
  blob_path = bucket_paths[1] if len(bucket_paths) > 1 else ''

  return bucket_name, blob_path


def prefixed_blobs(bucket_name, prefix, storage_client):
  return list(storage_client.list_blobs(
    bucket_name, prefix=prefix))


def matching_blobs(path, storage_client):
  """Find a blob with a name that matches the exact path.

  Returns:
    An array of matching Blobs.
  """

  # TODO(cbwilkes): Add tests for matching_blobs.
  # TODO(cbwilkes): Return matching blobs for directories.
  bucket_name, blob_path = parse_path(path)

  # List blobs in the bucket with the blob_path prefix
  blobs = prefixed_blobs(bucket_name, blob_path, storage_client)

  # Find a blob that is not a directory name and fully matches the blob_path
  # If there are any matches, we are retriving a single blob
  blobs_matching = [b
        for b in blobs
        # TODO(cbwilkes): protect against empty names
        if not re.match(".*/$", b.name) and b.name == blob_path]

  return blobs_matching


def matching_bucket(path, storage_client):
  bucket_name, _ = parse_path(path)

  # Raises google.cloud.exceptions.NotFound – If the bucket is not found.
  return storage_client.get_bucket(bucket_name)


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
    bucket_name, blob_path = parse_path(path)

    blobs_prefixed = prefixed_blobs(bucket_name, blob_path, storage_client)

    blobs_matching = matching_blobs(path, storage_client)

    if len(blobs_matching) == 1: # Single blob
      blob = blobs_matching[0]
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
        'content': list_dir(bucket_name, blob_path, blobs_prefixed)
        }


def delete(path, storage_client):
  path = path or '/'
  addDir = '/' if re.match(".+/$", path) else ''
  path = os.path.normpath(path) + addDir

  if path == '/':
    return {}
  else:
    blobs_matching = matching_blobs(path, storage_client)

    if len(blobs_matching) == 1: # Single blob
      blob = blobs_matching[0]
      blob.delete()

      return {}
    else: # Directory
      return {}


def upload(model, storage_client):
  bucket_name, blob_path = parse_path(model['path'])

  def uploadModel(storage_client, model, blob_path):
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_path)
    if model['format'] == 'base64':
      bytes_file = BytesIO(base64.b64decode(model['content']))
      blob.upload_from_file(bytes_file)
    elif model['format'] == 'json':
      blob.upload_from_string(json.dumps(model['content']))
    else:
      blob.upload_from_string(model['content'])

  def appendChunk(storage_client, model, last, temp, composite, deleteLast=False):
    bucket = storage_client.get_bucket(bucket_name)
    uploadModel(storage_client, model, temp)

    blob = bucket.blob(composite)

    blob_last = bucket.blob(last)
    blob_temp = bucket.blob(temp)

    blob.compose([blob_last, blob_temp])

    blob_temp.delete()

    if deleteLast:
      blob_last.delete()

  if 'chunk' not in model:
    uploadModel(storage_client, model, blob_path)
  else:
    if model['chunk'] == 1:
      blob_path_composite = '%s.temporary' % (blob_path)
      uploadModel(storage_client, model, blob_path_composite)
    elif model['chunk'] == -1:
      appendChunk(
        storage_client,
        model,
        '%s.temporary' % (blob_path),
        '%s.temporary-%s.tmp' % (blob_path, model['chunk']),
        blob_path,
        True)
    else:
      appendChunk(
        storage_client,
        model,
        '%s.temporary' % (blob_path),
        '%s.temporary-%s.tmp' % (blob_path, model['chunk']),
        '%s.temporary' % (blob_path))


def generate_next_unique_name(bucket_name, blob_name, storage_client):

  def generate_name(blob_name, name_addendum):
    root, ext = os.path.splitext(blob_name)
    addendum = ''
    if name_addendum:
      addendum = '-Copy%s' % name_addendum

    return '%s%s%s' % (root, addendum, ext)

  name_addendum = ''
  proposed_blob_name = generate_name(blob_name, name_addendum)

  while matching_blobs(
    '/%s/%s' % (bucket_name, proposed_blob_name), storage_client):
    if not name_addendum:
      name_addendum = 1
    else:
      name_addendum = name_addendum + 1

    proposed_blob_name = generate_name(blob_name, name_addendum)

  return generate_name(blob_name, name_addendum)


def copy(path, directory, storage_client):

  def copyFileName(path, directory):
    _, blob_name = parse_path(path)
    destination_bucket, destination_blob_name_dir = parse_path(directory)
    basename = os.path.basename(blob_name)

    if not basename:
      raise ValueError('"path" is not a valid blob name.')
    new_blob_name = '%s/%s' % (destination_blob_name_dir, basename)

    return destination_bucket, new_blob_name

  blobs_matching = matching_blobs(path, storage_client)
  current_bucket = matching_bucket(path, storage_client)
  destination_bucket_name, new_blob_name = copyFileName(path, directory)

  new_blob_name = generate_next_unique_name(
    destination_bucket_name, new_blob_name, storage_client)

  destination_bucket = storage_client.get_bucket(destination_bucket_name)

  return current_bucket.copy_blob(
    blobs_matching[0], destination_bucket, new_blob_name)


def move(old, new, storage_client):
  blobs_matching = matching_blobs(old, storage_client)

  destination_bucket = matching_bucket(new, storage_client)

  _, new_blob_name = parse_path(new)
  return destination_bucket.rename_blob(blobs_matching[0], new_blob_name)


def create_storage_client():
  return storage.Client(
    client_info=ClientInfo(
      user_agent='jupyterlab_gcsfilebrowser/{}'.format(VERSION)
      )
    )


class GCSHandler(APIHandler):
  """Handles requests for GCS operations."""
  storage_client = None

  @gen.coroutine
  def get(self, path=''):
    try:
      if not self.storage_client:
        self.storage_client = create_storage_client()

      self.finish(json.dumps(
        getPathContents(path, self.storage_client)))

    except Exception as e:
      app_log.exception(str(e))
      self.set_status(500, str(e))


class UploadHandler(APIHandler):

  storage_client = None

  @gen.coroutine
  def post(self, *args, **kwargs):

    try:
      if not self.storage_client:
        self.storage_client = create_storage_client()

      model = self.get_json_body()

      upload(model, self.storage_client)

      self.finish({})
    except Exception as e:
      app_log.exception(str(e))
      self.set_status(500, str(e))


class DeleteHandler(APIHandler):

  storage_client = None

  @gen.coroutine
  def delete(self, path=''):

    try:
      if not self.storage_client:
        self.storage_client = create_storage_client()

      self.finish(json.dumps(delete(path, self.storage_client)))

    except Exception as e:
      app_log.exception(str(e))
      self.set_status(500, str(e))


class MoveHandler(APIHandler):

  storage_client = None

  @gen.coroutine
  def post(self, path=''):

    move_obj = self.get_json_body()

    try:
      if not self.storage_client:
        self.storage_client = create_storage_client()

      blob = move(move_obj['oldLocalPath'], move_obj['newLocalPath'], self.storage_client)
      self.finish({
                  'type': 'file',
                  'path': blob.path,
                  'name': blob.name
                })

    except Exception as e:
      app_log.exception(str(e))
      self.set_status(500, str(e))


class CopyHandler(APIHandler):

  storage_client = None

  @gen.coroutine
  def post(self, path=''):

    copy_obj = self.get_json_body()

    try:
      if not self.storage_client:
        self.storage_client = create_storage_client()

      blob = copy(
        copy_obj['localPath'], copy_obj['toLocalDir'], self.storage_client)
      self.finish({
                  'type': 'file',
                  'path': blob.path,
                  'name': blob.name
                })

    except Exception as e:
      app_log.exception(str(e))
      self.set_status(500, str(e))
