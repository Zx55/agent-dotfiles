#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rename, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import {
  currentPdfManifest, defaultWorkspace, dependency, exists, inventory, sha256, visualSnapshot,
} from './lib/common.mjs';

function run(command, args) {
  try { return execFileSync(command, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 120_000, maxBuffer: 8 * 1024 * 1024 }); }
  catch (error) { throw new Error(`${command} failed: ${error.stderr || error.message}`); }
}

async function main() {
  const { values } = parseArgs({ options: {
    help: { type: 'boolean', short: 'h' }, check: { type: 'boolean' },
    workspace: { type: 'string' }, 'pdf-dir': { type: 'string' }, 'notes-dir': { type: 'string' },
    out: { type: 'string' }, pdftoppm: { type: 'string' }, python: { type: 'string' },
    'strict-notes': { type: 'boolean' }, overwrite: { type: 'boolean' },
  } });
  if (values.help) {
    console.log(`Usage: node scripts/export-pptx.mjs [options]
  --workspace DIR  Default: parent of this script's directory, independent of cwd
  --pdf-dir DIR    Full PDF export directory containing manifest.json (default: exports)
  --notes-dir DIR  Default: <workspace>/notes
  --out FILE       Default: <workspace>/exports/presentation.pptx
  --pdftoppm PATH  Poppler executable (or PDFTOPPM_PATH, otherwise PATH)
  --python PATH    Python 3 for standard-library OOXML checks (or RUNTIME_PYTHON)
  --strict-notes   Require nonempty notes for every slide, including the cover
  --overwrite      Replace an existing PPTX only after the new file passes validation
  --check          Validate PDFs, freshness, notes, dependencies and tools; no PPTX written
Each reviewed PDF becomes a 3200 × 1800 full-slide PNG. Entire Markdown notes are
inserted as text, not parsed or summarized. Missing notes warn and remain blank.
HTML/CSS/assets changes require a new full PDF export. Notes-only edits do not.`);
    return;
  }
  const workspace = path.resolve(values.workspace ?? defaultWorkspace);
  const outputDir = path.resolve(values['pdf-dir'] ?? path.join(workspace, 'exports'));
  const notesDir = path.resolve(values['notes-dir'] ?? path.join(workspace, 'notes'));
  const finalPath = path.resolve(values.out ?? path.join(workspace, 'exports/presentation.pptx'));
  if (path.extname(finalPath).toLowerCase() !== '.pptx') throw new Error('--out must end in .pptx');
  const slides = await inventory(workspace);
  const { PDFDocument } = await dependency('pdf-lib', workspace);
  const manifest = await currentPdfManifest(workspace, outputDir, slides, PDFDocument);
  const { Presentation, PresentationFile, FileBlob } = await dependency('@oai/artifact-tool', workspace);
  const pdftoppm = values.pdftoppm || process.env.PDFTOPPM_PATH || 'pdftoppm';
  const projectPython = path.join(workspace, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  const python = values.python || process.env.RUNTIME_PYTHON || (await exists(projectPython) ? projectPython : 'python3');
  run(pdftoppm, ['-v']);
  run(python, ['-c', 'import sys, zipfile, xml.etree.ElementTree; assert sys.version_info >= (3, 9)']);
  const notes = [];
  for (const slide of slides) {
    const filename = path.join(notesDir, `${slide.stem}.md`);
    const text = await exists(filename) ? await readFile(filename, 'utf8') : '';
    if (!text.trim()) {
      if (values['strict-notes']) throw new Error(`Missing or empty note: ${filename}`);
      console.warn(`Warning: ${slide.stem} has no spoken note; speaker notes will be blank.`);
    }
    // XML 1.0 cannot represent these control characters. Never silently drop text.
    if (/[\x00-\x08\x0B\x0C\x0E-\x1F]/.test(text)) throw new Error(`${filename}: unsupported XML control character`);
    notes.push(text.replace(/\r\n?/g, '\n'));
  }
  console.log(`Slides: ${slides.length}; populated notes: ${notes.filter((text) => text.trim()).length}`);
  if (values.check) { console.log('Preflight OK. PDF pixels and the final PPTX have NOT been rendered or visually inspected.'); return; }
  if (await exists(finalPath) && !values.overwrite) throw new Error(`Output exists: ${finalPath}. Choose --out or explicitly pass --overwrite.`);
  await mkdir(path.dirname(finalPath), { recursive: true });
  const staging = await mkdtemp(path.join(path.dirname(finalPath), '.pptx-build-'));
  try {
    const presentation = Presentation.create({ slideSize: manifest.canvas });
    const expected = { canvas: manifest.canvas, slides: [] };
    for (const [index, entry] of manifest.slides.entries()) {
      const pdfPath = path.join(outputDir, entry.pdf);
      // Check again at consumption time, not just at preflight.
      if (sha256(await readFile(pdfPath)) !== entry.pdfHash) throw new Error(`${entry.pdf} changed during export`);
      const prefix = path.join(staging, entry.stem);
      run(pdftoppm, ['-png', '-singlefile', '-scale-to-x', '3200', '-scale-to-y', '1800', pdfPath, prefix]);
      const png = await readFile(`${prefix}.png`);
      if (png.length < 24 || png.toString('hex', 0, 8) !== '89504e470d0a1a0a' ||
          png.readUInt32BE(16) !== 3200 || png.readUInt32BE(20) !== 1800) throw new Error(`${entry.name}: invalid rendered PNG dimensions`);
      const slide = presentation.slides.add();
      slide.images.add({
        blob: new Uint8Array(png.buffer, png.byteOffset, png.byteLength),
        contentType: 'image/png', alt: `Rendered slide ${entry.id}`, fit: 'contain',
        position: { left: 0, top: 0, width: manifest.canvas.width, height: manifest.canvas.height },
      });
      slide.speakerNotes.textFrame.setText(notes[index]);
      slide.speakerNotes.setVisible(Boolean(notes[index].trim()));
      expected.slides.push({ name: entry.name, notes: notes[index], imageHash: sha256(png) });
      console.log(`${entry.stem}: PDF image + full notes`);
    }
    const candidate = path.join(staging, 'candidate.pptx');
    await (await PresentationFile.exportPptx(presentation)).save(candidate);
    const expectedFile = path.join(staging, 'expected.json');
    await writeFile(expectedFile, JSON.stringify(expected));
    const verifier = fileURLToPath(new URL('./verify_pptx.py', import.meta.url));
    console.log(run(python, [verifier, candidate, expectedFile]).trim());
    const imported = await PresentationFile.importPptx(await FileBlob.load(candidate));
    if (imported.slides.items.length !== slides.length) throw new Error('Artifact Tool reimport changed the slide count');
    if ((await visualSnapshot(workspace)).hash !== manifest.visualHash) throw new Error('Visual sources changed during PPTX export. Rerender PDFs first.');
    // Catch concurrent note edits rather than publishing an unexpectedly old script.
    for (const [index, slide] of slides.entries()) {
      const filename = path.join(notesDir, `${slide.stem}.md`);
      const text = await exists(filename) ? (await readFile(filename, 'utf8')).replace(/\r\n?/g, '\n') : '';
      if (text !== notes[index]) throw new Error(`${slide.stem} notes changed during export. Retry.`);
    }
    if (await exists(finalPath) && !values.overwrite) throw new Error('Output appeared during export. Choose a different --out path.');
    await rename(candidate, finalPath);
    console.log(`Done: ${finalPath}\n${slides.length} image-based slides, exact full notes verified, first-party reimport passed.`);
  } finally {
    await rm(staging, { recursive: true, force: true });
  }
}

main().catch((error) => { console.error(`PPTX export failed: ${error.message}`); process.exitCode = 1; });
