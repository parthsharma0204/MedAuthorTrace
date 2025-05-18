import argparse
import csv
import sys
from typing import Optional
from get_papers_list.fetcher import search_pubmed, fetch_details

FIELDNAMES = [
    'PubmedID', 'Title', 'PublicationDate',
    'NonAcademicAuthors', 'CompanyAffiliations', 'CorrespondingAuthorEmail'
]

def main() -> None:
    parser = argparse.ArgumentParser(
        description='Fetch PubMed papers with pharma/biotech affiliations'
    )
    parser.add_argument('query', help='PubMed query string')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-f', '--file', help='Output CSV filename')
    args = parser.parse_args()

    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    ids = search_pubmed(args.query)
    details = fetch_details(ids)

    if args.file:
        with open(args.file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(details)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(details)
