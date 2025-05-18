import pytest
from get_papers_list import fetcher
from unittest.mock import patch

mock_search_response = {
    'esearchresult': {
        'idlist': ['12345678']
    }
}

mock_fetch_response = """<?xml version=\"1.0\"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>12345678</PMID>
      <Article>
        <ArticleTitle>Example Title One</ArticleTitle>
      </Article>
      <DateCompleted>
        <Year>2022</Year>
        <Month>07</Month>
        <Day>15</Day>
      </DateCompleted>
      <AuthorList>
        <Author>
          <LastName>Smith</LastName>
          <Initials>J</Initials>
          <AffiliationInfo>
            <Affiliation>XYZ Biotech Inc, USA. smith@xyz.com</Affiliation>
          </AffiliationInfo>
        </Author>
      </AuthorList>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""

@patch('get_papers_list.fetcher.requests.get')
def test_search_pubmed(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_search_response
    ids = fetcher.search_pubmed("cancer pharma")
    assert ids == ['12345678']

@patch('get_papers_list.fetcher.requests.get')
def test_fetch_details(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = mock_fetch_response
    details = fetcher.fetch_details(['12345678'])
    assert details[0]['PubmedID'] == '12345678'
    assert "Smith" in details[0]['NonAcademicAuthors']
    assert "XYZ Biotech" in details[0]['CompanyAffiliations']
    assert details[0]['CorrespondingAuthorEmail'] == 'smith@xyz.com'
