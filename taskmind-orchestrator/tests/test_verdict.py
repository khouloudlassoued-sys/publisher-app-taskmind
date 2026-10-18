from verdict import parse_verdict


def test_parse_verdict_plain_value():
    assert parse_verdict("## Verdict\nApproved\n") == "Approved"


def test_parse_verdict_bold_value():
    assert parse_verdict("## Verdict\n\n**Approved with notes**\n") == "Approved with notes"


def test_parse_verdict_invalid_value():
    assert parse_verdict("## Verdict\nPending\n") is None


def test_parse_verdict_missing_section():
    assert parse_verdict("## Findings\n- A finding\n") is None
