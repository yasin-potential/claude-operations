import { execFile } from 'node:child_process';

export interface NotifyOptions {
  title: string;
  message: string;
  sound?: boolean;
}

export async function notify(opts: NotifyOptions): Promise<void> {
  const { title, message, sound = true } = opts;

  const banner = `\n[33m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m`;
  const lines = [
    banner,
    `[33m▶ ${title}[0m`,
    message,
    banner,
    '',
  ];
  process.stdout.write(lines.join('\n'));

  if (process.platform === 'darwin') {
    await osascriptNotify(title, message, sound).catch(() => undefined);
  }
}

function osascriptNotify(title: string, message: string, sound: boolean): Promise<void> {
  return new Promise((resolve) => {
    const escapedTitle = title.replace(/"/g, '\\"');
    const escapedMessage = message.replace(/"/g, '\\"');
    const soundClause = sound ? ' sound name "Submarine"' : '';
    const script = `display notification "${escapedMessage}" with title "${escapedTitle}"${soundClause}`;
    execFile('osascript', ['-e', script], () => resolve());
  });
}
