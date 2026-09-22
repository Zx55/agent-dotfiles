import { access, readFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const defaultWorkspace = fileURLToPath(new URL('../../', import.meta.url));
export const timeout = 30_000;

export async function exists(filename) {
  try { await access(filename); return true; }
  catch (error) { if (error.code === 'ENOENT') return false; throw error; }
}

export function resolveDependency(name, workspace) {
  const roots = [
    path.join(workspace, 'package.json'),
    ...[process.env.RUNTIME_NODE_MODULES, ...(process.env.NODE_PATH ?? '').split(path.delimiter)]
      .filter(Boolean).map((root) => path.join(root, '__resolver__.cjs')),
  ];
  for (const root of roots) {
    try { return createRequire(path.resolve(root)).resolve(name); }
    catch (error) { if (error.code !== 'MODULE_NOT_FOUND') throw error; }
  }
  throw new Error(`Missing ${name}. Install workspace dependencies or set RUNTIME_NODE_MODULES to the available runtime's node_modules directory.`);
}

export async function dependency(name, workspace) {
  const module = await import(pathToFileURL(resolveDependency(name, workspace)).href);
  // Some CommonJS packages expose APIs only through the ESM default export.
  return module.default && typeof module.default === 'object' ? { ...module.default, ...module } : module;
}

export async function inventory(workspace) {
  const filenames = await readdir(path.join(workspace, 'slides'));
  const suspicious = filenames.filter((name) => /^slide\d.*\.html$/i.test(name) && !/^slide\d{2,}\.html$/.test(name));
  if (suspicious.length) throw new Error(`Use slideNN.html names: ${suspicious.join(', ')}`);
  const slides = filenames.filter((name) => /^slide\d{2,}\.html$/.test(name))
    .map((name) => ({ name, id: Number(name.match(/\d+/)[0]), stem: name.slice(0, -5) }))
    .sort((a, b) => a.id - b.id);
  if (!slides.length) throw new Error('No slideNN.html files. The blank template is not a content slide.');
  for (const [index, slide] of slides.entries()) {
    if (slide.id !== index + 1 || !Number.isSafeInteger(slide.id)) {
      throw new Error(`Slide numbers must be unique and continuous from 1. Found: ${slides.map((s) => s.name).join(', ')}`);
    }
  }
  return slides;
}

export function selectSlides(slides, specification) {
  if (!specification) return slides;
  const selected = new Set();
  for (const token of specification.split(',')) {
    const match = /^(\d+)(?:-(\d+))?$/.exec(token.trim());
    if (!match) throw new Error(`Invalid --slides expression: ${token}`);
    const start = Number(match[1]);
    const end = Number(match[2] ?? match[1]);
    if (start < 1 || end < start || end > slides.length) throw new Error(`Invalid slide range: ${token}`);
    for (let id = start; id <= end; id++) selected.add(id);
  }
  return slides.filter((slide) => selected.has(slide.id));
}

export function sha256(bytes) { return createHash('sha256').update(bytes).digest('hex'); }

// Conservative whole-deck snapshot. Notes and provenance prose do not affect visuals.
export async function visualSnapshot(workspace) {
  const files = {};
  async function walk(relative) {
    const directory = path.join(workspace, relative);
    if (!await exists(directory)) return;
    for (const entry of (await readdir(directory, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
      const name = path.posix.join(relative, entry.name);
      if (entry.isSymbolicLink()) throw new Error(`Copy visual resources into the workspace instead of symlinking: ${name}`);
      if (entry.isDirectory()) await walk(name);
      else if (entry.isFile() && !/\.md$/i.test(name)) files[name] = sha256(await readFile(path.join(workspace, name)));
    }
  }
  await walk('slides');
  await walk('assets');
  return { hash: sha256(JSON.stringify(files)), files };
}

export function assertCanvas(size) {
  if (!Number.isFinite(size.width) || !Number.isFinite(size.height) || size.width <= 0 || size.height <= 0 ||
      Math.abs(size.width / size.height - 16 / 9) > 0.0001) {
    throw new Error(`Expected a positive 16:9 canvas, got ${JSON.stringify(size)}`);
  }
}

export function validatePdf(document, count, size, label) {
  if (document.getPageCount() !== count) throw new Error(`${label}: expected ${count} page(s), got ${document.getPageCount()}`);
  for (const page of document.getPages()) {
    const box = page.getSize();
    if (Math.abs(box.width - size.width * 0.75) > 0.5 || Math.abs(box.height - size.height * 0.75) > 0.5 || page.getRotation().angle !== 0) {
      throw new Error(`${label}: wrong page dimensions or rotation: ${JSON.stringify(box)}`);
    }
  }
}

export async function currentPdfManifest(workspace, outputDir, slides, PDFDocument) {
  const filename = path.join(outputDir, 'manifest.json');
  if (!await exists(filename)) throw new Error('No PDF manifest. Run export-pdf.mjs first.');
  const manifest = JSON.parse(await readFile(filename, 'utf8'));
  if (manifest.version !== 1 || manifest.complete !== true ||
      JSON.stringify(manifest.slides?.map((slide) => slide.name)) !== JSON.stringify(slides.map((slide) => slide.name))) {
    throw new Error('PDF manifest is not a complete export of the current slide sequence. Rerender the full deck.');
  }
  assertCanvas(manifest.canvas);
  const snapshot = await visualSnapshot(workspace);
  if (manifest.visualHash !== snapshot.hash) throw new Error('PDFs are stale: HTML, styles, runtime or assets changed. Rerun export-pdf.mjs. Notes-only changes do not require rendering.');
  for (const slide of manifest.slides) {
    const expected = `pdf/${slide.name.slice(0, -5)}.pdf`;
    if (slide.pdf !== expected) throw new Error(`Unexpected PDF path in manifest: ${slide.pdf}`);
    const bytes = await readFile(path.join(outputDir, expected));
    if (sha256(bytes) !== slide.pdfHash) throw new Error(`${slide.pdf} changed since PDF export. Rerender the full deck.`);
    validatePdf(await PDFDocument.load(bytes), 1, manifest.canvas, slide.pdf);
  }
  return manifest;
}
