import type { Page, Locator } from '@playwright/test';

export type FieldKind = 'text' | 'email' | 'tel' | 'password' | 'select' | 'checkbox' | 'radio';

export interface FormField {
  name: string;
  selector: string;
  kind?: FieldKind;
  value: string | boolean;
  frame?: string;
  validateValue?: boolean;
  required?: boolean;
}

export interface FormSchema {
  fields: FormField[];
}

export interface FillFormOptions {
  stopOnError?: boolean;
}

export async function fillForm(
  page: Page,
  schema: FormSchema,
  options: FillFormOptions = {},
): Promise<void> {
  const { stopOnError = true } = options;
  const errors: string[] = [];

  for (const field of schema.fields) {
    try {
      const locator = resolveLocator(page, field);
      await fillField(locator, field);
      if (field.validateValue) {
        await verifyField(locator, field);
      }
    } catch (err) {
      const msg = `[${field.name}] ${(err as Error).message}`;
      if (stopOnError) throw new Error(msg);
      errors.push(msg);
    }
  }

  if (errors.length) {
    throw new Error(`Form fill had ${errors.length} error(s):\n${errors.join('\n')}`);
  }
}

function resolveLocator(page: Page, field: FormField): Locator {
  if (field.frame) {
    return page.frameLocator(field.frame).locator(field.selector);
  }
  return page.locator(field.selector);
}

async function fillField(locator: Locator, field: FormField): Promise<void> {
  const kind = field.kind ?? 'text';

  switch (kind) {
    case 'text':
    case 'email':
    case 'tel':
    case 'password':
      if (typeof field.value !== 'string') {
        throw new Error(`value must be string for kind=${kind}`);
      }
      await locator.fill(field.value);
      return;
    case 'select':
      if (typeof field.value !== 'string') {
        throw new Error('value must be string for kind=select');
      }
      await locator.selectOption(field.value);
      return;
    case 'checkbox':
      if (typeof field.value !== 'boolean') {
        throw new Error('value must be boolean for kind=checkbox');
      }
      if (field.value) await locator.check();
      else await locator.uncheck();
      return;
    case 'radio':
      await locator.check();
      return;
    default:
      throw new Error(`Unknown field kind: ${kind}`);
  }
}

async function verifyField(locator: Locator, field: FormField): Promise<void> {
  const kind = field.kind ?? 'text';

  if (kind === 'checkbox') {
    const actual = await locator.isChecked();
    if (actual !== field.value) {
      throw new Error(`checkbox expected=${field.value} actual=${actual}`);
    }
    return;
  }

  if (kind === 'text' || kind === 'email' || kind === 'tel' || kind === 'password' || kind === 'select') {
    const actual = await locator.inputValue();
    if (actual !== field.value) {
      throw new Error(`value expected="${field.value}" actual="${actual}"`);
    }
  }
}

export function loadSchemaFromEnv(schema: FormSchema, env: NodeJS.ProcessEnv): FormSchema {
  return {
    fields: schema.fields.map((f) => {
      if (typeof f.value !== 'string') return f;
      const match = f.value.match(/^\$\{([A-Z0-9_]+)\}$/);
      if (!match) return f;
      const key = match[1];
      const resolved = env[key];
      if (resolved === undefined) {
        throw new Error(`Env var ${key} required for field ${f.name} but not set`);
      }
      return { ...f, value: resolved };
    }),
  };
}
