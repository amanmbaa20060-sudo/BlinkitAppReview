/**
 * Copy the Phase 5 static dashboard into /public for Vercel.
 * Publishes only static dashboard files. Python deps live under deploy/
 * and are excluded from Vercel via .vercelignore.
 */
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const src = path.join(root, "phase5");
const dest = path.join(root, "public");

const SKIP_NAMES = new Set([
  "scripts",
  "docs",
  "requirements.txt",
  "README.md",
  "stitch_ui_prompt.md",
]);

function shouldSkip(name) {
  if (SKIP_NAMES.has(name)) return true;
  if (name.endsWith(".py")) return true;
  if (name.endsWith(".md")) return true;
  return false;
}

function copyRecursive(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const entry of fs.readdirSync(from, { withFileTypes: true })) {
    if (shouldSkip(entry.name)) continue;
    const sourcePath = path.join(from, entry.name);
    const destPath = path.join(to, entry.name);
    if (entry.isDirectory()) {
      copyRecursive(sourcePath, destPath);
    } else {
      fs.copyFileSync(sourcePath, destPath);
    }
  }
}

fs.rmSync(dest, { recursive: true, force: true });
copyRecursive(src, dest);

const required = ["index.html", "app.js", "styles.css", "dashboard-data.js"];
for (const file of required) {
  if (!fs.existsSync(path.join(dest, file))) {
    console.error(`Missing required file after copy: ${file}`);
    process.exit(1);
  }
}

console.log("Copied phase5/ -> public/ for Vercel static deploy");
