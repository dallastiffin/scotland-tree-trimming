"""Full verification. Run after any CSS/copy/build change."""
import os, re, glob, json, html
from collections import Counter
S='site'; pages=sorted(glob.glob(S+'/*.html'))
fails=[]

# ---- 1. no comment in style.css closes early -------------------------------
css=open(S+'/style.css',encoding='utf-8').read()
depth=0; i=0; badcomment=None
while i < len(css)-1:
    if css[i:i+2]=='/*':
        j=css.find('*/', i+2)
        body=css[i+2:j]
        if '*/' in body: badcomment=body[:60]
        i=j+2
    else: i+=1
print("1. style.css comments terminate correctly:", "yes" if not badcomment else "NO -> "+str(badcomment))
if badcomment: fails.append("css comment closes early")

# ---- 2. every custom property used is declared ------------------------------
stripped=re.sub(r'/\*.*?\*/','',css,flags=re.S)
declared=set(re.findall(r'(--[a-z0-9-]+)\s*:\s*[^;{]+;', stripped))
used=set(re.findall(r'var\((--[a-z0-9-]+)', css))
undef=sorted(used-declared)
print("2. custom properties used but not declared:", undef or "none")
if undef: fails.append("undeclared css vars: %s" % undef)

# ---- 3. links, images, h1, alt, ids, meta ----------------------------------
missing=[]; probs=[]
for p in pages:
    s=open(p,encoding='utf-8').read()
    urls=[m.group(2) for m in re.finditer(r'\b(href|src)="([^"]+)"',s)]
    for m in re.finditer(r'\b(?:srcset|imagesrcset)="([^"]+)"',s):
        urls += [x.strip().split(' ')[0] for x in m.group(1).split(',')]
    for u in urls:
        if not u or u.startswith(('#','tel:','mailto:','data:','http://','https://')): continue
        c=(u.lstrip('/') or 'index.html').split('?')[0]
        if not os.path.exists(os.path.join(S,c)) and not os.path.exists(os.path.join(S,c+'.html')):
            missing.append((os.path.basename(p),u))
    if len(re.findall(r'<h1[ >]',s))!=1: probs.append((p,'h1 count'))
    if [x for x in re.findall(r'<img\b[^>]*>',s) if 'alt=' not in x]: probs.append((p,'img without alt'))
    ids=re.findall(r'\bid="([^"]+)"',s)
    d=[k for k,v in Counter(ids).items() if v>1]
    if d: probs.append((p,'duplicate id %s'%d))
    if re.search(r'href="[^"]*\.html"',s): probs.append((p,'internal .html link'))
print("3. broken refs:", len(missing), missing[:4], "| structural problems:", probs or "none")
if missing or probs: fails.append("links/structure")

# ---- 3b. asset URLs inside JSON-LD resolve to a real file ------------------
# Added after the schema "logo" was found pointing at /images/logo.jpg, which
# make-logo.py has never produced. Attribute-based link checking cannot see
# these because they live inside a <script type="application/ld+json"> string.
import json as _json
ld_missing=[]
for p in pages:
    s=open(p,encoding='utf-8').read()
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        for u in re.findall(r'"(?:logo|image|url|contentUrl)"\s*:\s*"([^"]+)"', blk):
            m=re.match(r'https?://[^/]+(/.*)$', u)
            path=(m.group(1) if m else u)
            if not re.search(r'\.(png|jpe?g|webp|svg|ico|gif)$', path, re.I):
                continue
            f=os.path.join(S, path.lstrip('/').split('?')[0])
            if not os.path.exists(f):
                ld_missing.append((os.path.basename(p), u))
print("3b. JSON-LD asset URLs that 404:", sorted(set(ld_missing)) or "none")
if ld_missing: fails.append("json-ld asset 404: %s" % sorted(set(x[1] for x in ld_missing)))

# ---- 4. meta uniqueness and length ----------------------------------------
t={};d={}
for p in pages:
    s=open(p,encoding='utf-8').read()
    t.setdefault(re.search(r'<title>(.*?)</title>',s,re.S).group(1).strip(),[]).append(p)
    d.setdefault(re.search(r'<meta name="description" content="([^"]*)"',s).group(1),[]).append(p)
dupT=[k for k,v in t.items() if len(v)>1]; dupD=[k for k,v in d.items() if len(v)>1]
badlen=[(len(k),os.path.basename(v[0])) for k,v in d.items() if not 120<=len(k)<=160]
print("4. duplicate titles:",dupT or "none","| duplicate descs:",dupD or "none","| desc outside 120-160:",badlen or "none")
if dupT or dupD or badlen: fails.append("meta")

# ---- 5. contrast ----------------------------------------------------------
def lum(h):
    h=h.lstrip('#'); r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    f=lambda c: c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return .2126*f(r)+.7152*f(g)+.0722*f(b)
def cr(a,b):
    l1,l2=sorted([lum(a),lum(b)],reverse=True); return (l1+.05)/(l2+.05)
V=dict(re.findall(r'(--color-[a-z-]+):\s*(#[0-9a-fA-F]{6})',stripped))
bad=[]; n=0
for sel,body in re.findall(r'([^{}]+)\{([^{}]*)\}',css):
    bg=re.search(r'background(?:-color)?\s*:\s*[^;]*var\((--color-[a-z-]+)\)',body)
    fg=re.search(r'(?<!-)\bcolor\s*:\s*var\((--color-[a-z-]+)\)',body)
    if bg and fg and bg.group(1) in V and fg.group(1) in V:
        n+=1; r=cr(V[fg.group(1)],V[bg.group(1)])
        if r<4.5: bad.append((round(r,2),sel.strip()[:50]))
ui=cr(V['--color-border-strong'],V['--color-bg'])
print(f"5. rules with bg+text: {n} | below 4.5:1: {bad or 'none'} | input border on white: {ui:.2f}:1 (needs 3:1)")
if bad or ui<3: fails.append("contrast")

# ---- 6. fingerprints ------------------------------------------------------
fps={re.search(r'style\.css\?v=([0-9a-f]+)',open(p,encoding='utf-8').read()).group(1) for p in pages}
print("6. style.css fingerprint consistent across pages:", len(fps)==1, fps)
if len(fps)!=1: fails.append("fingerprint")

print("\n" + ("ALL CHECKS PASSED" if not fails else "FAILURES: %s" % fails))
