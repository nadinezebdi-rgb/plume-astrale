import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontendRailwayRuntimeTest(unittest.TestCase):
    def test_railway_node_version_satisfies_package_engine(self):
        package = json.loads((ROOT / 'frontend/package.json').read_text())
        engine = re.fullmatch(r'>=(\d+)(?:\.\d+\.\d+)?', package['engines']['node'])
        self.assertIsNotNone(engine)

        railway = tomllib.loads((ROOT / 'frontend/railway.toml').read_text())
        configured_version = int(railway['env']['NODE_VERSION'])
        self.assertGreaterEqual(configured_version, int(engine.group(1)))
