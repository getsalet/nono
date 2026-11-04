"""Remove whole sentences that carry banned climate/commercial terms or stray Latin words.

Deleting an unsupported sentence never adds a claim; every remaining QA rule
(word count, links, structure, editorial review) still runs unchanged afterwards.
Sentences containing links are never touched.
"""
import re

BANNED = ('اقلیم', 'آب و هوای', 'آب‌وهوای', 'ارسال رایگان', 'نمایندگی رسمی', 'گارانتی مادام', 'موجود در انبار', 'تخفیف ویژه')
LATIN_OK = {'afp', 'pe', 'uv', 'iso', 'cm', 'mm'}
POLICY = 'afp-sentence-claim-scrub-v1'


def _bad(sentence):
    plain = re.sub(r'<[^>]+>', ' ', sentence)
    if any(term in plain for term in BANNED):
        return True
    return bool({w.lower() for w in re.findall(r'[A-Za-z]+', plain)} - LATIN_OK)


def _scrub_block(inner):
    if '<a' in inner.lower():
        parts = re.split(r'(?<=[.!؟])\s+', inner)
        return ' '.join(p for p in parts if '<a' in p.lower() or not _bad(p)), None
    parts = re.split(r'(?<=[.!؟])\s+', inner)
    kept = [p for p in parts if not _bad(p)]
    return ' '.join(kept), len(parts) - len(kept)


def scrub(obj):
    if not isinstance(obj, dict) or not isinstance(obj.get('html'), str):
        return 0
    removed = 0

    def repl(m):
        nonlocal removed
        tag, attrs, inner = m.group(1), m.group(2) or '', m.group(3)
        new, _ = _scrub_block(inner)
        if new != inner:
            removed += 1
        if not re.sub(r'<[^>]+>|\s', '', new):
            return ''
        return f'<{tag}{attrs}>{new}</{tag}>'

    obj['html'] = re.sub(r'<(p|li)(\s[^>]*)?>(.*?)</\1>', repl, obj['html'], flags=re.S | re.I)
    return removed
