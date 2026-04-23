import type { Page } from '@playwright/test';

export class DunsLandingPage {
  constructor(private readonly page: Page) {}

  static readonly URL = 'https://www.dnb.com/en-us/smb/duns/get-a-duns.html';

  async goto(): Promise<void> {
    await this.page.goto(DunsLandingPage.URL);
  }

  async startNewRegistration(): Promise<void> {
    await this.page.getByRole('link', { name: /Get (a |your )?D-?U-?N-?S/i }).first().click();
  }
}
