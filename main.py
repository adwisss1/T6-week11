# Nama  : Baiq Adelia Dwi Savitri
# NIM   : F1D02310006
# Kelas : D

import sys
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTextEdit, QSplitter, QHeaderView, QMessageBox, QDialog,
    QFrame, QStatusBar
)
from PySide6.QtGui import QColor, QFont

from dialogs import PostDialog    #  dari dialogs.py
from api_worker import ApiWorker  #  dari api_worker.py


class PostManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Post Manager — Threading & REST API")
        self.setGeometry(100, 100, 1000, 650)

        self.posts_data = []   # cache data posts dari API
        self._thread = None
        self._worker = None

        self.setup_ui()
        self.apply_styles()
        self.fetch_posts()     # langsung fetch saat aplikasi dibuka

    
    # SETUP UI
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # Header 
        header = QWidget()
        header.setFixedHeight(40)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("📋 Post Manager")
        title_label.setObjectName("appTitle")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.status_label = QLabel("Memuat data...")
        self.status_label.setObjectName("statusLabel")
        header_layout.addWidget(self.status_label)

        main_layout.addWidget(header)

        # Garis pemisah
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        line.setObjectName("divider")
        main_layout.addWidget(line)

        # Toolbar tombol
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_refresh = QPushButton("🔄  Refresh")
        self.btn_tambah = QPushButton("➕  Tambah Post")
        self.btn_edit = QPushButton("✏️  Edit Post")
        self.btn_hapus = QPushButton("🗑️  Hapus Post")

        self.btn_refresh.setObjectName("btnRefresh")
        self.btn_tambah.setObjectName("btnTambah")
        self.btn_edit.setObjectName("btnEdit")
        self.btn_hapus.setObjectName("btnHapus")

        # Edit & Hapus awalnya disabled — aktif hanya saat ada baris dipilih
        self.btn_edit.setEnabled(False)
        self.btn_hapus.setEnabled(False)

        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_tambah)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_hapus)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        #  Splitter: tabel (kiri) | detail (kanan)
        splitter = QSplitter(Qt.Horizontal)

        # Tabel posts
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Title', 'Author', 'Status'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 90)
        splitter.addWidget(self.table)

        # Panel detail
        detail_container = QWidget()
        detail_layout = QVBoxLayout(detail_container)
        detail_layout.setContentsMargins(8, 0, 0, 0)

        detail_header = QLabel("Detail Post")
        detail_header.setObjectName("detailHeader")
        detail_layout.addWidget(detail_header)

        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        self.detail.setObjectName("detailBox")
        self.detail.setPlaceholderText("Klik baris pada tabel untuk melihat detail post...")
        detail_layout.addWidget(self.detail)

        splitter.addWidget(detail_container)
        splitter.setSizes([480, 520])
        main_layout.addWidget(splitter)

        # Status bar bawah
        self.statusBar().showMessage("Siap")

        # Hubungkan signals ke slots
        self.btn_refresh.clicked.connect(self.fetch_posts)
        self.btn_tambah.clicked.connect(self.add_post)
        self.btn_edit.clicked.connect(self.edit_post)
        self.btn_hapus.clicked.connect(self.delete_post)
        self.table.currentCellChanged.connect(self.on_row_selected)

    def apply_styles(self):
        """Terapkan stylesheet ke seluruh aplikasi."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f4f6f8;
                font-size: 13px;
            }
            #appTitle {
                font-size: 17px;
                font-weight: bold;
                color: #1a252f;
            }
            #statusLabel {
                font-size: 12px;
                color: #555;
                padding: 3px 10px;
                border-radius: 3px;
                background: #dde1e5;
            }
            QPushButton {
                padding: 7px 18px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 4px;
                border: none;
                min-height: 32px;
                min-width: 100px;
            }
            #btnRefresh {
                background-color: #dde1e5;
                color: #2c3e50;
                border: 1px solid #bbb;
            }
            #btnRefresh:hover { background-color: #c8ced4; }
            #btnTambah {
                background-color: #27ae60;
                color: white;
            }
            #btnTambah:hover { background-color: #1e8449; }
            #btnEdit {
                background-color: #2471a3;
                color: white;
            }
            #btnEdit:hover { background-color: #1a5276; }
            #btnHapus {
                background-color: #c0392b;
                color: white;
            }
            #btnHapus:hover { background-color: #922b21; }
            QPushButton:disabled {
                background-color: #c8ced4;
                color: #999;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #c8ced4;
                gridline-color: #e8ecef;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #2471a3;
                color: white;
            }
            QHeaderView::section {
                background-color: #1a252f;
                color: white;
                padding: 7px 8px;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-right: 1px solid #2c3e50;
            }
            #detailHeader {
                font-size: 13px;
                font-weight: bold;
                color: #1a252f;
                padding: 2px 0 4px 0;
            }
            #detailBox {
                background-color: white;
                border: 1px solid #c8ced4;
                padding: 8px;
                color: #1a252f;
                font-size: 12px;
            }
            QStatusBar {
                background-color: #1a252f;
                color: #ecf0f1;
                font-size: 12px;
            }
            QSplitter::handle {
                background-color: #c8ced4;
                width: 2px;
            }
            QTextEdit {
                font-size: 12px;
            }
        """)

    
    # HELPER: JALANKAN WORKER DI THREAD TERPISAH
    
    def run_worker(self, action, on_success, **kwargs):
        """
        Helper: buat QThread + ApiWorker, hubungkan signals, lalu start.
        Semua API call melewati method ini agar konsisten.
        """
        self._thread = QThread()
        self._worker = ApiWorker(action, **kwargs)
        self._worker.moveToThread(self._thread)

        # Hubungkan signals
        self._thread.started.connect(self._worker.run)
        self._worker.success.connect(on_success)
        self._worker.error.connect(self.on_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(lambda: self.set_loading(False))

        self.set_loading(True)
        self._thread.start()

    def set_loading(self, is_loading):
        """Aktifkan/nonaktifkan tombol dan update label saat request berjalan."""
        self.btn_refresh.setEnabled(not is_loading)
        self.btn_tambah.setEnabled(not is_loading)

        # Edit & Hapus hanya aktif jika ada baris dipilih DAN tidak loading
        has_selection = self.table.currentRow() >= 0
        self.btn_edit.setEnabled(not is_loading and has_selection)
        self.btn_hapus.setEnabled(not is_loading and has_selection)

        if is_loading:
            self.status_label.setText(" Loading...")
            self.status_label.setStyleSheet(
                "font-size:12px; color:#2980b9; padding:4px 8px; "
                "border-radius:4px; background:#ebf5fb; font-weight:bold;"
            )
            self.statusBar().showMessage("Menghubungi server...")
        else:
            self.status_label.setStyleSheet(
                "font-size:12px; color:#7f8c8d; padding:4px 8px; "
                "border-radius:4px; background:#ecf0f1;"
            )

    def set_status_success(self, msg):
        self.status_label.setText(f" {msg}")
        self.status_label.setStyleSheet(
            "font-size:12px; color:#27ae60; padding:4px 8px; "
            "border-radius:4px; background:#eafaf1; font-weight:bold;"
        )
        self.statusBar().showMessage(msg)

    def set_status_error(self, msg):
        self.status_label.setText(f" Error")
        self.status_label.setStyleSheet(
            "font-size:12px; color:#e74c3c; padding:4px 8px; "
            "border-radius:4px; background:#fdedec; font-weight:bold;"
        )
        self.statusBar().showMessage(f"Error: {msg}")

    
    # FETCH POSTS (GET /api/posts)
    
    def fetch_posts(self):
        """Ambil semua posts dari server dan tampilkan ke tabel."""
        self.run_worker("get_posts", self.on_posts_loaded)

    def on_posts_loaded(self, posts):
        """Dipanggil saat data posts berhasil diterima dari server."""
        self.posts_data = posts

        # Bersihkan tabel dan isi ulang
        self.table.setRowCount(0)
        for post in self.posts_data:
            row = self.table.rowCount()
            self.table.insertRow(row)

            id_item = QTableWidgetItem(str(post['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(post['title']))
            self.table.setItem(row, 2, QTableWidgetItem(post.get('author', '-')))

            # Tampilkan badge status dengan warna
            status_item = QTableWidgetItem(post.get('status', '-'))
            status_item.setTextAlignment(Qt.AlignCenter)
            if post.get('status') == 'published':
                status_item.setForeground(QColor('#27ae60'))
            else:
                status_item.setForeground(QColor('#e67e22'))
            self.table.setItem(row, 3, status_item)

        self.set_status_success(f"{len(posts)} post dimuat")
        self.detail.clear()
        self.detail.setPlaceholderText(
            "Klik baris pada tabel untuk melihat detail post..."
        )

    
    # ROW SELECTED → TAMPILKAN DETAIL
    def on_row_selected(self, row, col, prev_row, prev_col):
        """Dipanggil saat baris tabel berubah — fetch detail post via GET /id."""
        if row < 0 or row >= len(self.posts_data):
            self.btn_edit.setEnabled(False)
            self.btn_hapus.setEnabled(False)
            return

        # Aktifkan tombol Edit & Hapus
        self.btn_edit.setEnabled(True)
        self.btn_hapus.setEnabled(True)

        # Tampilkan data dari cache lokal dulu (cepat)
        post = self.posts_data[row]
        self.detail.setPlainText(
            f" Memuat detail post [{post['id']}]..."
        )

        # Fetch detail lengkap (termasuk comments) di background
        self.run_worker(
            "get_post",
            self.on_post_detail_loaded,
            post_id=post['id']
        )

    def on_post_detail_loaded(self, post):
        """Tampilkan detail lengkap post beserta comments."""
        comments = post.get('comments', [])
        comment_text = ""
        if comments:
            comment_text = "\n".join(
                f"  [{c.get('id', '?')}] {c.get('author', 'Anonim')}: {c.get('body', '')}"
                for c in comments
            )
        else:
            comment_text = "  (belum ada komentar)"

        detail_text = (
            f"  POST DETAIL\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ID         : {post.get('id', '-')}\n"
            f"Title      : {post.get('title', '-')}\n"
            f"Author     : {post.get('author', '-')}\n"
            f"Slug       : {post.get('slug', '-')}\n"
            f"Status     : {post.get('status', '-')}\n"
            f"Created    : {post.get('created_at', '-')[:10] if post.get('created_at') else '-'}\n"
            f"Updated    : {post.get('updated_at', '-')[:10] if post.get('updated_at') else '-'}\n"
            f"\n"
            f"  BODY\n"
            f"{post.get('body', '-')}\n"
            f"\n"
            f"  COMMENTS ({len(comments)})\n"
            f"{comment_text}\n"
        )
        self.detail.setPlainText(detail_text)

    
    # ADD POST (POST /api/posts)
    
    def add_post(self):
        """Buka dialog tambah post, kirim data ke server jika OK."""
        dialog = PostDialog(self)  # form kosong (mode Tambah)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()

            # Validasi field wajib di sisi client
            if not data['title'] or not data['body'] or not data['author']:
                QMessageBox.warning(
                    self, "Validasi",
                    "Title, Body, dan Author wajib diisi!"
                )
                return
            if not data['slug']:
                QMessageBox.warning(
                    self, "Validasi",
                    "Slug wajib diisi dan harus unik!\n"
                    "Contoh: judul-post-saya"
                )
                return

            self.run_worker(
                "create_post",
                self.on_post_created,
                title=data['title'],
                body=data['body'],
                author=data['author'],
                slug=data['slug'],
                status=data['status'],
            )

    def on_post_created(self, result):
        """Dipanggil saat post baru berhasil dibuat di server."""
        post_id = result.get('data', {}).get('id', '?')
        QMessageBox.information(
            self, "Sukses",
            f"Post berhasil ditambahkan!\nID baru dari server: {post_id}"
        )
        self.fetch_posts()  # refresh tabel

    
    # EDIT POST (PUT /api/posts/{id})
    def edit_post(self):
        """Buka dialog edit dengan data lama, kirim update ke server."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih post terlebih dahulu!")
            return

        post = self.posts_data[row]
        dialog = PostDialog(self, post)  # form terisi data lama (mode Edit)

        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()

            if not data['title'] or not data['body'] or not data['author']:
                QMessageBox.warning(
                    self, "Validasi",
                    "Title, Body, dan Author wajib diisi!"
                )
                return

            self.run_worker(
                "update_post",
                self.on_post_updated,
                post_id=post['id'],
                title=data['title'],
                body=data['body'],
                author=data['author'],
                slug=data['slug'],
                status=data['status'],
            )

    def on_post_updated(self, result):
        """Dipanggil saat post berhasil diupdate di server."""
        QMessageBox.information(self, "Sukses", "Post berhasil diperbarui!")
        self.fetch_posts()  # refresh tabel

    
    # DELETE POST (DELETE /api/posts/{id})
    def delete_post(self):
        """Konfirmasi lalu hapus post yang dipilih (cascade delete comments)."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih post terlebih dahulu!")
            return

        post = self.posts_data[row]
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus post ini?\n\n"
            f"ID    : {post['id']}\n"
            f"Title : {post['title']}\n\n"
            f"⚠️ Semua komentar pada post ini juga akan ikut terhapus (cascade delete).",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # default = No, agar tidak tidak sengaja hapus
        )

        if reply == QMessageBox.Yes:
            self.run_worker(
                "delete_post",
                self.on_post_deleted,
                post_id=post['id']
            )

    def on_post_deleted(self, result):
        """Dipanggil saat post berhasil dihapus dari server."""
        QMessageBox.information(self, "Sukses", "Post berhasil dihapus!")
        self.detail.clear()
        self.fetch_posts()  # refresh tabel

    
    # ERROR HANDLER
    def on_error(self, message):
        """Dipanggil saat ApiWorker mengirim signal error."""
        self.set_status_error(message)
        QMessageBox.critical(
            self, "Terjadi Error",
            f"Request gagal:\n\n{message}\n\n"
            f"Pastikan koneksi internet aktif dan coba lagi."
        )


# ENTRY POINT
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Post Manager")
    window = PostManagerApp()
    window.show()
    sys.exit(app.exec())