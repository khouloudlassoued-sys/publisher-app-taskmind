VALID_VERDICTS = {
    "Approved",
    "Approved with notes",
    "Changes Requested",
    "Blocked",
}


def parse_verdict(markdown_text):
    lines = markdown_text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != "## Verdict":
            continue
        for candidate in lines[index + 1:]:
            candidate = candidate.strip()
            if candidate:
                verdict = candidate.strip("*").strip()
                return verdict if verdict in VALID_VERDICTS else None
        return None
    return None
