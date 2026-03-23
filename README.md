# 🚀 GeM Tender Scraper

## 📌 Description

This project automates the extraction of tender and contract data from the GeM (Government e-Marketplace) platform.
It uses browser automation and OCR-based CAPTCHA solving to navigate, search, and collect structured data efficiently.

---

## ⚙️ Features

* 🔹 Automated navigation of GeM website
* 🔹 Advanced search functionality
* 🔹 OCR-based CAPTCHA solving (Tesseract)
* 🔹 Multi-page data scraping
* 🔹 Real-time data extraction
* 🔹 Export data to Excel and CSV
* 🔹 Error handling and retry mechanism

---

## 🛠️ Tech Stack

* Python
* Selenium
* Tesseract OCR
* Pandas
* OpenCV (for CAPTCHA preprocessing)

---

## 📂 Project Structure

```
gem-tender-scraper/
│── main.py
│── scraper.py
│── captcha_solver.py
│── requirements.txt
│── README.md
│── screenshots/
│── output/
```

---

## ▶️ How to Run

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/gem-tender-scraper.git
cd gem-tender-scraper
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Install Tesseract OCR

* Download and install Tesseract
* Set path in code:

```python
pytesseract.pytesseract.tesseract_cmd = r'YOUR_TESSERACT_PATH'
```

### 4️⃣ Run the Script

```bash
python main.py
```

---

## 📸 Screenshots

(Add your screenshots in the `screenshots/` folder)

Example:

```
screenshots/homepage.png
screenshots/output.png
```

---

## 📊 Output Data

The scraper extracts:

* Tender ID
* Organization Name
* Contract Details
* Date & Time
* Status

Saved in:

* Excel (.xlsx)
* CSV (.csv)

---

## 🔥 Real-World Use Case

* Government tender monitoring
* Business intelligence & analysis
* Automated data collection for decision making

---

## ⚠️ Challenges Solved

* CAPTCHA handling using OCR
* Dynamic website navigation
* Handling timeouts and exceptions

---

## 🚀 Future Improvements

* GUI version (PyQt)
* EXE desktop application
* Advanced CAPTCHA bypass (AI-based)
* Cloud deployment

---

## 👨‍💻 Author

**Tejveer Singh**
Python Automation Developer

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
