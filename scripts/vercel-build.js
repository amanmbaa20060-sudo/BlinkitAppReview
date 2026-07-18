/**
 * Copy the Phase 5 static dashboard into /public for Vercel.
 * Rewrites asset URLs with a build stamp so browsers cannot reuse stale JS.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const root = path.join(__dirname, "..");
const src = path.join(root, "phase5");
const dest = path.join(root, "public");

const SKIP_NAMES = new Set([
  "scripts",
  "docs",
  "requirements.txt",
  "README.md",
  "stitch_ui_prompt.md",
  "vercel.json",
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

function fileHash(filePath) {
  const buf = fs.readFileSync(filePath);
  return crypto.createHash("sha256").update(buf).digest("hex").slice(0, 10);
}

function ensureLlmStatusFile(targetDir) {
  const statusPath = path.join(targetDir, "llm-status.json");
  if (fs.existsSync(statusPath)) return;

  const bundlePath = path.join(targetDir, "dashboard-data.js");
  const fallback = {
    ok: true,
    run_id: "unknown",
    llm_used_in_pipeline: false,
    provider: null,
    summary: "llm-status.json was missing at build time",
    insight_synthesis: {},
    models: {},
  };

  if (fs.existsSync(bundlePath)) {
    const text = fs.readFileSync(bundlePath, "utf8");
    const prefix = "window.DASHBOARD_DATA = ";
    if (text.startsWith(prefix)) {
      try {
        const payload = JSON.parse(text.slice(prefix.length).replace(/;\s*$/, ""));
        if (payload.llm) {
          fs.writeFileSync(statusPath, JSON.stringify(payload.llm, null, 2) + "\n", "utf8");
          return;
        }
      } catch (_) {
        // keep fallback
      }
    }
  }

  fs.writeFileSync(statusPath, JSON.stringify(fallback, null, 2) + "\n", "utf8");
}

function stampHtml(targetDir, stamp) {
  const indexPath = path.join(targetDir, "index.html");
  let html = fs.readFileSync(indexPath, "utf8");

  const replacements = [
    ["styles.css", `styles.${stamp}.css`],
    ["config.js", `config.${stamp}.js`],
    ["dashboard-data.js", `dashboard-data.${stamp}.js`],
    ["app.js", `app.${stamp}.js`],
    ["llm-status.json", `llm-status.${stamp}.json`],
  ];

  for (const [fromName, toName] of replacements) {
    const fromPath = path.join(targetDir, fromName);
    const toPath = path.join(targetDir, toName);
    if (!fs.existsSync(fromPath)) {
      console.error(`Missing asset for stamping: ${fromName}`);
      process.exit(1);
    }
    fs.copyFileSync(fromPath, toPath);
    html = html.split(fromName).join(toName);
  }

  // Absolute fetch paths used by the inline LLM probe.
  html = html.replaceAll("/llm-status.json", `/llm-status.${stamp}.json`);
  html = html.replaceAll("llm-status.json?v=5", `llm-status.${stamp}.json`);
  html = html.replaceAll("llm-status.json?v=6", `llm-status.${stamp}.json`);

  // Drop stale query cache-busters; hashed filenames are enough.
  html = html.replace(/\.(css|js|json)\?v=\d+/g, ".$1");

  const metaTag = `<meta name="dashboard-build" content="${stamp}" />`;
  if (!html.includes('name="dashboard-build"')) {
    html = html.replace("</head>", `    ${metaTag}\n  </head>`);
  }

  fs.writeFileSync(indexPath, html, "utf8");
  return replacements.map(([, toName]) => toName);
}

fs.rmSync(dest, { recursive: true, force: true });
copyRecursive(src, dest);
ensureLlmStatusFile(dest);

const apiBase = String(process.env.API_BASE_URL || "").replace(/\/$/, "");
const configJs = `window.APP_CONFIG = ${JSON.stringify(
  { API_BASE_URL: apiBase },
  null,
  2
)};\n`;
fs.writeFileSync(path.join(dest, "config.js"), configJs, "utf8");

const dataPath = path.join(dest, "dashboard-data.js");
const stamp = fileHash(dataPath);
const stamped = stampHtml(dest, stamp);

// Prove the published bundle has distinct Q&A confidence values.
const dataText = fs.readFileSync(dataPath, "utf8");
const prefix = "window.DASHBOARD_DATA = ";
if (!dataText.startsWith(prefix)) {
  console.error("dashboard-data.js missing DASHBOARD_DATA payload");
  process.exit(1);
}
const payload = JSON.parse(dataText.slice(prefix.length).replace(/;\s*$/, ""));
const confidences = (payload.discoveryQna || []).map((i) => Number(i.confidence));
const unique = new Set(confidences.map((c) => c.toFixed(4)));
if (unique.size < 5) {
  console.error("Refusing to publish: Discovery Q&A confidences are not distinct enough.", [
    ...unique,
  ]);
  process.exit(1);
}

const required = ["index.html", ...stamped];
for (const file of required) {
  if (!fs.existsSync(path.join(dest, file))) {
    console.error(`Missing required file after copy: ${file}`);
    process.exit(1);
  }
}

fs.writeFileSync(
  path.join(dest, "build-info.json"),
  JSON.stringify(
    {
      stamp,
      builtAt: new Date().toISOString(),
      apiBaseUrl: apiBase || null,
      confidenceScores: (payload.discoveryQna || []).map((i) => ({
        question_id: i.question_id,
        confidence_pct: Math.round(Number(i.confidence) * 1000) / 10,
      })),
    },
    null,
    2
  ) + "\n",
  "utf8"
);

console.log("Copied phase5/ -> public/ for Vercel static deploy");
console.log(`build stamp=${stamp}`);
console.log(`API_BASE_URL=${apiBase || "(empty — pipeline provenance only)"}`);
console.log(
  "confidence:",
  (payload.discoveryQna || [])
    .map((i) => `${i.question_id}=${Math.round(Number(i.confidence) * 1000) / 10}%`)
    .join(" ")
);
