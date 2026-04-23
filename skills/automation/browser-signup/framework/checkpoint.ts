import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import type { BrowserContext, Page, TestInfo } from '@playwright/test';

export interface CheckpointData {
  name: string;
  flowName: string;
  url: string;
  savedAt: string;
  storageStatePath: string;
  screenshotPath: string;
}

export function clientSlug(): string | undefined {
  const fromArg = process.argv.find((a) => a.startsWith('--client='));
  if (fromArg) return fromArg.split('=')[1];
  return process.env.CLIENT_SLUG || undefined;
}

export function checkpointDir(flowName: string, runId: string, slug?: string): string {
  const client = slug ?? clientSlug();
  if (client) {
    return resolve(process.cwd(), 'artifacts', client, flowName, runId);
  }
  return resolve(process.cwd(), 'artifacts', flowName, runId);
}

export async function saveCheckpoint(
  name: string,
  page: Page,
  context: BrowserContext,
  flowName: string,
  runId: string,
  testInfo?: TestInfo,
  slug?: string,
): Promise<CheckpointData> {
  const dir = checkpointDir(flowName, runId, slug);
  await mkdir(dir, { recursive: true });

  const storageStatePath = join(dir, `${name}.storage.json`);
  const screenshotPath = join(dir, `${name}.png`);
  const metaPath = join(dir, `${name}.json`);

  await context.storageState({ path: storageStatePath });
  await page.screenshot({ path: screenshotPath, fullPage: true });

  const data: CheckpointData = {
    name,
    flowName,
    url: page.url(),
    savedAt: new Date().toISOString(),
    storageStatePath,
    screenshotPath,
  };

  await writeFile(metaPath, JSON.stringify(data, null, 2));

  if (testInfo) {
    await testInfo.attach(`checkpoint-${name}.json`, { path: metaPath, contentType: 'application/json' });
    await testInfo.attach(`checkpoint-${name}.png`, { path: screenshotPath, contentType: 'image/png' });
  }

  return data;
}

export async function loadCheckpoint(
  name: string,
  flowName: string,
  runId: string,
  slug?: string,
): Promise<CheckpointData> {
  const metaPath = join(checkpointDir(flowName, runId, slug), `${name}.json`);
  if (!existsSync(metaPath)) {
    throw new Error(`Checkpoint "${name}" not found at ${metaPath}`);
  }
  const raw = await readFile(metaPath, 'utf-8');
  return JSON.parse(raw) as CheckpointData;
}

export async function saveResult(
  flowName: string,
  runId: string,
  result: unknown,
  slug?: string,
): Promise<string> {
  const dir = checkpointDir(flowName, runId, slug);
  await mkdir(dir, { recursive: true });
  const path = join(dir, 'result.json');
  await writeFile(path, JSON.stringify(result, null, 2));
  return path;
}

export async function writeHandoff(
  flowName: string,
  runId: string,
  content: string,
  slug?: string,
): Promise<string> {
  const dir = checkpointDir(flowName, runId, slug);
  await mkdir(dir, { recursive: true });
  const path = join(dir, 'handoff.md');
  await writeFile(path, content, 'utf-8');
  return path;
}

export function deriveRunId(explicit?: string): string {
  if (explicit) return explicit;
  return new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').slice(0, 19);
}

export function resumeName(): string | undefined {
  const fromArg = process.argv.find((a) => a.startsWith('--resume='));
  if (fromArg) return fromArg.split('=')[1];
  return process.env.RESUME_FROM || undefined;
}

export function resumeRunId(): string | undefined {
  const fromArg = process.argv.find((a) => a.startsWith('--run-id='));
  if (fromArg) return fromArg.split('=')[1];
  return process.env.RESUME_RUN_ID || undefined;
}

export function ensureParent(path: string): Promise<void> {
  return mkdir(dirname(path), { recursive: true }).then(() => undefined);
}
