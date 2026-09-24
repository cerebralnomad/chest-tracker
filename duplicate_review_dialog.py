"""
Dialog for reviewing OCR-flagged possible-duplicate player names.

Shown by MainWindow right after processing completes (if anything was
flagged during that run), and again on app close as a safety net if
anything is still unresolved.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame
)


class DuplicateReviewDialog(QDialog):
    """
    Presents each flagged (new_name, matched_name) pair with two choices:

      - "Merge into <matched_name>": folds new_name's chest history into
        matched_name and removes new_name as a separate member going
        forward. Use only when you're sure it's the same person.

      - "Keep Separate": dismisses this flag and remembers the pair so it
        is never raised again.

    Closing the dialog without acting on a row (via the bottom button)
    leaves that row pending for next time - it is NOT treated as either
    decision.

    `on_merge(new_name, matched_name)` and `on_keep_separate(pair_key)` are
    callables supplied by the caller that actually perform the action and
    update the pending-review store.
    """

    def __init__(self, pending_items, on_merge, on_keep_separate, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Possible Duplicate Player Names")
        self.setMinimumWidth(540)
        self._on_merge = on_merge
        self._on_keep_separate = on_keep_separate
        self._pending_items = list(pending_items)

        layout = QVBoxLayout()

        intro = QLabel(
            "These newly-seen names look like they might be OCR misreads of "
            "existing members. Choose \"Merge\" only if you're sure it's the "
            "same person - a trailing number or numeral (I, II, III, ...) "
            "often means a different real alt account, not a typo."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout()
        content.setLayout(self.content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._frames = {}
        for item in self._pending_items:
            self._add_row(item)

        button_row = QHBoxLayout()
        button_row.addStretch()
        close_btn = QPushButton("Decide Later")
        close_btn.clicked.connect(self.accept)
        button_row.addWidget(close_btn)
        layout.addLayout(button_row)

        self.setLayout(layout)

    def _add_row(self, item):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        row_layout = QVBoxLayout()

        label = QLabel(
            f"'<b>{item['new_name']}</b>' looks similar to existing member "
            f"'<b>{item['matched_name']}</b>'"
        )
        label.setWordWrap(True)
        row_layout.addWidget(label)

        btn_row = QHBoxLayout()
        merge_btn = QPushButton(f"Merge into '{item['matched_name']}'")
        keep_btn = QPushButton("Keep Separate")
        btn_row.addWidget(merge_btn)
        btn_row.addWidget(keep_btn)
        row_layout.addLayout(btn_row)

        frame.setLayout(row_layout)
        self.content_layout.addWidget(frame)
        self._frames[item['pair_key']] = frame

        merge_btn.clicked.connect(lambda _, i=item: self._handle_merge(i))
        keep_btn.clicked.connect(lambda _, i=item: self._handle_keep_separate(i))

    def _handle_merge(self, item):
        self._on_merge(item['new_name'], item['matched_name'])
        self._remove_row(item)

    def _handle_keep_separate(self, item):
        self._on_keep_separate(item['pair_key'])
        self._remove_row(item)

    def _remove_row(self, item):
        frame = self._frames.pop(item['pair_key'], None)
        if frame is not None:
            frame.setParent(None)
        self._pending_items = [i for i in self._pending_items if i['pair_key'] != item['pair_key']]
        if not self._pending_items:
            self.accept()
