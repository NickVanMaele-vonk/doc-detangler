"""Markdown table well-formedness, including both PR #65 regressions."""

from detangle.tables import cell_count, check_text


def test_escaped_pipe_is_content_not_separator():
    """The ad-hoc awk check false-flagged this exact row in concepts/README.md."""
    row = "| `placement` | `glossary` \\| `UCE` \\| `SBSP` \\| `MCL` — computed |"
    assert cell_count(row) == 2


def test_outer_pipes_delimit_rather_than_separate():
    assert cell_count("| a | b | c |") == 3
    assert cell_count("|a|b|") == 2


def test_consistent_table_is_clean():
    text = "| a | b |\n|---|---|\n| 1 | 2 |\n"
    assert check_text(text, "t.md") == []


def test_row_with_a_missing_cell_is_reported():
    text = "| a | b | c |\n|---|---|---|\n| 1 | 2 |\n"
    findings = check_text(text, "t.md")
    assert [f.check for f in findings] == ["table-cell-count"]
    assert findings[0].where == "t.md:3"
    assert "2 cells" in findings[0].message


def test_dropped_leading_pipe_is_caught():
    """The PR #65 defect: a four-column row collapsed to three."""
    text = "| a | b | c | d |\n|---|---|---|---|\n1 | 2 | 3 |\n"
    findings = check_text(text, "t.md")
    assert [f.check for f in findings] == ["table-cell-count"]
    assert findings[0].where == "t.md:3"


def test_escaped_pipes_do_not_create_a_false_finding():
    text = "| a | b |\n|---|---|\n| x \\| y | z |\n"
    assert check_text(text, "t.md") == []


def test_pipes_inside_a_fenced_block_are_ignored():
    text = "```\n| not | a | table |\n| broken |\n```\n"
    assert check_text(text, "t.md") == []


def test_two_tables_are_measured_separately():
    text = "| a | b |\n|---|---|\n\n| a | b | c |\n|---|---|---|\n"
    assert check_text(text, "t.md") == []


def test_a_lone_pipe_line_is_not_a_table():
    assert check_text("| just one line |\n", "t.md") == []
