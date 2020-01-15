// Ensure styles are loaded by webpack
import '../style/index.css';

import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {IDocumentManager} from '@jupyterlab/docmanager';
import {IFileBrowserFactory} from '@jupyterlab/filebrowser';
import {GCSDrive} from './contents';
import {GCSFileBrowser} from './browser';

const NAMESPACE = 'gcs-filebrowser';

async function activateGCSFileBrowser(
  app: JupyterFrontEnd,
  manager: IDocumentManager,
  factory: IFileBrowserFactory,
  restorer: ILayoutRestorer
) {

  const drive = new GCSDrive(app.docRegistry);
  manager.services.contents.addDrive(drive);

  const browser = factory.createFileBrowser(NAMESPACE, {
    driveName: drive.name,
    refreshInterval: 300000
  });

  const GCSBrowser = new GCSFileBrowser(browser, drive);

  GCSBrowser.title.iconClass = 'jp-GCSFilebrowserIcon jp-SideBar-tabIcon';
  GCSBrowser.title.caption = 'Browse GCS';
  GCSBrowser.id = 'gcs-filebrowser';


  restorer.add(GCSBrowser, NAMESPACE);
  app.shell.add(GCSBrowser, 'left', {rank: 100});

}
/**
 * The JupyterLab plugin for the GCS Filebrowser.
 */
const GCSFileBrowserPlugin: JupyterFrontEndPlugin<void> = {
  id: 'gcsfilebrowser:drive',
  requires: [
    IDocumentManager,
    IFileBrowserFactory,
    ILayoutRestorer
  ],
  activate: activateGCSFileBrowser,
  autoStart: true
};

/**
 * Export the plugin as default.
 */
export default [GCSFileBrowserPlugin];
