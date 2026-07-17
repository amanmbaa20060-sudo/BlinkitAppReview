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
        const insights = payload.discoveryQna || [];
        const groqCount = insights.filter((i) => i.synthesis_source === "groq_llm").length;
        fallback.llm_used_in_pipeline = groqCount > 0;
        fallback.provider = groqCount ? "groq" : null;
        fallback.run_id = (payload.meta && payload.meta.run_id) || "unknown";
        fallback.summary = groqCount
          ? `Groq LLM used for ${groqCount}/${insights.length} published insights`
          : "No Groq LLM markers found in dashboard bundle";
        fallback.insight_synthesis = { groq_llm: groqCount };
      } catch (_) {
        // keep fallback
      }
    }
  }

  fs.writeFileSync(statusPath, JSON.stringify(fallback, null, 2) + "\n", "utf8");
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

const required = ["index.html", "app.js", "styles.css", "dashboard-data.js", "llm-status.json", "config.js"];
for (const file of required) {
  if (!fs.existsSync(path.join(dest, file))) {
    console.error(`Missing required file after copy: ${file}`);
    process.exit(1);
  }
}

console.log("Copied phase5/ -> public/ for Vercel static deploy");
console.log(`API_BASE_URL=${apiBase || "(empty — pipeline provenance only)"}`);
console.log("llm-status.json ready at public/llm-status.json");
