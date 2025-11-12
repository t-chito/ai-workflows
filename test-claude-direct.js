#!/usr/bin/env node
/**
 * Claude CLIを直接テストするスクリプト
 *
 * 使い方:
 *   node test-claude-direct.js
 */

import { spawn } from 'child_process';

console.log('Testing: claude -p "Say hello in one word"');
console.log('---');

const claude = spawn('claude', ['-p', 'Say hello in one word'], {
  stdio: ['inherit', 'pipe', 'pipe'],
});

let stdout = '';
let stderr = '';

claude.stdout.on('data', (data) => {
  const text = data.toString();
  console.log('STDOUT:', text);
  stdout += text;
});

claude.stderr.on('data', (data) => {
  const text = data.toString();
  console.log('STDERR:', text);
  stderr += text;
});

claude.on('close', (code) => {
  console.log('---');
  console.log(`Exit code: ${code}`);
  console.log(`Final stdout: "${stdout.trim()}"`);
  console.log(`Final stderr: "${stderr.trim()}"`);

  if (code === 0) {
    console.log('✅ Success!');
  } else {
    console.log('❌ Failed!');
  }
});

claude.on('error', (error) => {
  console.error('Spawn error:', error.message);
});

// 30秒タイムアウト
setTimeout(() => {
  console.log('⏱️  Timeout - killing process');
  claude.kill();
  process.exit(1);
}, 30000);
