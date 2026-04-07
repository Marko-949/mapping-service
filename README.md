#AI E-commerce Category & Attribute Mapper 🚀
This application leverages Google Gemini AI for intelligent mapping of external categories and attributes (e.g., from WooCommerce or Shopify) to internal system codes (Mungos taxonomy). The system is designed to process thousands of items using Celery for asynchronous processing and a Batching strategy to ensure accuracy and stability of AI responses.

🌟 Key Features
Smart Category Mapping: Automatic matching of full category paths using semantic similarity.

Batch Processing: Data processing in batches of 50 items to stay within AI model limits and optimize performance.

Dynamic Formatters: Support for various input JSON formats (WooCommerce, standard recursive JSON, flat lists).

Asynchronous Execution: Integration with Celery allows background processing of large files without blocking the API.

Excel Export: Generation of ready-to-use Excel spreadsheets for database import.

# Installation

pip install -r requirements.txt

# Running the Project

uvicorn app.main:app --reload

# Running Celery Worker

celery -A app.core.celery_app worker --loglevel=info -P solo

# Tech Stack

- **Backend:** FastAPI (Python 3.13+)
- **AI:** Google Generative AI (Gemini 3.0 Flash)
- **Task Queue:** Celery + Redis
- **Data Handling:** Pandas, Openpyxl
- **Environment:** Dotenv

---

#Project Structure

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
