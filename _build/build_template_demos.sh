#!/bin/zsh
# Build every website template as a static demo under /demos/<slug>/ of this site.
# The product source in _releases/websites/<slug>/build is cloned to a work folder first
# and never changed. Usage: _build/build_template_demos.sh <work-folder> [slug ...]
set -u
SITE="${0:A:h:h}"
SRC="${SITE:h}/_releases/websites"
WORK="${1:?work folder}"; shift
mkdir -p "$WORK" "$SITE/demos"
slugs=("$@"); [[ ${#slugs} -eq 0 ]] && slugs=($(ls "$SRC"))
fail=0
for slug in $slugs; do
  w="$WORK/$slug"
  rm -rf "$w"
  cp -Rc "$SRC/$slug/build" "$w" || { echo "FAIL clone $slug"; fail=1; continue; }
  rm -rf "$w/out" "$w/.next"
  python3 - "$w/next.config.mjs" "$slug" <<'PY' || { echo "FAIL config $slug"; fail=1; continue; }
import re, sys
p, slug = sys.argv[1], sys.argv[2]
s = open(p).read()
new, n = re.subn(r"basePath:[^,]+,", f"basePath:'/demos/{slug}',", s, count=1)
assert n == 1, "basePath not found"
open(p, "w").write(new)
PY
  (cd "$w" && ./node_modules/.bin/next build --webpack >"$WORK/$slug.log" 2>&1) || { echo "FAIL build $slug (see $WORK/$slug.log)"; fail=1; continue; }
  # Next does not prefix metadata icons with basePath.
  python3 - "$w/out" "$slug" <<'PY'
import sys
from pathlib import Path
out, slug = Path(sys.argv[1]), sys.argv[2]
for f in list(out.rglob("*.html")) + list(out.rglob("*.txt")):
    s = f.read_text()
    t = s
    for icon in ("favicon.svg", "icon.svg"):
        t = t.replace(f'"/{icon}', f'"/demos/{slug}/{icon}').replace(f'\\"/{icon}', f'\\"/demos/{slug}/{icon}')
    if t != s:
        f.write_text(t)
PY
  rm -rf "$SITE/demos/$slug"
  cp -R "$w/out" "$SITE/demos/$slug"
  echo "ok $slug $(du -sh "$SITE/demos/$slug" | cut -f1)"
done
exit $fail
