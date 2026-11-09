import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import update_scholar_citations as updater


def html(*rows, total=100, more=False, user="example"):
    publications = "".join(
        '<tr class="gsc_a_tr"><td><a class="gsc_a_at" '
        f'href="/citations?citation_for_view={user}:{index}">{title}</a></td>'
        f'<td><a class="gsc_a_ac" href="/scholar?cites={clusters}">{count}</a></td></tr>'
        for index, (title, count, clusters) in enumerate(rows)
    )
    return (f'<link rel="canonical" href="https://scholar.google.com/citations?user={user}">'
            '<div id="gsc_prf_in">Example Author</div>'
            f'<td class="gsc_rsb_std">{total}</td>{publications}'
            f'<button id="gsc_bpf_more" {"" if more else "disabled"}></button>')


def publication(title, count=None, clusters="12"):
    text = f"1. `TWC` [{title}](https://doi.org/example), authors, *Journal*, 2026."
    if count is not None:
        text += updater.badge(updater.Paper(title, count, tuple(clusters.split(",")), "example:0"))
    return text + "\n"


class CitationUpdaterTests(unittest.TestCase):
    def test_threshold_and_preserve_prose(self):
        source = "Heading\n" + publication("Paper A", 31) + publication("Paper B")
        papers = [updater.Paper("Paper A", 30, ("12",), "a"), updater.Paper("Paper B", 31, ("34",), "b")]
        result, matched = updater.update_publications(source, papers)
        self.assertEqual(matched, 2)
        self.assertEqual(result, "Heading\n" + publication("Paper A") + publication("Paper B", 31, "34"))
        self.assertEqual(updater.BADGE.sub("", result), updater.BADGE.sub("", source))

    def test_merged_clusters_use_one_count_and_preserve_url(self):
        source = publication("Original title", 37, "12,34")
        papers = [updater.Paper("Changed Scholar title", 39, ("12", "34"), "a")]
        result, _ = updater.update_publications(source, papers)
        self.assertEqual(result, publication("Original title", 39, "12,34"))

    def test_normalized_title_match(self):
        source = publication("RIS-Aided ISAC: Robust Design")
        papers = [updater.Paper("RIS aided ISAC — robust design", 40, ("12",), "a")]
        result, _ = updater.update_publications(source, papers)
        self.assertEqual(result, publication("RIS-Aided ISAC: Robust Design", 40))

    def test_missing_badged_and_ambiguous_matches_fail(self):
        with self.assertRaisesRegex(ValueError, "Missing or ambiguous"):
            updater.update_publications(publication("Missing", 31), [])
        papers = [updater.Paper("Paper", 31, ("12",), "a"), updater.Paper("Paper", 32, ("34",), "b")]
        with self.assertRaisesRegex(ValueError, "Missing or ambiguous"):
            updater.update_publications(publication("Paper"), papers)

    def test_identity_and_incomplete_rows_fail(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            updater.parse_page(html(("Paper", 31, "12"), user="other"), "example", "Example Author")
        with self.assertRaisesRegex(ValueError, "Incomplete Scholar publication row"):
            updater.parse_page(html(("Paper", 31, "12")).replace('class="gsc_a_ac"', 'class="missing"'), "example", "Example Author")

    def repository(self, directory):
        root = Path(directory)
        (root / "_includes/about").mkdir(parents=True)
        (root / "_config.yml").write_text(
            'author:\n  name: "Example Author"\n'
            '  googlescholar: "https://scholar.google.com/citations?user=example"\n'
            '  scholar_citations: 100\n  scholar_citations_updated: "2020-01-01"\n'
        )
        (root / "_includes/about/publications.md").write_text(
            '<!-- Google Scholar citation snapshot, checked 2020-01-01. -->\n' + publication("Paper", 31)
        )
        return root

    def test_blocked_partial_and_dry_run_never_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.repository(directory)
            config = (root / "_config.yml").read_bytes()
            publications = (root / "_includes/about/publications.md").read_bytes()
            fixture = root / "scholar.html"
            for response in ("<html>CAPTCHA / unusual traffic</html>", html(("Paper", 40, "12"), more=True)):
                fixture.write_text(response)
                with self.assertRaises(ValueError):
                    updater.update_repository(root, fixture)
                self.assertEqual((root / "_config.yml").read_bytes(), config)
                self.assertEqual((root / "_includes/about/publications.md").read_bytes(), publications)
            fixture.write_text(html(("Paper", 40, "12"), total=110))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(updater.update_repository(root, fixture, check=True))
            self.assertEqual((root / "_config.yml").read_bytes(), config)
            self.assertEqual((root / "_includes/about/publications.md").read_bytes(), publications)

    def test_unchanged_snapshot_keeps_date_and_decreases_update(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.repository(directory)
            fixture = root / "scholar.html"
            fixture.write_text(html(("Paper", 31, "12")))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(updater.update_repository(root, fixture))
            self.assertIn('"2020-01-01"', (root / "_config.yml").read_text())
            fixture.write_text(html(("Paper", 30, "12"), total=99))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(updater.update_repository(root, fixture))
            self.assertIn("scholar_citations: 99", (root / "_config.yml").read_text())
            self.assertNotIn("Citations:", (root / "_includes/about/publications.md").read_text())


if __name__ == "__main__":
    unittest.main()
