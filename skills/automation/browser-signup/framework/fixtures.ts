import { test as base, expect } from '@playwright/test';
import type { Page, BrowserContext, TestInfo } from '@playwright/test';
import { fillForm, type FormSchema } from './form-schema.js';
import {
  saveCheckpoint,
  loadCheckpoint,
  saveResult,
  writeHandoff,
  clientSlug,
  deriveRunId,
  resumeRunId,
  type CheckpointData,
} from './checkpoint.js';
import { notify } from './notify.js';

export interface FlowContext {
  flowName: string;
  runId: string;
  client?: string;
}

export interface WaitForHumanOptions {
  reason: string;
  checkpoint?: string;
  timeoutMin?: number;
  sentinel?: string;
  allowPause?: boolean;
}

export interface WaitForSMSCodeOptions {
  reason?: string;
  inputSelector: string;
  expectedFrom?: string;
  checkpoint?: string;
  timeoutMin?: number;
}

export interface UploadDocumentOptions {
  inputSelector: string;
  filePath: string;
  frame?: string;
  previewSelector?: string;
  confirmSelector?: string;
}

export interface SignupFixtures {
  flow: FlowContext;
  fillForm: (schema: FormSchema) => Promise<void>;
  waitForHuman: (opts: WaitForHumanOptions) => Promise<CheckpointData | undefined>;
  waitForSMSCode: (opts: WaitForSMSCodeOptions) => Promise<CheckpointData | undefined>;
  checkpoint: (name: string) => Promise<CheckpointData>;
  resumeFrom: (name: string) => Promise<CheckpointData>;
  uploadDocument: (opts: UploadDocumentOptions) => Promise<void>;
  expectOtpEntered: (selector: string, timeoutMin?: number) => Promise<void>;
  saveResult: (result: unknown) => Promise<string>;
  writeHandoff: (content: string) => Promise<string>;
}

export const test = base.extend<SignupFixtures>({
  flow: async ({}, use, testInfo) => {
    const flowName = deriveFlowName(testInfo);
    const runId = resumeRunId() ?? deriveRunId();
    const client = clientSlug();
    await use({ flowName, runId, client });
  },

  fillForm: async ({ page }, use) => {
    await use((schema: FormSchema) => fillForm(page, schema));
  },

  waitForHuman: async ({ page, context, flow }, use, testInfo) => {
    await use(async (opts) => {
      const timeoutMs = (opts.timeoutMin ?? 15) * 60_000;

      await notify({
        title: `[${flow.client ?? 'internal'}/${flow.flowName}] Human input required`,
        message: opts.reason,
      });

      if (opts.sentinel) {
        await page.waitForSelector(opts.sentinel, { timeout: timeoutMs, state: 'visible' });
      } else if (opts.allowPause !== false && !process.env.CI) {
        await page.pause();
      } else {
        await page.waitForTimeout(timeoutMs);
      }

      if (opts.checkpoint) {
        return saveCheckpoint(
          opts.checkpoint,
          page,
          context,
          flow.flowName,
          flow.runId,
          testInfo,
          flow.client,
        );
      }
      return undefined;
    });
  },

  waitForSMSCode: async ({ page, context, flow }, use, testInfo) => {
    await use(async (opts) => {
      const timeoutMs = (opts.timeoutMin ?? 10) * 60_000;
      const from = opts.expectedFrom ?? 'Apple / Google / D&B';
      const reason =
        opts.reason ??
        `SMS code required. Client forwards SMS from ${from} via KakaoTalk. ` +
          `Paste the 6-digit code into the input field, then click Resume.`;

      await notify({
        title: `[${flow.client ?? 'internal'}/${flow.flowName}] SMS code needed`,
        message: reason,
      });

      if (!process.env.CI) {
        await page.pause();
      } else {
        await page.waitForFunction(
          (sel: string) => {
            const el = document.querySelector(sel) as HTMLInputElement | null;
            return !!(el && el.value && el.value.length >= 4);
          },
          opts.inputSelector,
          { timeout: timeoutMs },
        );
      }

      if (opts.checkpoint) {
        return saveCheckpoint(
          opts.checkpoint,
          page,
          context,
          flow.flowName,
          flow.runId,
          testInfo,
          flow.client,
        );
      }
      return undefined;
    });
  },

  checkpoint: async ({ page, context, flow }, use, testInfo) => {
    await use((name: string) =>
      saveCheckpoint(name, page, context, flow.flowName, flow.runId, testInfo, flow.client),
    );
  },

  resumeFrom: async ({ page, flow }, use) => {
    await use(async (name: string) => {
      if (!resumeRunId()) {
        throw new Error(
          'resumeFrom requires --run-id=<id> or RESUME_RUN_ID env var pointing to a prior run',
        );
      }
      const data = await loadCheckpoint(name, flow.flowName, flow.runId, flow.client);
      await page.goto(data.url);
      return data;
    });
  },

  uploadDocument: async ({ page }, use) => {
    await use(async (opts: UploadDocumentOptions) => {
      const base = opts.frame ? page.frameLocator(opts.frame) : page;
      const input = base.locator(opts.inputSelector);
      await input.setInputFiles(opts.filePath);

      if (opts.previewSelector) {
        await expect(base.locator(opts.previewSelector)).toBeVisible({ timeout: 20_000 });
      }

      if (opts.confirmSelector) {
        await base.locator(opts.confirmSelector).click();
      }
    });
  },

  expectOtpEntered: async ({ page }, use) => {
    await use(async (selector: string, timeoutMin = 10) => {
      await page.waitForFunction(
        (sel: string) => {
          const el = document.querySelector(sel) as HTMLInputElement | null;
          return !!(el && el.value && el.value.length >= 4);
        },
        selector,
        { timeout: timeoutMin * 60_000 },
      );
    });
  },

  saveResult: async ({ flow }, use) => {
    await use((result: unknown) => saveResult(flow.flowName, flow.runId, result, flow.client));
  },

  writeHandoff: async ({ flow }, use) => {
    await use((content: string) => writeHandoff(flow.flowName, flow.runId, content, flow.client));
  },
});

export { expect } from '@playwright/test';
export { resumeName, clientSlug } from './checkpoint.js';

function deriveFlowName(testInfo: TestInfo): string {
  return testInfo.project.name || 'unknown-flow';
}

export type { Page, BrowserContext };
