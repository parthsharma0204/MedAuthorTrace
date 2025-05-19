# 🧬 PubMed Pharma Paper Finder

## 📖 Overview

This Python-based command-line tool enables users to query **PubMed** for research articles and filter results to include only those with **at least one author affiliated with a pharmaceutical or biotechnology company**. The program compiles the extracted data into a structured **CSV file** for downstream use.

---

## 🎯 Key Features

- Supports **full PubMed query syntax** for precise and flexible searches.
- Identifies papers with authors affiliated with **non-academic institutions**, specifically **biotech and pharmaceutical companies**.
- Extracts essential metadata, including:
  - 🆔 **PubMed ID**
  - 📝 **Title**
  - 🗓️ **Publication Date**
  - 🧑‍🔬 **Non-academic Author(s)**
  - 🏢 **Company Affiliation(s)**
  - 📧 **Corresponding Author Email**
- Outputs the results in a well-formatted **CSV file**.
- Includes command-line options for user assistance and debugging.

---

## 🧰 Usage

### 🔧 Command-Line Options

- `-h` or `--help`: Display usage instructions.
- `-d` or `--debug`: Enable debug output during execution.
- `-f` or `--file`: Specify the output CSV file name.

### ▶️ Example

```bash
poetry run python -m src.get_paper_list.cli "cancer immunotherapy" -f results.csv --debug
