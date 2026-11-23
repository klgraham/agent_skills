import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_plugin import inspect


class CheckPluginTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.vault = Path(tmp.name)
        self.config = self.vault / ".obsidian"
        self.config.mkdir()

    def add_plugin(self, config=None, plugin_id="annotated-equations"):
        folder = (config or self.config) / "plugins" / "annotated-equations"
        folder.mkdir(parents=True)
        (folder / "manifest.json").write_text(json.dumps(
            {"id": plugin_id, "version": "0.1.0", "minAppVersion": "1.15.0"}))
        (folder / "main.js").write_text("module.exports = {}")
        (folder / "styles.css").write_text(".example {}")
        return folder

    def set_enabled(self, enabled, config=None):
        ((config or self.config) / "community-plugins.json").write_text(json.dumps(enabled))

    def test_enabled_install_reports_version(self):
        self.add_plugin()
        self.set_enabled(["other", "annotated-equations"])
        status = inspect(self.vault)
        self.assertEqual(status["install"], "installed")
        self.assertTrue(status["enabled_in_config"])
        self.assertEqual((status["version"], status["min_app_version"]), ("0.1.0", "1.15.0"))

    def test_disabled_and_unknown_are_distinct(self):
        self.add_plugin()
        self.assertIsNone(inspect(self.vault)["enabled_in_config"])
        self.set_enabled([])
        self.assertIs(inspect(self.vault)["enabled_in_config"], False)
        self.set_enabled({"annotated-equations": True})
        self.assertIsNone(inspect(self.vault)["enabled_in_config"])

    def test_stale_enabled_entry_is_not_install(self):
        self.set_enabled(["annotated-equations"])
        status = inspect(self.vault)
        self.assertEqual(status["install"], "missing")
        self.assertTrue(status["enabled_in_config"])

    def test_incomplete_install_and_invalid_manifest(self):
        folder = self.add_plugin(plugin_id="other")
        self.assertEqual(inspect(self.vault)["install"], "incomplete")
        (folder / "manifest.json").write_text("{")
        self.assertEqual(inspect(self.vault)["install"], "incomplete")
        (folder / "main.js").unlink()
        self.assertEqual(inspect(self.vault)["install"], "incomplete")

    def test_custom_config_and_wrong_vault(self):
        custom = self.vault / ".obsidian-mobile"
        self.add_plugin(custom)
        self.set_enabled(["annotated-equations"], custom)
        self.assertEqual(inspect(self.vault)["install"], "missing")
        self.assertEqual(inspect(self.vault, custom.name)["install"], "installed")
        self.assertEqual(inspect(self.vault / "not-a-vault")["install"], "unknown")
