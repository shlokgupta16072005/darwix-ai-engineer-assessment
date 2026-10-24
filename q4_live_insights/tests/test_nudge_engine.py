
import unittest

from app.audio_stream import AudioStreamBuffer
from app.signal_detector import detect_signals
from app.nudge_engine import NudgeEngine


class TestQ4Core(unittest.TestCase):

    def test_audio_chunks_keep_order(self):
        buffer = AudioStreamBuffer()
        buffer.add_chunk(b"audio-1")
        buffer.add_chunk(b"audio-2")

        self.assertEqual(len(buffer), 2)
        self.assertEqual(
            [chunk.sequence for chunk in buffer],
            [1, 2],
        )

    def test_empty_audio_chunk_is_rejected(self):
        buffer = AudioStreamBuffer()

        with self.assertRaises(ValueError):
            buffer.add_chunk(b"")

    def test_non_bytes_audio_chunk_is_rejected(self):
        buffer = AudioStreamBuffer()

        with self.assertRaises(TypeError):
            buffer.add_chunk("not bytes")

    def test_payment_difficulty_is_detected(self):
        signals = detect_signals(
            "The customer cannot afford the payment."
        )

        self.assertIn(
            "payment_difficulty",
            [signal["signal"] for signal in signals],
        )

    def test_compliance_gap_is_detected(self):
        signals = detect_signals(
            "The agent guaranteed approval without telling the customer."
        )

        self.assertIn(
            "compliance_gap",
            [signal["signal"] for signal in signals],
        )

    def test_rising_frustration_is_detected(self):
        signals = detect_signals(
            "The customer says this is frustrating."
        )

        self.assertIn(
            "rising_frustration",
            [signal["signal"] for signal in signals],
        )

    def test_callback_request_is_detected(self):
        signals = detect_signals(
            "The customer asked to call me back."
        )

        self.assertIn(
            "callback_needed",
            [signal["signal"] for signal in signals],
        )

    def test_cross_sell_opportunity_is_detected(self):
        signals = detect_signals(
            "The customer is interested in a second vehicle."
        )

        self.assertIn(
            "missed_cross_sell",
            [signal["signal"] for signal in signals],
        )

    def test_vehicle_coverage_question_is_not_cross_sell(self):
        signals = detect_signals(
            "The customer asked whether a second vehicle was covered."
        )

        self.assertNotIn(
            "missed_cross_sell",
            [signal["signal"] for signal in signals],
        )

    def test_duplicate_nudge_is_suppressed(self):
        engine = NudgeEngine(cooldown_seconds=30)

        # Test-only value; not a calibrated model probability.
        signals = [
            {
                "signal": "payment_difficulty",
                "priority": "medium",
                "nudge": "Explore approved payment-support options.",
                "method": "keyword_rule",
                "confidence": 0.85,
            }
        ]

        first = engine.generate(signals, now=1000)
        repeated = engine.generate(signals, now=1010)
        after_cooldown = engine.generate(signals, now=1031)

        self.assertEqual(len(first), 1)
        self.assertEqual(len(repeated), 0)
        self.assertEqual(len(after_cooldown), 1)

    def test_missing_confidence_does_not_generate_nudge(self):
        engine = NudgeEngine()

        signals = [
            {
                "signal": "payment_difficulty",
                "priority": "medium",
                "nudge": "Explore approved payment-support options.",
                "method": "model_prediction",
            }
        ]

        self.assertEqual(
            engine.generate(signals, now=1000),
            [],
        )

    def test_invalid_confidence_does_not_generate_nudge(self):
        engine = NudgeEngine()

        invalid_confidences = [
            "not-a-number",
            -0.1,
            1.1,
        ]

        for confidence in invalid_confidences:
            with self.subTest(confidence=confidence):
                signals = [
                    {
                        "signal": "payment_difficulty",
                        "priority": "medium",
                        "nudge": "Explore approved payment-support options.",
                        "method": "model_prediction",
                        "confidence": confidence,
                    }
                ]

                self.assertEqual(
                    engine.generate(signals, now=1000),
                    [],
                )

    def test_confidence_below_threshold_does_not_generate_nudge(self):
        engine = NudgeEngine(min_confidence=0.70)

        signals = [
            {
                "signal": "payment_difficulty",
                "priority": "medium",
                "nudge": "Explore approved payment-support options.",
                "method": "model_prediction",
                "confidence": 0.60,
            }
        ]

        self.assertEqual(
            engine.generate(signals, now=1000),
            [],
        )

    def test_keyword_rule_can_generate_nudge_without_confidence(self):
        engine = NudgeEngine()

        signals = detect_signals(
            "The customer cannot afford the payment."
        )

        nudges = engine.generate(signals, now=1000)

        self.assertIn(
            "payment_difficulty",
            [nudge["signal"] for nudge in nudges],
        )

        self.assertNotIn("confidence", nudges[0])

    def test_normal_conversation_produces_no_signals(self):
        signals = detect_signals(
            "Hello, thank you for calling. How can I help you today?"
        )

        self.assertEqual(signals, [])

    def test_negated_frustration_is_not_flagged(self):
        signals = detect_signals(
            "I am not frustrated with the service."
        )

        self.assertNotIn(
            "rising_frustration",
            [signal["signal"] for signal in signals],
        )

    def test_unrelated_vehicle_mention_is_not_automatically_an_opportunity(self):
        signals = detect_signals(
            "The customer sold their second vehicle last year."
        )

        self.assertNotIn(
            "missed_cross_sell",
            [signal["signal"] for signal in signals],
        )

    def test_explicit_compliance_risk_still_triggers(self):
        signals = detect_signals(
            "The agent guaranteed approval without telling the customer."
        )

        self.assertIn(
            "compliance_gap",
            [signal["signal"] for signal in signals],
        )

    def test_negated_payment_difficulty_is_not_flagged(self):
        signals = detect_signals(
            "I can afford the payment and am able to pay."
        )

        self.assertNotIn(
            "payment_difficulty",
            [signal["signal"] for signal in signals],
        )

    def test_denial_of_guaranteed_approval_is_not_flagged(self):
        signals = detect_signals(
            "The agent did not promise guaranteed approval."
        )

        self.assertNotIn(
            "compliance_gap",
            [signal["signal"] for signal in signals],
        )


if __name__ == "__main__":
    unittest.main()
