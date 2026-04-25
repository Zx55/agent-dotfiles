import { mkdir, rm, cp } from "node:fs/promises";
import { createWriteStream } from "node:fs";
import { join } from "node:path";
import { spawn } from "node:child_process";

const root = new URL("..", import.meta.url).pathname;
const buildDir = join(root, "build", "xpi");
const outFile = join(root, "build", "zotero-add-local-file-plugin.xpi");

await rm(join(root, "build"), { recursive: true, force: true });
await mkdir(buildDir, { recursive: true });
await cp(join(root, "manifest.json"), join(buildDir, "manifest.json"));
await cp(join(root, "bootstrap.js"), join(buildDir, "bootstrap.js"));
await mkdir(join(buildDir, "dist"), { recursive: true });
await cp(join(root, "dist", "main.js"), join(buildDir, "dist", "main.js"));

await new Promise((resolve, reject) => {
  const child = spawn("zip", ["-qr", outFile, "."], { cwd: buildDir, stdio: "inherit" });
  child.on("exit", code => code === 0 ? resolve(undefined) : reject(new Error(`zip exited ${code}`)));
  child.on("error", reject);
});

console.log(outFile);

