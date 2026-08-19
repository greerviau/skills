#!/usr/bin/env python3
"""Collect Wayfinder issues and render them as a standalone browser map."""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
import tempfile
import webbrowser
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

ISSUE_URL = re.compile(r"https://github\.com/([^/]+/[^/]+)/issues/(\d+)")
ISSUE_REFERENCE = re.compile(r"^([^#/:\s]+/[^#/:\s]+)#(\d+)$")


@dataclass(frozen=True, order=True)
class IssueReference:
    repository: str
    number: int

    @property
    def identifier(self) -> str:
        return f"{self.repository}#{self.number}"


@dataclass
class IssueNode:
    reference: IssueReference
    title: str
    body: str
    state: str
    url: str
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    is_map: bool = False
    is_north_star: bool = False
    status: str = "open"
    depth: int = 0

    def as_json(self) -> dict[str, Any]:
        return {
            "id": self.reference.identifier,
            "repository": self.reference.repository,
            "number": self.reference.number,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "url": self.url,
            "labels": self.labels,
            "assignees": self.assignees,
            "isMap": self.is_map,
            "isNorthStar": self.is_north_star,
            "status": self.status,
            "depth": self.depth,
        }


def run_gh(arguments: list[str]) -> Any:
    result = subprocess.run(
        ["gh", *arguments], check=True, capture_output=True, text=True
    )
    return json.loads(result.stdout)


def current_repository() -> str:
    return run_gh(["repo", "view", "--json", "nameWithOwner"])["nameWithOwner"]


def parse_reference(value: str, default_repository: str) -> IssueReference:
    if value.isdigit():
        return IssueReference(default_repository, int(value))

    match = ISSUE_URL.fullmatch(value)
    if match:
        return IssueReference(match.group(1), int(match.group(2)))

    match = ISSUE_REFERENCE.fullmatch(value)
    if match:
        return IssueReference(match.group(1), int(match.group(2)))

    raise ValueError(
        f"Unsupported issue reference {value!r}; use NUMBER, OWNER/REPO#NUMBER, or a GitHub issue URL"
    )


def issue(reference: IssueReference) -> dict[str, Any]:
    return run_gh(["api", f"repos/{reference.repository}/issues/{reference.number}"])


def children(reference: IssueReference) -> list[IssueReference]:
    try:
        records = run_gh(
            [
                "api",
                f"repos/{reference.repository}/issues/{reference.number}/sub_issues?per_page=100",
            ]
        )
    except subprocess.CalledProcessError:
        return []
    return [
        IssueReference(reference.repository, record["number"])
        for record in records
        if "number" in record
    ]


def blockers(reference: IssueReference) -> list[IssueReference]:
    try:
        records = run_gh(
            [
                "api",
                f"repos/{reference.repository}/issues/{reference.number}/dependencies/blocked_by?per_page=100",
            ]
        )
    except subprocess.CalledProcessError:
        return []
    return [
        IssueReference(
            record.get("repository", {}).get("full_name", reference.repository),
            record["number"],
        )
        for record in records
        if "number" in record
    ]


def discover_maps(repository: str) -> list[IssueReference]:
    records = run_gh(
        [
            "issue",
            "list",
            "--repo",
            repository,
            "--label",
            "wayfinder:map",
            "--state",
            "all",
            "--limit",
            "100",
            "--json",
            "number",
        ]
    )
    return [IssueReference(repository, record["number"]) for record in records]


def linked_references(body: str) -> Iterable[IssueReference]:
    for match in ISSUE_URL.finditer(body):
        yield IssueReference(match.group(1), int(match.group(2)))


def label_names(record: dict[str, Any]) -> list[str]:
    return [label.get("name", "") for label in record.get("labels", [])]


def make_node(record: dict[str, Any], reference: IssueReference, depth: int) -> IssueNode:
    labels = label_names(record)
    is_map = "wayfinder:map" in labels
    return IssueNode(
        reference=reference,
        title=record.get("title", reference.identifier),
        body=record.get("body") or "",
        state=record.get("state", "OPEN").lower(),
        url=record.get("html_url", f"https://github.com/{reference.identifier.replace('#', '/issues/') }"),
        labels=labels,
        assignees=[user.get("login", "") for user in record.get("assignees", [])],
        is_map=is_map,
        is_north_star=is_map,
        depth=depth,
    )


def collect(roots: list[IssueReference]) -> tuple[list[IssueNode], list[dict[str, str]], list[str]]:
    records: dict[IssueReference, dict[str, Any]] = {}
    depths: dict[IssueReference, int] = {}
    edge_keys: set[tuple[str, str, str]] = set()
    fog: list[str] = []
    queue: deque[tuple[IssueReference, int]] = deque((root, 0) for root in roots)

    while queue:
        reference, depth = queue.popleft()
        if reference in records:
            depths[reference] = min(depths[reference], depth)
            continue
        try:
            record = issue(reference)
        except subprocess.CalledProcessError as error:
            print(f"Skipping {reference.identifier}: GitHub returned an error", file=sys.stderr)
            if error.stderr:
                print(error.stderr.strip(), file=sys.stderr)
            continue

        records[reference] = record
        depths[reference] = depth
        for child in children(reference):
            edge_keys.add((reference.identifier, child.identifier, "parent"))
            queue.append((child, depth + 1))
        for blocker in blockers(reference):
            edge_keys.add((blocker.identifier, reference.identifier, "blocks"))
            queue.append((blocker, max(depth - 1, 0)))

        if "## Not yet specified" in (record.get("body") or ""):
            body = record["body"]
            section = body.split("## Not yet specified", 1)[1]
            section = section.split("## ", 1)[0]
            fog.extend(
                line.strip(" -*\t")
                for line in section.splitlines()
                if line.strip(" -*\t")
            )
        for linked in linked_references(record.get("body") or ""):
            if linked not in records:
                edge_keys.add((reference.identifier, linked.identifier, "reference"))
                queue.append((linked, depth + 1))

    nodes = [make_node(records[ref], ref, depths[ref]) for ref in records]
    root_ids = {root.identifier for root in roots}
    for node in nodes:
        if node.reference.identifier in root_ids:
            node.is_map = True
            node.is_north_star = True
    node_ids = {node.reference.identifier for node in nodes}
    open_blockers: defaultdict[str, set[str]] = defaultdict(set)
    for source, target, edge_type in edge_keys:
        if edge_type == "blocks" and source in node_ids and target in node_ids:
            source_node = next(node for node in nodes if node.reference.identifier == source)
            if source_node.state == "open":
                open_blockers[target].add(source)

    for node in nodes:
        if node.is_north_star:
            node.status = "north-star"
        elif node.state == "closed":
            node.status = "complete"
        elif open_blockers[node.reference.identifier]:
            node.status = "blocked"
        elif not node.assignees:
            node.status = "frontier"
        else:
            node.status = "claimed"

    edges = [
        {"source": source, "target": target, "type": edge_type}
        for source, target, edge_type in sorted(edge_keys)
        if source in node_ids and target in node_ids
    ]
    return nodes, edges, fog


def filter_nodes(
    nodes: list[IssueNode], edges: list[dict[str, str]], focuses: list[str]
) -> tuple[list[IssueNode], list[dict[str, str]]]:
    if not focuses:
        return nodes, edges

    node_ids = {node.reference.identifier for node in nodes}
    selected = {focus for focus in focuses if focus in node_ids}
    if not selected:
        raise ValueError("None of the --focus references occur in the collected map")

    changed = True
    while changed:
        changed = False
        for edge in edges:
            if edge["type"] == "parent" and edge["target"] in selected and edge["source"] not in selected:
                selected.add(edge["source"])
                changed = True
            if edge["type"] == "parent" and edge["source"] in selected and edge["target"] not in selected:
                selected.add(edge["target"])
                changed = True
            if edge["type"] != "parent" and edge["source"] in selected and edge["target"] not in selected:
                selected.add(edge["target"])
                changed = True
            if edge["type"] != "parent" and edge["target"] in selected and edge["source"] not in selected:
                selected.add(edge["source"])
                changed = True

    filtered_nodes = [node for node in nodes if node.reference.identifier in selected]
    filtered_edges = [edge for edge in edges if edge["source"] in selected and edge["target"] in selected]
    return filtered_nodes, filtered_edges


def output_path() -> Path:
    directory = Path(tempfile.gettempdir())
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return directory / f"wayfinder-star-map-{timestamp}.html"


def render(data: dict[str, Any], destination: Path) -> None:
    encoded = json.dumps(data, separators=(",", ":")).replace("<", "\\u003c")
    html = HTML_TEMPLATE.replace("__MAP_DATA__", encoded)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")


def open_in_browser(path: Path) -> None:
    if platform.system() == "Darwin":
        subprocess.Popen(["open", str(path)])
    else:
        webbrowser.open(path.as_uri())


def load_data(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("references", nargs="*", help="Map issue references")
    parser.add_argument(
        "--repo",
        action="append",
        default=[],
        help="Repository to scan for wayfinder:map issues; repeat for multiple repositories",
    )
    parser.add_argument(
        "--focus",
        action="append",
        default=[],
        help="Issue reference to focus on; repeat to show multiple subsections",
    )
    parser.add_argument("--output", type=Path, help="HTML path; defaults to the system temp directory")
    parser.add_argument("--data-file", type=Path, help="Use a saved map JSON file instead of GitHub")
    parser.add_argument("--no-open", action="store_true", help="Write the HTML without opening a browser")
    return parser


def main() -> int:
    parser = build_parser()
    arguments = parser.parse_args()
    default_repository = current_repository() if not arguments.data_file else "local/data"

    if arguments.data_file:
        data = load_data(arguments.data_file)
    else:
        repositories = arguments.repo or [default_repository]
        references = [
            parse_reference(value, default_repository) for value in arguments.references
        ]
        if not references:
            references = [
                reference
                for repository in repositories
                for reference in discover_maps(repository)
            ]
        if not references:
            parser.error("No map issues found; pass an issue reference or --repo")
        nodes, edges, fog = collect(sorted(set(references)))
        focus_references = [parse_reference(value, default_repository).identifier for value in arguments.focus]
        nodes, edges = filter_nodes(nodes, edges, focus_references)
        data = {
            "nodes": [node.as_json() for node in nodes],
            "edges": edges,
            "fogOfWar": fog,
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
        }

    destination = arguments.output or output_path()
    render(data, destination)
    print(destination)
    if not arguments.no_open:
        open_in_browser(destination)
    return 0


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%23050913'/%3E%3Cpath d='m32 8 5.5 18.5L56 32 37.5 37.5 32 56l-5.5-18.5L8 32l18.5-5.5z' fill='%23ffe9a6'/%3E%3Ccircle cx='32' cy='32' r='4' fill='white'/%3E%3C/svg%3E">
<title>Wayfinder star map</title>
<style>
:root { color-scheme: dark; --ink: #e8eefb; --muted: #8c9ab4; --line: #27344e; --panel: rgba(11, 18, 34, .86); }
* { box-sizing: border-box; }
html, body { width: 100%; height: 100%; margin: 0; overflow: hidden; background: #050913; color: var(--ink); font: 13px/1.45 ui-sans-serif, system-ui, -apple-system, sans-serif; }
body { background: radial-gradient(circle at 50% 42%, #15213e 0, #080e1e 38%, #050913 78%); }
canvas { display: block; width: 100%; height: 100%; cursor: grab; }
canvas.dragging { cursor: grabbing; }
.topbar, .legend, .details { position: fixed; z-index: 2; border: 1px solid rgba(157, 181, 230, .18); background: var(--panel); box-shadow: 0 16px 45px rgba(0, 0, 0, .28); backdrop-filter: blur(18px); }
.topbar { top: 18px; left: 18px; right: 18px; display: flex; align-items: center; gap: 18px; padding: 12px 16px; border-radius: 16px; }
h1 { margin: 0; font-size: 15px; font-weight: 650; letter-spacing: .01em; }
.subtitle { color: var(--muted); margin-left: 4px; }
.stats { display: flex; gap: 8px; margin-left: auto; color: var(--muted); }
.stat { padding: 3px 8px; border: 1px solid rgba(157, 181, 230, .16); border-radius: 99px; }
.actions { display: flex; gap: 7px; }
button, input { border: 1px solid rgba(157, 181, 230, .2); border-radius: 8px; color: var(--ink); background: rgba(255, 255, 255, .06); font: inherit; }
button { padding: 6px 10px; cursor: pointer; }
button:hover { background: rgba(255, 255, 255, .13); }
input { width: 150px; padding: 6px 9px; outline: none; }
input:focus { border-color: #82aaff; }
.legend { left: 18px; bottom: 18px; display: flex; flex-wrap: wrap; gap: 10px 14px; max-width: 430px; padding: 10px 13px; border-radius: 12px; color: var(--muted); }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.details { top: 88px; right: 18px; width: min(350px, calc(100vw - 36px)); max-height: calc(100vh - 150px); overflow: auto; padding: 18px; border-radius: 15px; transform: translateX(calc(100% + 24px)); transition: transform .2s ease; }
.details.visible { transform: translateX(0); }
.details h2 { margin: 0 0 7px; font-size: 17px; line-height: 1.25; }
.details p { margin: 8px 0; }
.kicker { color: #91a9d9; text-transform: uppercase; letter-spacing: .12em; font-size: 10px; }
.meta { color: var(--muted); }
.status { display: inline-block; padding: 3px 8px; border-radius: 99px; background: rgba(255, 255, 255, .08); }
.details a { color: #9cc2ff; }
.preview { color: #b7c2d8; white-space: pre-wrap; }
#empty { color: var(--muted); }
@media (max-width: 760px) { .topbar { flex-wrap: wrap; gap: 9px; } .stats { order: 3; width: 100%; margin-left: 0; } .details { top: 132px; } .subtitle { display: block; } }
</style>
</head>
<body>
<canvas id="map" aria-label="Interactive Wayfinder star map"></canvas>
<header class="topbar">
  <div><h1 id="title">Wayfinder star map</h1><span class="subtitle">drag to explore · scroll to zoom</span></div>
  <div class="stats" id="stats"></div>
  <div class="actions"><input id="search" type="search" placeholder="Find a star" aria-label="Find a star"><button id="reset" type="button">Reset view</button></div>
</header>
<aside class="details" id="details" aria-live="polite"><div id="empty">Hover over a star to inspect its issue.</div><div id="content" hidden>
  <div class="kicker" id="repository"></div><h2 id="issue-title"></h2><span class="status" id="status"></span><p class="meta" id="issue-meta"></p><p class="preview" id="preview"></p><a id="issue-link" target="_blank" rel="noreferrer">Open GitHub issue ↗</a>
</div></aside>
<div class="legend" id="legend"></div>
<script>
const mapData = __MAP_DATA__;
const canvas = document.querySelector('#map');
const context = canvas.getContext('2d');
const details = document.querySelector('#details');
const empty = document.querySelector('#empty');
const content = document.querySelector('#content');
const colors = { 'north-star': '#ffe9a6', complete: '#62d6a7', blocked: '#ff7695', frontier: '#76b7ff', claimed: '#b196ff', open: '#91a9d9' };
const statusNames = { 'north-star': 'North star', complete: 'Complete', blocked: 'Blocked', frontier: 'Frontier', claimed: 'Claimed', open: 'Open' };
let pixelRatio = window.devicePixelRatio || 1;
let view = { x: 0, y: 0, scale: 1 };
let pointer = { x: 0, y: 0, worldX: 0, worldY: 0, down: false, moved: false, node: null };
let hovered = null;
let selected = null;
let positions = new Map();

function resize() {
  pixelRatio = window.devicePixelRatio || 1;
  canvas.width = innerWidth * pixelRatio;
  canvas.height = innerHeight * pixelRatio;
  context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  layout();
  draw();
}
function layout() {
  const roots = mapData.nodes.filter(node => node.isNorthStar);
  const byParent = new Map();
  mapData.edges.filter(edge => edge.type === 'parent').forEach(edge => {
    if (!byParent.has(edge.source)) byParent.set(edge.source, []);
    byParent.get(edge.source).push(edge.target);
  });
  const rootSpacing = Math.max(480, Math.min(800, innerWidth * .6));
  roots.forEach((root, rootIndex) => {
    const rootX = (rootIndex - (roots.length - 1) / 2) * rootSpacing;
    place(root, rootX, 0, 0, rootIndex);
  });
  mapData.nodes.forEach((node, index) => {
    if (!positions.has(node.id)) place(node, Math.cos(index * 2.4) * 320, Math.sin(index * 2.4) * 240, node.depth, index);
  });
  function place(node, x, y, depth, seed) {
    if (positions.has(node.id)) return;
    positions.set(node.id, { x, y, depth });
    const descendants = byParent.get(node.id) || [];
    const radius = 155 + depth * 22;
    descendants.forEach((childId, index) => {
      const angle = (index - (descendants.length - 1) / 2) * Math.min(.8, 4.2 / Math.max(1, descendants.length)) + (seed * .37);
      place(mapData.nodes.find(node => node.id === childId), x + Math.cos(angle) * radius, y + Math.sin(angle) * radius, depth + 1, seed + index + 1);
    });
  }
  const bounds = [...positions.values()];
  if (bounds.length && view.x === 0 && view.y === 0) {
    view.x = innerWidth / 2;
    view.y = innerHeight * .52;
  }
}
function worldPoint(event) {
  const box = canvas.getBoundingClientRect();
  const x = event.clientX - box.left;
  const y = event.clientY - box.top;
  return { x, y, worldX: (x - view.x) / view.scale, worldY: (y - view.y) / view.scale };
}
function hitNode(worldX, worldY) {
  let hit = null;
  let distance = Infinity;
  mapData.nodes.forEach(node => {
    const point = positions.get(node.id);
    const radius = (node.isNorthStar ? 15 : 9) / view.scale;
    const currentDistance = Math.hypot(worldX - point.x, worldY - point.y);
    if (currentDistance < radius && currentDistance < distance) { hit = node; distance = currentDistance; }
  });
  return hit;
}
function draw() {
  context.clearRect(0, 0, innerWidth, innerHeight);
  context.save();
  context.translate(view.x, view.y);
  context.scale(view.scale, view.scale);
  drawEdges();
  mapData.nodes.forEach(drawNode);
  context.restore();
}
function drawEdges() {
  mapData.edges.forEach(edge => {
    const source = positions.get(edge.source), target = positions.get(edge.target);
    if (!source || !target) return;
    const targetNode = mapData.nodes.find(node => node.id === edge.target);
    const active = hovered && (hovered.id === edge.source || hovered.id === edge.target);
    context.beginPath();
    context.moveTo(source.x, source.y);
    if (edge.type === 'reference') {
      context.setLineDash([3, 8]);
      context.strokeStyle = active ? 'rgba(151, 174, 218, .6)' : 'rgba(111, 135, 184, .2)';
    } else {
      context.setLineDash([]);
      context.strokeStyle = active ? 'rgba(178, 206, 255, .78)' : 'rgba(111, 135, 184, .28)';
    }
    context.lineWidth = active ? 1.8 : 1;
    const bend = Math.max(18, Math.min(75, Math.hypot(target.x - source.x, target.y - source.y) * .22));
    context.quadraticCurveTo((source.x + target.x) / 2, (source.y + target.y) / 2 - bend, target.x, target.y);
    context.stroke();
    context.setLineDash([]);
    if (edge.type === 'blocks') drawArrow(source, target, targetNode.status === 'blocked');
  });
}
function drawArrow(source, target, blocked) {
  const angle = Math.atan2(target.y - source.y, target.x - source.x);
  const x = target.x - Math.cos(angle) * 12, y = target.y - Math.sin(angle) * 12;
  context.beginPath(); context.moveTo(x, y); context.lineTo(x - Math.cos(angle - .55) * 7, y - Math.sin(angle - .55) * 7); context.lineTo(x - Math.cos(angle + .55) * 7, y - Math.sin(angle + .55) * 7); context.closePath();
  context.fillStyle = blocked ? colors.blocked : 'rgba(178, 206, 255, .6)'; context.fill();
}
function drawNode(node) {
  const point = positions.get(node.id), color = colors[node.status] || colors.open;
  const active = hovered && hovered.id === node.id, locked = selected && selected.id === node.id;
  const radius = node.isNorthStar ? 11 : 6;
  context.save();
  if (node.isNorthStar || active || locked) {
    const glow = context.createRadialGradient(point.x, point.y, 0, point.x, point.y, radius * 4.5);
    glow.addColorStop(0, color + '66'); glow.addColorStop(1, color + '00');
    context.fillStyle = glow; context.beginPath(); context.arc(point.x, point.y, radius * 4.5, 0, Math.PI * 2); context.fill();
  }
  context.fillStyle = color; context.beginPath(); context.arc(point.x, point.y, radius, 0, Math.PI * 2); context.fill();
  context.strokeStyle = active || locked ? '#ffffff' : color + 'aa'; context.lineWidth = active || locked ? 2 : 1; context.stroke();
  if (node.isNorthStar) { context.strokeStyle = color + '55'; context.lineWidth = 1; context.beginPath(); context.arc(point.x, point.y, radius * 1.8, 0, Math.PI * 2); context.stroke(); }
  if (node.isNorthStar || active || locked) {
    context.fillStyle = '#e8eefb'; context.font = `${node.isNorthStar ? 600 : 500} ${node.isNorthStar ? 14 : 12}px ui-sans-serif, system-ui, sans-serif`; context.textAlign = 'center'; context.fillText(node.title, point.x, point.y + radius + 19);
  }
  context.restore();
}
function showNode(node) {
  if (!node) return;
  document.querySelector('#repository').textContent = `${node.repository} · #${node.number}`;
  document.querySelector('#issue-title').textContent = node.title;
  document.querySelector('#status').textContent = statusNames[node.status] || node.status;
  document.querySelector('#status').style.color = colors[node.status] || colors.open;
  document.querySelector('#issue-meta').textContent = `${node.state.toUpperCase()}${node.assignees.length ? ' · ' + node.assignees.join(', ') : ''}${node.labels.length ? ' · ' + node.labels.join(', ') : ''}`;
  const preview = node.body.replace(/[#*_`]/g, '').replace(/\s+/g, ' ').trim();
  document.querySelector('#preview').textContent = preview ? preview.slice(0, 280) + (preview.length > 280 ? '…' : '') : 'No issue description.';
  const link = document.querySelector('#issue-link'); link.href = node.url;
  empty.hidden = true; content.hidden = false; details.classList.add('visible');
}
function updateStats() {
  const counts = {}; mapData.nodes.forEach(node => counts[node.status] = (counts[node.status] || 0) + 1);
  document.querySelector('#title').textContent = mapData.nodes.find(node => node.isNorthStar)?.title || 'Wayfinder star map';
  document.querySelector('#stats').innerHTML = `<span class="stat">${mapData.nodes.length} stars</span><span class="stat">${mapData.edges.length} links</span><span class="stat">${counts.complete || 0} complete</span>`;
  const statuses = ['north-star', 'frontier', 'claimed', 'blocked', 'complete'];
  document.querySelector('#legend').innerHTML = statuses.filter(status => counts[status]).map(status => `<span><i class="dot" style="background:${colors[status]}"></i>${statusNames[status]} ${counts[status]}</span>`).join('');
  if (mapData.fogOfWar?.length) document.querySelector('#legend').insertAdjacentHTML('beforeend', `<span><i class="dot" style="background:#77839b"></i>Fog ${mapData.fogOfWar.length}</span>`);
}
canvas.addEventListener('pointerdown', event => { pointer = { ...worldPoint(event), down: true, moved: false, node: hitNode(...Object.values(worldPoint(event)).slice(2)) }; canvas.classList.add('dragging'); canvas.setPointerCapture(event.pointerId); });
canvas.addEventListener('pointermove', event => {
  const next = worldPoint(event);
  if (pointer.down) {
    const deltaX = next.x - pointer.x, deltaY = next.y - pointer.y;
    if (Math.hypot(deltaX, deltaY) > 2) pointer.moved = true;
    view.x += deltaX; view.y += deltaY; pointer.x = next.x; pointer.y = next.y; draw(); return;
  }
  hovered = hitNode(next.worldX, next.worldY); if (hovered) showNode(hovered); draw();
});
canvas.addEventListener('pointerup', event => { canvas.classList.remove('dragging'); if (!pointer.moved && pointer.node) { selected = pointer.node; showNode(selected); draw(); } pointer.down = false; });
canvas.addEventListener('pointerleave', () => { if (!pointer.down) { hovered = null; draw(); } });
canvas.addEventListener('wheel', event => { event.preventDefault(); const before = worldPoint(event); const factor = event.deltaY < 0 ? 1.12 : .89; view.scale = Math.max(.28, Math.min(3.5, view.scale * factor)); view.x = before.x - before.worldX * view.scale; view.y = before.y - before.worldY * view.scale; draw(); }, { passive: false });
document.querySelector('#reset').addEventListener('click', () => { view = { x: innerWidth / 2, y: innerHeight * .52, scale: 1 }; draw(); });
document.querySelector('#search').addEventListener('input', event => { const query = event.target.value.toLowerCase().trim(); if (!query) { selected = null; details.classList.remove('visible'); draw(); return; } const node = mapData.nodes.find(candidate => `${candidate.title} ${candidate.repository}#${candidate.number}`.toLowerCase().includes(query)); if (node) { selected = node; const point = positions.get(node.id); view.x = innerWidth / 2 - point.x * view.scale; view.y = innerHeight * .52 - point.y * view.scale; showNode(node); draw(); } });
window.addEventListener('resize', resize); updateStats(); resize();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
