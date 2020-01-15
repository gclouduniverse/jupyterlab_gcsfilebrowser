
import {DocumentRegistry} from '@jupyterlab/docregistry';
import {ISignal, Signal} from '@phosphor/signaling';
import {Contents, ServerConnection} from '@jupyterlab/services';

/**
 * A Contents.IDrive implementation that Google Cloud Storage.
 */
export class GCSDrive implements Contents.IDrive {

  /**
   * Construct a new drive object.
   *
   * @param options - The options used to initialize the object.
   */
  constructor(registry: DocumentRegistry) {
  }

  private _isDisposed = false;
  private _fileChanged = new Signal<this, Contents.IChangedArgs>(this);

  /**
   * The name of the drive.
   */
  get name(): 'GCS' {
    return 'GCS';
  }

  /**
    * The server settings of the manager.
    */
  readonly serverSettings: ServerConnection.ISettings;

  /**
    * A signal emitted when a file operation takes place.
    */
  //fileChanged: ISignal<IDrive, IChangedArgs>;
  get fileChanged(): ISignal<this, Contents.IChangedArgs> {
    return this._fileChanged;
  }

  /**
   * Test whether the manager has been disposed.
   */
  get isDisposed(): boolean {
    return this._isDisposed;
  }

  /**
   * Dispose of the resources held by the manager.
   */
  dispose(): void {
    if (this.isDisposed) {
      return;
    }
    this._isDisposed = true;
    Signal.clearData(this);
  }

  /**
    * Get a file or directory.
    *
    * @param localPath: The path to the file.
    *
    * @param options: The options used to fetch the file.
    *
    * @returns A promise which resolves with the file content.
    */
  get(localPath: string, options?: Contents.IFetchOptions): Promise<Contents.IModel> {
    return Promise.reject('Unimplemented');
  }

  /**
    * Get an encoded download url given a file path.
    *
    * @param A promise which resolves with the absolute POSIX
    *   file path on the server.
    */
  getDownloadUrl(localPath: string): Promise<string> {
    return Promise.reject('Unimplemented');
  }

  /**
    * Create a new untitled file or directory in the specified directory path.
    *
    * @param options: The options used to create the file.
    *
    * @returns A promise which resolves with the created file content when the
    *    file is created.
    */
  newUntitled(options?: Contents.ICreateOptions): Promise<Contents.IModel> {
    return Promise.reject('Unimplemented');
  }

  /**
    * Delete a file.
    *
    * @param localPath - The path to the file.
    *
    * @returns A promise which resolves when the file is deleted.
    */
  delete(localPath: string): Promise<void> {
    return Promise.reject('Unimplemented');
  }

  /**
    * Rename a file or directory.
    *
    * @param oldLocalPath - The original file path.
    *
    * @param newLocalPath - The new file path.
    *
    * @returns A promise which resolves with the new file content model when the
    *   file is renamed.
    */
  rename(oldLocalPath: string, newLocalPath: string): Promise<Contents.IModel> {
    return Promise.reject('Unimplemented');
  }

  /**
    * Save a file.
    *
    * @param localPath - The desired file path.
    *
    * @param options - Optional overrides to the model.
    *
    * @returns A promise which resolves with the file content model when the
    *   file is saved.
    */
  save(localPath: string, options?: Partial<Contents.IModel>): Promise<Contents.IModel> {
    return Promise.reject('Unimplemented');
  }

  /**
    * Copy a file into a given directory.
    *
    * @param localPath - The original file path.
    *
    * @param toLocalDir - The destination directory path.
    *
    * @returns A promise which resolves with the new content model when the
    *  file is copied.
    */
  copy(localPath: string, toLocalDir: string): Promise<Contents.IModel> {
    return Promise.reject('Unimplemented');
  }

  /**
    * Create a checkpoint for a file.
    *
    * @param localPath - The path of the file.
    *
    * @returns A promise which resolves with the new checkpoint model when the
    *   checkpoint is created.
    */
  createCheckpoint(localPath: string): Promise<Contents.ICheckpointModel> {
    return Promise.reject('Unimplemented');
  }

  /**
    * List available checkpoints for a file.
    *
    * @param localPath - The path of the file.
    *
    * @returns A promise which resolves with a list of checkpoint models for
    *    the file.
    */
  listCheckpoints(localPath: string): Promise<Contents.ICheckpointModel[]> {
    return Promise.reject('Unimplemented');
  }

  /**
    * Restore a file to a known checkpoint state.
    *
    * @param localPath - The path of the file.
    *
    * @param checkpointID - The id of the checkpoint to restore.
    *
    * @returns A promise which resolves when the checkpoint is restored.
    */
  restoreCheckpoint(localPath: string, checkpointID: string): Promise<void> {
    return Promise.reject('Unimplemented');
  }

  /**
    * Delete a checkpoint for a file.
    *
    * @param localPath - The path of the file.
    *
    * @param checkpointID - The id of the checkpoint to delete.
    *
    * @returns A promise which resolves when the checkpoint is deleted.
    */
  deleteCheckpoint(localPath: string, checkpointID: string): Promise<void> {
    return Promise.reject('Unimplemented');
  }
}
