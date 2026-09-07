# 📄 AI Text Summarizer

An elegant, abstractive text summarization web studio powered by Hugging Face's **BART Large CNN** model and built with **Streamlit**. Transform long-form articles, reports, research papers, and meeting notes into clear, structured, and actionable summaries in seconds.

---

## ✨ Key Features

- **🧠 Neural Abstractive Summarization**: Distills core ideas into coherent, human-like summaries using `facebook/bart-large-cnn`.
- **📑 Multiple Output Formats**:
  - **Standard Paragraph**: Cohesive narrative summary.
  - **Executive Summary**: Core headline with structured supporting details.
  - **Key Bullet Points**: Itemized key takeaways for rapid scanning.
  - **TL;DR (Quick Take)**: Single high-impact overview sentence.
- **🎚️ Adjustable Compression Modes**: Choose between *Concise*, *Balanced*, or *Comprehensive* summary lengths.
- **📊 Real-time Document & Reduction Analytics**:
  - Input analysis: Word count, sentence count, character count, and estimated reading time.
  - Output metrics: Percentage reduction ratio, summary word count, and estimated time saved.
- **🏷️ Automated Key Topic Extraction**: Automatically surfaces top recurring themes and keywords.
- **📂 Flexible Input Methods**:
  - Direct text paste.
  - **1-Click Sample Loaders**: Preloaded datasets (AI Research, Financial Report, Climate & Energy).
  - **File Upload**: Direct ingestion of `.txt` and `.md` documents.
- **🔊 Speech Synthesis**: Integrated browser text-to-speech (TTS) to listen to generated summaries aloud.
- **💾 Markdown Export**: Download polished summary reports (`.md`) complete with metadata and topics.
- **🎨 Editorial UI with Light & Dark Modes**: Responsive, typography-focused aesthetic styled with *Playfair Display* and *Plus Jakarta Sans*.
- **🗄️ Session History & Archive**: Review previous summaries generated during your current session.
- **🛡️ Built-in Fallback Engine**: Gracefully handles offline states or missing API keys with intelligent sentence extraction.

---

## 🛠️ Tech Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **AI Model & Inference**: [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index) (`facebook/bart-large-cnn`)
- **Language**: Python 3.9+
- **HTTP Client**: [Requests](https://requests.readthedocs.io/)
- **Configuration**: [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 📁 Project Structure

```text
ai-text-summarizer/
├── .env                  # Environment variables (HF_API_TOKEN)
├── .gitignore            # Git ignore rules
├── app.py                # Main Streamlit application & summarization logic
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have **Python 3.9 or higher** installed on your machine.

### 2. Clone the Repository

```bash
git clone https://github.com/abdulwahabshafqat2007-ops/AI-text-summarizer.git
cd ai-text-summarizer
```

### 3. Set Up Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration

1. Create a `.env` file in the root directory:

```env
HF_API_TOKEN=your_huggingface_api_token_here
```

2. **Obtaining a Hugging Face Token:**
   - Sign up or log in at [Hugging Face](https://huggingface.co/).
   - Navigate to **Settings** → **Access Tokens**.
   - Create a new token with **Read** permissions.
   - Paste the token into your `.env` file.

> **Note**: If `HF_API_TOKEN` is not configured, the app will continue to work using a local extractive fallback algorithm.

---

## 💻 Running the App

Start the Streamlit application:

```bash
streamlit run app.py
```

Once launched, the app will automatically open in your default browser at `http://localhost:8501`.

---

## 📖 Usage Guide

1. **Input Document**: Paste your text into the input box, click one of the quick sample buttons, or upload a `.txt`/`.md` document.
2. **Select Format & Length**: Pick your desired summary format (*Standard Paragraph*, *Executive Summary*, *Bullet Points*, or *TL;DR*) and adjust the length slider.
3. **Generate Summary**: Click **⚡ Summarize Text**.
4. **Analyze & Export**:
   - Inspect reduction percentage and key topics.
   - Click **🔊 Read Summary Aloud** to listen to the audio readout.
   - Click **💾 Export Summary (.md)** to save your summary to disk.
5. **View History**: Switch to the **🗄️ History & Archive** tab to review your session's past summaries.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/abdulwahabshafqat2007-ops/AI-text-summarizer/issues).

---

## 📜 License

Distributed under the [MIT License](LICENSE).
