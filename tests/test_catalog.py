import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CatalogValidatorTests(unittest.TestCase):
    def run_validator(self, root, *targets):
        return subprocess.run(
            [sys.executable, str(root / "catalog.py"), "verify", *targets],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

    def copy_catalog(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        shutil.copy2(ROOT / "catalog.py", root / "catalog.py")
        shutil.copy2(ROOT / "catalog.yaml", root / "catalog.yaml")
        shutil.copytree(ROOT / "specs", root / "specs")
        return root

    def test_committed_catalog_is_admitted(self):
        result = self.run_validator(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("catalog status: ADMITTED", result.stdout)

    def test_empty_specs_directory_is_blocked(self):
        root = self.copy_catalog()
        shutil.rmtree(root / "specs")
        (root / "specs").mkdir()

        result = self.run_validator(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no .spec.md artifacts found", result.stdout)

    def test_missing_specs_directory_is_blocked(self):
        root = self.copy_catalog()
        shutil.rmtree(root / "specs")

        result = self.run_validator(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("specs directory is missing", result.stdout)

    def test_orphan_registry_entry_is_blocked(self):
        root = self.copy_catalog()
        with (root / "catalog.yaml").open("a", encoding="utf-8") as registry:
            registry.write("  - id: bench/orphan\n    class: bench\n")

        result = self.run_validator(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "registry id 'bench/orphan' has no matching spec artifact", result.stdout
        )

    def test_duplicate_registry_id_is_blocked(self):
        root = self.copy_catalog()
        with (root / "catalog.yaml").open("a", encoding="utf-8") as registry:
            registry.write(
                "  - id: bench/retrieval-wave1\n"
                "    class: bench\n"
            )

        result = self.run_validator(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate registry id: bench/retrieval-wave1", result.stdout)

    def test_duplicate_spec_id_at_wrong_path_is_blocked(self):
        root = self.copy_catalog()
        shutil.copy2(
            root / "specs" / "bench" / "retrieval-wave1.spec.md",
            root / "specs" / "bench" / "duplicate.spec.md",
        )

        result = self.run_validator(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be stored at specs", result.stdout)
        self.assertIn("duplicate spec id", result.stdout)

    def test_missing_selected_artifact_is_blocked(self):
        root = self.copy_catalog()

        result = self.run_validator(root, "specs/bench/missing.spec.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("selected artifact is missing", result.stdout)
        self.assertIn("no valid selected spec artifacts", result.stdout)

    def test_bad_receipt_is_blocked(self):
        root = self.copy_catalog()
        spec = root / "specs" / "bench" / "retrieval-wave1.spec.md"
        text = spec.read_text(encoding="utf-8")
        spec.write_text(text.replace("receipt: f939", "receipt: 0000"), encoding="utf-8")

        result = self.run_validator(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("receipt mismatch", result.stdout)

    def test_workflow_is_source_only_and_fail_closed(self):
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        self.assertFalse((ROOT / ".github" / "workflows" / "mirror.yml").exists())
        for forbidden in (
            "HF_WRITE_TOKEN",
            "huggingface.co",
            "curl ",
            "upload/main",
            "secrets.",
            "|| true",
        ):
            self.assertNotIn(forbidden, workflow)
        self.assertIn("python3 catalog.py verify", workflow)
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)


if __name__ == "__main__":
    unittest.main()
