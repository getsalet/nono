#!/usr/bin/env python3
"""Deterministic varied placement for inline images and internal article links."""
from __future__ import annotations

import hashlib
import html
import random
import re

FAQ_RE = re.compile(
    r'<h3\b[^>]*>\s*(?:پرسش|سوال|سؤالات|سوالات).*?(?:متداول|FAQ).*?</h3>',
    re.I | re.S,
)
BLOCK_END_RE = re.compile(r'</(?:p|ul|ol|table)>', re.I)
MARKER_RE = re.compile(r'\[\[\[IMAGE_[2-5]\]\]\]')
TAG_RE = re.compile(r'<[^>]+>')
WORD_RE = re.compile(r'[\u0600-\u06ff\u200c]{4,}|[A-Za-z]{4,}')


def _split_before_faq(body: str) -> tuple[str, str]:
    match = FAQ_RE.search(body or '')
    if not match:
        return body or '', ''
    return body[: match.start()], body[match.start() :]


def _insert_blocks(body: str, blocks: list[str], fractions: list[float]) -> str:
    """Insert blocks after content paragraphs, before FAQ, at spread positions."""
    main, tail = _split_before_faq(body)
    positions = [match.end() for match in BLOCK_END_RE.finditer(main)]
    if not positions:
        return main + ''.join('\n' + block for block in blocks) + tail
    chosen = []
    for index, block in enumerate(blocks):
        fraction = fractions[index] if index < len(fractions) else (index + 1) / (len(blocks) + 1)
        position_index = min(len(positions) - 1, max(0, round((len(positions) - 1) * fraction)))
        chosen.append((positions[position_index], index, block))
    # Reverse insertion keeps earlier offsets stable. The index makes same-position
    # insertions deterministic and preserves the requested order.
    for position, _, block in sorted(chosen, key=lambda row: (row[0], row[1]), reverse=True):
        main = main[:position] + '\n' + block + main[position:]
    return main + tail


def distribute_image_markers(body: str) -> str:
    """Place the four inline-image markers across the article instead of its tail."""
    cleaned = MARKER_RE.sub('', body or '')
    markers = [f'[[[IMAGE_{kind}]]]' for kind in range(2, 6)]
    return _insert_blocks(cleaned, markers, [0.16, 0.37, 0.58, 0.79])


def _seed_number(seed: str) -> int:
    return int(hashlib.sha256(seed.encode('utf-8')).hexdigest()[:16], 16)


def select_internal_links(links: list[dict], seed: str, body: str, count: int) -> list[dict]:
    """Choose a varied mix of relevant and random unique links for one article."""
    unique = []
    seen = set()
    for link in links:
        url = str(link.get('url') or '')
        title = str(link.get('title') or '').strip()
        if not url or not title or url in seen:
            continue
        unique.append({'url': url, 'title': title, 'post_type': link.get('post_type')})
        seen.add(url)
    if len(unique) < count:
        raise RuntimeError('Not enough unique internal links')

    visible = TAG_RE.sub(' ', body or '').lower()
    scored = []
    for link in unique:
        words = {word.lower() for word in WORD_RE.findall(link['title'])}
        score = sum(1 for word in words if word in visible)
        scored.append((score, link))

    rng = random.Random(_seed_number(seed))
    relevant = [link for score, link in scored if score > 0]
    rng.shuffle(relevant)
    chosen = relevant[: min(max(1, count // 2), len(relevant))]
    chosen_urls = {link['url'] for link in chosen}
    remaining = [link for link in unique if link['url'] not in chosen_urls]
    rng.shuffle(remaining)
    chosen.extend(remaining[: count - len(chosen)])
    rng.shuffle(chosen)
    return chosen


def insert_internal_links(body: str, links: list[dict]) -> str:
    phrases = [
        'برای تکمیل این بخش، راهنمای {link} را نیز ببینید.',
        'مطالعه مطلب {link} می‌تواند جزئیات بیشتری در اختیارتان بگذارد.',
        'در همین زمینه، مقاله {link} نیز پیشنهاد می‌شود.',
        'برای مقایسه و تصمیم‌گیری بهتر، مطلب {link} را بخوانید.',
        'اطلاعات تکمیلی در نوشته {link} در دسترس است.',
    ]
    blocks = []
    for index, link in enumerate(links):
        anchor = f'<a href="{html.escape(link["url"], quote=True)}">{html.escape(link["title"])}</a>'
        blocks.append('<p class="navar-related-inline">' + phrases[index % len(phrases)].format(link=anchor) + '</p>')
    fractions = [0.25, 0.46, 0.67, 0.88][: len(blocks)]
    return _insert_blocks(body, blocks, fractions)
