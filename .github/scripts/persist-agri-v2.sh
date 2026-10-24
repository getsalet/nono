#!/usr/bin/env bash
set -euo pipefail
branch=feat/agri-generator-v2-2905-merge593
work=$(mktemp -d)
mkdir -p "$work/artifacts"
if test -d artifacts/agri-v2; then cp -a artifacts/agri-v2 "$work/artifacts/"; rm -f "$work/artifacts/agri-v2/.writer.lock"; fi
if test -f data/agri-v2/health/latest.json; then cp data/agri-v2/health/latest.json "$work/health.json"; fi
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
start=$(git rev-parse HEAD)
for attempt in 1 2 3; do
 git fetch origin "$branch"
 if ! git diff --quiet "$start" "origin/$branch" -- artifacts/agri-v2; then echo 'Remote article state changed; stop rather than overwrite.'; exit 1; fi
 git reset --hard "origin/$branch"
 if test -d "$work/artifacts/agri-v2"; then mkdir -p artifacts/agri-v2; cp -a "$work/artifacts/agri-v2/." artifacts/agri-v2/; git add -f artifacts/agri-v2; fi
 if test -f "$work/health.json"; then mkdir -p data/agri-v2/health; cp "$work/health.json" data/agri-v2/health/latest.json; git add -f data/agri-v2/health/latest.json; fi
 if git diff --cached --quiet; then exit 0; fi
 git commit -m 'Record bounded agriculture cycle and WordPress receipt [skip ci]'
 if git push origin "HEAD:$branch"; then exit 0; fi
 sleep 3
done
exit 1
