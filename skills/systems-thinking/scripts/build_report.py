#!/usr/bin/env python3
"""Render a systems review payload into an interactive HTML report and an
Obsidian-friendly Markdown document.

Both deliverables come from one JSON payload so they cannot drift, and the
system model is declared once as nodes and edges: this script derives the
HTML's inline SVG and the Markdown's Mermaid block from the same declaration.

Usage:
    python3 build_report.py findings.json [--out-dir DIR] [--html-only|--md-only]

No third-party dependencies, so the HTML is fully self-contained and offline.
See references/findings-schema.md for the payload contract.
"""

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- vocabularies

SEVERITIES = ["critical", "high", "medium", "low"]
KINDS = ["risk", "positive"]
NODE_KINDS = ["actor", "service", "store", "queue", "external", "process"]
EDGE_KINDS = ["sync", "async", "data", "control"]
EVIDENCE_CLASSES = ["observed", "inferred"]
CONFIDENCES = ["high", "medium", "low"]
VERIF_STATES = ["proposed", "executed", "blocked"]
REVIEW_MODES = ["repository", "pull_request", "architecture", "combined"]

STATUS_LABEL = {
    "introduced_by_change": "Introduced by change",
    "made_more_severe_by_change": "Made more severe by change",
    "pre_existing_exposed_by_change": "Pre-existing, exposed by change",
    "unrelated_pre_existing": "Unrelated pre-existing architecture",
    "architectural": "Architectural",
    "positive_pattern": "Positive pattern",
}

MODE_LABEL = {
    "repository": "Repository review",
    "pull_request": "Pull request review",
    "architecture": "Architecture review",
    "combined": "Combined review",
}

CALLOUT = {
    ("risk", "critical"): "danger",
    ("risk", "high"): "danger",
    ("risk", "medium"): "warning",
    ("risk", "low"): "info",
    ("positive", None): "success",
}

# ---------------------------------------------------------------- validation


def validate(payload):
    """Return (errors, warnings). Errors block rendering; warnings do not."""
    errs, warns = [], []

    def need(cond, msg):
        if not cond:
            errs.append(msg)

    need(isinstance(payload, dict), "payload must be a JSON object")
    if errs:
        return errs, warns

    meta = payload.get("meta") or {}
    need(bool(meta.get("slug")), "meta.slug is required (drives output filenames)")
    need(bool(meta.get("title")), "meta.title is required")
    mode = meta.get("review_mode")
    need(mode in REVIEW_MODES, "meta.review_mode must be one of %s" % REVIEW_MODES)
    if not meta.get("target"):
        warns.append("meta.target is empty: the reader cannot tell what was reviewed")
    if not meta.get("coverage_limits"):
        warns.append("meta.coverage_limits is empty: state what the review did not cover")

    model = payload.get("system_model") or {}
    nodes = model.get("nodes") or []
    need(isinstance(nodes, list) and len(nodes) > 0, "system_model.nodes must be a non-empty list")
    ids = set()
    for i, n in enumerate(nodes):
        nid = n.get("id")
        need(bool(nid), "system_model.nodes[%d].id is required" % i)
        need(nid not in ids, "duplicate node id %r" % nid)
        ids.add(nid)
        if not n.get("label"):
            warns.append("node %r has no label" % nid)
        if n.get("kind") and n["kind"] not in NODE_KINDS:
            warns.append("node %r kind %r not in %s" % (nid, n["kind"], NODE_KINDS))
    if len(nodes) > 24:
        warns.append(
            "system_model has %d nodes: this is a diagram rather than an analysis. "
            "Narrow the reviewed scope and record the rest as excluded." % len(nodes)
        )

    for i, e in enumerate(model.get("edges") or []):
        need(e.get("from") in ids, "edge[%d].from %r is not a declared node" % (i, e.get("from")))
        need(e.get("to") in ids, "edge[%d].to %r is not a declared node" % (i, e.get("to")))
        if e.get("kind") and e["kind"] not in EDGE_KINDS:
            warns.append("edge[%d] kind %r not in %s" % (i, e["kind"], EDGE_KINDS))

    for b in model.get("trust_boundaries") or []:
        for nid in b.get("nodes") or []:
            need(nid in ids, "trust boundary %r references unknown node %r" % (b.get("label"), nid))

    seen_fids = set()
    findings = payload.get("findings")
    need(isinstance(findings, list), "findings must be a list (empty is valid)")
    for i, f in enumerate(findings or []):
        tag = "findings[%d]" % i
        fid = f.get("id")
        need(bool(fid), "%s.id is required" % tag)
        need(fid not in seen_fids, "duplicate finding id %r" % fid)
        seen_fids.add(fid)
        kind = f.get("kind")
        need(kind in KINDS, "%s.kind must be one of %s" % (tag, KINDS))
        if kind == "risk":
            need(f.get("severity") in SEVERITIES, "%s.severity must be one of %s" % (tag, SEVERITIES))
        need(f.get("status") in STATUS_LABEL, "%s.status must be one of %s" % (tag, sorted(STATUS_LABEL)))
        if kind == "risk" and f.get("status") == "positive_pattern":
            errs.append("%s is a risk but carries status positive_pattern" % tag)
        if kind == "positive" and f.get("status") != "positive_pattern":
            warns.append("%s is a positive pattern with status %r" % (tag, f.get("status")))
        need(f.get("evidence_class") in EVIDENCE_CLASSES,
             "%s.evidence_class must be one of %s (unknown belongs in open_questions)" % (tag, EVIDENCE_CLASSES))
        need(f.get("confidence") in CONFIDENCES, "%s.confidence must be one of %s" % (tag, CONFIDENCES))
        need(bool(f.get("title")), "%s.title is required" % tag)
        need(bool(f.get("comment")), "%s.comment is required" % tag)

        srcs = f.get("sources") or []
        need(len(srcs) > 0, "%s needs at least one source: the evidence gate requires a location" % tag)
        for j, s in enumerate(srcs):
            need(bool(s.get("location")), "%s.sources[%d].location is required" % (tag, j))
            if not s.get("excerpt"):
                warns.append("%s.sources[%d] has no excerpt: the reader must not have to hunt for context"
                             % (tag, j))
        chain = f.get("causal_chain") or []
        if len(chain) < 2:
            warns.append("%s.causal_chain has %d step(s): a mechanism needs at least two"
                         % (tag, len(chain)))
        if not f.get("recommendation"):
            warns.append("%s has no recommendation" % tag)
        if not f.get("tradeoffs"):
            warns.append("%s has no tradeoffs: a recommendation without cost is not decision-ready" % tag)
        v = f.get("verification") or {}
        if v.get("state") and v["state"] not in VERIF_STATES:
            errs.append("%s.verification.state must be one of %s" % (tag, VERIF_STATES))
        if not v.get("method"):
            warns.append("%s has no verification method" % tag)
        unknown = [nid for nid in (f.get("node_ids") or []) if nid not in ids]
        for nid in unknown:
            errs.append("%s.node_ids references unknown node %r" % (tag, nid))
        if not f.get("node_ids"):
            warns.append("%s has no node_ids: it will not be reachable from the diagram" % tag)

    for q in payload.get("open_questions") or []:
        for fid in q.get("affects") or []:
            if fid not in seen_fids:
                warns.append("open question references unknown finding %r" % fid)
    for p in payload.get("validation_plan") or []:
        for fid in p.get("affects") or []:
            if fid not in seen_fids:
                warns.append("validation item references unknown finding %r" % fid)

    return errs, warns


# ---------------------------------------------------------------- graph layout

NODE_W = 172
NODE_GAP_Y = 26
LAYER_GAP = 98
MARGIN = 26
CHAR_W = 6.35          # ~11.5px sans
LINE_H = 14
MAX_LABEL_CHARS = 25


def wrap_label(text, limit=MAX_LABEL_CHARS, max_lines=3):
    words, lines, cur = str(text or "").split(), [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if len(cand) <= limit or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
        if len(lines) == max_lines - 1 and len(cur) > limit:
            cur = cur[: limit - 1] + "\u2026"
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: limit - 1] + "\u2026"
    return lines or [""]


def find_back_edges(nodes, edges):
    """Iterative DFS marking edges that close a cycle, so layering stays acyclic
    and real feedback loops can be drawn as feedback rather than flattened."""
    adj = {n["id"]: [] for n in nodes}
    for i, e in enumerate(edges):
        if e["from"] != e["to"]:
            adj[e["from"]].append((e["to"], i))
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n["id"]: WHITE for n in nodes}
    back = set()
    for root in [n["id"] for n in nodes]:
        if color[root] != WHITE:
            continue
        stack = [(root, iter(adj[root]))]
        color[root] = GREY
        while stack:
            v, it = stack[-1]
            advanced = False
            for w, idx in it:
                if color[w] == GREY:
                    back.add(idx)
                elif color[w] == WHITE:
                    color[w] = GREY
                    stack.append((w, iter(adj[w])))
                    advanced = True
                    break
            if not advanced:
                color[v] = BLACK
                stack.pop()
    return back


def layout(model):
    nodes = model.get("nodes") or []
    edges = [e for e in (model.get("edges") or [])]
    order_index = {n["id"]: i for i, n in enumerate(nodes)}
    back = find_back_edges(nodes, edges)

    fwd = [(e["from"], e["to"]) for i, e in enumerate(edges) if i not in back and e["from"] != e["to"]]
    preds = {n["id"]: [] for n in nodes}
    succs = {n["id"]: [] for n in nodes}
    for a, b in fwd:
        preds[b].append(a)
        succs[a].append(b)

    # longest-path layering over the acyclic subgraph
    layer = {}

    def depth(nid, seen):
        if nid in layer:
            return layer[nid]
        if nid in seen:
            return 0
        seen.add(nid)
        d = 0 if not preds[nid] else 1 + max(depth(p, seen) for p in preds[nid])
        layer[nid] = d
        return d

    sys.setrecursionlimit(10000)
    for n in nodes:
        depth(n["id"], set())

    # boundary grouping keeps enclosures contiguous within a layer
    group = {}
    for gi, b in enumerate(model.get("trust_boundaries") or []):
        for nid in b.get("nodes") or []:
            group.setdefault(nid, gi)

    layers = {}
    for n in nodes:
        layers.setdefault(layer[n["id"]], []).append(n["id"])
    for k in layers:
        layers[k].sort(key=lambda nid: (group.get(nid, 99), order_index[nid]))

    # two barycenter passes to reduce crossings, boundary grouping preserved
    for _ in range(2):
        pos = {nid: i for k in layers for i, nid in enumerate(layers[k])}
        for k in sorted(layers):
            if k == 0:
                continue
            def bary(nid):
                ps = [pos[p] for p in preds[nid] if p in pos]
                return sum(ps) / len(ps) if ps else pos[nid]
            layers[k].sort(key=lambda nid: (group.get(nid, 99), bary(nid), order_index[nid]))

    # geometry
    boxes = {}
    for n in nodes:
        lines = wrap_label(n.get("label") or n["id"])
        boxes[n["id"]] = {"lines": lines, "h": max(46, 30 + LINE_H * len(lines))}

    col_h = {}
    for k, ids in layers.items():
        col_h[k] = sum(boxes[i]["h"] for i in ids) + NODE_GAP_Y * (len(ids) - 1)
    tallest = max(col_h.values()) if col_h else 0

    for k in sorted(layers):
        y = MARGIN + (tallest - col_h[k]) / 2.0
        x = MARGIN + k * (NODE_W + LAYER_GAP)
        for nid in layers[k]:
            b = boxes[nid]
            b.update(x=x, y=y, w=NODE_W, layer=k)
            y += b["h"] + NODE_GAP_Y

    n_back = len([i for i in back]) + len([e for e in edges if e["from"] == e["to"]])
    feedback_lanes = max(0, n_back)
    width = MARGIN * 2 + len(layers) * NODE_W + max(0, len(layers) - 1) * LAYER_GAP
    height = MARGIN * 2 + tallest + (26 + 18 * feedback_lanes if feedback_lanes else 0)

    return {"boxes": boxes, "layers": layers, "back": back, "edges": edges,
            "width": width, "height": height, "base_bottom": MARGIN + tallest}


# ---------------------------------------------------------------- svg emit

def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def bezier_mid(x1, y1, c1x, c1y, c2x, c2y, x2, y2):
    t = 0.5
    mt = 1 - t
    x = mt ** 3 * x1 + 3 * mt ** 2 * t * c1x + 3 * mt * t ** 2 * c2x + t ** 3 * x2
    y = mt ** 3 * y1 + 3 * mt ** 2 * t * c1y + 3 * mt * t ** 2 * c2y + t ** 3 * y2
    return x, y


def edge_label(x, y, text):
    if not text:
        return ""
    w = len(str(text)) * 6.15 + 8
    return (
        '<rect x="%.1f" y="%.1f" width="%.1f" height="13" rx="2" fill="var(--surface)" '
        'stroke="var(--rule)" stroke-width="0.7"/>'
        '<text class="elabel" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
        % (x - w / 2, y - 6.5, w, x, y + 3.4, esc(text))
    )


def render_svg(model, lay, hits):
    boxes, edges, back = lay["boxes"], lay["edges"], lay["back"]
    node_by_id = {n["id"]: n for n in model.get("nodes") or []}
    parts = [
        '<svg class="model" viewBox="0 0 %d %d" width="%d" role="img" '
        'aria-label="System model diagram" xmlns="http://www.w3.org/2000/svg">'
        % (lay["width"], lay["height"], lay["width"]),
        '<defs>'
        '<marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse"><path d="M0.5 0.8 L7 4 L0.5 7.2 z" fill="var(--rule-strong)"/></marker>'
        '<marker id="ahf" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse"><path d="M0.5 0.8 L7 4 L0.5 7.2 z" fill="var(--high)"/></marker>'
        '</defs>',
    ]

    # trust boundaries behind the nodes, drawn only when the enclosure is honest
    caption_only = []
    for b in model.get("trust_boundaries") or []:
        members = [nid for nid in (b.get("nodes") or []) if nid in boxes]
        if not members:
            continue
        xs0 = min(boxes[m]["x"] for m in members) - 12
        ys0 = min(boxes[m]["y"] for m in members) - 19
        xs1 = max(boxes[m]["x"] + boxes[m]["w"] for m in members) + 12
        ys1 = max(boxes[m]["y"] + boxes[m]["h"] for m in members) + 12
        intruder = any(
            nid not in members
            and boxes[nid]["x"] >= xs0 and boxes[nid]["x"] + boxes[nid]["w"] <= xs1
            and boxes[nid]["y"] >= ys0 and boxes[nid]["y"] + boxes[nid]["h"] <= ys1
            for nid in boxes
        )
        if intruder:
            caption_only.append(b)
            continue
        parts.append('<rect class="boundary" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4"/>'
                     % (xs0, ys0, xs1 - xs0, ys1 - ys0))
        parts.append('<text class="blabel" x="%.1f" y="%.1f">%s</text>'
                     % (xs0 + 5, ys0 + 12, esc((b.get("label") or "").upper())))

    # edges
    lane = 0
    for i, e in enumerate(edges):
        a, b = boxes.get(e["from"]), boxes.get(e["to"])
        if not a or not b:
            continue
        kind = e.get("kind") or "sync"
        lbl = e.get("label")
        is_back = i in back or e["from"] == e["to"]
        cls = "edge %s%s" % (kind, " feedback" if is_back else "")
        marker = "ahf" if is_back else "ah"

        if is_back:
            lane += 1
            ybase = lay["base_bottom"] + 14 + 18 * (lane - 1)
            x1, y1 = a["x"] + a["w"] / 2, a["y"] + a["h"]
            x2, y2 = b["x"] + b["w"] / 2, b["y"] + b["h"]
            d = ("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f"
                 % (x1, y1, x1, ybase, x2, ybase, x2, y2))
            parts.append('<path class="%s" d="%s" marker-end="url(#%s)"/>' % (cls, d, marker))
            parts.append(edge_label((x1 + x2) / 2, ybase, lbl))
            continue

        if a["layer"] == b["layer"]:
            x1, y1 = a["x"] + a["w"], a["y"] + a["h"] / 2
            x2, y2 = b["x"] + b["w"], b["y"] + b["h"] / 2
            off = 34
            d = ("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f"
                 % (x1, y1, x1 + off, y1, x2 + off, y2, x2, y2))
            parts.append('<path class="%s" d="%s" marker-end="url(#%s)"/>' % (cls, d, marker))
            parts.append(edge_label(max(x1, x2) + off * 0.62, (y1 + y2) / 2, lbl))
            continue

        x1, y1 = a["x"] + a["w"], a["y"] + a["h"] / 2
        x2, y2 = b["x"], b["y"] + b["h"] / 2
        dx = max(28.0, (x2 - x1) * 0.45)
        skip = abs(b["layer"] - a["layer"]) > 1
        bow = -18 if skip else 0
        c1 = (x1 + dx, y1 + bow)
        c2 = (x2 - dx, y2 + bow)
        d = ("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f"
             % (x1, y1, c1[0], c1[1], c2[0], c2[1], x2, y2))
        parts.append('<path class="%s" d="%s" marker-end="url(#%s)"/>' % (cls, d, marker))
        mx, my = bezier_mid(x1, y1, c1[0], c1[1], c2[0], c2[1], x2, y2)
        parts.append(edge_label(mx, my, lbl))

    # nodes on top
    for nid, bx in boxes.items():
        n = node_by_id.get(nid, {})
        kind = n.get("kind") or "service"
        count = hits.get(nid, 0)
        parts.append(
            '<g class="node n-%s" data-node-id="%s" data-node-label="%s" tabindex="0" role="button" '
            'aria-label="%s, %d finding(s)">'
            % (esc(kind), esc(nid), esc(n.get("label") or nid), esc(n.get("label") or nid), count)
        )
        rx = 14 if kind == "actor" else 3
        parts.append('<rect class="hitpad" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
                     % (bx["x"] - 4, bx["y"] - 4, bx["w"] + 8, bx["h"] + 8))
        parts.append('<rect class="nodebox" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d"/>'
                     % (bx["x"], bx["y"], bx["w"], bx["h"], rx))
        parts.append('<text class="nkind" x="%.1f" y="%.1f">%s</text>'
                     % (bx["x"] + 9, bx["y"] + 14, esc(kind.upper())))
        ty = bx["y"] + 29
        for line in bx["lines"]:
            parts.append('<text class="nlabel" x="%.1f" y="%.1f">%s</text>'
                         % (bx["x"] + 9, ty, esc(line)))
            ty += LINE_H
        if count:
            cx, cy = bx["x"] + bx["w"] - 11, bx["y"] + 11
            parts.append('<circle class="badge" cx="%.1f" cy="%.1f" r="8.5"/>' % (cx, cy))
            parts.append('<text class="badgetext" x="%.1f" y="%.1f" text-anchor="middle">%d</text>'
                         % (cx, cy + 3, count))
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts), caption_only


# ---------------------------------------------------------------- mermaid emit

MERMAID_SHAPE = {
    "actor": '{id}(["{label}"])',
    "service": '{id}["{label}"]',
    "store": '{id}[("{label}")]',
    "queue": '{id}[["{label}"]]',
    "external": '{id}{{{{"{label}"}}}}',
    "process": '{id}[/"{label}"/]',
}


def mm_id(nid):
    s = re.sub(r"[^0-9A-Za-z_]", "_", str(nid))
    return s if s and not s[0].isdigit() else "n_" + s


def mm_text(s):
    return str(s or "").replace('"', "'").replace("|", "/")


def render_mermaid(model):
    lines = ["flowchart LR"]
    members = set()
    for b in model.get("trust_boundaries") or []:
        for nid in b.get("nodes") or []:
            members.add(nid)
    declared = set()

    def decl(n):
        kind = n.get("kind") or "service"
        tpl = MERMAID_SHAPE.get(kind, MERMAID_SHAPE["service"])
        return tpl.format(id=mm_id(n["id"]), label=mm_text(n.get("label") or n["id"]))

    by_id = {n["id"]: n for n in model.get("nodes") or []}
    for gi, b in enumerate(model.get("trust_boundaries") or []):
        lines.append('    subgraph tb%d["%s"]' % (gi, mm_text(b.get("label") or "boundary")))
        for nid in b.get("nodes") or []:
            if nid in by_id and nid not in declared:
                lines.append("        " + decl(by_id[nid]))
                declared.add(nid)
        lines.append("    end")
    for n in model.get("nodes") or []:
        if n["id"] not in declared:
            lines.append("    " + decl(n))
            declared.add(n["id"])
    for e in model.get("edges") or []:
        arrow = "-.->" if (e.get("kind") in ("async", "control")) else "-->"
        lbl = mm_text(e.get("label"))
        mid = "|%s|" % lbl if lbl else ""
        lines.append("    %s %s%s %s" % (mm_id(e["from"]), arrow, mid, mm_id(e["to"])))
    return "\n".join(lines)


# ---------------------------------------------------------------- html body

def chip(text, cls=""):
    return '<span class="chip %s">%s</span>' % (cls, esc(text))


def sev_chip(f):
    if f.get("kind") == "positive":
        return chip("positive pattern", "pos")
    sev = f.get("severity") or "low"
    return chip(sev, "sev-%s" % sev)


def tb_cell(label, value, mono=False):
    if not value:
        return ""
    return ('<div class="tb-cell"><span class="label">%s</span>'
            '<span class="val%s">%s</span></div>'
            % (esc(label), " mono" if mono else "", esc(value)))


def joinlist(v):
    if not v:
        return ""
    if isinstance(v, str):
        return v
    return ", ".join(str(x) for x in v)


def block(label, body_html):
    if not body_html:
        return ""
    return '<div class="block"><span class="label">%s</span>%s</div>' % (esc(label), body_html)


def ul(items):
    if not items:
        return ""
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % esc(i) for i in items)


def render_html_body(payload, lay, svg, caption_only):
    meta = payload.get("meta") or {}
    model = payload.get("system_model") or {}
    findings = payload.get("findings") or []
    out = []

    # ---- title block
    out.append('<header class="titleblock"><div class="wrap">')
    out.append('<div class="tb-mode"><span class="dot"></span><span class="label">%s</span></div>'
               % esc(MODE_LABEL.get(meta.get("review_mode"), "Systems review")))
    out.append("<h1>%s</h1>" % esc(meta.get("title")))
    if meta.get("inferred_purpose"):
        out.append('<p class="tb-sub"><span class="label">Inferred purpose</span> %s</p>'
                   % esc(meta["inferred_purpose"]))
    out.append('<div class="tb-grid">')
    out.append(tb_cell("Target", meta.get("target"), mono=True))
    out.append(tb_cell("Baseline", meta.get("baseline"), mono=True))
    out.append(tb_cell("Date", meta.get("date"), mono=True))
    risks = [f for f in findings if f.get("kind") == "risk"]
    tally = " · ".join("%d %s" % (len([f for f in risks if f.get("severity") == s]), s)
                       for s in SEVERITIES if any(f.get("severity") == s for f in risks))
    out.append(tb_cell("Findings", "%d (%s)" % (len(findings), tally) if tally else str(len(findings))))
    out.append(tb_cell("Depth", meta.get("depth")))
    out.append(tb_cell("Scope included", joinlist(meta.get("scope_included")), mono=True))
    out.append(tb_cell("Scope excluded", joinlist(meta.get("scope_excluded")), mono=True))
    out.append("</div></div></header>")

    out.append('<div class="wrap">')
    out.append('<div class="filterbar" id="filterbar"><span id="filtertext"></span>'
               '<button type="button">Clear</button></div>')

    # ---- headline
    headline = payload.get("headline") or []
    if headline:
        out.append('<section><div class="sec-head"><h2>What matters most</h2></div>'
                   '<div class="card"><ul class="headline">')
        for i, h in enumerate(headline, 1):
            out.append('<li data-n="%02d">%s</li>' % (i, esc(h)))
        out.append("</ul></div></section>")

    # ---- system model
    out.append('<section><div class="sec-head"><h2>System model as reviewed</h2>'
               '<span class="count">click a component to see its findings</span></div>')
    out.append('<div class="card pad">')
    if model.get("summary"):
        out.append('<p class="model-note">%s</p>' % esc(model["summary"]))
    out.append('<div class="diagram-scroll">%s</div>' % svg)
    out.append('<div class="legend">'
               '<span><i class="sw"></i>component</span>'
               '<span><i class="sw store"></i>state or queue</span>'
               '<span><i></i>sync</span>'
               '<span><i class="async"></i>async</span>'
               '<span><i class="control"></i>control</span>'
               '<span><i class="feedback"></i>feedback loop</span>'
               '</div>')
    for b in caption_only:
        out.append('<p class="model-note" style="margin-top:.7rem"><span class="label">'
                   'Trust boundary</span> %s encloses %s (not drawn: the layout interleaves '
                   'non-members).</p>' % (esc(b.get("label")), esc(joinlist(b.get("nodes")))))
    if model.get("sources_of_truth"):
        out.append('<p class="model-note" style="margin-top:.7rem">'
                   '<span class="label">Sources of truth</span> %s</p>'
                   % esc(joinlist(model["sources_of_truth"])))
    out.append("</div></section>")

    # ---- summary table
    out.append('<section><div class="sec-head"><h2>Findings</h2>'
               '<span class="count">%d</span></div>' % len(findings))
    if not findings:
        out.append('<div class="card empty">No findings passed the evidence gate at this scope. '
                   'The coverage limits and open questions below describe what that does and does '
                   'not rule out.</div>')
    else:
        out.append('<div class="card" style="overflow-x:auto;margin-bottom:1.2rem">'
                   '<table class="summary"><thead><tr>'
                   '<th>ID</th><th>Finding</th><th>Severity</th><th>Status</th>'
                   '<th>Evidence</th><th>Confidence</th></tr></thead><tbody>')
        for f in findings:
            out.append('<tr data-nodes="%s"><td class="id"><a href="#%s">%s</a></td>'
                       '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                       % (esc(" ".join(f.get("node_ids") or [])), esc(f.get("id")), esc(f.get("id")),
                          esc(f.get("title")), sev_chip(f),
                          esc(STATUS_LABEL.get(f.get("status"), f.get("status") or "")),
                          esc(f.get("evidence_class") or ""), esc(f.get("confidence") or "")))
        out.append("</tbody></table></div>")

    # ---- detailed findings
    for f in findings:
        kind = f.get("kind")
        sev = f.get("severity") or ""
        out.append('<article class="finding k-%s s-%s" id="%s" data-nodes="%s">'
                   % (esc(kind), esc(sev), esc(f.get("id")), esc(" ".join(f.get("node_ids") or []))))
        out.append('<button class="f-head" type="button">')
        out.append('<div class="f-meta"><span class="fid">%s</span>%s%s%s%s</div>'
                   % (esc(f.get("id")), sev_chip(f),
                      chip(STATUS_LABEL.get(f.get("status"), ""), "plain"),
                      chip("%s evidence" % (f.get("evidence_class") or ""), "plain"),
                      chip("%s confidence" % (f.get("confidence") or ""), "plain")))
        out.append("<h3>%s</h3>" % esc(f.get("title")))
        if f.get("lenses"):
            out.append('<div class="f-lenses">Lenses · %s</div>' % esc(joinlist(f["lenses"])))
        out.append('<div class="f-hint">Highlight on diagram</div>')
        out.append("</button>")

        out.append('<div class="panes">')
        # evidence pane
        out.append('<div class="pane evidence"><span class="label">Evidence</span>')
        for s in f.get("sources") or []:
            out.append('<div class="src"><div class="src-loc">%s</div>' % esc(s.get("location")))
            if s.get("excerpt"):
                prose = s.get("lang") == "prose" or (
                    "\n" not in str(s["excerpt"]) and len(str(s["excerpt"])) > 160)
                if prose:
                    out.append('<p class="excerpt-quote">%s</p>' % esc(s["excerpt"]))
                else:
                    out.append("<pre>%s</pre>" % esc(s["excerpt"]))
            if s.get("note"):
                out.append('<p class="note">%s</p>' % esc(s["note"]))
            out.append("</div>")
        out.append("</div>")

        # reasoning pane
        out.append('<div class="pane"><span class="label">Comment</span>')
        out.append('<p class="comment">%s</p>' % esc(f.get("comment")))
        chain = f.get("causal_chain") or []
        if chain:
            out.append('<span class="label">Mechanism</span><ol class="trace">')
            for step in chain:
                out.append("<li>%s</li>" % esc(step))
            out.append("</ol>")
        if f.get("affected"):
            out.append(block("Affected", '<div class="affected">%s</div>'
                             % "".join(chip(a, "plain") for a in f["affected"])))
        if f.get("recommendation"):
            out.append('<div class="block rec"><span class="label">Recommendation</span>'
                       "<p>%s</p></div>" % esc(f["recommendation"]))
        if f.get("tradeoffs"):
            out.append(block("Tradeoffs", "<p>%s</p>" % esc(f["tradeoffs"])))
        if f.get("alternatives"):
            out.append(block("Alternatives", ul(f["alternatives"])))
        if f.get("acceptance"):
            out.append(block("When this is acceptable", "<p>%s</p>" % esc(f["acceptance"])))
        if f.get("assumptions"):
            out.append(block("Assumptions", ul(f["assumptions"])))
        v = f.get("verification") or {}
        if v.get("method") or v.get("state"):
            inner = "<p>%s%s</p>" % (esc(v.get("method") or ""),
                                     '<span class="state">%s</span>'
                                     % chip(v.get("state") or "proposed",
                                            "solid" if v.get("state") == "executed" else "plain"))
            if v.get("result"):
                inner += "<p>%s</p>" % esc(v["result"])
            out.append('<div class="verif">%s</div>' % block("Verification", inner))
        out.append("</div></div></article>")
    out.append("</section>")

    # ---- open questions
    qs = payload.get("open_questions") or []
    if qs:
        out.append('<section><div class="sec-head"><h2>Open questions and uncertainties</h2>'
                   '<span class="count">%d</span></div>' % len(qs))
        for q in qs:
            out.append('<div class="qcard"><h3>%s</h3>' % esc(q.get("question")))
            if q.get("affects"):
                out.append('<p><span class="label">Affects</span> %s</p>' % esc(joinlist(q["affects"])))
            if q.get("why_it_matters"):
                out.append("<p>%s</p>" % esc(q["why_it_matters"]))
            if q.get("how_to_resolve"):
                out.append('<p><span class="label">How to resolve</span> %s</p>'
                           % esc(q["how_to_resolve"]))
            out.append("</div>")
        out.append("</section>")

    # ---- coverage
    cov = []
    for label, key in [("Sampled paths", "sampled_paths"), ("Coverage limits", "coverage_limits"),
                       ("Unavailable evidence", "unavailable_evidence"), ("Assumptions", "assumptions")]:
        vals = meta.get(key)
        if vals:
            cov.append('<div class="block"><span class="label">%s</span>%s</div>'
                       % (esc(label), ul(vals if isinstance(vals, list) else [vals])))
    if cov:
        out.append('<section><div class="sec-head"><h2>Coverage and limits</h2></div>'
                   '<div class="card pad">%s</div></section>' % "".join(cov))

    # ---- validation plan
    plan = payload.get("validation_plan") or []
    if plan:
        out.append('<section><div class="sec-head"><h2>Validation plan</h2>'
                   '<span class="count">proposed unless marked otherwise</span></div>'
                   '<div class="card"><ol class="plan">')
        for p in sorted(plan, key=lambda x: x.get("order", 0)):
            bits = []
            if p.get("affects"):
                bits.append(joinlist(p["affects"]))
            bits.append(p.get("state") or "proposed")
            if p.get("notes"):
                bits.append(p["notes"])
            out.append("<li>%s<span class=\"meta\">%s</span></li>"
                       % (esc(p.get("action")), esc(" · ".join(bits))))
        out.append("</ol></div></section>")

    note = meta.get("reviewer_note") or ""
    out.append('<footer class="foot">Read-only systems review · verification items are proposals '
               'unless marked executed%s</footer>' % (" · " + esc(note) if note else ""))
    out.append("</div>")
    return "\n".join(x for x in out if x)


# ---------------------------------------------------------------- markdown

def md_callout(kind, sev, title, body_lines):
    ctype = CALLOUT.get((kind, sev if kind == "risk" else None), "note")
    lines = ["> [!%s] %s" % (ctype, title)]
    for line in body_lines:
        lines.extend(("> " + l).rstrip() for l in str(line).split("\n"))
    return "\n".join(lines)


def render_markdown(payload, mermaid):
    meta = payload.get("meta") or {}
    model = payload.get("system_model") or {}
    findings = payload.get("findings") or []
    risks = [f for f in findings if f.get("kind") == "risk"]

    tags = list(meta.get("obsidian_tags") or [])
    for t in ["review/systems-thinking", "review-mode/%s" % (meta.get("review_mode") or "unknown")]:
        if t not in tags:
            tags.append(t)
    for s in SEVERITIES:
        if any(f.get("severity") == s for f in risks):
            tags.append("severity/%s" % s)

    L = ["---", "title: %s" % json.dumps(meta.get("title") or "", ensure_ascii=False), "tags:"]
    L += ["  - %s" % t for t in tags]
    for key, val in [("review-mode", meta.get("review_mode")), ("target", meta.get("target")),
                     ("baseline", meta.get("baseline")), ("date", meta.get("date"))]:
        if val:
            L.append("%s: %s" % (key, json.dumps(str(val), ensure_ascii=False)))
    L.append("findings: %d" % len(findings))
    L.append("---")
    L.append("")
    L.append("# %s" % (meta.get("title") or "Systems review"))
    L.append("")
    L.append("*%s · read-only. Verification items are proposals unless marked executed.*"
             % MODE_LABEL.get(meta.get("review_mode"), "Systems review"))
    L.append("")

    rows = [("Target", meta.get("target")), ("Baseline", meta.get("baseline")),
            ("Date", meta.get("date")), ("Inferred purpose", meta.get("inferred_purpose")),
            ("Depth", meta.get("depth")),
            ("Scope included", joinlist(meta.get("scope_included"))),
            ("Scope excluded", joinlist(meta.get("scope_excluded")))]
    rows = [(k, v) for k, v in rows if v]
    if rows:
        L += ["| Field | Value |", "| --- | --- |"]
        L += ["| %s | %s |" % (k, str(v).replace("|", "\\|")) for k, v in rows]
        L.append("")

    if payload.get("headline"):
        L.append("## What matters most")
        L.append("")
        for i, h in enumerate(payload["headline"], 1):
            L.append("%d. %s" % (i, h))
        L.append("")

    L.append("## System model as reviewed")
    L.append("")
    if model.get("summary"):
        L += [model["summary"], ""]
    L += ["```mermaid", mermaid, "```", ""]
    if model.get("sources_of_truth"):
        L += [md_callout("positive", None, "Sources of truth",
                         ["- %s" % s for s in (model["sources_of_truth"] if
                          isinstance(model["sources_of_truth"], list) else [model["sources_of_truth"]])]), ""]

    L.append("## Findings")
    L.append("")
    if not findings:
        L += [md_callout("positive", None, "No findings passed the evidence gate",
                         ["Nothing at this scope met the evidence bar. See coverage limits and open "
                          "questions for what that does and does not rule out."]), ""]
    else:
        L += ["| ID | Finding | Severity | Status | Evidence | Confidence |",
              "| --- | --- | --- | --- | --- | --- |"]
        for f in findings:
            sev = "positive" if f.get("kind") == "positive" else (f.get("severity") or "")
            L.append("| %s | %s | %s | %s | %s | %s |"
                     % (f.get("id"), str(f.get("title") or "").replace("|", "\\|"), sev,
                        STATUS_LABEL.get(f.get("status"), ""), f.get("evidence_class") or "",
                        f.get("confidence") or ""))
        L.append("")

    for f in findings:
        sev = f.get("severity")
        head = "### %s — %s" % (f.get("id"), f.get("title"))
        L += [head, ""]
        badges = [("positive pattern" if f.get("kind") == "positive" else "severity: %s" % sev),
                  "" if f.get("kind") == "positive" else STATUS_LABEL.get(f.get("status"), ""),
                  "%s evidence" % (f.get("evidence_class") or ""),
                  "%s confidence" % (f.get("confidence") or "")]
        L += ["`" + "`  `".join(b for b in badges if b) + "`", ""]
        if f.get("lenses"):
            L += ["*Lenses: %s*" % joinlist(f["lenses"]), ""]
        if f.get("node_ids"):
            L += ["*Touches: %s*" % joinlist(f["node_ids"]), ""]

        L += [md_callout(f.get("kind"), sev, "Comment", [f.get("comment") or ""]), ""]

        L += ["**Evidence**", ""]
        for s in f.get("sources") or []:
            L += ["`%s`" % s.get("location"), ""]
            if s.get("excerpt"):
                lang = s.get("lang") or ""
                if lang == "prose":
                    L += ["> " + str(s["excerpt"]).replace("\n", "\n> "), ""]
                else:
                    L += ["```%s" % lang, str(s["excerpt"]), "```", ""]
            if s.get("note"):
                L += ["*%s*" % s["note"], ""]

        if f.get("causal_chain"):
            L.append("> [!abstract] Mechanism")
            for i, step in enumerate(f["causal_chain"]):
                L.append("> %s%s" % ("" if i == 0 else "\u2192 ", step))
            L.append("")
        if f.get("affected"):
            L += ["**Affected:** %s" % joinlist(f["affected"]), ""]
        if f.get("recommendation"):
            L += [md_callout("positive", None, "Recommendation", [f["recommendation"]]), ""]
        if f.get("tradeoffs"):
            L += ["**Tradeoffs.** %s" % f["tradeoffs"], ""]
        if f.get("alternatives"):
            L += ["**Alternatives**", ""] + ["- %s" % a for a in f["alternatives"]] + [""]
        if f.get("acceptance"):
            L += ["**When this is acceptable.** %s" % f["acceptance"], ""]
        if f.get("assumptions"):
            L += ["**Assumptions**", ""] + ["- %s" % a for a in f["assumptions"]] + [""]
        v = f.get("verification") or {}
        if v.get("method"):
            body = ["%s" % v["method"], "", "State: **%s**" % (v.get("state") or "proposed")]
            if v.get("result"):
                body += ["", "Result: %s" % v["result"]]
            L += [md_callout("risk", "low", "Verification", body), ""]

    qs = payload.get("open_questions") or []
    if qs:
        L += ["## Open questions and uncertainties", ""]
        for q in qs:
            body = []
            if q.get("affects"):
                body.append("Affects: %s" % joinlist(q["affects"]))
            if q.get("why_it_matters"):
                body += ["", q["why_it_matters"]]
            if q.get("how_to_resolve"):
                body += ["", "How to resolve: %s" % q["how_to_resolve"]]
            L += ["> [!question] %s" % q.get("question")]
            L += [("> " + l).rstrip() for line in body for l in str(line).split("\n")]
            L.append("")

    cov = [("Sampled paths", meta.get("sampled_paths")), ("Coverage limits", meta.get("coverage_limits")),
           ("Unavailable evidence", meta.get("unavailable_evidence")),
           ("Assumptions", meta.get("assumptions"))]
    cov = [(k, v) for k, v in cov if v]
    if cov:
        L += ["## Coverage and limits", ""]
        for k, v in cov:
            L += ["**%s**" % k, ""] + ["- %s" % x for x in (v if isinstance(v, list) else [v])] + [""]

    plan = payload.get("validation_plan") or []
    if plan:
        L += ["## Validation plan", "",
              "*Proposed unless marked otherwise. Nothing here has been run against shared or "
              "production state.*", ""]
        for p in sorted(plan, key=lambda x: x.get("order", 0)):
            suffix = []
            if p.get("affects"):
                suffix.append(joinlist(p["affects"]))
            suffix.append(p.get("state") or "proposed")
            box = "x" if p.get("state") == "executed" else " "
            L.append("- [%s] %s *(%s)*" % (box, p.get("action"), " · ".join(suffix)))
            if p.get("notes"):
                L.append("\t- %s" % p["notes"])
        L.append("")

    return "\n".join(L).rstrip() + "\n"


# ---------------------------------------------------------------- main

def resolve_out_dir(explicit, slug):
    if explicit:
        return Path(explicit)
    shared = Path("/mnt/user-data/outputs")
    if shared.is_dir():
        return shared
    return Path.cwd() / "reviews" / slug


def main():
    ap = argparse.ArgumentParser(description="Render a systems review into HTML + Obsidian Markdown.")
    ap.add_argument("payload", help="path to findings JSON")
    ap.add_argument("--out-dir", default=None,
                    help="output directory (default: /mnt/user-data/outputs if present, else ./reviews/<slug>)")
    ap.add_argument("--template", default=None, help="override HTML template path")
    ap.add_argument("--html-only", action="store_true")
    ap.add_argument("--md-only", action="store_true")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    errs, warns = validate(payload)
    for w in warns:
        print("warning: %s" % w, file=sys.stderr)
    if errs:
        for e in errs:
            print("error: %s" % e, file=sys.stderr)
        print("\n%d error(s): fix the payload, not the output. "
              "See references/findings-schema.md." % len(errs), file=sys.stderr)
        return 2
    if warns and args.strict:
        print("\n--strict: %d warning(s) treated as errors." % len(warns), file=sys.stderr)
        return 2

    meta = payload["meta"]
    slug = re.sub(r"[^a-z0-9._-]+", "-", str(meta["slug"]).lower()).strip("-") or "review"
    model = payload["system_model"]
    findings = payload.get("findings") or []

    hits = {}
    for f in findings:
        for nid in f.get("node_ids") or []:
            hits[nid] = hits.get(nid, 0) + 1

    out_dir = resolve_out_dir(args.out_dir, slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    if not args.md_only:
        tpl_path = Path(args.template) if args.template else \
            Path(__file__).resolve().parent.parent / "assets" / "report_template.html"
        tpl = tpl_path.read_text(encoding="utf-8")
        lay = layout(model)
        svg, caption_only = render_svg(model, lay, hits)
        body = render_html_body(payload, lay, svg, caption_only)
        doc = tpl.replace("__TITLE__", html.escape(str(meta.get("title") or "Systems review"))) \
                 .replace("__BODY__", body)
        p = out_dir / ("%s-review.html" % slug)
        p.write_text(doc, encoding="utf-8")
        written.append(p)

    if not args.html_only:
        md = render_markdown(payload, render_mermaid(model))
        p = out_dir / ("%s-review.md" % slug)
        p.write_text(md, encoding="utf-8")
        written.append(p)

    for p in written:
        print(p.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
