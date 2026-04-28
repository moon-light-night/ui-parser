/**
 * Proto generation script for frontend.
 * Uses @protobuf-ts/protoc + protoc-gen-ts from devDependencies.
 * Run via: npm run proto:generate
 */

import { execSync } from 'child_process';
import { existsSync, mkdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');
const binDir = join(projectRoot, 'node_modules', '.bin');
const protoDir = join(projectRoot, '..', 'proto');
const outDir = join(projectRoot, 'src', 'proto', 'generated');

console.log('Proto generation for frontend (@protobuf-ts)');
console.log('=============================================');
console.log(`Proto directory: ${protoDir}`);
console.log(`Output directory: ${outDir}`);

if (!existsSync(outDir)) {
  mkdirSync(outDir, { recursive: true });
}

const protoFiles = ['common.proto', 'screenshot.proto', 'chat.proto', 'system.proto'];

const cmd = [
  join(binDir, 'protoc'),
  `--ts_out ${outDir}`,
  `--proto_path ${protoDir}`,
  ...protoFiles.map(f => join(protoDir, f)),
].join(' ');

console.log(`Running: ${cmd}\n`);

execSync(cmd, {
  stdio: 'inherit',
  cwd: projectRoot,
  env: {
    ...process.env,
    // Make protoc-gen-ts visible to protoc
    PATH: `${binDir}:${process.env.PATH}`,
  },
});

console.log('\nCode generation completed');
console.log(`Generated files are in: ${outDir}`);
