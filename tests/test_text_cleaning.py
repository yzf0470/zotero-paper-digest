from src.text_cleaning import clean_abstract, clean_text


def test_clean_abstract_removes_jats_markup() -> None:
    dirty = (
        "<jats:title>ABSTRACT</jats:title> <jats:sec><jats:title>Purpose</jats:title> "
        "To demonstrate dynamic mode decomposition for cardiac MRI.</jats:sec>"
    )

    assert clean_abstract(dirty) == "Purpose To demonstrate dynamic mode decomposition for cardiac MRI."


def test_clean_abstract_drops_numeric_stub() -> None:
    assert clean_abstract("1.") == ""


def test_clean_text_unescapes_html_entities() -> None:
    assert clean_text("MRI &amp; CMR") == "MRI & CMR"
