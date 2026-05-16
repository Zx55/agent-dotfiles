#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

function usage() {
  console.error("Usage: build_poster_pptx.mjs <poster-spec.json> [--out exports/poster.pptx]");
}

function argValue(args, name) {
  const idx = args.indexOf(name);
  if (idx === -1) return null;
  if (idx + 1 >= args.length) throw new Error(`Missing value for ${name}`);
  return args[idx + 1];
}

function resolveFromSpec(specDir, candidate) {
  if (!candidate) return null;
  return path.isAbsolute(candidate) ? candidate : path.join(specDir, candidate);
}

function themeColor(spec, key, fallback) {
  return spec.theme?.colors?.[key] || fallback;
}

function addText(slide, element, defaults = {}) {
  slide.addText(element.text || "", {
    x: element.x,
    y: element.y,
    w: element.w,
    h: element.h,
    fontFace: element.fontFace || defaults.fontFace || "Aptos",
    fontSize: element.fontSize || defaults.fontSize || 24,
    color: element.color || defaults.color || "111827",
    bold: Boolean(element.bold),
    italic: Boolean(element.italic),
    align: element.align || "left",
    valign: element.valign || "top",
    margin: element.margin ?? 0.08,
    fit: element.fit || "shrink",
    breakLine: false,
    bullet: element.bullet || undefined,
  });
}

function addImage(slide, element, specDir) {
  const imagePath = resolveFromSpec(specDir, element.path);
  if (!imagePath || !fs.existsSync(imagePath)) {
    throw new Error(`Missing image asset for ${element.id || "image"}: ${element.path}`);
  }

  const options = {
    path: imagePath,
    x: element.x,
    y: element.y,
    w: element.w,
    h: element.h,
    transparency: element.transparency,
    rotate: element.rotate,
  };

  if (element.sizing === "crop") {
    options.sizing = { type: "crop", x: element.x, y: element.y, w: element.w, h: element.h };
  } else if (element.sizing === "contain") {
    options.sizing = { type: "contain", x: element.x, y: element.y, w: element.w, h: element.h };
  }

  slide.addImage(options);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes("--help")) {
    usage();
    return args.length === 0 ? 1 : 0;
  }

  const specPath = path.resolve(args[0]);
  const specDir = path.dirname(specPath);
  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  const outArg = argValue(args, "--out");
  const outPath = path.resolve(specDir, outArg || spec.exports?.pptx || "exports/poster.pptx");
  fs.mkdirSync(path.dirname(outPath), { recursive: true });

  let pptxgen;
  try {
    pptxgen = (await import("pptxgenjs")).default;
  } catch (err) {
    throw new Error("Missing dependency: install pptxgenjs before building poster PPTX");
  }

  const pptx = new pptxgen();
  const width = spec.canvas?.width_in;
  const height = spec.canvas?.height_in;
  if (!width || !height) throw new Error("poster-spec.json must define canvas.width_in and canvas.height_in");

  pptx.defineLayout({ name: "ACADEMIC_POSTER", width, height });
  pptx.layout = "ACADEMIC_POSTER";
  pptx.author = spec.author || "Codex academic-poster";
  pptx.subject = spec.title || "Academic poster";
  pptx.title = spec.title || "Academic poster";
  pptx.company = spec.institution || "";
  pptx.lang = "en-US";
  pptx.theme = {
    headFontFace: spec.theme?.fonts?.title || "Aptos Display",
    bodyFontFace: spec.theme?.fonts?.body || "Aptos",
    lang: "en-US",
  };

  const slide = pptx.addSlide();
  slide.background = { color: themeColor(spec, "background", "FFFFFF") };

  const defaults = {
    fontFace: spec.theme?.fonts?.body || "Aptos",
    fontSize: 24,
    color: themeColor(spec, "ink", "111827"),
  };

  for (const element of spec.elements || []) {
    switch (element.type) {
      case "text":
        addText(slide, element, defaults);
        break;
      case "section_bar": {
        const fill = element.fill || themeColor(spec, "section", "334155");
        const textColor = element.color || themeColor(spec, "sectionText", "FFFFFF");
        slide.addShape(pptx.ShapeType.rect, {
          x: element.x,
          y: element.y,
          w: element.w,
          h: element.h,
          fill: { color: fill },
          line: { color: fill, transparency: 100 },
        });
        addText(
          slide,
          {
            ...element,
            type: "text",
            x: element.x + (element.padX ?? 0.18),
            y: element.y,
            w: element.w - 2 * (element.padX ?? 0.18),
            h: element.h,
            color: textColor,
            bold: element.bold ?? false,
            valign: "mid",
            fontSize: element.fontSize || spec.theme?.section_style?.fontSize || 28,
          },
          defaults
        );
        break;
      }
      case "rect":
        slide.addShape(pptx.ShapeType.rect, {
          x: element.x,
          y: element.y,
          w: element.w,
          h: element.h,
          fill: { color: element.fill || "FFFFFF", transparency: element.fillTransparency ?? 0 },
          line: {
            color: element.line || element.fill || "D1D5DB",
            transparency: element.lineTransparency ?? 0,
            width: element.lineWidth ?? 1,
          },
          radius: element.radius,
        });
        break;
      case "line":
        slide.addShape(pptx.ShapeType.line, {
          x: element.x,
          y: element.y,
          w: element.w,
          h: element.h,
          line: {
            color: element.color || themeColor(spec, "muted", "475569"),
            width: element.width || 1,
            transparency: element.transparency ?? 0,
          },
        });
        break;
      case "image":
        addImage(slide, element, specDir);
        break;
      default:
        throw new Error(`Unsupported element type: ${element.type}`);
    }
  }

  await pptx.writeFile({ fileName: outPath });
  console.log(`Wrote PPTX: ${outPath}`);
}

main().then(
  (code) => process.exit(code || 0),
  (err) => {
    console.error(err.message || err);
    process.exit(1);
  }
);
