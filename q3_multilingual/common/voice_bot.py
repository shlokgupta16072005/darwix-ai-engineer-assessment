
"""Shared response logic for the localized voice bots."""

from common.config import BotConfig
from common.language_router import get_bot_config


class VoiceBot:
    """Generate safe, localized responses for supported languages."""

    def __init__(self, config: BotConfig):
        self.config = config

    def respond(self, message: str) -> str:
        """Return a deterministic, localized response for a recognized intent."""
        if not message or not message.strip():
            return self.config.fallback_message

        lowered = message.strip().lower()
        detected_config = get_bot_config(message)

        # Reject unsupported and cross-language inputs.
        if detected_config is None:
            return self.config.fallback_message

        if detected_config.language_code != self.config.language_code:
            return self.config.fallback_message

        # Filipino
        if self.config.language_code == "fil":

            if any(x in lowered for x in ["gaano na katagal", "katagal dapat",
                                          "ilang buwan", "edad ng negosyo",
                                          "operasyon"]):
                return (
                    "Ang negosyo ay kailangang may hindi bababa sa "
                    "24 na buwan ng tuloy-tuloy na operasyon, ayon "
                    "sa eligibility requirement."
                )

            if any(x in lowered for x in ["dokumentong kailangan",
                                          "mga dokumento", "dokumento",
                                          "documents", "requirements"]):
                return (
                    "Karaniwang kailangan ang identity proof, PAN o "
                    "naaangkop na tax identification, business proof "
                    "o registration kung naaangkop, at recent business "
                    "bank statements o iba pang hinihinging financial records."
                )

            if any(x in lowered for x in ["interest rate", "rate ngayon",
                                          "kasalukuyang rate",
                                          "magkano ang rate", "pricing"]):
                return (
                    "Ang kasalukuyang live interest rate ay hindi "
                    "available sa knowledge base. Maaari kitang "
                    "tulungan na mag-request ng human follow-up "
                    "para sa current pricing."
                )

            if any(x in lowered for x in ["kumusta", "hello", "hi"]):
                return self.config.greeting

            if any(x in lowered for x in ["business loan", "pautang", "negosyo"]):
                return (
                    "Sige. Maaari kitang tulungan sa mga pangunahing "
                    "impormasyon tungkol sa business loan."
                )

            return self.config.fallback_message

        # Indonesian
        if self.config.language_code == "id":

            if any(x in lowered for x in ["berapa lama", "sudah berjalan",
                                          "minimal berapa", "lama usaha",
                                          "beroperasi", "kelayakan"]):
                return (
                    "Usaha harus telah beroperasi secara berkelanjutan "
                    "selama minimal 24 bulan sesuai dengan persyaratan "
                    "kelayakan."
                )

            if any(x in lowered for x in ["dokumen", "diperlukan",
                                          "persyaratan"]):
                return (
                    "Dokumen yang biasanya diperlukan meliputi "
                    "identitas, PAN atau identifikasi pajak yang berlaku, "
                    "bukti usaha atau pendaftaran jika diperlukan, serta "
                    "rekening koran bisnis terbaru atau dokumen keuangan "
                    "lain yang diminta."
                )

            if any(x in lowered for x in ["suku bunga", "bunga saat ini",
                                          "bunga sekarang", "harga saat ini",
                                          "pricing"]):
                return (
                    "Suku bunga saat ini tidak tersedia dalam knowledge "
                    "base. Saya dapat membantu mengatur tindak lanjut "
                    "dengan perwakilan untuk informasi harga terkini."
                )

            if any(x in lowered for x in ["halo", "hai", "hello"]):
                return self.config.greeting

            if any(x in lowered for x in ["pinjaman bisnis", "pinjaman",
                                          "usaha saya", "butuh pinjaman"]):
                return (
                    "Tentu. Saya dapat membantu memberikan informasi "
                    "dasar mengenai pinjaman bisnis."
                )

            return self.config.fallback_message

        return self.config.fallback_message