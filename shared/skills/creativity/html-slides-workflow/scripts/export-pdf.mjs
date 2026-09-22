#!/usr/bin/env node
import { mkdir, mkdtemp, readFile, rename, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';
import {
  assertCanvas, defaultWorkspace, dependency, exists, inventory, selectSlides,
  sha256, timeout, validatePdf, visualSnapshot,
} from './lib/common.mjs';

async function readyForPrint(page, slide) {
  await page.addStyleTag({ content: '* { animation: none !important; transition: none !important; }' });
  await page.evaluate(async (limit) => {
    let timer;
    try {
      await Promise.race([
        (async () => {
          await document.fonts.ready;
          await Promise.all([...document.images].map((img) => img.decode()));
          await Promise.all([...document.querySelectorAll('svg image')].map(async (element) => {
            const href = element.getAttribute('href') || element.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
            if (!href) throw new Error('SVG image has no href');
            const image = new Image();
            image.src = new URL(href, element.baseURI).href;
            await image.decode();
          }));
        })(),
        new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('Fonts/images readiness timed out')), limit); }),
      ]);
    } finally { clearTimeout(timer); }
  }, timeout);
  if (await page.locator('.slide').count() !== 1) throw new Error('Each HTML must contain exactly one .slide');
  const bounds = await page.locator('.slide').evaluate((element) => {
    const { x, y, width, height } = element.getBoundingClientRect();
    return { x, y, width, height };
  });
  assertCanvas(bounds);
  if (Math.abs(bounds.x) > 0.1 || Math.abs(bounds.y) > 0.1) throw new Error('Print canvas must start at (0, 0). Check shared print CSS.');
  const number = await page.locator('.slide-number').textContent();
  if (!/^\s*\d+\s*$/.test(number) || Number(number) !== slide.id) throw new Error(`${slide.name}: visible page number must be ${slide.id}`);
  const size = { width: bounds.width, height: bounds.height };
  await page.addStyleTag({ content: `@page { size: ${size.width}px ${size.height}px; margin: 0; }` });
  return size;
}

async function main() {
  const { values } = parseArgs({ options: {
    help: { type: 'boolean', short: 'h' }, check: { type: 'boolean' },
    workspace: { type: 'string' }, out: { type: 'string' }, browser: { type: 'string' },
    slides: { type: 'string' }, title: { type: 'string' },
  } });
  if (values.help) {
    console.log(`Usage: node scripts/export-pdf.mjs [options]
  --workspace DIR  Default: parent of this script's directory, independent of cwd
  --out DIR        Export directory (default: <workspace>/exports)
  --slides 2,4-6   Preview selected slides under <out>/preview; full exports unchanged
  --browser PATH  Chrome/Chromium executable (or CHROME_PATH)
  --title TEXT    PDF metadata title (default: workspace directory name)
  --check         Check inventory, dependencies and browser path only
Outputs: pdf/slideNN.pdf, presentation.pdf, manifest.json
Full reruns replace these generated outputs after validation. Sources are never modified.`);
    return;
  }
  const workspace = path.resolve(values.workspace ?? defaultWorkspace);
  const allSlides = await inventory(workspace);
  const slides = selectSlides(allSlides, values.slides);
  const { chromium } = await dependency('playwright', workspace);
  const { PDFDocument } = await dependency('pdf-lib', workspace);
  const macChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  const executable = values.browser || process.env.CHROME_PATH ||
    (process.platform === 'darwin' && await exists(macChrome) ? macChrome : chromium.executablePath());
  if (!await exists(executable)) throw new Error(`Browser not found: ${executable}. Set --browser or install a Playwright Chromium browser.`);
  const before = await visualSnapshot(workspace);
  console.log(`Slides: ${slides.map((slide) => slide.id).join(', ')}\nBrowser: ${executable}`);
  if (values.check) { console.log('Preflight OK. Browser launch, layout and media readiness have NOT been tested.'); return; }

  const base = path.resolve(values.out ?? path.join(workspace, 'exports'));
  const outputDir = values.slides ? path.join(base, 'preview') : base;
  let browser;
  let staging;
  try {
    try { browser = await chromium.launch({ executablePath: executable, headless: true, timeout }); }
    catch (error) { throw new Error(`Chrome could not start. If the agent environment blocks launch, run the same command in your terminal.\n${error.message}`); }
    await mkdir(outputDir, { recursive: true });
    staging = await mkdtemp(path.join(outputDir, '.pdf-build-'));
    await mkdir(path.join(staging, 'pdf'));
    const context = await browser.newContext({ offline: true, colorScheme: 'light', reducedMotion: 'reduce' });
    const merged = await PDFDocument.create();
    merged.setTitle(values.title ?? path.basename(workspace));
    merged.setCreator('HTML Slide Workflow');
    const entries = [];
    let canvas;
    for (const slide of slides) {
      const page = await context.newPage();
      page.setDefaultTimeout(timeout);
      const errors = [];
      page.on('pageerror', (error) => errors.push(error.message));
      page.on('requestfailed', (request) => errors.push(`${request.url()}: ${request.failure()?.errorText}`));
      page.on('request', (request) => {
        const url = request.url();
        if (url.startsWith('file:')) {
          const relative = path.relative(workspace, fileURLToPath(url));
          if (relative.startsWith(`..${path.sep}`) || relative === '..' || path.isAbsolute(relative)) errors.push(`Resource outside workspace: ${url}`);
          else if (!/^(slides|assets)[/\\]/.test(relative)) errors.push(`Put visual resources under slides/ or assets/: ${url}`);
        } else if (!url.startsWith('data:') && !url.startsWith('blob:')) errors.push(`Nonlocal resource: ${url}`);
      });
      try {
        await page.emulateMedia({ media: 'print' });
        await page.goto(pathToFileURL(path.join(workspace, 'slides', slide.name)).href, { waitUntil: 'load', timeout });
        const size = await readyForPrint(page, slide);
        canvas ??= size;
        if (Math.abs(canvas.width - size.width) > 0.1 || Math.abs(canvas.height - size.height) > 0.1) throw new Error('Canvas dimensions differ across slides');
        const bytes = await page.pdf({ preferCSSPageSize: true, printBackground: true, displayHeaderFooter: false,
          margin: { top: 0, right: 0, bottom: 0, left: 0 }, scale: 1 });
        if (errors.length) throw new Error(errors.join('\n'));
        const document = await PDFDocument.load(bytes);
        validatePdf(document, 1, canvas, slide.name);
        const [copied] = await merged.copyPages(document, [0]);
        merged.addPage(copied);
        const pdf = `pdf/${slide.stem}.pdf`;
        await writeFile(path.join(staging, pdf), bytes);
        entries.push({ ...slide, pdf, pdfHash: sha256(bytes) });
        console.log(`${slide.name} → PDF OK`);
      } finally { await page.close(); }
    }
    const after = await visualSnapshot(workspace);
    if (before.hash !== after.hash) throw new Error('Visual sources changed during rendering. Retry after edits finish.');
    const mergedBytes = await merged.save();
    validatePdf(await PDFDocument.load(mergedBytes), slides.length, canvas, 'Merged PDF');
    await writeFile(path.join(staging, 'presentation.pdf'), mergedBytes);
    const manifest = {
      version: 1, complete: !values.slides, createdAt: new Date().toISOString(), canvas,
      visualHash: before.hash, visualFiles: before.files, slides: entries,
      mergedHash: sha256(mergedBytes),
    };
    await writeFile(path.join(staging, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
    await mkdir(path.join(outputDir, 'pdf'), { recursive: true });
    for (const entry of entries) await rename(path.join(staging, entry.pdf), path.join(outputDir, entry.pdf));
    await rename(path.join(staging, 'presentation.pdf'), path.join(outputDir, 'presentation.pdf'));
    // Manifest is committed last. Interrupted publication cannot pass subsequent hash checks.
    await rename(path.join(staging, 'manifest.json'), path.join(outputDir, 'manifest.json'));
    console.log(`Done: ${path.join(outputDir, 'presentation.pdf')} (${slides.length} pages)`);
  } finally {
    await browser?.close();
    if (staging) await rm(staging, { recursive: true, force: true });
  }
}

main().catch((error) => { console.error(`PDF export failed: ${error.message}`); process.exitCode = 1; });
