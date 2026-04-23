import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { test, expect, resumeName } from '../../framework/fixtures.js';
import { loadSchemaFromEnv, type FormSchema } from '../../framework/form-schema.js';
import { DunsLandingPage } from './page-objects/DunsLandingPage.js';
import { DunsSearchPage } from './page-objects/DunsSearchPage.js';
import { DunsIUpdatePage } from './page-objects/DunsIUpdatePage.js';
import { DunsDocumentUploadPage } from './page-objects/DunsDocumentUploadPage.js';

interface DunsSchemaFile {
  companySearch: FormSchema;
  companyDetails: FormSchema;
}

async function loadSchema(): Promise<DunsSchemaFile> {
  const path = resolve(__dirname, 'schema.json');
  const raw = await readFile(path, 'utf-8');
  return JSON.parse(raw) as DunsSchemaFile;
}

test.describe('DUNS iUpdate registration', () => {
  test('register new DUNS number', async ({
    page,
    fillForm,
    waitForHuman,
    checkpoint,
    resumeFrom,
    uploadDocument,
    saveResult,
  }) => {
    const schemas = await loadSchema();
    const resume = resumeName();

    if (resume === 'post-email') {
      await resumeFrom('post-email');
    } else {
      const landing = new DunsLandingPage(page);
      await landing.goto();
      await landing.startNewRegistration();

      await fillForm(loadSchemaFromEnv(schemas.companySearch, process.env));

      const search = new DunsSearchPage(page);
      await search.proceedAfterNoMatch();

      await waitForHuman({
        reason:
          'Verify email link from D&B. Click the link, then return here and press Resume in the Inspector.',
        checkpoint: 'post-email',
        timeoutMin: 30,
      });
    }

    await fillForm(loadSchemaFromEnv(schemas.companyDetails, process.env));
    await checkpoint('post-details');

    const certPath = process.env.DUNS_BUSINESS_CERT_PATH;
    if (!certPath) {
      throw new Error('DUNS_BUSINESS_CERT_PATH not set — cannot upload business registration certificate');
    }

    const upload = new DunsDocumentUploadPage(page);
    await uploadDocument({
      frame: upload.frameSelector(),
      inputSelector: upload.uploadInputSelector(),
      filePath: certPath,
      previewSelector: upload.previewSelector(),
      confirmSelector: upload.confirmSelector(),
    });
    await checkpoint('post-upload');

    await waitForHuman({
      reason: 'Review the summary page. If everything looks correct, press Resume to submit.',
      checkpoint: 'pre-submit',
      timeoutMin: 30,
    });

    const iupdate = new DunsIUpdatePage(page);
    await iupdate.submit();

    const dunsNumber = await iupdate.waitForConfirmation();
    expect(dunsNumber, 'DUNS number should appear in success alert or confirmation email').toBeDefined();

    const resultPath = await saveResult({
      dunsNumber,
      submittedAt: new Date().toISOString(),
    });
    console.log(`\n✓ Result saved to ${resultPath}\n`);
  });
});
