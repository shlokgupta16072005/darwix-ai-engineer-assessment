
import unittest

from common.config import PHILIPPINES_CONFIG, INDONESIA_CONFIG
from common.voice_bot import VoiceBot


class TestMultilingualVoiceBots(unittest.TestCase):

    def setUp(self):
        self.ph = VoiceBot(PHILIPPINES_CONFIG)
        self.idn = VoiceBot(INDONESIA_CONFIG)

    def test_filipino_greeting(self):
        self.assertIn(
            "Kumusta",
            self.ph.respond("Kumusta")
        )

    def test_filipino_loan_inquiry(self):
        self.assertIn(
            "business loan",
            self.ph.respond(
                "Kailangan ko ng business loan para sa aking negosyo."
            )
        )

    def test_filipino_eligibility(self):
        self.assertIn(
            "24 na buwan",
            self.ph.respond(
                "Gaano na katagal dapat ang negosyo ko?"
            )
        )

    def test_filipino_documents(self):
        self.assertIn(
            "identity proof",
            self.ph.respond(
                "Ano ang mga dokumentong kailangan?"
            )
        )

    def test_filipino_rate_fallback(self):
        response = self.ph.respond(
            "Magkano ang interest rate ngayon?"
        )
        self.assertIn("hindi", response.lower())
        self.assertIn("human follow-up", response.lower())

    def test_indonesian_greeting(self):
        self.assertIn(
            "Halo",
            self.idn.respond("Halo")
        )

    def test_indonesian_loan_inquiry(self):
        self.assertIn(
            "pinjaman bisnis",
            self.idn.respond(
                "Saya membutuhkan pinjaman bisnis untuk usaha saya."
            )
        )

    def test_indonesian_eligibility(self):
        self.assertIn(
            "24 bulan",
            self.idn.respond(
                "Berapa lama usaha saya harus sudah berjalan?"
            )
        )

    def test_indonesian_documents(self):
        self.assertIn(
            "identitas",
            self.idn.respond(
                "Dokumen apa saja yang diperlukan?"
            )
        )

    def test_indonesian_rate_fallback(self):
        response = self.idn.respond(
            "Berapa suku bunga saat ini?"
        )
        self.assertIn("tidak tersedia", response.lower())
        self.assertIn("tindak lanjut", response.lower())

    def test_empty_input(self):
        self.assertEqual(
            self.ph.respond(""),
            PHILIPPINES_CONFIG.fallback_message
        )
        self.assertEqual(
            self.idn.respond(""),
            INDONESIA_CONFIG.fallback_message
        )

    def test_cross_language_rejection(self):
        self.assertEqual(
            self.ph.respond("Halo, saya butuh pinjaman untuk usaha"),
            PHILIPPINES_CONFIG.fallback_message
        )
        self.assertEqual(
            self.idn.respond("Kumusta, kailangan ko ng pautang"),
            INDONESIA_CONFIG.fallback_message
        )

    def test_unknown_language_fallback(self):
        self.assertEqual(
            self.ph.respond("What is the weather in Mumbai?"),
            PHILIPPINES_CONFIG.fallback_message
        )
        self.assertEqual(
            self.idn.respond("What is the weather in Mumbai?"),
            INDONESIA_CONFIG.fallback_message
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)