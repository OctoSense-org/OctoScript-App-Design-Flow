"""Keep the worked examples aligned with the safer connected-app contracts."""
import json
from pathlib import Path
import unittest

EXAMPLES = Path(__file__).resolve().parents[1] / 'examples/connected-apps'

class ConnectedContracts(unittest.TestCase):
    def test_inbox_requires_installed_workspace(self):
        bundle = EXAMPLES / 'inbox/bundle'
        tool = next(x for x in json.loads((bundle / 'tools.json').read_text())['tools'] if x['name'] == 'inbox.notify')
        schema = tool['input_schema']
        self.assertFalse(schema['additionalProperties'])
        self.assertTrue({'template', 'initial', 'summary', 'notify'}.issubset(schema['required']))
        self.assertTrue({'source', 'script', 'data'}.isdisjoint(schema['properties']))
        for template in schema['properties']['template']['enum']:
            self.assertTrue((bundle / template).is_file())

    def test_notes_agent_is_explicit_without_write_or_background_tools(self):
        bundle = EXAMPLES / 'github-notes/bundle'
        agent = json.loads((bundle / 'manifest.json').read_text())['agent']
        self.assertEqual(agent['instructions'], 'AGENT.md')
        self.assertTrue((bundle / agent['instructions']).is_file())
        self.assertFalse(agent['background'])
        self.assertEqual(agent['profile'], 'read-only')
        self.assertEqual(agent['tools'], [])
        for tool in json.loads((bundle / 'tools.json').read_text())['tools']:
            self.assertEqual(tool['risk'], 'read')
            self.assertTrue(tool['private_data'])
            self.assertFalse(tool['shareable'])
            self.assertFalse(tool['background'])

if __name__ == '__main__': unittest.main()
