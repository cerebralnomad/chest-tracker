"""
Persisted store for the possible-duplicate-name review workflow.

Keeps track of two things, in a small JSON file next to the chest
databases:

  - "pending": possible-duplicate flags raised during capture that are
    still waiting on a Merge / Keep Separate decision. Persisted (rather
    than kept only in memory) so a "Decide Later" choice survives even if
    the app is closed and reopened before you get back to it.

  - "ignored_pairs": pairs of names you've explicitly told the app are two
    different real people, so the same pair is never flagged again.
"""

import json
from pathlib import Path
from datetime import datetime

from name_matching import pair_key


class PendingReviewStore:
    def __init__(self, db_dir='databases'):
        self.path = Path(db_dir) / 'pending_name_reviews.json'
        self._data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data.setdefault('pending', [])
                    data.setdefault('ignored_pairs', [])
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return {'pending': [], 'ignored_pairs': []}

    def _save(self):
        self.path.parent.mkdir(exist_ok=True)
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2)

    def add_pending(self, new_name, matched_name):
        """Record a flagged pair, unless it's already pending or already
        confirmed as two different people."""
        key = pair_key(new_name, matched_name)
        if key in self._data['ignored_pairs']:
            return
        if any(p['pair_key'] == key for p in self._data['pending']):
            return
        self._data['pending'].append({
            'new_name': new_name,
            'matched_name': matched_name,
            'pair_key': key,
            'flagged_at': datetime.now().isoformat()
        })
        self._save()

    def get_pending(self):
        return list(self._data['pending'])

    def has_pending(self):
        return len(self._data['pending']) > 0

    def resolve(self, key, keep_separate=False):
        """Clear a pending item. If keep_separate is True, also remember
        the pair so it's never flagged again."""
        self._data['pending'] = [p for p in self._data['pending'] if p['pair_key'] != key]
        if keep_separate and key not in self._data['ignored_pairs']:
            self._data['ignored_pairs'].append(key)
        self._save()

    def get_ignored_pairs(self):
        return set(self._data['ignored_pairs'])
