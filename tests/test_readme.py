from pathlib import Path
import unittest


class ReadmeTests(unittest.TestCase):
    def test_readme_mentions_smoke_scripts(self) -> None:
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("scripts/smoke_openai.sh", readme)
        self.assertIn("scripts/smoke_claude.sh", readme)
        self.assertIn("scripts/smoke_both.sh", readme)
