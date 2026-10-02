# AI Hub

Groq, Hugging Face, Gemini ve Kimi için tek bir FastAPI sohbet uç noktası ve Türkçe web arayüzü.

**Canlı site:** https://ai-hub-bjo0.onrender.com/  
**Kaynak depo:** https://github.com/serapcakici035-netizen/ai-hub

## Kurulum

1. Python 3.10+ kurun.
2. `py -3 -m venv .venv` çalıştırın (Python komutu PATH üzerindeyse `python -m venv .venv` de olur).
3. Windows PowerShell'de `.venv\Scripts\Activate.ps1` çalıştırın.
4. `pip install -r backend/requirements.txt` çalıştırın.
5. `.env.example` dosyasını `.env` adıyla kopyalayın ve kullanacağınız sağlayıcıların anahtarlarını doldurun. İki Groq anahtarını `GROQ_API_KEYS` değerine virgülle ayırarak yazabilirsiniz; uygulama bunları sırayla kullanır. BYOK kullanacaksanız ilgili sunucu anahtarını boş bırakabilirsiniz.
6. `uvicorn backend.main:app --reload` çalıştırın.
7. `http://127.0.0.1:8000` adresini açın.

`POST /api/chat` gövdesi: `{ "provider": "groq", "model": "openai/gpt-oss-20b", "prompt": "Merhaba" }`. İsteğe bağlı `X-API-Key` başlığı sunucu anahtarını o istek için geçersiz kılar. Yanıt: `{ "provider": "...", "model": "...", "answer": "..." }`.

Kota ve model erişimi sağlayıcı hesabına göre değişir. Basit IP sınırı dakikada 5 istektir; tek süreç belleğinde tutulur. Çok işçili veya dağıtık dağıtımda Redis gibi paylaşılan bir sınırlandırıcı kullanın. Üretimde HTTPS kullanın; Tailwind CDN yerine derlenmiş CSS sunun. BYOK anahtarları tarayıcı LocalStorage alanında saklanır.

## GitHub üzerinden yayınlama

Proje kökündeki `render.yaml`, frontend ve API'yi tek Render web servisinde çalıştırır. GitHub deposu oluşturup bu dosyaları `main` dalına yükleyin. Render'da **New → Blueprint** seçerek depoyu bağlayın. `GROQ_API_KEYS`, `HF_TOKEN`, `GEMINI_API_KEY` ve `KIMI_API_KEY` değerlerini Render ortam değişkenlerinde sağlayın; kullanmayacağınız sağlaycılar için boş bırakabilirsiniz. Dağıtım tamamlanınca site `https://<servis-adı>.onrender.com/` adresinde açılır. Kullanıcı kendi anahtarını arayüzde de girebilir.

Ücretsiz Render web servisi uzun süre kullanılmadığında uykuya geçebilir; ilk istek daha yavaş yanıtlanabilir. Yayın öncesinde gerçek anahtarların `.env` içinde kaldığını ve `.gitignore` tarafından hariç tutulduğunu kontrol edin.
