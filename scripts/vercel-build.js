/**
 * Copy the Phase 5 static dashboard into /public for Vercel.
 * Also writes config.js from API_BASE_URL (Render API origin).
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

const apiBase = String(process.env.API_BASE_URL || "").replace(/\/$/, "");
const configJs = `window.APP_CONFIG = ${JSON.stringify(
  { API_BASE_URL: apiBase },
  null,
  2
)};\n`;
fs.writeFileSync(path.join(dest, "config.js"), configJs, "utf8");

const required = ["index.html", "app.js", "styles.css", "dashboard-data.js", "llm-status.json", "config.js"];
for (const file of required) {
  if (!fs.existsSync(path.join(dest, file))) {
    console.error(`Missing required file after copy: ${file}`);
    process.exit(1);
  }
}

console.log("Copied phase5/ -> public/ for Vercel static deploy");
console.log(`API_BASE_URL=${apiBase || "(empty — pipeline provenance only)"}`);
