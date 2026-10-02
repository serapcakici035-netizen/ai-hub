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

Proje kökündeki `render.yaml`, frontend ve API'yi tek Render web servisinde çalıştırır. GitHub deposu oluşturup bu dosyaları `main` dalına yükleyin. Render'da **New → Blueprint** seçerek depoyu bağlayın. `GROQ_API_KEYS`, `HF_TOKEN`, `GEMINI_API_KEY` ve `KIMI_API_KEY` değerlerini Render ortam değişkenlerinde sağlayın; kullanmayacağınız sağlayıcılar için boş bırakabilirsiniz. Dağıtım tamamlanınca site `https://<servis-adı>.onrender.com/` adresinde açılır. Kullanıcı kendi anahtarını arayüzde de girebilir.

Ücretsiz Render web servisi uzun süre kullanılmadığında uykuya geçebilir; ilk istek daha yavaş yanıtlanabilir. Yayın öncesinde gerçek anahtarların `.env` içinde kaldığını ve `.gitignore` tarafından hariç tutulduğunu kontrol edin. Arayüz stilleri derlenmiş `frontend/styles.css` dosyasından gelir; HTML sınıflarını değiştirdiğinizde `npm install` ve `npm run build:css` çalıştırıp üretilen CSS dosyasını commit edin.

## Başka bir sağlayıcı veya anahtar ekleme

**Anahtarı sohbete ya da GitHub'a yazmayın.** Render'da `ai-hub` web servisini açın; **Environment → Edit → Add variable** yolunu izleyin. Değişken adını ve anahtar değerini girip **Save, rebuild, and deploy** seçin. Yerel geliştirmede aynı değişkeni yalnızca `.env` dosyasına ekleyin; `.env` Git tarafından yok sayılır. Mevcut sağlayıcıların değişken adları `.env.example` dosyasında listelenmiştir. Groq için birden fazla anahtarı `GROQ_API_KEYS` alanında virgülle ayırabilirsiniz.

Yeni bir **OpenAI uyumlu** sağlayıcı eklemek için `backend/main.py` içindeki `MODELS` listesine sağlayıcı adı ve kullanılacak gerçek model kimliğini, `URLS` listesine sağlayıcının resmi chat completions uç noktasını, `ENV_KEYS` listesine de ortam değişkeni adını ekleyin. Aynı değişken adını `.env.example` ve `render.yaml` dosyalarına (`sync: false` ile) yazın. `frontend/index.html` dosyası sağlayıcı ve modelleri `/api/models` üzerinden aldığı için ayrıca seçenek kodlamanız gerekmez. Sonra commit'i GitHub'a gönderin; Render otomatik dağıtır. Sağlayıcının istek veya yanıt biçimi OpenAI uyumlu değilse `backend/main.py` içindeki özel Gemini dalı gibi ayrı bir dönüştürme dalı ekleyin.
