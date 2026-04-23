import dotenv from "dotenv";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

dotenv.config();

const REQUIRED_DUNS = [
  "DUNS_COMPANY_NAME_EN",
  "DUNS_COMPANY_NAME_KO",
  "DUNS_REPRESENTATIVE",
  "DUNS_BUSINESS_REGISTRATION_NUMBER",
  "DUNS_ADDRESS_EN",
  "DUNS_PHONE",
  "DUNS_EMAIL",
];

const hasPlaintextEnv = existsSync(resolve(".env"));

const problems = [];
const warnings = [];
const ok = [];

for (const key of REQUIRED_DUNS) {
  const value = process.env[key];
  if (!value || value.includes("replace_me")) {
    problems.push(`${key} missing or still set to placeholder`);
  } else {
    const masked = value.length > 8 ? `${value.slice(0, 3)}***${value.slice(-2)}` : "***";
    ok.push(`${key} present (${masked})`);
  }
}

if (hasPlaintextEnv) {
  warnings.push("Plaintext .env file detected. 1Password is the source of truth — delete .env with `rm .env` to avoid stale/leaked credentials.");
}

console.log("\nbrowser-signup env check\n");
for (const line of ok) console.log(`  ✓ ${line}`);
for (const line of warnings) console.log(`  ⚠ ${line}`);
for (const line of problems) console.log(`  ✗ ${line}`);

if (problems.length) {
  console.log("\nSee README.md → Team Onboarding for how to obtain credentials.\n");
  process.exit(1);
}

console.log("\nReady. Next: npm run flow -- --project=duns-iupdate\n");
