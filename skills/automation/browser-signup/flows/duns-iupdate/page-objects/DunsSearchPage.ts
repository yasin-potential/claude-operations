import type { Page } from '@playwright/test';

export class DunsSearchPage {
  constructor(private readonly page: Page) {}

  async proceedAfterNoMatch(): Promise<void> {
    await this.page.getByRole('button', { name: /Continue|Proceed/i }).click();
  }

  async selectExistingMatch(companyName: string): Promise<void> {
    await this.page.getByText(companyName, { exact: false }).first().click();
  }
}
