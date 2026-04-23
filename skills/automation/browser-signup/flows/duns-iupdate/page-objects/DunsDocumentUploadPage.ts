import type { Page } from '@playwright/test';

export class DunsDocumentUploadPage {
  static readonly FRAME = 'iframe[name="uploadFrame"], iframe#documentUpload';
  static readonly INPUT = 'input[type="file"]';
  static readonly PREVIEW = '[data-testid="file-preview"], .file-preview, .uploaded-file';
  static readonly CONFIRM = 'button:has-text("Upload"), button:has-text("Confirm")';

  constructor(private readonly page: Page) {}

  uploadInputSelector() {
    return DunsDocumentUploadPage.INPUT;
  }

  frameSelector() {
    return DunsDocumentUploadPage.FRAME;
  }

  previewSelector() {
    return DunsDocumentUploadPage.PREVIEW;
  }

  confirmSelector() {
    return DunsDocumentUploadPage.CONFIRM;
  }
}
