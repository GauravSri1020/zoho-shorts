#!/bin/bash
# usage: pub.sh <id> <publish_at UTC>  -> previews/<id>.mp4 + meta on longform-previews, request on long-videos
set -e
ID=$1; PUB=$2
R=$(cd /home/claude/zoho-shorts && git remote get-url origin)
rm -rf /tmp/lp && git clone -q --depth 1 -b longform-previews "$R" /tmp/lp
cp /home/claude/jh/$ID.mp4 /tmp/lp/previews/$ID.mp4
cp /home/claude/jh/meta/$ID.meta.json /tmp/lp/previews/$ID.meta.json
cd /tmp/lp && git add previews/$ID.* && git commit -q -m "preview: $ID (Jensen Huang Short)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Xrtm8Hv76gXmCZ4TCqdR6m" && git push -q origin longform-previews
cd /tmp/lv && git pull -q --rebase
echo "{\"id\": \"$ID\", \"publish_at\": \"$PUB\", \"upscale\": false, \"why\": \"Gaurav 24 Nov: ~10 Jensen Huang Shorts today\"}" > docs/longform/upload-requests/$ID.json
git add docs/longform/upload-requests/$ID.json && git commit -q -m "upload request: $ID at $PUB

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Xrtm8Hv76gXmCZ4TCqdR6m" && git push -q origin long-videos
echo "requested $ID $PUB"
