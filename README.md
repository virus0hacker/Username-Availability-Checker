Username Availability Checker

**Project name:** Username Availability Checker
**Author:** ViRuS-HaCkEr
**Interface:** GUI (Tkinter)

---

## 🧩 Overview :

A simple, open-source GUI tool to check **username availability** across major social platforms:

* **Snapchat**
* **Twitter / X**
* **Instagram**
* **Telegram**

The tool is safe, fast, and designed for everyday use without login or API keys.
It uses HTTP requests to test the existence of public profile URLs and infers availability using HTTP status codes.

---

## ⚙️ Features :

* ✅ Checks username availability across multiple platforms
* 🖥️ GUI interface built with Tkinter (dark green theme)
* 📊 Color-coded results (Available / Taken / Unknown)
* 📥 Bulk input support (multiple usernames at once)
* 💾 Export results as **CSV** or **JSON**
* ⚡ Multi-threaded for fast concurrent checks
* 🧩 No authentication or login required

---

## 🔒 Privacy & Safety :

* The tool does **not** collect or store any data.
* All requests are read-only to public URLs.
* No authentication, cookies, or tracking.

---

## 💻 Installation :

pip install requests
```bash
python username_availability_checker.py
```

---

## 🧠 How It Works :

Each platform is checked using its public profile URL pattern:

| Platform  | Profile URL                                                                        | Method | Meaning                      |
| --------- | ---------------------------------------------------------------------------------- | ------ | ---------------------------- |
| Twitter   | [https://twitter.com/{username}](https://twitter.com/{username})                   | GET    | 200 → Taken, 404 → Available |
| Instagram | [https://instagram.com/{username}/](https://instagram.com/{username}/)             | GET    | 200 → Taken, 404 → Available |
| Telegram  | [https://t.me/{username}](https://t.me/{username})                                 | GET    | 200 → Taken, 404 → Available |
| Snapchat  | [https://www.snapchat.com/add/{username}](https://www.snapchat.com/add/{username}) | GET    | Uses text & status check     |

The app respects delays between requests (configurable) to avoid rate limits.

---

## 📦 Output Example :

```json
{
  "username": "mlftt_test",
  "results": {
    "Twitter": {"verdict": "taken"},
    "Instagram": {"verdict": "available"},
    "Telegram": {"verdict": "taken"},
    "Snapchat": {"verdict": "available"}
  }
}
```

You can export results as CSV or JSON via the GUI buttons.

---

## 🧰 Technical Details :

**Dependencies:**

* Python ≥ 3.8
* `requests`
* `tkinter` (bundled with Python on most systems)

**Command line run:**

```bash
python username_availability_checker.py
```

---

## 📘 License :

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
