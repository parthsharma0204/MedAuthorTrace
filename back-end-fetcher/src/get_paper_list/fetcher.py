import argparse
import csv
import logging
import os
from typing import List, Dict, Any
import requests
from xml.etree import ElementTree as ET
from tqdm import tqdm
from time import sleep
from get_paper_list.utils import is_non_academic, extract_email, extract_company_name

# URLs for PubMed API
PUBMED_SEARCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
PUBMED_FETCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'

# Read API key from environment variable (optional but recommended)
API_KEY = os.getenv("NCBI_API_KEY")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def retry_request(url: str, params: dict, retries: int = 3, delay: int = 2) -> requests.Response:
    """Make a request with retries and delay."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.warning(f"Request failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                sleep(delay)
            else:
                raise


def search_pubmed(query: str, max_results: int = 1000) -> List[str]:
    """Search PubMed for a query and return up to max_results IDs with pagination."""
    all_ids = []
    batch_size = 100  # PubMed max retmax per request

    for start in range(0, max_results, batch_size):
        params = {
            'db': 'pubmed',
            'term': query,
            'retmode': 'json',
            'retmax': str(batch_size),
            'retstart': str(start),
        }
        if API_KEY:
            params['api_key'] = API_KEY

        resp = retry_request(PUBMED_SEARCH_URL, params)
        data = resp.json()

        ids = data.get('esearchresult', {}).get('idlist', [])
        if not ids:
            break
        all_ids.extend(ids)

        # Stop early if less than requested results returned
        if len(ids) < batch_size:
            break

    return all_ids


def fetch_details(ids: List[str]) -> List[Dict[str, Any]]:
    """Fetch detailed info for a list of PubMed IDs."""
    if not ids:
        return []

    # PubMed efetch max batch size - let's keep 100
    batch_size = 100
    papers = []

    # Process IDs in batches
    for i in tqdm(range(0, len(ids), batch_size), desc="Fetching article details"):
        batch_ids = ids[i:i+batch_size]
        ids_str = ','.join(batch_ids)
        params = {
            'db': 'pubmed',
            'id': ids_str,
            'retmode': 'xml',
        }
        if API_KEY:
            params['api_key'] = API_KEY

        resp = retry_request(PUBMED_FETCH_URL, params)
        root = ET.fromstring(resp.text)

        for article in root.findall('.//PubmedArticle'):
            pmid = article.findtext('.//PMID')
            title = article.findtext('.//ArticleTitle') or ""

            pub_date_node = article.find('.//DateCompleted')
            if pub_date_node is not None:
                year = pub_date_node.findtext('Year')
                month = pub_date_node.findtext('Month') or '01'
                day = pub_date_node.findtext('Day') or '01'
                pub_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            else:
                pub_date = ""

            journal = article.findtext('.//Journal/Title') or ""

            # Extract DOI if present
            doi = ""
            for id_node in article.findall(".//ArticleId"):
                if id_node.attrib.get("IdType") == "doi":
                    doi = id_node.text
                    break

            # Concatenate all abstract text parts
            abstract_parts = [a.text for a in article.findall('.//AbstractText') if a.text]
            abstract = ' '.join(abstract_parts)

            non_acad_authors, company_affils = [], []
            email = ""

            for author in article.findall('.//Author'):
                aff = author.findtext('AffiliationInfo/Affiliation') or ''
                lastname = author.findtext('LastName') or ''
                initials = author.findtext('Initials') or ''
                name = ' '.join(filter(None, [lastname, initials]))
                if is_non_academic(aff):
                    non_acad_authors.append(name)
                    company_affils.append(extract_company_name(aff))
                if not email:
                    email_candidate = extract_email(aff)
                    if email_candidate:
                        email = email_candidate

            papers.append({
                'PubmedID': pmid,
                'Title': title,
                'Publication Date': pub_date,
                'Journal': journal,
                'DOI': doi,
                'Abstract': abstract,
                'Non-academic Author(s)': '; '.join(non_acad_authors),
                'Company Affiliation(s)': '; '.join(set(company_affils)),
                'Corresponding Author Email': email
            })

    return papers


def save_to_csv(papers: List[Dict[str, Any]], filename: str) -> None:
    if not papers:
        logging.info("No papers to save.")
        return

    # Use keys from first paper as CSV columns dynamically
    fieldnames = papers[0].keys()

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(papers)

    logging.info(f"✅ Results saved to {filename}")


def main(queries: List[str], output_dir: str, max_results: int):
    os.makedirs(output_dir, exist_ok=True)

    for query in queries:
        logging.info(f"\n🔎 Searching PubMed for: '{query}'")
        try:
            paper_ids = search_pubmed(query, max_results=max_results)
            logging.info(f"Found {len(paper_ids)} paper IDs.")

            papers = fetch_details(paper_ids)
            num_non_acad = sum(1 for p in papers if p['Non-academic Author(s)'])
            logging.info(f"{num_non_acad} papers had at least one non-academic author.")

            filename = os.path.join(output_dir, f"pubmed_papers_{query.replace(' ', '_')}.csv")
            save_to_csv(papers, filename)

        except Exception as e:
            logging.error(f"❌ Error processing query '{query}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PubMed papers with non-academic authors.")
    parser.add_argument(
        "--output", type=str, default="results",
        help="Directory to save CSV files"
    )
    parser.add_argument(
        "--queries", nargs="+", default=[
            "pharmaceutical company",
            "biotech company",
            "clinical research organization",
            "medical device company",
            "drug development industry"
        ],
        help="List of queries to search PubMed"
    )
    parser.add_argument(
        "--max-results", type=int, default=1000,
        help="Maximum number of paper IDs to retrieve per query"
    )
    args = parser.parse_args()

    logging.info("🚀 Running fetcher.py with advanced features...")
    main(args.queries, args.output, args.max_results)
