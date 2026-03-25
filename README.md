# AI E-commerce Category & Attribute Mapper 🚀

Ova aplikacija koristi **Google Gemini AI** za inteligentno mapiranje eksternih kategorija i atributa (npr. iz WooCommerce-a ili Shopify-a) na interne sistemske kodove (Mungos taksonomija). Sistem je dizajniran da obrađuje hiljade stavki koristeći **Celery** za asinhronu obradu i **Batching** strategiju kako bi se osigurala preciznost i stabilnost AI odgovora.

## 🌟 Ključne Karakteristike

- **Smart Category Mapping:** Automatsko uparivanje punih putanja kategorija koristeći semantičku sličnost.
- **Batch Processing:** Obrada podataka u grupama (batch-evima) od po 50 stavki radi izbjegavanja limita AI modela.
- **Dynamic Formatters:** Podrška za različite ulazne JSON formate (WooCommerce, standardni rekurzivni JSON, liste).
- **Asinhroni Rad:** Integracija sa Celery-jem omogućava obradu velikih fajlova u pozadini bez blokiranja API-ja.
- **Excel Export:** Generisanje gotovih Excel tabela spremnih za import u bazu podataka.

# Instalacija zavisnosti

pip install -r requirements.txt

# Pokretanje projekta

uvicorn app.main:app --reload

# Pokretanje celery

celery -A app.core.celery_app worker --loglevel=info -P solo

## 🛠 Tehnologije

- **Backend:** FastAPI (Python 3.13+)
- **AI:** Google Generative AI (Gemini 3.0 Flash)
- **Task Queue:** Celery + Redis
- **Data Handling:** Pandas, Openpyxl
- **Environment:** Dotenv

---

## 📂 Struktura Projekta

```text
.
├── app
│   ├── api                 # Kontroleri i rutiranje
│   ├── core                # Celery i Config podešavanja
│   ├── data                # Lokalna baza kategorija i privremeni fajlovi
│   ├── services            # AI klijenti, Worklow logika i Provideri
│   ├── utils               # Formatteri i pomoćne funkcije
│   └── main.py             # Ulazna tačka aplikacije
├── .env.example            # Šablon za environment varijable
├── .gitignore              # Fajlovi isključeni sa Git-a
└── requirements.txt        # Python zavisnosti
```
