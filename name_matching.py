"""
Name matching utilities for the Chest Tracker.

Handles small OCR misreads of player names in two tiers:

  Tier 1 - "fold match": the name differs from an existing member only in
  case and/or accent marks (e.g. "AsiL" vs "ASiL", "Savi" vs "Sàvi"). No two
  real Total Battle accounts are ever distinguished purely by case or
  diacritics, so this is safe to auto-correct silently.

  Tier 2 - "fuzzy candidate": the name is close to exactly one existing
  member (small edit distance) but not safely foldable. This is NEVER
  auto-merged. In particular, names that differ only in a trailing
  digit/roman-numeral-like character ("Little John II" vs "Little John I1")
  are exactly the pattern clans use to distinguish different real alt
  accounts, so guessing wrong here would silently corrupt two different
  people's history. These are only ever flagged for a human decision.
"""

import unicodedata
import difflib
import re

# Characters commonly confused by OCR in a trailing numeral/roman-numeral
# suffix (I, II, III, ...). Used only to decide whether a close match is
# too risky to even suggest with confidence beyond "please check this".
_NUMERAL_SUFFIX_CHARS = "Il1iOo0"


def fold_name(name):
    """Lowercase + strip diacritics, for COMPARISON ONLY.
    Never use the result for storage or display."""
    if not name:
        return name
    nfkd = unicodedata.normalize('NFKD', name)
    stripped = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return stripped.lower()


def differs_only_in_trailing_numeral(a, b):
    """True if two names are identical except for a differing trailing run
    of numeral/roman-numeral-like characters. This pattern usually
    distinguishes real, different alt accounts, so it's a signal to be
    extra cautious rather than a signal to merge."""
    if a == b:
        return False
    base_a = re.sub(f'[{_NUMERAL_SUFFIX_CHARS}]+$', '', a)
    base_b = re.sub(f'[{_NUMERAL_SUFFIX_CHARS}]+$', '', b)
    return base_a == base_b and base_a != ''


def find_fold_match(name, known_members):
    """Tier 1: exact match once case/diacritics are folded away.
    Returns the canonical existing member name, or None."""
    folded = fold_name(name)
    for member in known_members:
        if member != name and fold_name(member) == folded:
            return member
    return None


def find_fuzzy_candidates(name, known_members, ratio_threshold=0.90, max_len_diff=1):
    """Tier 2: existing members close enough to `name` to be worth a human's
    attention. Excludes anything that's actually a fold match (Tier 1
    handles those). Returns a list of (member_name, ratio), most similar
    first."""
    folded = fold_name(name)
    candidates = []
    for member in known_members:
        if member == name:
            continue
        folded_member = fold_name(member)
        if folded_member == folded:
            continue  # handled by find_fold_match, not a fuzzy candidate
        if abs(len(folded_member) - len(folded)) > max_len_diff:
            continue
        ratio = difflib.SequenceMatcher(None, folded, folded_member).ratio()
        if ratio >= ratio_threshold:
            candidates.append((member, ratio))
    candidates.sort(key=lambda c: c[1], reverse=True)
    return candidates


def pair_key(name_a, name_b):
    """Stable, order-independent key identifying a pair of names for the
    pending-review / ignored-pairs stores."""
    return '|'.join(sorted([fold_name(name_a), fold_name(name_b)]))


def resolve_player_name(name, known_members, ignored_pairs=None):
    """Resolve a freshly-OCR'd player name against the known member list.

    Returns (name_to_use, flagged_match):
      - name_to_use: the name to actually record. This is the canonical
        existing name if a safe Tier-1 fold match was found; otherwise it's
        exactly the original OCR'd name, unchanged.
      - flagged_match: the name of a close-but-unconfirmed existing member
        to raise for manual review, or None if there's nothing to flag.

    `ignored_pairs` is a set of pair_key() values the user has already
    confirmed are two different real people; those are never re-flagged.
    """
    ignored_pairs = ignored_pairs or set()

    fold_match = find_fold_match(name, known_members)
    if fold_match:
        return fold_match, None

    candidates = find_fuzzy_candidates(name, known_members)
    if not candidates:
        return name, None

    # Only flag when there's a single unambiguous best candidate. If two
    # or more existing members are all similarly close, guessing which one
    # (if any) is intended is worse than just leaving it alone.
    if len(candidates) > 1:
        return name, None

    best_match, _ratio = candidates[0]

    if pair_key(name, best_match) in ignored_pairs:
        return name, None

    return name, best_match
