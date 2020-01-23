#!/usr/bin/env bash
user="$1"
IFS= read -sp "Polygon Password: " pass
cid="$2"
xml=$(curl -X POST --data "login=${user}&password=${pass}" "https://polygon.codeforces.com/c/$cid/contest.xml" 2>/dev/null | grep "problem index" | sed -e 's/\s*<problem index="\([^"]*\)" url="\([^"]*\)"\/>\s*/\1 \2/')
while read id url; do
	printf "Downloading problem %s (%s)\n" "$id" "$url"
	curl -X POST --data "login=${user}&password=${pass}&type=linux" "$url" -o "$id.zip"
done <<< "$xml"

