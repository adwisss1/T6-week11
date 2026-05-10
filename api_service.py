# Nama  : Baiq Adelia Dwi Savitri
# NIM   : F1D02310006
# Kelas : [Kelas Anda]

import requests


class ApiService:
    """
    Service class untuk semua interaksi HTTP dengan Posts API.
    Setiap method melempar exception jika request gagal —
    exception ini akan ditangkap oleh ApiWorker di layer atas.
    """

    BASE_URL = "https://api.pahrul.my.id/api"
    TIMEOUT = 10  # batas waktu tunggu response (detik)

    #  POSTS 
    def get_posts(self):
        """GET /api/posts - Ambil semua posts"""
        response = requests.get(
            f"{self.BASE_URL}/posts",
            timeout=self.TIMEOUT
        )
        response.raise_for_status()
        return response.json()['data']

    def get_post(self, post_id):
        """GET /api/posts/{id} - Ambil 1 post beserta comments"""
        response = requests.get(
            f"{self.BASE_URL}/posts/{post_id}",
            timeout=self.TIMEOUT
        )
        response.raise_for_status()
        return response.json()['data']

    def create_post(self, title, body, author, slug, status):
        """POST /api/posts - Tambah post baru"""
        payload = {
            'title': title,
            'body': body,
            'author': author,
            'slug': slug,
            'status': status,
        }
        response = requests.post(
            f"{self.BASE_URL}/posts",
            json=payload,
            timeout=self.TIMEOUT
        )
        # Tangani error validasi 422 (misal: slug sudah ada)
        if response.status_code == 422:
            errors = response.json().get('errors', {})
            msg = '\n'.join(
                f"{field}: {', '.join(msgs)}"
                for field, msgs in errors.items()
            )
            raise ValueError(f"Validasi gagal:\n{msg}")
        response.raise_for_status()
        return response.json()

    def update_post(self, post_id, title, body, author, slug, status):
        """PUT /api/posts/{id} - Update seluruh data post"""
        payload = {
            'title': title,
            'body': body,
            'author': author,
            'slug': slug,
            'status': status,
        }
        response = requests.put(
            f"{self.BASE_URL}/posts/{post_id}",
            json=payload,
            timeout=self.TIMEOUT
        )
        if response.status_code == 422:
            errors = response.json().get('errors', {})
            msg = '\n'.join(
                f"{field}: {', '.join(msgs)}"
                for field, msgs in errors.items()
            )
            raise ValueError(f"Validasi gagal:\n{msg}")
        response.raise_for_status()
        return response.json()

    def delete_post(self, post_id):
        """DELETE /api/posts/{id} - Hapus post (cascade delete comments)"""
        response = requests.delete(
            f"{self.BASE_URL}/posts/{post_id}",
            timeout=self.TIMEOUT
        )
        response.raise_for_status()
        return True

if __name__ == "__main__":
    svc = ApiService()
    posts = svc.get_posts()
    print(f"Total posts: {len(posts)}")
    if posts:
        print(f"Post pertama: [{posts[0]['id']}] {posts[0]['title']}")