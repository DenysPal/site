#!/usr/bin/env python3
"""
Replace all Tawk.to chat embeds with Jivo widget:
  <script src="//code.jivosite.com/widget/EW50Bpt4ko" async></script>

Handles blocks with Tawk.to comments and generic script tags containing embed.tawk.to.
"""
import os
import re
from typing import Tuple

JIVO_SNIPPET = '<script src="//code.jivosite.com/widget/EW50Bpt4ko" async></script>'

# Regex for commented Tawk.to block
RE_TAWK_COMMENTED = re.compile(
    r"<!--\s*Start of Tawk\.to Script\s*-->[\s\S]*?<!--\s*End of Tawk\.to Script\s*-->",
    re.IGNORECASE,
)

# Regex for any <script>...</script> that contains embed.tawk.to
RE_TAWK_GENERIC = re.compile(
    r"<script[^>]*>[^<]*[\s\S]*?embed\.tawk\.to[\s\S]*?</script>",
    re.IGNORECASE,
)

def replace_in_content(content: str) -> Tuple[str, int]:
    replaced = 0

    def replace_block(match):
        nonlocal replaced
        replaced += 1
        # Keep surrounding whitespace similar
        return JIVO_SNIPPET

    # First pass: replace commented blocks
    content, count1 = RE_TAWK_COMMENTED.subn(replace_block, content)
    replaced += 0  # count captured in callback

    # Second pass: replace any remaining generic script blocks with tawk
    content, count2 = RE_TAWK_GENERIC.subn(replace_block, content)

    return content, (count1 + count2)


def process_file(path: str) -> int:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception:
        return 0

    if 'tawk.to' not in original and 'embed.tawk.to' not in original and 'Tawk_API' not in original:
        return 0

    updated, count = replace_in_content(original)
    if count > 0 and updated != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated)
        return count
    return 0


def main():
    total_files = 0
    total_replacements = 0
    html_files = []
    for root, _, files in os.walk('.'):
        for name in files:
            if name.lower().endswith('.html'):
                html_files.append(os.path.join(root, name))

    print(f'Found {len(html_files)} HTML files')
    for fp in html_files:
        count = process_file(fp)
        if count:
            total_files += 1
            total_replacements += count
            print(f'  Updated {fp} ({count} block(s))')

    print(f'Finished. Files updated: {total_files}, Tawk blocks replaced: {total_replacements}')

if __name__ == '__main__':
    main()
