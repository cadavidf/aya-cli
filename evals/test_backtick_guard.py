import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import aya


class BacktickGuardTest(unittest.TestCase):
    def test_direct_generation_rejects_wrapped_command(self):
        with patch.object(aya, 'model_generate', return_value='`pwd`'):
            with self.assertRaisesRegex(RuntimeError, 'wrapped in backticks'):
                aya.generate('show working directory')

    def test_generation_keeps_embedded_backticks(self):
        with patch.object(aya, 'model_generate', return_value='echo `date`'):
            self.assertEqual(aya.generate('show date'), 'echo `date`')

    def test_wrapped_output_is_rejected_and_plain_output_is_reviewed(self):
        for proposal, expected_rejection in [('`pwd`', True), ('pwd', False)]:
            with self.subTest(proposal=proposal):
                answers = iter(['/command test', 'exit'] if expected_rejection
                               else ['/command test', 'n', 'exit'])
                output = io.StringIO()
                with patch.object(aya, 'banner'), patch.object(aya, 'generate', return_value=proposal), \
                     patch('builtins.input', side_effect=lambda *args: next(answers)), \
                     contextlib.redirect_stdout(output):
                    aya.main()
                self.assertEqual('wrapped in backticks' in output.getvalue(), expected_rejection)


if __name__ == '__main__':
    unittest.main()
