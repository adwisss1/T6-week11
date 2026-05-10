# Nama  : Baiq Adelia Dwi Savitri
# NIM   : F1D02310006
# Kelas : D

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QFrame
)
from PySide6.QtCore import Qt


class PostDialog(QDialog):
    def __init__(self, parent=None, post=None):
        super().__init__(parent)

        # Judul dialog berbeda tergantung mode
        is_edit = post is not None
        self.setWindowTitle("Edit Post" if is_edit else "Tambah Post Baru")
        self.setMinimumWidth(480)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header label
        mode_label = QLabel("Edit Post" if is_edit else "Tambah Post Baru")
        mode_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 4px;"
        )
        layout.addWidget(mode_label)

        # Garis pemisah
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #bdc3c7;")
        layout.addWidget(line)

        # Form fields
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Masukkan judul post...")
        self.title_input.setMinimumHeight(32)

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Masukkan isi konten post...")
        self.body_input.setMinimumHeight(100)

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Masukkan nama penulis...")
        self.author_input.setMinimumHeight(32)

        self.slug_input = QLineEdit()
        self.slug_input.setPlaceholderText("contoh: judul-post-saya (harus unik)")
        self.slug_input.setMinimumHeight(32)

        self.status_input = QComboBox()
        self.status_input.addItems(["published", "draft"])
        self.status_input.setMinimumHeight(32)

        form.addRow("Title *:", self.title_input)
        form.addRow("Body *:", self.body_input)
        form.addRow("Author *:", self.author_input)
        form.addRow("Slug *:", self.slug_input)
        form.addRow("Status:", self.status_input)

        layout.addLayout(form)

        # Catatan validasi
        note = QLabel("* Field wajib diisi. Slug harus unik di seluruh data.")
        note.setStyleSheet("font-size: 11px; color: #7f8c8d; font-style: italic;")
        layout.addWidget(note)

        # Tombol OK dan Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Ok).setText(
            "Simpan Perubahan" if is_edit else "Tambah Post"
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Jika mode Edit, isi form dengan data yang sudah ada
        if post:
            self.title_input.setText(post.get('title', ''))
            self.body_input.setPlainText(post.get('body', ''))
            self.author_input.setText(post.get('author', ''))
            self.slug_input.setText(post.get('slug', ''))
            # Set nilai combobox sesuai status lama
            idx = self.status_input.findText(post.get('status', 'draft'))
            if idx >= 0:
                self.status_input.setCurrentIndex(idx)

    def get_data(self):
        """Ambil data dari form sebagai dict siap kirim ke API."""
        return {
            'title': self.title_input.text().strip(),
            'body': self.body_input.toPlainText().strip(),
            'author': self.author_input.text().strip(),
            'slug': self.slug_input.text().strip(),
            'status': self.status_input.currentText(),
        }