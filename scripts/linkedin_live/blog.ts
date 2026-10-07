// What the blog already has: imported articles and shares, native posts
// and the LinkedIn articles they claim (same rules as scripts/native_posts.py).

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, relative, sep } from "node:path";

export interface BlogEntry {
  path: string; // index.md, relative to the blog root
  kind: "linkedin" | "native" | "share";
  title: string;
  slug: string;
  date: string | null;
  original_url: string | null;
  linkedin_id: string | null;
  share_id: string | null;
  intro_share_id: string | null;
  claims: string[];
  body: string;
}

export const slugify = (s: string) =>
  s.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "")
    .replace(/['’]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

export function claimKey(value: string): string {
  value = value.trim().replace(/^["']|["']$/g, "");
  const pulse = value.match(/linkedin\.com\/pulse\/([^/?#]+)/);
  if (pulse) return "pulse:" + pulse[1].toLowerCase().replace(/\/$/, "");
  if (/^[a-z0-9]{5}$/.test(value)) return "id:" + value;
  return slugify(value);
}

function frontmatter(text: string): string | null {
  const m = text.match(/^---\n([\s\S]*?)\n---\n/);
  return m ? m[1] : null;
}
function scalar(fm: string, key: string): string | null {
  const m = fm.match(new RegExp(`^${key}:[ \\t]*(.*?)\\s*$`, "m"));
  return m ? m[1].trim().replace(/^["']|["']$/g, "") || null : null;
}
function list(fm: string, key: string): string[] {
  const m = (fm + "\n").match(new RegExp(`^${key}:[ \\t]*(.*?)\\n((?:[ \\t]+-.*\\n?)*)`, "m"));
  if (!m) return [];
  const inline = m[1].trim();
  const clean = (v: string) => v.trim().replace(/^["']|["']$/g, "");
  if (inline.startsWith("[")) return inline.slice(1, -1).split(",").map(clean).filter(Boolean);
  if (inline) return [clean(inline)];
  return m[2].split("\n").filter((l) => l.trim()).map((l) => clean(l.trim().slice(1)));
}

function walk(dir: string): string[] {
  if (!existsSync(dir)) return [];
  const out: string[] = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else if (/^index\.mdx?$/.test(name)) out.push(p);
  }
  return out.sort();
}

export function loadBlog(blogDir: string): BlogEntry[] {
  const entries: BlogEntry[] = [];
  const blogRoot = join(blogDir, "src/content/blog");
  const shareRoot = join(blogDir, "src/content/shares");
  for (const [root, isShare] of [[blogRoot, false], [shareRoot, true]] as const) {
    for (const p of walk(root)) {
      const text = readFileSync(p, "utf8");
      const fm = frontmatter(text);
      if (fm === null) continue;
      const rel = relative(root, p).split(sep);
      const intro = fm.match(/^intro_share:\n(?:[ \t]+.*\n)*?[ \t]+share_id:[ \t]*"?(\d+)"?/m);
      entries.push({
        path: relative(blogDir, p),
        kind: isShare ? "share" : rel[0] === "linkedin" ? "linkedin" : "native",
        title: scalar(fm, "title") || rel[rel.length - 2],
        slug: scalar(fm, "slug") || rel[rel.length - 2],
        date: scalar(fm, "date"),
        original_url: scalar(fm, "original_url"),
        linkedin_id: scalar(fm, "linkedin_id"),
        share_id: scalar(fm, "share_id"),
        intro_share_id: intro ? intro[1] : null,
        claims: list(fm, "supersedes_linkedin"),
        body: text.slice(text.indexOf("\n---\n", 4) + 5),
      });
    }
  }
  return entries;
}

export function articleKeys(a: { title: string; basename: string; linkedin_id: string }): Set<string> {
  const keys = new Set([slugify(a.title), "pulse:" + a.basename.toLowerCase()]);
  if (a.linkedin_id) keys.add("id:" + a.linkedin_id);
  return keys;
}

export function nativeKeys(n: BlogEntry): Set<string> {
  const keys = new Set([n.slug, slugify(n.title), ...n.claims.map(claimKey)]);
  keys.delete("");
  return keys;
}

// The native post that supersedes this article, if any.
export function findClaim(a: { title: string; basename: string; linkedin_id: string }, blog: BlogEntry[]): BlogEntry | null {
  const keys = articleKeys(a);
  for (const n of blog.filter((e) => e.kind === "native")) {
    for (const k of nativeKeys(n)) if (keys.has(k)) return n;
  }
  return null;
}

// Block-level comparison of LinkedIn text against a blog post's markdown:
// which LinkedIn paragraphs have no close match in the blog version.
export function missingBlocks(linkedinText: string, markdown: string): string[] {
  const norm = (s: string) => s.toLowerCase().replace(/[‘’]/g, "'").replace(/[“”]/g, '"').replace(/<[^>]+>/g, "").replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/[*_`>#|]/g, "").replace(/\s+/g, " ").trim();
  const plain = markdown
    .replace(/<(style|script|svg)[\s\S]*?<\/\1>/gi, " ")
    .replace(/<\/?(p|div|li|h\d|figcaption|blockquote|br|tr)[^>]*>/gi, "\n")
    .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;|&rsquo;|&lsquo;/g, "'").replace(/&ldquo;|&rdquo;/g, '"').replace(/&mdash;/g, "—").replace(/&ndash;/g, "–");
  const blogText = norm(plain);
  const shingles = (s: string) => { const w = s.split(" "); const out: string[] = []; for (let i = 0; i + 4 < w.length; i++) out.push(w.slice(i, i + 5).join(" ")); return out; };
  const blogShingles = new Set(shingles(blogText));
  const out: string[] = [];
  for (const raw of linkedinText.split(/\n+/)) {
    const b = norm(raw);
    if (b.length < 40) continue;
    if (blogText.includes(b)) continue;
    const sh = shingles(b);
    if (!sh.length) continue;
    // 5-word phrases missing from the blog version: a one-word edit in a
    // 30-word paragraph drops ~5 of 26 phrases.
    const hit = sh.filter((x) => blogShingles.has(x)).length / sh.length;
    if (hit < 0.95) out.push(raw.trim().slice(0, 160));
  }
  return out;
}
