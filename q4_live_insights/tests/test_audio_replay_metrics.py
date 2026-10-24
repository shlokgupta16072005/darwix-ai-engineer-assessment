import unittest

from app.audio_replay import percentile
from app.audio_replay import clean_asr_text


class TestAudioReplayMetrics(unittest.TestCase):

    def test_empty_asr_text_returns_empty(self):
        self.assertEqual(clean_asr_text(""), "")

    def test_whitespace_asr_text_returns_empty(self):
        self.assertEqual(clean_asr_text("   \t\n "), "")

    def test_punctuation_only_asr_text_returns_empty(self):
        self.assertEqual(clean_asr_text(". . . . . ."), "")

    def test_normal_asr_text_is_preserved(self):
        text = "I want to speak to a human representative."
        self.assertEqual(clean_asr_text(text), text)

    def test_question_punctuation_is_preserved(self):
        self.assertEqual(clean_asr_text("isn't it too?"), "isn't it too?")

    def test_extra_whitespace_is_normalized(self):
        self.assertEqual(
            clean_asr_text("  hello   there!  "),
            "hello there!",
        )

    def test_p50_matches_median_for_even_number_of_values(self):
        values = [1151.296, 1296.696, 6028.336, 11770.747]

        self.assertAlmostEqual(
            percentile(values, 0.50),
            3662.516,
        )

    def test_p50_matches_middle_value_for_odd_number_of_values(self):
        self.assertEqual(percentile([1, 3, 5], 0.50), 3)

    def test_p95_interpolates_between_observations(self):
        self.assertAlmostEqual(percentile([10, 20, 30, 40], 0.95), 38.5)

    def test_empty_values_return_zero(self):
        self.assertEqual(percentile([], 0.50), 0.0)

    def test_invalid_percentile_is_rejected(self):
        with self.assertRaises(ValueError):
            percentile([1, 2, 3], 1.1)