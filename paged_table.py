"""
paged_table.py  –  drop-in replacement for Ui.PagedTable

Same API used by main.py:
    PagedTable(headers, center_cols=(), fit_columns=True, default_size="50")
    .set_columns(cols)  .set_rows(rows)  .clear()

What's new
  * Column widths adapt to the real content (header + cell text), clamped to a min/max,
    and stretch to fill the view when the data is narrow (fit_columns=True).
  * Reliable vertical AND horizontal scrolling (per-pixel, scrollbars only when needed).
  * Record view: double-click a row (or press "Record view") to see every field of the
    record, wrapped to its content, with Prev / Next navigation and Copy.
  * Filter box (searches all columns), click a header to sort, rows-per-page selector,
    real record numbers in the row header, tooltips for long values, Ctrl+C copy.
"""
import datetime as dt

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFontMetrics, QKeySequence
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QDialog, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

MIN_COL, MAX_COL = 70, 420
PAGE_SIZES = ["25", "50", "100", "200", "500"]


def fmt(v):
    """Value -> display text."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "✔" if v else "✘"
    if isinstance(v, dt.datetime):
        return v.strftime("%Y-%m-%d %H:%M")
    return str(v)


# ----------------------------------------------------------------------------
# Record view dialog
# ----------------------------------------------------------------------------
class RecordDialog(QDialog):
    def __init__(self, columns, records, index, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record view")
        self.resize(640, 560)
        self.columns, self.records, self.index = columns, records, index

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)
        self.title = QLabel()
        self.title.setObjectName("DialogTitle")
        lay.addWidget(self.title)

        self.grid = QTableWidget(0, 2)
        self.grid.setHorizontalHeaderLabels(["Field", "Value"])
        self.grid.verticalHeader().setVisible(False)
        self.grid.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.grid.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.grid.setWordWrap(True)
        self.grid.setAlternatingRowColors(True)
        self.grid.setShowGrid(False)
        self.grid.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.grid.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        hh = self.grid.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setStretchLastSection(True)
        lay.addWidget(self.grid, 1)

        bar = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Previous")
        self.btn_next = QPushButton("Next ▶")
        self.btn_copy = QPushButton("📋 Copy")
        self.btn_close = QPushButton("Close")
        for b in (self.btn_prev, self.btn_next, self.btn_copy, self.btn_close):
            b.setObjectName("SecondaryButton")
        self.btn_prev.clicked.connect(lambda: self.go(-1))
        self.btn_next.clicked.connect(lambda: self.go(1))
        self.btn_copy.clicked.connect(self.copy)
        self.btn_close.clicked.connect(self.accept)
        bar.addWidget(self.btn_prev)
        bar.addWidget(self.btn_next)
        bar.addStretch()
        bar.addWidget(self.btn_copy)
        bar.addWidget(self.btn_close)
        lay.addLayout(bar)
        self.show_record()

    def go(self, step):
        self.index = max(0, min(len(self.records) - 1, self.index + step))
        self.show_record()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Left:
            self.go(-1)
        elif e.key() == Qt.Key.Key_Right:
            self.go(1)
        else:
            super().keyPressEvent(e)

    def show_record(self):
        rec = self.records[self.index]
        self.title.setText(f"Record {self.index + 1} of {len(self.records)}")
        self.btn_prev.setEnabled(self.index > 0)
        self.btn_next.setEnabled(self.index < len(self.records) - 1)
        g = self.grid
        g.setRowCount(len(self.columns))
        fm = QFontMetrics(g.font())
        field_w = 90
        for i, name in enumerate(self.columns):
            text = fmt(rec[i]) if i < len(rec) else ""
            fi = QTableWidgetItem(str(name))
            f = fi.font()
            f.setBold(True)
            fi.setFont(f)
            fi.setFlags(fi.flags() & ~Qt.ItemFlag.ItemIsEditable)
            vi = QTableWidgetItem(text if text != "" else "—")
            vi.setFlags(vi.flags() & ~Qt.ItemFlag.ItemIsEditable)
            vi.setToolTip(text[:1000])
            g.setItem(i, 0, fi)
            g.setItem(i, 1, vi)
            field_w = max(field_w, fm.horizontalAdvance(str(name)) + 36)
        g.setColumnWidth(0, min(field_w, 260))
        self.refit_rows()

    def refit_rows(self):
        self.grid.resizeRowsToContents()   # rows grow to fit wrapped content

    def resizeEvent(self, e):
        super().resizeEvent(e)
        QTimer.singleShot(0, self.refit_rows)

    def copy(self):
        rec = self.records[self.index]
        QApplication.clipboard().setText(
            "\n".join(f"{c}: {fmt(rec[i])}" for i, c in enumerate(self.columns)))


# ----------------------------------------------------------------------------
# PagedTable
# ----------------------------------------------------------------------------
class PagedTable(QWidget):
    def __init__(self, headers=(" ",), center_cols=(), fit_columns=True, default_size="50",
                 parent=None):
        super().__init__(parent)
        self.center_cols = set(center_cols)
        self.fit_columns = fit_columns
        self.columns = list(headers)
        self._all, self._view, self._hay = [], [], []
        self._page = 0
        self._sort = (None, Qt.SortOrder.AscendingOrder)
        self._manual = False          # user dragged a column border
        self._applying = False
        self._base_widths = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # ---- top bar
        top = QHBoxLayout()
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("🔍 Filter records (all columns)…")
        self.filter.setClearButtonEnabled(True)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._refilter)
        self.filter.textChanged.connect(lambda _: self._timer.start())
        self.btn_record = QPushButton("🗂 Record view")
        self.btn_record.setObjectName("SecondaryButton")
        self.btn_record.clicked.connect(self.open_record)
        top.addWidget(self.filter, 1)
        top.addWidget(self.btn_record)
        root.addLayout(top)

        # ---- table
        t = self.table = QTableWidget(0, len(self.columns))
        t.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        t.setAlternatingRowColors(True)
        t.setShowGrid(False)
        t.setWordWrap(False)
        t.setTextElideMode(Qt.TextElideMode.ElideRight)
        # scrolling: per-pixel, bars only when needed, both directions work
        t.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        t.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        t.verticalHeader().setDefaultSectionSize(34)
        t.verticalHeader().setMinimumWidth(46)
        t.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        hh = t.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hh.setStretchLastSection(False)
        hh.setMinimumSectionSize(50)
        hh.setSectionsClickable(True)
        hh.setSortIndicatorShown(True)
        hh.setSortIndicatorClearable(True) if hasattr(hh, "setSortIndicatorClearable") else None
        hh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hh.sectionClicked.connect(self._sort_by)
        hh.sectionResized.connect(self._on_section_resized)
        t.cellDoubleClicked.connect(lambda r, c: self.open_record(r))
        root.addWidget(t, 1)

        # ---- pager
        bar = QHBoxLayout()
        self.lbl_info = QLabel("")
        self.lbl_info.setObjectName("SubHeader")
        self.size_combo = QComboBox()
        sizes = PAGE_SIZES if str(default_size) in PAGE_SIZES else sorted(
            PAGE_SIZES + [str(default_size)], key=int)
        self.size_combo.addItems(sizes)
        self.size_combo.setCurrentText(str(default_size))
        self.size_combo.currentIndexChanged.connect(lambda _: self._goto(0))
        self.btn_first, self.btn_prev, self.btn_next, self.btn_last = (
            QPushButton("⏮"), QPushButton("◀"), QPushButton("▶"), QPushButton("⏭"))
        for b in (self.btn_first, self.btn_prev, self.btn_next, self.btn_last):
            b.setObjectName("SecondaryButton")
            b.setFixedWidth(44)
        self.btn_first.clicked.connect(lambda: self._goto(0))
        self.btn_prev.clicked.connect(lambda: self._goto(self._page - 1))
        self.btn_next.clicked.connect(lambda: self._goto(self._page + 1))
        self.btn_last.clicked.connect(lambda: self._goto(self._pages() - 1))
        self.lbl_page = QLabel("Page 1 / 1")
        bar.addWidget(self.lbl_info, 1)
        bar.addWidget(QLabel("Rows per page"))
        bar.addWidget(self.size_combo)
        bar.addSpacing(10)
        for w in (self.btn_first, self.btn_prev, self.lbl_page, self.btn_next, self.btn_last):
            bar.addWidget(w)
        root.addLayout(bar)
        self._render()

    # ------------------------------------------------------------------ public API
    def set_columns(self, cols):
        self.columns = list(cols)
        self._sort = (None, Qt.SortOrder.AscendingOrder)
        self.table.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in self.columns])

    def set_rows(self, rows):
        self._all = [list(r) for r in rows]
        self._hay = [" ".join(fmt(v) for v in r).lower() for r in self._all]
        self._page = 0
        self._manual = False
        self._refilter()

    def clear(self):
        self._all, self._view, self._hay = [], [], []
        self._page = 0
        self._render()

    # ------------------------------------------------------------------ internals
    def page_size(self):
        return int(self.size_combo.currentText())

    def _pages(self):
        return max(1, -(-len(self._view) // self.page_size()))

    def _goto(self, p):
        self._page = max(0, min(self._pages() - 1, p))
        self._manual = False
        self._render()

    def _refilter(self):
        q = self.filter.text().strip().lower()
        self._view = [i for i, h in enumerate(self._hay) if q in h] if q else list(range(len(self._all)))
        self._resort()
        self._page = 0
        self._manual = False
        self._render()

    def _sort_by(self, col):
        cur, order = self._sort
        order = (Qt.SortOrder.DescendingOrder if cur == col and order == Qt.SortOrder.AscendingOrder
                 else Qt.SortOrder.AscendingOrder)
        self._sort = (col, order)
        self.table.horizontalHeader().setSortIndicator(col, order)
        self._resort()
        self._page = 0
        self._render()

    def _resort(self):
        col, order = self._sort
        if col is None or not self._view:
            return

        def key(i):
            v = self._all[i][col] if col < len(self._all[i]) else None
            return (v is None, v if isinstance(v, (int, float)) else fmt(v).lower())
        rev = order == Qt.SortOrder.DescendingOrder
        try:
            self._view.sort(key=key, reverse=rev)
        except TypeError:   # mixed types in one column
            self._view.sort(key=lambda i: (self._all[i][col] is None, fmt(self._all[i][col]).lower()),
                            reverse=rev)

    def _page_rows(self):
        ps = self.page_size()
        idx = self._view[self._page * ps:(self._page + 1) * ps]
        return idx

    def _render(self):
        t = self.table
        idx = self._page_rows()
        start = self._page * self.page_size()
        ncols = len(self.columns)
        t.setUpdatesEnabled(False)
        t.clearContents()
        t.setRowCount(len(idx))
        t.setColumnCount(ncols)
        t.setHorizontalHeaderLabels([str(c) for c in self.columns])
        t.setVerticalHeaderLabels([str(start + k + 1) for k in range(len(idx))])

        fm = QFontMetrics(t.font())
        hf = t.horizontalHeader().font()
        hf.setBold(True)
        hfm = QFontMetrics(hf)
        widths = [hfm.horizontalAdvance(str(c)) + 48 for c in self.columns]   # + sort arrow/padding
        center = Qt.AlignmentFlag.AlignCenter
        left = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        for r, i in enumerate(idx):
            row = self._all[i]
            for c in range(min(ncols, len(row))):
                text = fmt(row[c])
                one = text.replace("\r", " ").replace("\n", " ")
                item = QTableWidgetItem(one)
                item.setTextAlignment(center if c in self.center_cols else left)
                if len(text) > 30 or "\n" in text:
                    item.setToolTip(text[:1000])
                t.setItem(r, c, item)
                if r < 300:   # sample the first rows for width
                    widths[c] = max(widths[c], fm.horizontalAdvance(one[:150]) + 34)
        self._base_widths = [max(MIN_COL, min(MAX_COL, w)) for w in widths]
        t.setUpdatesEnabled(True)
        self._apply_widths()

        total, pages = len(self._view), self._pages()
        shown_from = start + 1 if total else 0
        shown_to = start + len(idx)
        extra = f"  (filtered from {len(self._all):,})" if total != len(self._all) else ""
        self.lbl_info.setText(f"Records {shown_from:,}–{shown_to:,} of {total:,}{extra}")
        self.lbl_page.setText(f"Page {self._page + 1} / {pages}")
        self.btn_first.setEnabled(self._page > 0)
        self.btn_prev.setEnabled(self._page > 0)
        self.btn_next.setEnabled(self._page < pages - 1)
        self.btn_last.setEnabled(self._page < pages - 1)
        self.btn_record.setEnabled(total > 0)

    def _apply_widths(self):
        """Content-based widths; if they don't fill the view, share the extra space."""
        if not self._base_widths:
            return
        self._applying = True
        widths = list(self._base_widths)
        vw = self.table.viewport().width()
        total = sum(widths)
        if self.fit_columns and 0 < total < vw:
            extra = vw - total
            widths = [w + int(extra * w / total) for w in widths]
        for c, w in enumerate(widths):
            self.table.setColumnWidth(c, w)
        self._applying = False

    def _on_section_resized(self, *_):
        if not self._applying:
            self._manual = True      # keep the user's own widths

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if not self._manual:
            QTimer.singleShot(0, self._apply_widths)

    # ------------------------------------------------------------------ record view
    def open_record(self, row=None):
        if not self._view:
            return
        if not isinstance(row, int) or row < 0:
            sel = self.table.selectionModel().selectedRows()
            row = sel[0].row() if sel else 0
        records = [self._all[i] for i in self._view]
        pos = self._page * self.page_size() + row
        RecordDialog(self.columns, records, min(pos, len(records) - 1), self).exec()

    # ------------------------------------------------------------------ Ctrl+C
    def keyPressEvent(self, e):
        if e.matches(QKeySequence.StandardKey.Copy):
            rows = sorted({i.row() for i in self.table.selectedIndexes()})
            lines = ["\t".join(fmt(self._all[self._page_rows()[r]][c]) if c < len(self._all[self._page_rows()[r]]) else ""
                               for c in range(len(self.columns))) for r in rows]
            QApplication.clipboard().setText("\n".join(lines))
        else:
            super().keyPressEvent(e)
