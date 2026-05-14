# Latin Vocabulary Quiz Generator

A cross-platform desktop application built with Python and PyQt6 that automatically generates printable, randomized, two-column vocabulary quizzes as PDFs. 

Originally designed for Latin pedagogy, this tool easily accommodates long vocabulary entries (like full principal parts) and properly renders Unicode diacritics (macrons), making it perfect for Classical languages.

## ✨ Features
* **Modern GUI**: A clean, intuitive interface built with PyQt6.
* **Clipboard or File Import**: Copy a vocabulary list directly from Quizlet/Excel, or import a `.tsv` file.
* **Randomization**: Automatically pulls 20 random items from your master list.
* **Smart Typesetting**: Uses ReportLab to generate a beautifully formatted 8.5"x11" PDF.
* **Dynamic Layouts**: Automatically calculates text-wrapping and shifts answer lines downward to accommodate multi-line entries (e.g., *afferō, afferre, abstulī, ālātum*).
* **Cross-Platform Unicode**: Automatically detects macOS or Windows to embed native system fonts (Times New Roman) so macrons and diacritics render perfectly.
* **Auto-Open**: Automatically launches the generated PDF in your default system viewer for rapid printing.

## 📋 Prerequisites
* Python 3.9 or higher

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/vocab-quiz-generator.git
   cd vocab-quiz-generator
   ```

2. **Create and activate a virtual environment:**

    Windows:

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

    Mac/Linux:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
Install the dependencies:

```bash
pip install -r requirements.txt
```