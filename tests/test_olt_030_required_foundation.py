"""Protect the GitHub-required foundation status gate against accidental bypass."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "foundation.yml"


def violations(s: str) -> list[str]:
    bad: list[str] = []
    # A required PR check cannot be excluded by a path filter.
    if not s.startswith(
        "name: OLT fresh foundation (NOT translation certification)\n"
        "on:\n"
        "  push:\n"
        "    branches: [main]\n"
        "  pull_request:\n"
    ):
        bad.append("FOUNDATION_MUST_RUN_ON_EVERY_PULL_REQUEST")
    event_segment = s.split("permissions:", 1)[0]
    if re.search(r"(?m)^\s+(?:paths|paths-ignore|branches-ignore):", event_segment):
        bad.append("FILTER_CAN_SKIP_REQUIRED_CHECK")
    if "permissions:\n  contents: read\n" not in s:
        bad.append("MINIMAL_READ_PERMISSIONS_REQUIRED")
    if "jobs:\n  foundation:\n" not in s or s.count("\n  foundation:\n") != 1:
        bad.append("PROTECTED_CHECK_NAME_CHANGED")
    if "runs-on: ubuntu-latest" not in s:
        bad.append("FOUNDATION_RUNNER_MISSING")
    if "      - uses: actions/checkout@v6\n        with:\n          persist-credentials: false\n" not in s:
        bad.append("SECURE_CHECKOUT_REQUIRED")
    if "      - uses: actions/setup-python@v6\n        with:\n          python-version: '3.12'\n" not in s:
        bad.append("SUPPORTED_PYTHON_ACTION_REQUIRED")
    for required in (
        "run: python scripts/check.py",
        "run: python -m unittest discover -s tests -v",
        "if python scripts/check.py --release; then",
        'echo "ERROR: release gate falsely passed"',
        "exit 1",
        'echo "Expected: Source verification and Genesis release BLOCKED"',
    ):
        if required not in s:
            bad.append("MISSING_CHECK_OR_FAIL_CLOSED_RELEASE_STEP:" + required)
    for forbidden in (
        "contents: write", "persist-credentials: true",
        "git push", "git commit", "continue-on-error:",
        "|| true", "exit 0", "pull_request_target:"
    ):
        if forbidden in s:
            bad.append("FORBIDDEN_BYPASS:" + forbidden)
    if re.search(r"(?m)^[ \t]+if:", s):
        bad.append("CONDITIONAL_FOUNDATION_STEP_OR_JOB")
    return bad


class TestOLT030(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = WORKFLOW.read_text(encoding="utf-8")

    def test_required_foundation_is_readonly_unconditional_and_fail_closed(self):
        self.assertEqual(violations(self.reference), [])

    def test_reject_missing_pr_trigger(self):
        changed = self.reference.replace("  pull_request:\n", "")
        self.assertIn("FOUNDATION_MUST_RUN_ON_EVERY_PULL_REQUEST", violations(changed))

    def test_reject_required_check_rename(self):
        changed = self.reference.replace("  foundation:\n", "  optional-ci:\n")
        self.assertIn("PROTECTED_CHECK_NAME_CHANGED", violations(changed))

    def test_reject_pr_path_filter(self):
        changed = self.reference.replace("  pull_request:\n", "  pull_request:\n    paths:\n      - 'docs/**'\n")
        self.assertIn("FILTER_CAN_SKIP_REQUIRED_CHECK", violations(changed))

    def test_reject_write_permission_and_retained_credentials(self):
        changed = self.reference.replace("contents: read", "contents: write").replace(
            "persist-credentials: false", "persist-credentials: true")
        problems = violations(changed)
        self.assertIn("MINIMAL_READ_PERMISSIONS_REQUIRED", problems)
        self.assertIn("FORBIDDEN_BYPASS:contents: write", problems)
        self.assertIn("SECURE_CHECKOUT_REQUIRED", problems)

    def test_reject_masked_failures_and_conditional_tests(self):
        changed = self.reference.replace("run: python -m unittest discover -s tests -v",
                                         "run: python -m unittest discover -s tests -v || true")
        changed = changed.replace("      - name: Run regression and negative tests",
                                  "      - name: Run regression and negative tests\n        continue-on-error: true")
        problems = violations(changed)
        self.assertIn("FORBIDDEN_BYPASS:|| true", problems)
        self.assertIn("FORBIDDEN_BYPASS:continue-on-error:", problems)

    def test_reject_release_check_removed(self):
        changed = self.reference.replace("if python scripts/check.py --release; then",
                                         "echo 'release irrelevant'")
        self.assertTrue(any(p.startswith("MISSING_CHECK_OR_FAIL_CLOSED_RELEASE_STEP:")
                            for p in violations(changed)))


if __name__ == "__main__":
    unittest.main()
