
import {FileBrowser} from '@jupyterlab/filebrowser';
import {PanelLayout, Widget} from '@phosphor/widgets';

import {GCSDrive} from './contents';

/**
 * Widget for hosting the GitHub filebrowser.
 */
export class GCSFileBrowser extends Widget {
  constructor(browser: FileBrowser, drive: GCSDrive) {
    super();
    this.addClass('jp-GitHubBrowser');
    this.layout = new PanelLayout();
    (this.layout as PanelLayout).addWidget(browser);
  }
}
