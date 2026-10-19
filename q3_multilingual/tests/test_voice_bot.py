import unittest

from common.config import PHILIPPINES_CONFIG, INDONESIA_CONFIG
from common.voice_bot import VoiceBot


class TestMultilingualVoiceBots(unittest.TestCase):

    def setUp(self):
        self.ph = VoiceBot(PHILIPPINES_CONFIG)
        self.idn = VoiceBot(INDONESIA_CONFIG)

    def test_filipino_greeting(self):
        self.assertIn("Kumusta", self.ph.respond("Kumusta"))

    def test_filipino_loan_inquiry(self):
        self.assertIn(
            "business loan",
            self.ph.respond("Kailangan ko ng business loan para sa aking negosyo.")
        )

    def test_filipino_eligibility(self):
        self.assertIn(
            "24 na buwan",
            self.ph.respond("Gaano na katagal dapat ang negosyo ko?")
        )

    def test_filipino_documents(self):
        self.assertIn(
            "identity proof",
            self.ph.respond("Ano ang mga dokumentong kailangan?")
        )

    def test_filipino_rate_fallback(self):
        response = self.ph.respond("Magkano ang interest rate ngayon?")
        self.assertIn("hindi", response.lower())
        self.assertIn("human follow-up", response.lower())

    def test_indonesian_greeting(self):
        self.assertIn("Halo", self.idn.respond("Halo"))

    def test_indonesian_loan_inquiry(self):
        self.assertIn(
            "pinjaman bisnis",
            self.idn.respond("Saya membutuhkan pinjaman bisnis untuk usaha saya.")
        )

    def test_indonesian_eligibility(self):
        self.assertIn(
            "24 bulan",
            self.idn.respond("Berapa lama usaha saya harus sudah berjalan?")
        )

    def test_indonesian_documents(self):
        self.assertIn(
            "identitas",
            self.idn.respond("Dokumen apa saja yang diperlukan?")
        )

    def test_indonesian_rate_fallback(self):
        response = self.idn.respond("Berapa suku bunga saat ini?")
        self.assertIn("tidak tersedia", response.lower())
        self.assertIn("tindak lanjut", response.lower())

    def test_empty_input(self):
        self.assertEqual(
            self.ph.respond(""), PHILIPPINES_CONFIG.fallback_message
        )
        self.assertEqual(
            self.idn.respond(""), INDONESIA_CONFIG.fallback_message
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

    def test_filipino_asr_eligibility_transcript(self):
        self.assertIn(
            "24 na buwan",
            self.ph.respond("gaano nakatagaldapat ang nigos ako.")
        )

    def test_filipino_asr_documents_transcript(self):
        self.assertIn(
            "identity proof",
            self.ph.respond("ano ang mga dokumentong ka ilangan.")
        )

    # New scenario tests

    def test_filipino_human_escalation_request(self):
        response = self.ph.respond("Gusto kong makipag-usap sa human agent.")
        self.assertTrue(
            any(term in response.lower() for term in (
                "human", "representative", "follow-up", "tao"
            )),
            response
        )

    def test_indonesian_human_escalation_request(self):
        response = self.idn.respond("Saya ingin berbicara dengan petugas.")
        self.assertTrue(
            any(term in response.lower() for term in (
                "perwakilan", "petugas", "tindak lanjut", "manusia"
            )),
            response
        )

    def test_filipino_english_code_switching(self):
        response = self.ph.respond(
            "Ano ang requirements for life insurance?"
        )
        self.assertIn("life insurance", response.lower())
        self.assertIn("coverage", response.lower())
        self.assertIn("follow-up", response.lower())

    def test_indonesian_english_code_switching(self):
        response = self.idn.respond(
            "Apa saja requirements untuk consumer financing?"
        )
        self.assertIn("pembiayaan", response.lower())
        self.assertIn("terverifikasi", response.lower())
        self.assertIn("tindak lanjut", response.lower())

    def test_filipino_insurance_objection_does_not_invent_policy(self):
        response = self.ph.respond(
            "Mahal ang premium. Is this life insurance required?"
        )
        self.assertIn("life insurance", response.lower())
        self.assertIn("coverage", response.lower())
        self.assertIn("premium", response.lower())
        self.assertIn("follow-up", response.lower())

    def test_indonesian_financing_objection_does_not_invent_fees(self):
        response = self.idn.respond(
            "Biaya pembiayaan terlalu mahal, can you reduce it?"
        )
        self.assertIn("pembiayaan", response.lower())
        self.assertIn("biaya", response.lower())
        self.assertIn("terverifikasi", response.lower())
        self.assertIn("tindak lanjut", response.lower())

    def test_filipino_out_of_scope_fallback(self):
        self.assertEqual(
            self.ph.respond("Tell me today's weather in Mumbai."),
            PHILIPPINES_CONFIG.fallback_message
        )

    def test_indonesian_out_of_scope_fallback(self):
        self.assertEqual(
            self.idn.respond("Tolong beri tahu skor pertandingan hari ini."),
            INDONESIA_CONFIG.fallback_message
        )


    def test_filipino_premium_question_uses_safe_sector_response(self):
        response = self.ph.respond("Magkano ang premium ng life insurance?")
        self.assertIn("premium", response.lower())
        self.assertIn("knowledge base", response.lower())
        self.assertIn("follow-up", response.lower())

    def test_indonesian_installment_question_uses_safe_sector_response(self):
        response = self.idn.respond("Berapa cicilan untuk consumer financing?")
        self.assertIn("cicilan", response.lower())
        self.assertIn("terverifikasi", response.lower())
        self.assertIn("tindak lanjut", response.lower())

    def test_indonesian_colloquial_installment_question_is_recognized(self):
        response = self.idn.respond("Kok cicilannya mahal banget?")
        self.assertIn("pembiayaan", response.lower())
        self.assertIn("biaya", response.lower())
        self.assertIn("tindak lanjut", response.lower())

    def test_indonesian_fee_objection_does_not_invent_terms(self):
        response = self.idn.respond("Biaya pembiayaan terlalu mahal, bisa dikurangi?")
        self.assertIn("terverifikasi", response.lower())
        self.assertIn("biaya", response.lower())
        self.assertIn("tindak lanjut", response.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
