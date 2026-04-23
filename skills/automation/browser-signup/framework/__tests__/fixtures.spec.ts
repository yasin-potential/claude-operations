import { existsSync } from 'node:fs';
import { test, expect } from '../fixtures.js';

test.describe('framework smoke', () => {
  test('checkpoint saves storageState + screenshot + meta', async ({ page, checkpoint }) => {
    await page.goto('https://example.com');
    const data = await checkpoint('smoke');

    expect(data.name).toBe('smoke');
    expect(data.url).toContain('example.com');
    expect(existsSync(data.storageStatePath)).toBe(true);
    expect(existsSync(data.screenshotPath)).toBe(true);
  });

  test('fillForm + validateValue works on a real form', async ({ page, fillForm }) => {
    await page.setContent(`
      <form>
        <input name="q" type="text" />
        <select name="lang"><option value="en">en</option><option value="ko">ko</option></select>
        <input name="agree" type="checkbox" />
      </form>
    `);

    await fillForm({
      fields: [
        { name: 'query', selector: 'input[name="q"]', kind: 'text', value: 'hello world', validateValue: true },
        { name: 'lang', selector: 'select[name="lang"]', kind: 'select', value: 'ko', validateValue: true },
        { name: 'agree', selector: 'input[name="agree"]', kind: 'checkbox', value: true, validateValue: true },
      ],
    });

    expect(await page.locator('input[name="q"]').inputValue()).toBe('hello world');
    expect(await page.locator('select[name="lang"]').inputValue()).toBe('ko');
    expect(await page.locator('input[name="agree"]').isChecked()).toBe(true);
  });
});
