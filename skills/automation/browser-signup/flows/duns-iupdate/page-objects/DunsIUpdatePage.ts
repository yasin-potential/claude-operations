import type { Page } from '@playwright/test';

export class DunsIUpdatePage {
  constructor(private readonly page: Page) {}

  async submit(): Promise<void> {
    await this.page.getByRole('button', { name: /Submit/i }).click();
  }

  async waitForConfirmation(): Promise<string | undefined> {
    const toast = this.page.getByRole('alert');
    try {
      await toast.waitFor({ state: 'visible', timeout: 10_000 });
    } catch {
      return undefined;
    }
    const text = await toast.textContent();
    if (!text) return undefined;
    const match = text.match(/\b\d{9}\b/);
    return match?.[0];
  }
}
