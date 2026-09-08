import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import catalog


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

    def rewrite_retrieval_spec_id(self, root, replacement):
        original = "bench/retrieval-wave1"
        registry = root / "catalog.yaml"
        registry.write_text(
            registry.read_text(encoding="utf-8").replace(original, replacement, 1),
            encoding="utf-8",
        )

        spec = root / "specs" / "bench" / "retrieval-wave1.spec.md"
        text = spec.read_text(encoding="utf-8").replace(
            f"id: {original}", f"id: {replacement}", 1
        )
        meta, error = catalog.parse_front_matter(text)
        self.assertIsNone(error)
        receipt = catalog.canonical_receipt(meta)
        text = re.sub(
            r"(?m)^receipt:\s*[^\r\n]+$", f"receipt: {receipt}", text, count=1
        )
        spec.write_text(text, encoding="utf-8")

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

    def test_outdented_registry_class_is_blocked(self):
        root = self.copy_catalog()
        registry = root / "catalog.yaml"
        registry.write_text(
            registry.read_text(encoding="utf-8").replace(
                "    class: bench", "class: bench", 1
            ),
            encoding="utf-8",
        )

        result = self.run_validator(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unparseable registry line", result.stdout)
        self.assertIn("is missing class", result.stdout)

    def test_selected_artifact_with_symlinked_parent_is_blocked(self):
        root = self.copy_catalog()
        selected_parent = root / "specs" / "bench"
        escaped_parent = root / "escaped-bench"
        selected_parent.rename(escaped_parent)
        try:
            selected_parent.symlink_to(escaped_parent, target_is_directory=True)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"directory symlinks are unavailable: {exc}")

        result = self.run_validator(
            root, "specs/bench/retrieval-wave1.spec.md"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("selected artifact path contains symlink", result.stdout)
        self.assertIn("no valid selected spec artifacts", result.stdout)

    def test_dot_segments_in_ids_are_blocked(self):
        for aliased_id in (
            "bench/./retrieval-wave1",
            "alias/../bench/retrieval-wave1",
        ):
            with self.subTest(aliased_id=aliased_id):
                root = self.copy_catalog()
                self.rewrite_retrieval_spec_id(root, aliased_id)

                result = self.run_validator(root)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"invalid registry id: {aliased_id}", result.stdout)
                self.assertIn(f"invalid id: {aliased_id}", result.stdout)

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
