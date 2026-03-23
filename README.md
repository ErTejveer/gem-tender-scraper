# 🚀 GeM Tender Scraper (Full JSON Extractor)

## 📌 Description

An advanced Python automation tool that scrapes tender data from the GeM (Government e-Marketplace) platform.
It navigates through listing pages, opens each bid detail page, extracts structured information, and saves it into a JSON file.

---

## ⚙️ Features

* 🔹 Automated web scraping using Selenium
* 🔹 Multi-page navigation (pagination support)
* 🔹 Extracts complete bid details
* 🔹 Extracts documents and links
* 🔹 Captures BOQ / item tables
* 🔹 CAPTCHA detection (manual solving supported)
* 🔹 Structured JSON output
* 🔹 Handles dynamic website content

---

## 🛠️ Tech Stack

* Python
* Selenium
* BeautifulSoup
* WebDriver Manager
* JSON

---

## 📂 Project Structure

```
gem-tender-scraper/
│── gem_full_json_scraper.py
│── requirements.txt
│── README.md
│── screenshots/
│── output/
```

---

## ▶️ How to Run

### 1️⃣ Clone Repository

```bash
git clone https://github.com/ErTejveer/gem-tender-scraper.git
cd gem-tender-scraper
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run Script

```bash
python gem_full_json_scraper.py
```

### 4️⃣ Solve CAPTCHA

* If CAPTCHA appears, solve it manually in browser
* Press ENTER in terminal to continue

---

## ⚙️ Configuration

You can modify settings inside the script:

```python
MAX_PAGES = 200       # Number of pages to scrape
HEADLESS = False      # Set True to run without browser UI
DELAY_BETWEEN_ACTIONS = 1.0
```

---

## 📊 Output

The scraper generates:

```
gem_all_bids.json
```

### Contains:

* Bid details
* Documents links
* Item/BOQ tables
* Page metadata

---

## 📸 Screenshots

(Add your screenshots here)

Example:

```
screenshots/output.png
```

---

## 🔥 Real-World Use Case

* Government tender tracking
* Business intelligence
* Data analysis & automation
* Market research

---

## ⚠️ Challenges Solved

* Dynamic page handling
* CAPTCHA detection
* Multi-page scraping
* Data extraction & structuring

---

## 🧠 Key Highlights

* Uses intelligent heuristics for data extraction
* Handles multiple HTML structures
* Scalable scraping architecture
* Efficient navigation system

---

## 🚀 Future Improvements

* GUI application (PyQt)
* Automatic CAPTCHA solving (AI)
* Database integration (MongoDB/MySQL)
* Cloud deployment

---

## 👨‍💻 Author

Tejveer Singh
Python Automation Developer

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
