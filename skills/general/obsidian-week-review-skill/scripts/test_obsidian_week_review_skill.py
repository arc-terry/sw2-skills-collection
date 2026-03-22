from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import obsidian_week_review_skill as review


class ObsidianWeekReviewSkillTests(unittest.TestCase):
    def test_build_default_note_path_uses_year_month_week_pattern(self) -> None:
        week_path = Path("/vault/Journal/01-daily/2026/03/W12")

        note_path = review.build_default_note_path(week_path)

        self.assertEqual(note_path, week_path / "2026-03-W12-summary.md")

    def test_build_week_label_uses_week_path_not_output_filename(self) -> None:
        week_path = Path("/vault/Journal/01-daily/2026/03/W12")

        week_label = review.build_week_label(week_path)

        self.assertEqual(week_label, "2026-03-W12")

    def test_build_weekly_review_parses_real_note_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            week_path = Path(tmpdir)
            (week_path / "2026-03-17.md").write_text(
                "\n".join(
                    [
                        "# NOTE",
                        "",
                        "## AT&T",
                        "",
                        "### issue | SFP Receiver Module issue from ATT side",
                        "",
                        "### Solution",
                        'Enable lacking package from "build/.config" via "make menuconfig"',
                        "",
                        "# TODO",
                        "- [ ] Record the DHCP forwarding method",
                        "- [x] Think about how many projects I have",
                    ]
                ),
                encoding="utf-8",
            )
            (week_path / "2026-03-18.md").write_text(
                "\n".join(
                    [
                        "# NOTE",
                        "",
                        "## ATT",
                        "",
                        "## TPE POC",
                        "",
                        "### preconnect timeout (600 sec)",
                        "",
                        "Ask T.J. to check if the SFP laser turns off by default.",
                    ]
                ),
                encoding="utf-8",
            )
            (week_path / "2026-03-W12-summary.md").write_text(
                "# Existing summary\n\n## Focus areas\n\n### AT&T\n",
                encoding="utf-8",
            )

            weekly_review = review.build_weekly_review(week_path)

        self.assertEqual([(area.name, area.count) for area in weekly_review.focus_areas], [("AT&T", 2), ("TPE POC", 1)])
        self.assertEqual([item.text for item in weekly_review.open_tasks], ["Record the DHCP forwarding method"])
        self.assertEqual([item.text for item in weekly_review.completed_tasks], ["Think about how many projects I have"])
        self.assertEqual(
            [item.text for item in weekly_review.actions],
            [
                'Enable lacking package from "build/.config" via "make menuconfig"',
                "Ask T.J. to check if the SFP laser turns off by default.",
            ],
        )
        self.assertEqual(
            [item.text for item in weekly_review.blockers],
            ["issue | SFP Receiver Module issue from ATT side", "preconnect timeout (600 sec)"],
        )

    def test_render_summary_note_includes_toc_and_focus_subsections(self) -> None:
        weekly_review = review.WeeklyReview(
            week_path=Path("/vault/Journal/01-daily/2026/03/W12"),
            notes=[Path("2026-03-17.md"), Path("2026-03-18.md")],
            focus_areas=[review.FocusArea(name="AT&T", count=2, sources=("2026-03-17.md", "2026-03-18.md"))],
            tasks=[review.TaskItem(text="Finish weekly retro", source="2026-03-17.md", status="open")],
            actions=[review.HighlightItem(text="Enable missing package", source="2026-03-17.md")],
            blockers=[review.HighlightItem(text="SFP cannot activate properly", source="2026-03-18.md")],
        )

        note = review.render_summary_note(
            weekly_review,
            Path("/tmp/custom-output.md"),
            Path("/vault"),
        )

        self.assertIn("```table-of-contents", note)
        self.assertIn("# 2026-03-W12 Summary", note)
        self.assertIn("## Focus areas", note)
        self.assertIn("### AT&T", note)
        self.assertIn("- Source notes: `2026-03-17.md`, `2026-03-18.md`.", note)
        self.assertIn("## Open tasks", note)
        self.assertIn("- [2026-03-17.md] Finish weekly retro", note)


if __name__ == "__main__":
    unittest.main()
