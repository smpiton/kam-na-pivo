"""Bake OSM data + Leaflet CSS into the single-page app.

usage: python3 build.py <osm_dir> <leaflet.css> <out.html> [claude|github]
"""
import json, sys, pathlib

osm, lcss, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
here = pathlib.Path(__file__).parent
target = sys.argv[4] if len(sys.argv) > 4 else "claude"


def dp(pts, eps):
    """Douglas-Peucker simplification on [lat, lng] lists."""
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay
    n = (dx * dx + dy * dy) ** 0.5 or 1e-12
    imax, dmax = 0, 0.0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = abs(dy * (px - ax) - dx * (py - ay)) / n
        if d > dmax:
            imax, dmax = i, d
    if dmax > eps:
        return dp(pts[: imax + 1], eps)[:-1] + dp(pts[imax:], eps)
    return [pts[0], pts[-1]]


def line(geom, eps=0.00007):
    pts = [[g["lat"], g["lon"]] for g in geom]
    return [[round(a, 5), round(b, 5)] for a, b in dp(pts, eps)]


# pubs
pubs, seen = [], set()
for e in json.load(open(osm / "pubs.json"))["elements"]:
    t = e.get("tags", {})
    name = t.get("name")
    if not name:
        continue
    lat = e.get("lat") or e.get("center", {}).get("lat")
    lon = e.get("lon") or e.get("center", {}).get("lon")
    if lat is None:
        continue
    key = (name.lower(), round(lat, 3), round(lon, 3))
    if key in seen:
        continue
    seen.add(key)
    brewery = (t.get("brewery") or "").replace(";", ", ")
    site = t.get("website") or t.get("contact:website") or ""
    if site and not site.startswith("http"):
        site = "https://" + site
    pubs.append([name, round(lat, 5), round(lon, 5), brewery, site])
pubs.sort(key=lambda p: p[0])

# base geometry
geo = {"river": [], "roads": [], "major": [], "border": []}
for e in json.load(open(osm / "geo.json"))["elements"]:
    t = e.get("tags", {})
    if e["type"] == "way" and "geometry" in e:
        hw = t.get("highway")
        if t.get("waterway") == "river":
            geo["river"].append(line(e["geometry"], 0.00004))
        elif hw in ("motorway", "trunk"):
            geo["major"].append(line(e["geometry"]))
        elif hw == "primary":
            geo["roads"].append(line(e["geometry"]))
    elif e["type"] == "relation":
        for m in e.get("members", []):
            if m.get("type") == "way" and m.get("role") == "outer" and "geometry" in m:
                geo["border"].append(line(m["geometry"], 0.0001))

html = (here / "template.html").read_text()
html = html.replace("/*__LEAFLET_CSS__*/", lcss.read_text())
html = html.replace("/*__PUBS__*/[]", json.dumps(pubs, ensure_ascii=False, separators=(",", ":")))
html = html.replace("/*__GEO__*/{}", json.dumps(geo if target == "claude" else {}, separators=(",", ":")))
html = html.replace('/*__TARGET__*/"claude"', json.dumps(target))
if target == "github":
    fb = "https://www.gstatic.com/firebasejs/10.12.2/"
    extra = "\n".join(f'<script src="{fb}{m}-compat.js"></script>' for m in ("firebase-app", "firebase-auth", "firebase-firestore"))
    extra += '\n<script src="firebase-config.js"></script>'
    html = html.replace("<!--__EXTRA_SCRIPTS__-->", extra)
    html = ('<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<style>html,body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
            '</head>\n<body>\n' + html + '\n</body>\n</html>\n')
out.write_text(html)
print(f"pubs={len(pubs)} river={len(geo['river'])} roads={len(geo['roads'])} major={len(geo['major'])} border={len(geo['border'])} size={out.stat().st_size//1024}KB")
