#!/usr/bin/env python3
"""Check a launch-video scene plan and turn it into a storyboard, a shot list and,
optionally, a HyperFrames composition.

Standard library only. No network. HyperFrames (Apache 2.0, github.com/heygen-com/hyperframes)
is only used if the user has it; this tool just writes the HTML it reads.

Commands
  check      PLAN.json                        length, pacing, text size, claims, call to action
  storyboard PLAN.json --out media/launch/    writes storyboard.md and shotlist.csv
  hyperframes PLAN.json --out media/launch/hf  writes index.html for `npx hyperframes lint/preview/render`

Plan format (media/launch/plan.json)
{
  "title": "Tally launch", "format": "vertical",          # vertical 1080x1920, wide 1920x1080, square 1080x1080
  "brand": {"bg": "#1B2433", "ink": "#FFFFFF", "accent": "#E8664F", "font": "Inter"},
  "voice": "founder",                                     # founder (records it), tts, or none (text only)
  "cta": "Try Tally free at tallyapp.io",
  "claims": [{"text": "212 teams in beta", "source": "founder/context.md"}],
  "scenes": [
    {"id": "hook", "seconds": 4, "vo": "Your standup runs long because nobody says they're stuck.",
     "on_screen": "Nobody says they're stuck", "visual": "screen: Tally board with a red 'stuck' tag",
     "asset": "media/launch/assets/board.png", "motion": "slow push in"}
  ]
}
"""
import argparse
import csv
import html
import json
import os
import re
import sys

FORMATS = {"vertical": (1080, 1920), "wide": (1920, 1080), "square": (1080, 1080)}
WORDS_PER_SEC = 2.6      # a calm read; above about 3 it sounds rushed
MAX_ON_SCREEN = 48       # characters a viewer reads in about 2 seconds
MIN_SCENE, MAX_SCENE = 1.5, 10.0
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
NUM = re.compile(r"\d[\d,.]*\s*(%|x|k|m|\+)?", re.I)


def out(msg=""):
    print(msg)
    sys.stdout.flush()


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def words(text):
    return len(re.findall(r"[A-Za-z0-9']+", text or ""))


def check(plan, min_total=30, max_total=60):
    errors, warnings = [], []
    scenes = plan.get("scenes") or []
    if not scenes:
        return ["The plan has no scenes."], []
    fmt = plan.get("format", "vertical")
    if fmt not in FORMATS:
        errors.append("format must be one of %s" % ", ".join(FORMATS))
    total = 0.0
    ids = set()
    claims = plan.get("claims") or []
    claim_text = " ".join(c.get("text", "") for c in claims)
    for c in claims:
        if not (c.get("source") or "").strip():
            errors.append("claim %r has no source. Add where it came from, or cut it." % c.get("text"))
    for n, sc in enumerate(scenes, 1):
        tag = "scene %d (%s)" % (n, sc.get("id", "?"))
        sid = sc.get("id") or "s%d" % n
        if sid in ids:
            errors.append("%s: id is used twice" % tag)
        ids.add(sid)
        try:
            sec = float(sc.get("seconds"))
        except (TypeError, ValueError):
            errors.append("%s: needs seconds" % tag)
            continue
        total += sec
        if sec < MIN_SCENE:
            errors.append("%s: %.1fs is too short to read or see" % (tag, sec))
        if sec > MAX_SCENE:
            warnings.append("%s: %.1fs is long for a promo; split it or add motion" % (tag, sec))
        vo = sc.get("vo", "")
        if plan.get("voice", "founder") != "none" and vo:
            need = words(vo) / WORDS_PER_SEC
            if need > sec + 0.3:
                errors.append("%s: %d words of voiceover need about %.1fs, but the scene is %.1fs. Cut words or add time."
                              % (tag, words(vo), need, sec))
        text = sc.get("on_screen", "")
        if len(text) > MAX_ON_SCREEN:
            errors.append("%s: on-screen text is %d characters; keep it to %d" % (tag, len(text), MAX_ON_SCREEN))
        if not (sc.get("visual") or "").strip():
            errors.append("%s: say what is on screen (visual)" % tag)
        for field in ("vo", "on_screen"):
            for m in NUM.finditer(sc.get(field, "") or ""):
                figure = m.group(0).strip()
                if figure and figure not in claim_text and "{{" not in (sc.get(field) or ""):
                    errors.append("%s: the figure %r is not in the plan's claims list with a source. "
                                  "Add it there, or use {{your number}}." % (tag, figure))
        asset = sc.get("asset")
        if asset and not asset.startswith(("http://", "https://")) and not os.path.exists(asset):
            warnings.append("%s: asset %s does not exist yet; it is listed in the shot list as a to-do" % (tag, asset))
    if total < min_total or total > max_total:
        errors.append("Total length is %.1fs; a launch promo here is %d to %d seconds." % (total, min_total, max_total))
    if not (plan.get("cta") or "").strip():
        errors.append("Add a call to action (cta): what the viewer should do next.")
    brand = plan.get("brand") or {}
    for key in ("bg", "ink", "accent"):
        if key in brand and not HEX.match(brand[key]):
            errors.append("brand.%s must look like #RRGGBB" % key)
    return errors, warnings


def timeline(plan):
    t, rows = 0.0, []
    for n, sc in enumerate(plan["scenes"], 1):
        sec = float(sc["seconds"])
        rows.append(dict(sc, n=n, start=round(t, 2), end=round(t + sec, 2), id=sc.get("id") or "s%d" % n))
        t += sec
    return rows, round(t, 2)


def mmss(t):
    return "%d:%04.1f" % (int(t) // 60, t - 60 * (int(t) // 60))


def storyboard_md(plan):
    rows, total = timeline(plan)
    w, h = FORMATS.get(plan.get("format", "vertical"), FORMATS["vertical"])
    lines = ["# %s: storyboard" % plan.get("title", "Launch video"), "",
             "- Length: %.0f seconds, %s (%dx%d)" % (total, plan.get("format", "vertical"), w, h),
             "- Voice: %s" % {"founder": "you record the voiceover", "tts": "text to speech",
                              "none": "no voiceover, text on screen only"}.get(plan.get("voice", "founder"), plan.get("voice")),
             "- Call to action: %s" % plan.get("cta", ""), ""]
    if plan.get("claims"):
        lines += ["## Facts used, and where they come from", ""]
        lines += ["- %s (source: %s)" % (c["text"], c["source"]) for c in plan["claims"]]
        lines.append("")
    lines += ["## Scenes", ""]
    for r in rows:
        lines += ["### %d. %s  (%s to %s)" % (r["n"], r["id"], mmss(r["start"]), mmss(r["end"])), "",
                  "- On screen: %s" % r.get("visual", ""),
                  "- Text: %s" % (r.get("on_screen") or "(none)"),
                  "- Voiceover: %s" % (r.get("vo") or "(none)"),
                  "- Motion: %s" % (r.get("motion") or "cut"),
                  "- Asset: %s" % (r.get("asset") or "to make or capture"), ""]
    return "\n".join(lines)


def write_shotlist(plan, path):
    rows, _ = timeline(plan)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["scene", "id", "start_s", "end_s", "seconds", "visual", "on_screen_text", "voiceover",
                     "motion", "asset", "asset_status"])
        for r in rows:
            asset = r.get("asset") or ""
            status = "have it" if asset and os.path.exists(asset) else ("to capture or make" if not asset else "missing")
            wr.writerow([r["n"], r["id"], r["start"], r["end"], r.get("seconds"), r.get("visual", ""),
                         r.get("on_screen", ""), r.get("vo", ""), r.get("motion", ""), asset, status])


def _sid(raw):
    sid = re.sub(r"[^a-z0-9-]", "-", raw.lower()).strip("-") or "scene"
    return sid if sid[0].isalpha() else "s-" + sid


def hyperframes_files(plan, asset_prefix="../assets/"):
    """Return {relative_path: html}. index.html mounts one scene file per scene.

    Follows HyperFrames' composition format (README and `npx hyperframes docs compositions`,
    v0.8.x): scene files wrap everything in <template>, the host id, scene root id and
    timeline key match, and scenes use fromTo so seeking back works.
    """
    rows, total = timeline(plan)
    w, h = FORMATS.get(plan.get("format", "vertical"), FORMATS["vertical"])
    b = {"bg": "#111111", "ink": "#FFFFFF", "accent": "#FF6B4A", "font": "Inter"}
    b.update(plan.get("brand") or {})
    fs = int(min(w, h) * 0.075)
    files, hosts = {}, []
    for r in rows:
        sid = _sid(r["id"])
        dur = r["seconds"]
        inner, tweens = [], []
        asset = r.get("asset") or ""
        if asset and re.search(r"\.(png|jpe?g|webp|gif|svg)$", asset, re.I):
            inner.append('<img id="%s-shot" class="shot" src="%s" alt="">' % (sid, html.escape(asset_prefix + os.path.basename(asset))))
            if "push" in (r.get("motion") or "").lower():
                tweens.append('tl.fromTo("#%s-shot", { scale: 1 }, { scale: 1.08, duration: %s, ease: "none" }, 0);' % (sid, dur))
        elif asset and re.search(r"\.(mp4|webm|mov)$", asset, re.I):
            inner.append('<video id="%s-shot" class="shot clip" data-start="0" data-duration="%s" src="%s" muted playsinline></video>'
                         % (sid, dur, html.escape(asset_prefix + os.path.basename(asset))))
        else:
            inner.append('<div id="%s-todo" class="todo">%s</div>' % (sid, html.escape("Visual to add: " + r.get("visual", ""))))
        if r.get("on_screen"):
            inner.append('<h1 id="%s-line" class="line">%s</h1>' % (sid, html.escape(r["on_screen"])))
            tweens.append('tl.fromTo("#%s-line", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }, 0.15);' % sid)
        files["compositions/%s.html" % sid] = """<template>
  <style>
    #{sid} {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center;
      justify-content: center; gap: 48px; padding: 96px; background: var(--ground); color: var(--ink);
      font-family: var(--font-display); }}
    #{sid} .shot {{ max-width: 86%; max-height: 58%; object-fit: contain; border-radius: 24px; }}
    #{sid} .todo {{ width: 86%; padding: 48px; border: 4px dashed var(--accent); border-radius: 24px;
      font-size: {small}px; text-align: center; }}
    #{sid} .line {{ font-size: {fs}px; font-weight: 700; line-height: 1.1; text-align: center; letter-spacing: -0.02em; }}
  </style>
  <div id="{sid}" data-composition-id="{sid}" data-width="{w}" data-height="{h}">
    {inner}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {tweens}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
""".format(sid=sid, small=int(fs * 0.5), fs=fs, w=w, h=h, inner="\n    ".join(inner),
           tweens="\n    ".join(tweens) or "// no motion in this scene")
        hosts.append("""      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"
           data-start="{start}" data-duration="{dur}" data-track-index="1" data-width="{w}" data-height="{h}"></div>"""
                     .format(sid=sid, start=r["start"], dur=dur, w=w, h=h))
    files["index.html"] = """<!doctype html>
<!-- Made by launch-video (multimedia-skills) from media/launch/plan.json. Edit freely. -->
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={w}, height={h}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      :root {{ --ground: {bg}; --ink: {ink}; --accent: {accent}; --font-display: "{font}", sans-serif; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {w}px; height: {h}px; overflow: hidden; background: var(--ground); }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{w}" data-height="{h}">
{hosts}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""".format(w=w, h=h, bg=b["bg"], ink=b["ink"], accent=b["accent"], font=html.escape(b["font"]),
           total=total, hosts="\n".join(hosts))
    return files


def gate(plan, args):
    errors, warnings = check(plan, args.min, args.max)
    for w in warnings:
        out("warning: " + w)
    for e in errors:
        out("error: " + e)
    if errors:
        out("Fix the plan, then run again.")
    return not errors


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check a launch-video plan and build its outputs.")
    sub = ap.add_subparsers(dest="cmd")
    for name in ("check", "storyboard", "hyperframes"):
        p = sub.add_parser(name)
        p.add_argument("plan")
        p.add_argument("--min", type=float, default=30)
        p.add_argument("--max", type=float, default=60)
        if name != "check":
            p.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help()
        return 2
    plan = load(args.plan)
    if not gate(plan, args):
        return 1
    rows, total = timeline(plan)
    if args.cmd == "check":
        out("OK: %d scenes, %.1f seconds." % (len(rows), total))
        return 0
    os.makedirs(args.out, exist_ok=True)
    if args.cmd == "storyboard":
        md = os.path.join(args.out, "storyboard.md")
        with open(md, "w", encoding="utf-8") as fh:
            fh.write(storyboard_md(plan))
        csv_path = os.path.join(args.out, "shotlist.csv")
        write_shotlist(plan, csv_path)
        out("Wrote %s and %s (%.1f seconds, %d scenes)." % (md, csv_path, total, len(rows)))
        return 0
    index = os.path.join(args.out, "index.html")
    if os.path.exists(index):
        out("%s already exists. Not overwriting it; pick another --out or move it." % index)
        return 2
    files = hyperframes_files(plan)
    for rel, text in files.items():
        path = os.path.join(args.out, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    assets = os.path.join(args.out, "assets")
    os.makedirs(assets, exist_ok=True)
    copied = 0
    for sc in plan["scenes"]:
        src = sc.get("asset") or ""
        if src and os.path.isfile(src):
            dst = os.path.join(assets, os.path.basename(src))
            if not os.path.exists(dst):
                with open(src, "rb") as a, open(dst, "wb") as b2:
                    b2.write(a.read())
                copied += 1
    out("Wrote %s and %d scene files, copied %d assets. Next, in that folder: "
        "`npx hyperframes lint`, then `npx hyperframes preview`, then `npx hyperframes render -o launch.mp4`."
        % (index, len(files) - 1, copied))
    return 0


if __name__ == "__main__":
    sys.exit(main())
