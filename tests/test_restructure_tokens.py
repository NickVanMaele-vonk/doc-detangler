"""ADR-004 Decision 9: a tool-stamped marker is metadata, not a word.

The property under test is agreement between the project's two content
measures. ``para_hash`` normalises through ``pandoc -t plain``, which drops
raw HTML, so a marker has never been part of a block's provenance identity.
Criterion 5's token count used to disagree, which only mattered once the
input to a run could be a previous run's marked output — so each test below
compares a marked block against its unmarked twin and asserts both measures
say the same thing.
"""

from test_restructure_parity import SECTION, plan_for

from detangle.records.spans import block_hash, normalise
from detangle.restructure.execute import SOURCE, Part, Render, render
from detangle.restructure.parity import measure
from detangle.restructure.tokens import same_words, tokens

HEADING = "## Overview"
MARKED_HEADING = "<!-- sec:u-a48738c9 -->\n## Overview"

DEFINITION = "**Close window**\n\nThe period preceding the close."
MARKED_DEFINITION = (
    "<!-- concept:close-window:start -->\n"
    "**Close window**\n\nThe period preceding the close.\n"
    "<!-- concept:close-window:end -->"
)


def test_section_marker_is_not_a_word():
    assert tokens(MARKED_HEADING) == tokens(HEADING)


def test_concept_markers_are_not_words():
    assert tokens(MARKED_DEFINITION) == tokens(DEFINITION)


def test_multiline_marker_is_removed_whole():
    text = '<!-- AI addition:start\n   scope="section" -->\nBody text.'
    assert tokens(text) == tokens("Body text.")


def test_omission_marker_takes_its_attributes_with_it():
    text = '<!-- omitted src="U:3.1" approved-by="Nick" pr="118" -->\nKept.'
    assert tokens(text) == tokens("Kept.")


def test_visible_addition_tag_still_counts():
    """Only the comment goes. Ink on the page is still ink (2026-08-05)."""
    tagged = tokens("> [AI addition] This section introduces the document.")
    assert tagged["[AI"] == 1 and tagged["addition]"] == 1
    assert tagged != tokens("> This section introduces the document.")


def test_the_two_measures_now_agree():
    """The alignment claim itself, asserted on one block, both ways."""
    assert block_hash(normalise(MARKED_DEFINITION)) == block_hash(
        normalise(DEFINITION)
    )
    assert tokens(MARKED_DEFINITION) == tokens(DEFINITION)


def test_same_words_ignores_a_marker():
    assert same_words(MARKED_HEADING, HEADING)


MARKED_SOURCE = """\
<!-- sec:u-11111111 -->
## 1. Scope

<!-- concept:persistence-gate:start -->
The gate caps the recommendation at MEDIUM-INVESTIGATE.
<!-- concept:persistence-gate:end -->
"""

BARE_SOURCE = """\
## 1. Scope

The gate caps the recommendation at MEDIUM-INVESTIGATE.
"""


def _parity_of(source: str):
    """Run a whole-document parity measurement over ``source``."""
    plan = plan_for(source)
    rendered = render(plan, [], source)
    return measure(plan, source, rendered)


def test_a_rerun_over_marked_input_is_clean():
    """The failure Decision 9 exists to prevent, asserted directly.

    Every block of the marked document is assigned, and the renderer emits
    its own markers as authored parts rather than copying these. Before the
    fix the marker tokens sat in ``expected`` with nothing in ``actual`` to
    meet them, so a re-run reported source words lost that no reader had
    ever seen.
    """
    parity = _parity_of(MARKED_SOURCE)
    assert parity.clean, (parity.missing, parity.extra)
    assert parity.expected == _parity_of(BARE_SOURCE).expected


def test_output_side_is_unaffected():
    """Markers were already excluded on the output side; keep it that way."""
    rendered = Render()
    rendered.parts.append(
        Part(
            text=f"{MARKED_HEADING}\n",
            origin=SOURCE,
            kind="prose",
            section=SECTION.id,
        )
    )
    plan = plan_for(BARE_SOURCE)
    parity = measure(plan, BARE_SOURCE, rendered)
    assert "sec:u-a48738c9" not in parity.actual
    assert "<!--" not in parity.actual
