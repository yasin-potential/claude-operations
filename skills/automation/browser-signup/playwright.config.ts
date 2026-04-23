import { defineConfig } from '@playwright/test';

const isCI = !!process.env.CI;

export default defineConfig({
  testDir: '.',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'artifacts/_report', open: 'never' }],
  ],
  outputDir: 'artifacts/_runs',
  timeout: 30 * 60_000,
  expect: { timeout: 15_000 },
  use: {
    headless: isCI,
    viewport: { width: 1400, height: 900 },
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    launchOptions: {
      slowMo: isCI ? 0 : 100,
    },
  },
  projects: [
    {
      name: 'duns-iupdate',
      testMatch: /flows\/duns-iupdate\/.*\.spec\.ts$/,
    },
    {
      name: '_framework',
      testMatch: /framework\/__tests__\/.*\.spec\.ts$/,
    },
  ],
});
