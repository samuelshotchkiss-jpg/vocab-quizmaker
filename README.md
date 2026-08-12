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
* **Two kinds of quiz**: the classic 20-word, two-column sheet, or a *context* quiz — ten words a page, up to two pages, each word printed under a line of the Latin it was met in.

## 📖 The context quiz

The classic quiz asks for a headword and gives an answer line. The context quiz gives the poetry
around the word as well:

```
1.  accēdō, accēdere, accessī, accessum   ______________________________

      accēdet fātīs mātris miserābilis īnfāns,
      et nōndum nātō fūneris auctor eris,
      cumque parente suā frāter moriētur Iūlī, (Ov. Her. 7.135)
```

There are two ways to feed it.

### From a spreadsheet — add a third column

```
volō, volāre	to fly	inter utrumque **volā**. / nec tē spectāre Boōtēn	Ov. *Met.* 8.206
```

`headword` · `meaning` · `context` · `citation` (the fourth is optional). Inside the context
cell, `**word**` marks the word being quizzed and `/` starts a new line of verse — a cell cannot
hold a real line break. `*italic*` works in any column, which is how the title of a work is set
in a citation. A row with only two columns still prints; it just has no context, so a list you
are halfway through converting still makes a quiz.

### From the Latin Vocab Toolkit

Deciding *which* of a word's occurrences a student should meet takes more than the word list —
it depends on what the class has already read and in what order — so the toolkit chooses, and
also macronizes the line and clips it to its sentence:

```bash
python engine/cycles.py quiz --clipboard
```

It names the sheet too: the title box is filled with *Vocab Trial: Ov.* Met. *8.183–209* — the
lines the class has just read.

### Either way

Use **Import from Clipboard** (or *Import from TSV File*) as usual. The importer sniffs the
format, so a plain two-column word list still makes a classic quiz and nothing about that path
changes; the **Quiz type** choice only offers *With context* when the import actually carried
context.

Layout, and the reason it is not a column: see `context_quiz.py`.

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

This project is open-source and available under the GNU General Public License v3.0 (GPL-3.0).