from src.history import filter_previously_recommended
from src.models import Paper


def test_filter_previously_recommended_uses_doi_identity() -> None:
    candidates = [
        Paper(title="Already seen", doi="10.1/ABC", year=2025, abstract="useful abstract text for testing"),
        Paper(title="New paper", doi="10.2/NEW", year=2025, abstract="useful abstract text for testing"),
    ]

    filtered = filter_previously_recommended(candidates, {"doi:10.1/abc"})

    assert [paper.title for paper in filtered] == ["New paper"]
