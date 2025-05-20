# 🔬 MedAuthorTrace

## 📚 Overview

This Python command-line tool allows users to search **PubMed** for research articles and filter results to include only those with **at least one author affiliated with pharmaceutical, biotech, or related industry companies**. The extracted data is saved into structured **CSV files** for further analysis or reporting.

---

## 🚀 Key Features

* Supports **advanced PubMed queries** for targeted literature searches.
* Detects authors with **non-academic affiliations** such as pharmaceutical or biotech companies.
* Extracts detailed metadata including:

  * 🔖 **PubMed ID (PMID)**
  * 📰 **Article Title**
  * 📅 **Publication Date**
  * 👩‍💼 **Non-academic Author(s)**
  * 🏢 **Company Affiliation(s)**
  * 📧 **Corresponding Author Email**
  * 🏛️ **Journal Name**
  * 🌐 **DOI**
  * 📝 **Abstract**
* Saves results into CSV files named per query for easy organization.
* Robust error handling and retry logic.
* Displays progress bars during data fetching.
* Supports command-line arguments for customization.

---

## 🛠️ Installation

Make sure you have Python 3.7+ and `poetry` installed, then:

```bash
poetry install
```

Or install dependencies manually:

```bash
pip install requests tqdm
```

---

## 🎯 Usage

### Command-Line Options

* `--help` : Show help message and exit.
* `--output` : Directory to save CSV files (default: `results`).
* `--queries` : List of search queries (default includes pharma/biotech related terms).
* `--max-results` : Maximum number of PubMed records to retrieve per query (default: 1000).

### Example Command

```
poetry run python -m get_paper_list.fetcher --queries "pharmaceutical company" "biotech startup" "veterinary medicine" "healthcare AI" --output data_results --max-results 500

```

This will:

* Search PubMed for the three specified queries.
* Fetch up to 500 papers for each query.
* Save CSV files in the folder `data_results`.

---

## 📂 Output

The tool generates CSV files named like:

```
pubmed_papers_veterinary_medicine.csv
pubmed_papers_biotech_startup.csv
pubmed_papers_healthcare_AI.csv
pubmed_papers_pharmaceutical_company.csv
```

Each file contains the extracted metadata and filtered author info.

---

## ⚙️ Configuration

* Optionally set your **NCBI API key** as an environment variable for higher rate limits:

```bash
export NCBI_API_KEY="your_api_key_here"
```

* Make sure your `get_paper_list.utils` module is correctly implemented for affiliation and email extraction.

---

## 🆘 Troubleshooting

* Ensure required packages are installed (`requests`, `tqdm`).
* Check internet connectivity as PubMed APIs require network access.
* Use the `--max-results` flag wisely to avoid hitting API rate limits.

---

## 📄 License

MIT License
