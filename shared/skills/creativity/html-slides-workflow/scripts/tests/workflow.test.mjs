import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtemp, mkdir, readFile, rename, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import {
  currentPdfManifest, dependency, inventory, selectSlides, sha256, validatePdf, visualSnapshot,
} from '../lib/common.mjs';

const skill = fileURLToPath(new URL('../../', import.meta.url));
const python = process.env.RUNTIME_PYTHON || 'python3';

async function fixture(t, count = 2) {
  const parent = await mkdtemp(path.join(tmpdir(), 'html-slide-test-'));
  t.after(() => rm(parent, { recursive: true, force: true }));
  const workspace = path.join(parent, 'test deck with spaces');
  execFileSync(python, [path.join(skill, 'scripts/init_workspace.py'), workspace]);
  const template = await readFile(path.join(workspace, 'slides/template.html'), 'utf8');
  for (let id = 1; id <= count; id++) {
    const number = String(id).padStart(2, '0');
    const html = template.replace('>00</span>', `>${number}</span>`)
      .replace('<!-- Add slide content here. Common layout classes live in slide.css. -->',
        `<h1 class="slide-title">Fixture <span class="accent">${number}</span></h1>`);
    await writeFile(path.join(workspace, 'slides', `slide${number}.html`), html);
  }
  return workspace;
}

async function syntheticPdfs(workspace) {
  // Tests isolate packaging/freshness from browser availability. These are NOT HTML renders.
  const { PDFDocument } = await dependency('pdf-lib', workspace);
  const slides = await inventory(workspace);
  const canvas = { width: 1600, height: 900 };
  const snapshot = await visualSnapshot(workspace);
  const entries = [];
  const output = path.join(workspace, 'exports');
  await mkdir(path.join(output, 'pdf'), { recursive: true });
  for (const slide of slides) {
    const document = await PDFDocument.create();
    const page = document.addPage([1200, 675]);
    page.drawText(`Packaging test ${slide.id}`, { x: 80, y: 500, size: 40 });
    const bytes = await document.save();
    const pdf = `pdf/${slide.stem}.pdf`;
    await writeFile(path.join(output, pdf), bytes);
    entries.push({ ...slide, pdf, pdfHash: sha256(bytes) });
  }
  const manifest = { version: 1, complete: true, canvas, visualHash: snapshot.hash, slides: entries };
  await writeFile(path.join(output, 'manifest.json'), JSON.stringify(manifest));
  return { PDFDocument, slides, output };
}

test('initializer copies resources, preserves skill and refuses overwrite', async (t) => {
  const before = sha256(await readFile(path.join(skill, 'templates/slides/template.html')));
  const workspace = await fixture(t);
  const note = path.join(workspace, 'notes/slide01.md');
  await writeFile(note, 'Do not overwrite');
  const result = spawnSync(python, [path.join(skill, 'scripts/init_workspace.py'), workspace]);
  assert.equal(result.status, 1);
  assert.equal(await readFile(note, 'utf8'), 'Do not overwrite');
  assert.equal(sha256(await readFile(path.join(skill, 'templates/slides/template.html'))), before);
  const help = execFileSync(process.execPath, [path.join(workspace, 'scripts/export-pdf.mjs'), '--help'], { cwd: tmpdir(), encoding: 'utf8' });
  assert.match(help, /--slides/);
});

test('inventory sorts numerically and rejects duplicate IDs or gaps', async (t) => {
  const workspace = await fixture(t, 12);
  const slides = await inventory(workspace);
  assert.equal(slides[9].id, 10);
  assert.deepEqual(selectSlides(slides, '12,2,4-6').map((s) => s.id), [2, 4, 5, 6, 12]);
  assert.throws(() => selectSlides(slides, '0,13'));
  await writeFile(path.join(workspace, 'slides/slide010.html'), 'duplicate');
  await assert.rejects(() => inventory(workspace), /unique and continuous/);
  await rm(path.join(workspace, 'slides/slide010.html'));
  await rename(path.join(workspace, 'slides/slide03.html'), path.join(workspace, 'slides/archived.html'));
  await assert.rejects(() => inventory(workspace), /unique and continuous/);
});

test('freshness permits notes, rejects theme edits and PDF replacement', async (t) => {
  const workspace = await fixture(t);
  const { chromium } = await dependency('playwright', workspace);
  assert.equal(typeof chromium.launch, 'function');
  const { PDFDocument, slides, output } = await syntheticPdfs(workspace);
  await currentPdfManifest(workspace, output, slides, PDFDocument);
  await writeFile(path.join(workspace, 'notes/slide01.md'), '新的口播稿');
  await currentPdfManifest(workspace, output, slides, PDFDocument);
  const theme = path.join(workspace, 'slides/theme.css');
  const original = await readFile(theme, 'utf8');
  await writeFile(theme, original.replace('#8b1e2d', '#000099'));
  await assert.rejects(() => currentPdfManifest(workspace, output, slides, PDFDocument), /stale/);
  await writeFile(theme, original);
  await writeFile(path.join(output, 'pdf/slide01.pdf'), 'not a PDF');
  await assert.rejects(() => currentPdfManifest(workspace, output, slides, PDFDocument), /changed since/);
  const invalid = await PDFDocument.create();
  invalid.addPage([1200, 675]); invalid.addPage([1200, 675]);
  assert.throws(() => validatePdf(invalid, 1, { width: 1600, height: 900 }, 'test'), /expected 1 page/);
});

test('PPTX packages image pages and complete mixed-language notes', { skip: process.env.RUN_PPTX_TESTS !== '1' }, async (t) => {
  const workspace = await fixture(t);
  await syntheticPdfs(workspace);
  await writeFile(path.join(workspace, 'notes/slide02.md'), '\r\n  第一段：C_task < R & O >。\t🚀\r\n\r\n**Markdown retained**，不删标题或符号。\r\n最后一行。\r\n');
  const exporter = path.join(workspace, 'scripts/export-pptx.mjs');
  const result = execFileSync(process.execPath, [exporter], { cwd: tmpdir(), encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 120_000 });
  assert.match(result, /full notes verified/);
  const rejected = spawnSync(process.execPath, [exporter], { encoding: 'utf8', timeout: 120_000 });
  assert.equal(rejected.status, 1);
  assert.match(rejected.stderr, /Output exists/);
  const strict = spawnSync(process.execPath, [exporter, '--check', '--strict-notes'], { encoding: 'utf8', timeout: 120_000 });
  assert.equal(strict.status, 1);
  assert.match(strict.stderr, /Missing or empty note/);
  await writeFile(path.join(workspace, 'notes/slide02.md'), '仅更新口播。');
  const updated = execFileSync(process.execPath, [exporter, '--overwrite'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 120_000 });
  assert.match(updated, /full notes verified/);
});

test('browser renders full deck and isolated preview', { skip: process.env.RUN_BROWSER_TESTS !== '1' }, async (t) => {
  const workspace = await fixture(t);
  const exporter = path.join(workspace, 'scripts/export-pdf.mjs');
  execFileSync(process.execPath, [exporter], { cwd: tmpdir(), encoding: 'utf8', timeout: 120_000 });
  const { PDFDocument } = await dependency('pdf-lib', workspace);
  const pdf = await PDFDocument.load(await readFile(path.join(workspace, 'exports/presentation.pdf')));
  validatePdf(pdf, 2, { width: 1600, height: 900 }, 'HTML render');
  const fullHash = sha256(await readFile(path.join(workspace, 'exports/presentation.pdf')));
  execFileSync(process.execPath, [exporter, '--slides', '2'], { encoding: 'utf8', timeout: 120_000 });
  assert.equal(sha256(await readFile(path.join(workspace, 'exports/presentation.pdf'))), fullHash);
  const preview = await PDFDocument.load(await readFile(path.join(workspace, 'exports/preview/presentation.pdf')));
  validatePdf(preview, 1, { width: 1600, height: 900 }, 'Preview render');
});
