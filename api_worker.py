# Nama  : Baiq Adelia Dwi Savitri
# NIM   : F1D02310006
# Kelas : D

from PySide6.QtCore import QObject, Signal
from api_service import ApiService


class ApiWorker(QObject):

    # Signal untuk komunikasi balik ke Main Thread
    finished = Signal()        # selalu dipanggil di akhir (sukses maupun gagal)
    success = Signal(object)   # kirim data hasil (list/dict/bool)
    error = Signal(str)        # kirim pesan error

    def __init__(self, action, post_id=None, title=None, body=None,
                 author=None, slug=None, status=None):
        super().__init__()
        self.action = action       # nama aksi: 'get_posts', 'create_post', dst
        self.post_id = post_id     # dipakai untuk get_post, update, delete
        self.title = title         # dipakai untuk create & update
        self.body = body           # dipakai untuk create & update
        self.author = author       # dipakai untuk create & update
        self.slug = slug           # dipakai untuk create & update
        self.status = status       # dipakai untuk create & update
        self.service = ApiService()  # instance service dibuat di sini

    def run(self):
        """Dijalankan oleh QThread. Panggil service sesuai action."""
        try:
            if self.action == "get_posts":
                result = self.service.get_posts()

            elif self.action == "get_post":
                result = self.service.get_post(self.post_id)

            elif self.action == "create_post":
                result = self.service.create_post(
                    self.title, self.body, self.author,
                    self.slug, self.status
                )

            elif self.action == "update_post":
                result = self.service.update_post(
                    self.post_id, self.title, self.body,
                    self.author, self.slug, self.status
                )

            elif self.action == "delete_post":
                result = self.service.delete_post(self.post_id)

            else:
                raise ValueError(f"Action tidak dikenali: {self.action}")

            self.success.emit(result)  # kirim hasil ke main thread

        except Exception as e:
            self.error.emit(str(e))    # kirim pesan error ke main thread

        finally:
            self.finished.emit()       # selalu emit finished agar thread bersih