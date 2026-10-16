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

    def test_duplicate_nudge_is_suppressed(self):
        engine = NudgeEngine(cooldown_seconds=30)
        signals = detect_signals(
            "The customer cannot afford the payment."
        )

        first = engine.generate(signals, now=1000)
        repeated = engine.generate(signals, now=1010)
        after_cooldown = engine.generate(signals, now=1031)

        self.assertEqual(len(first), 1)
        self.assertEqual(len(repeated), 0)
        self.assertEqual(len(after_cooldown), 1)



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


if __name__ == "__main__":
    unittest.main()