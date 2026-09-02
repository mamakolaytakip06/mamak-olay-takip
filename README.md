# Mamak Olay Takip V3.1
Mamak ilçesiyle ilgili güncel açık web ve haber RSS kayıtlarını yaklaşık 5 dakikada bir tarayan mobil uyumlu sistem.

## Yayın
Settings → Pages → Build and deployment → Source bölümünde **GitHub Actions** seçilmelidir.

## Sınırlar
Kapalı sosyal medya hesaplarına erişmez. Kayıtlar açık kaynak bildirimidir; resmî doğrulama yerine geçmez. GitHub zamanlanmış görevleri yoğunlukta gecikebilir.


## Ücretsiz sosyal medya izleme (Google Alerts RSS)
Google Alerts üzerinde aşağıdaki sorguların her biri için ayrı alarm oluşturun:

1. `site:x.com Mamak (cinayet OR kavga OR kaza OR yangın OR polis)`
2. `site:facebook.com Mamak (cinayet OR kavga OR kaza OR yangın OR polis)`
3. `site:instagram.com Mamak (cinayet OR kavga OR kaza OR yangın OR polis)`
4. `site:x.com "Mamak son dakika"`
5. `site:facebook.com "Mamak son dakika"`
6. `site:instagram.com "Mamak son dakika"`
7. `site:x.com Ankara Mamak asayiş`
8. `site:facebook.com Ankara Mamak asayiş`
9. `site:instagram.com Ankara Mamak asayiş`

Seçenekler: **Anında**, **Otomatik**, **Türkçe**, **Türkiye**, **Tüm sonuçlar**, teslim yeri **RSS beslemesi**.

Oluşan dokuz RSS bağlantısını GitHub Actions secret alanındaki `GOOGLE_ALERT_FEEDS` değerine alt alta yapıştırın. Tarayıcı virgül, noktalı virgül ve yeni satırla ayrılmış adresleri kabul eder. Sosyal sonuç, başlık ve açıklamada Mamak ile adli/asayiş kriterlerini taşımıyorsa alınmaz. Telegram ve Threads kayıtları dışlanır.
