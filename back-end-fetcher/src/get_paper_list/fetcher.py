from typing import List, Dict, Any
import requests
from xml.etree import ElementTree as ET
from get_paper_list.utils import is_non_academic, extract_email, extract_company_name
import csv

PUBMED_SEARCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
PUBMED_FETCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'

def search_pubmed(query: str) -> List[str]:
    params = {
        'db': 'pubmed',
        'term': query,
        'retmode': 'json',
        'retmax': '100'
    }
    resp = requests.get(PUBMED_SEARCH_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data['esearchresult']['idlist']

def fetch_details(ids: List[str]) -> List[Dict[str, Any]]:
    ids_str = ','.join(ids)
    params = {'db': 'pubmed', 'id': ids_str, 'retmode': 'xml'}
    resp = requests.get(PUBMED_FETCH_URL, params=params)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    papers = []

    for article in root.findall('.//PubmedArticle'):
        pmid = article.findtext('.//PMID')
        title = article.findtext('.//ArticleTitle')

        pub_date_node = article.find('.//DateCompleted')
        if pub_date_node is not None:
            year = pub_date_node.findtext('Year')
            month = pub_date_node.findtext('Month')
            day = pub_date_node.findtext('Day')
            pub_date = f"{year}-{month or '01'}-{day or '01'}"
        else:
            pub_date = ""

        non_acad_authors, company_affils = [], []
        email = ""

        for author in article.findall('.//Author'):
            aff = author.findtext('AffiliationInfo/Affiliation') or ''
            name = ' '.join(filter(None, [author.findtext('LastName'), author.findtext('Initials')]))
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
            'Non-academic Author(s)': '; '.join(non_acad_authors),
            'Company Affiliation(s)': '; '.join(set(company_affils)),
            'Corresponding Author Email': email
        })

    return papers

def save_to_csv(papers: List[Dict[str, Any]], filename: str) -> None:
    if not papers:
        print("No papers to save.")
        return

    fieldnames = [
        'PubmedID',
        'Title',
        'Publication Date',
        'Non-academic Author(s)',
        'Company Affiliation(s)',
        'Corresponding Author Email'
    ]

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper)

    print(f"✅ Results saved to {filename}")

if __name__ == "__main__":
    print("🔍 Running fetcher.py...")

    queries = [
        "pharmaceutical company",
        "biotech company",
        "clinical research organization",
        "medical device company",
        "drug development industry"
    ]

    for query in queries:
        print(f"\n🔎 Searching PubMed for: '{query}'")
        try:
            paper_ids = search_pubmed(query)
            print(f"Found {len(paper_ids)} paper IDs.")
            papers = fetch_details(paper_ids)

            num_non_acad = sum(1 for p in papers if p['Non-academic Author(s)'])
            print(f"{num_non_acad} papers had at least one non-academic author.")

            filename = f"pubmed_papers_{query.replace(' ', '_')}.csv"
            save_to_csv(papers, filename)

        except Exception as e:
            print(f"❌ Error processing query '{query}': {e}")
