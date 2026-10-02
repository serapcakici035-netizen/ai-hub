# AI Hub

Groq modelleri için FastAPI sohbet uç noktası ve Türkçe web arayüzü. Kullanıcıdan API anahtarı istenmez; anahtarlar yalnızca sunucuda tutulur.

**Canlı site:** https://ai-hub-bjo0.onrender.com/  
**Kaynak depo:** https://github.com/serapcakici035-netizen/ai-hub

## Kurulum

1. Python 3.10+ kurun.
2. `py -3 -m venv .venv` çalıştırın (Python komutu PATH üzerindeyse `python -m venv .venv` de olur).
3. Windows PowerShell'de `.venv\Scripts\Activate.ps1` çalıştırın.
4. `pip install -r backend/requirements.txt` çalıştırın.
5. `.env.example` dosyasını `.env` adıyla kopyalayın. Tek anahtar için `GROQ_API_KEY`, birden fazla anahtar için virgülle ayrılmış `GROQ_API_KEYS` değerini doldurun. İkisi de varsa `GROQ_API_KEYS` kullanılır.
6. `uvicorn backend.main:app --reload` çalıştırın.
7. `http://127.0.0.1:8000` adresini açın.

`POST /api/chat` gövdesi: `{ "provider": "groq", "model": "openai/gpt-oss-20b", "prompt": "Merhaba" }`. Yanıt: `{ "provider": "groq", "model": "...", "answer": "..." }`.

Kota ve model erişimi Groq hesabına göre değişir. Basit IP sınırı dakikada 5 istektir; tek süreç belleğinde tutulur. Çok işçili veya dağıtık dağıtımda Redis gibi paylaşılan bir sınırlandırıcı kullanın.

## GitHub üzerinden yayınlama

Proje kökündeki `render.yaml`, frontend ve API'yi tek Render web servisinde çalıştırır. GitHub deposunu Render Blueprint'e bağlayın. Groq anahtarlarını Render'da **ai-hub → Environment → Edit** ekranında `GROQ_API_KEYS` değişkenine girip **Save, rebuild, and deploy** seçin.

Ücretsiz Render web servisi uzun süre kullanılmadığında uykuya geçebilir; ilk istek daha yavaş yanıtlanabilir. Yayın öncesinde gerçek anahtarların `.env` içinde kaldığını ve `.gitignore` tarafından hariç tutulduğunu kontrol edin. Arayüz stilleri derlenmiş `frontend/styles.css` dosyasından gelir; HTML sınıflarını değiştirdiğinizde `npm install` ve `npm run build:css` çalıştırıp üretilen CSS dosyasını commit edin.

## Groq anahtarlarını yönetme

**Anahtarı sohbete ya da GitHub'a yazmayın.** Yeni Groq anahtarını `GROQ_API_KEYS` değerine ekleyebilir veya eskisinin yerine yazabilirsiniz. Anahtar yenilediğinizde Render'daki değeri değiştirip eski anahtarı Groq panelinden iptal edin. Yerel geliştirmede anahtarı yalnızca Git tarafından yok sayılan `.env` dosyasına yazın.
