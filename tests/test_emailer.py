from src.emailer import display_doi, display_url
from src.models import Paper


def test_display_doi_strips_doi_url_prefix() -> None:
    paper = Paper(title="x", doi="https://doi.org/10.1002/mrm.70250")

    assert display_doi(paper) == "10.1002/mrm.70250"


def test_display_url_keeps_duplicate_doi_url_as_clickable_link() -> None:
    paper = Paper(
        title="x",
        doi="https://doi.org/10.1002/mrm.70250",
        url="https://doi.org/10.1002/mrm.70250",
    )

    assert display_url(paper) == "https://doi.org/10.1002/mrm.70250"
