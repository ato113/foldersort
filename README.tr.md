# foldersort

*Türkçe · [English](README.md)*

**Klasörlerini, okuyabileceğin kurallarla düzenle.**

[![CI](https://github.com/ato113/foldersort/actions/workflows/ci.yml/badge.svg)](https://github.com/ato113/foldersort/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Lisans: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

İndirilenler klasöründe 400 dosya var. `foldersort`, bir kez yazdığın YAML
dosyasındaki kurallara göre hepsini klasörlere ayırır — ve sonucu beğenmezsen
tek komutla her şeyi geri alır.

```
$ foldersort run --dry-run

12 file(s) to move:

  fatura-mart.pdf            ->  Documents/            [Documents]
  Ekran Görüntüsü.png        ->  Images/Screenshots/   [Screenshots]
  ubuntu-24.04.iso           ->  Review/               [Large and forgotten]
  ...

Dry run — nothing was moved. Drop --dry-run to apply.
```

## Neden bir dosya düzenleyici daha?

Çoğu araç kategorileri koda gömer; senin düzenin yazarınkinden farklıysa çaresiz
kalırsın. `foldersort`'ta genelde bulunmayan dört şey var:

- **Kuralları senin yerine yazar.** `foldersort suggest` klasörde gerçekten ne
  olduğuna bakıp çalışan bir yapılandırma verir. Boş bir YAML dosyasına bakıp
  "ne yazacağım" diye düşünmek yok.
- **Koşullar birleşir.** Tek bir kural hem uzantıya, hem boyuta, hem yaşa göre
  eşleşebilir — "altı aydır dokunmadığım 50 MB'tan büyük PDF'ler" tek kuraldır.
- **Önce planı gösterir.** Hiçbir şey taşınmadan önce ne olacağını görürsün.
- **Gerçek geri alma.** Her çalıştırma günlüğe yazılır; `foldersort undo` her
  dosyayı bulunduğu yere geri koyar.

## Kurulum

Python 3.9 veya üstü gerekiyor. Sende ne var, bakalım:

```bash
python3 --version
```

Sonra kaynaktan kur:

```bash
git clone https://github.com/ato113/foldersort
cd foldersort
pip install -e .
```

Çalıştığını doğrula:

```bash
foldersort --version
```

Komutun adı `foldersort`, kısa hali de `fsort` — hangisi kolayına gelirse.

<details>
<summary>Kurduktan sonra "komut bulunamadı" diyorsa</summary>

`pip` aracı `PATH` üzerinde olmayan bir yere kurmuş. İki çözüm:

```bash
python3 -m foldersort --version     # bu her zaman çalışır
```

ya da pip'in betik klasörünü `PATH`'e ekle — nereye kurduğunu
`pip show -f foldersort` söyler.
</details>

## Hızlı başlangıç

Üç komutla biter:

```bash
# 1. Klasöre bak ve kuralları otomatik oluştur
foldersort suggest ~/Downloads --write

# 2. Ne olacağını gör (hiçbir şey taşınmaz)
foldersort run --dry-run

# 3. Beğendiysen uygula (onay ister)
foldersort run
```

Fikrini değiştirdin mi:

```bash
foldersort undo
```

Sıfırdan kendi kurallarını yazmak istersen `foldersort init` açıklamalı bir
örnek dosya oluşturur.

### Kuralları foldersort'a yazdırmak

`foldersort suggest` klasörü tarar ve bulduğu her grup için bir kural önerir —
ekran görüntülerini birkaç dilde adlarından tanır, Türkçe "Ekran Görüntüsü"
dosyaları dahil.

```
$ foldersort suggest ~/Downloads

Found 6 rule(s) that would fit /home/sen/Downloads:

  Screenshots  (14 file(s))
  Images       (31 file(s))
  Documents    (22 file(s))
  Archives     (5 file(s))
  Audio        (9 file(s))
  BLEND files  (3 file(s))
```

`--write` eklersen bunu `foldersort.yaml` olarak kaydeder. Sıradan bir
yapılandırma dosyasıdır, dilediğin gibi düzenleyebilirsin.

## Yapılandırma

```yaml
source: ~/Downloads
recursive: false        # alt klasörlere de bak
on_conflict: rename     # rename | skip | overwrite

exclude:                # bu kalıplara uyan dosyalara hiç dokunma
  - "*.part"
  - "*.crdownload"

rules:
  # İlk eşleşen kural kazanır, o yüzden özel olanları üste koy.
  - name: Screenshots
    target: Images/Screenshots
    patterns: ["screenshot*", "Ekran*"]

  - name: Images
    target: Images
    extensions: [jpg, png, gif, webp, heic]

  - name: Large and forgotten
    target: Review
    larger_than: 500MB
    older_than: 90d
```

### Kural seçenekleri

| Anahtar | Anlamı | Örnek |
|---------|--------|-------|
| `name` | Plan çıktısında görünen ad. Zorunlu. | `Faturalar` |
| `target` | Hedef klasör, `source`'a göre. Zorunlu. | `Documents/Faturalar` |
| `extensions` | Dosya uzantıları, noktalı ya da noktasız. | `[pdf, docx]` |
| `patterns` | Dosya adına uygulanan kalıplar, büyük/küçük harf duyarsız. | `["fatura*", "*-makbuz"]` |
| `larger_than` / `smaller_than` | Boyut eşikleri. | `500MB`, `10KB` |
| `older_than` / `newer_than` | Son değişiklik tarihine göre yaş. | `90d`, `2w`, `1y` |

Bir dosya, o kuralda **belirtilmiş her koşulu** sağlıyorsa eşleşir. Yazmadığın
koşullar yok sayılır.

Üst düzey seçenekler: `source`, `recursive`, `on_conflict` (`rename` / `skip` /
`overwrite`) ve `exclude` — yarım inmiş `*.part`, `*.crdownload` gibi dosyaların
yeri burasıdır.

## Bilmekte fayda var

- Nokta ile başlayan gizli dosyalara hiç dokunulmaz.
- Hedef klasörün içindeki dosyalar atlanır, yani aynı komutu iki kez çalıştırmak
  güvenlidir.
- `foldersort undo` yalnızca en son çalıştırmayı geri alır;
  `foldersort undo --list` geçmişi gösterir. Günlük dosyası:
  `~/.local/share/foldersort/journal.jsonl`
- Terminalde renkli, boru hattında düz çıktı verir. `NO_COLOR=1` rengi her yerde
  kapatır.

## Geliştirme

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
```

## Katkı

Issue ve pull request'ler memnuniyetle karşılanır — kurulum, kontrol listesi ve
yeni bir kural koşulunun nasıl ekleneceği için [CONTRIBUTING.md](CONTRIBUTING.md)
dosyasına bak.

Yapay zekâ destekli katkılar sorun değil; yeter ki pull request'te belirt ve
gönderdiğin kodu açıklayabil.

## Lisans

MIT — [LICENSE](LICENSE) dosyasına bak.
