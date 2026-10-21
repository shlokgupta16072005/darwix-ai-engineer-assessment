
import re

from common.config import BotConfig
from common.language_router import get_bot_config


def normalize_filipino_transcript(text: str) -> str:
    """Normalize specific Filipino ASR errors observed in demo recordings."""
    text = text.lower().strip()

    replacements = [
        (r"\bkung\s*musta\b", "kumusta"),
        (r"\bma[- ]?tutulungan\b", "matutulungan"),
        (r"\bka\s+ilangan\b", "kailangan"),
        (r"\bnigos\b", "negosyo"),
        (r"\bnakatagaldapat\b", "na katagal dapat"),
    ]

    for regex, corrected in replacements:
        text = re.sub(regex, corrected, text, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", text).strip()


class VoiceBot:
    """Generate safe, localized responses for supported languages."""

    def __init__(self, config: BotConfig):
        self.config = config

    def _human_escalation_requested(self, message: str) -> bool:
        """Detect explicit requests for a human representative."""
        lowered = message.lower()

        if self.config.language_code == "fil":
            escalation_terms = (
                "human agent",
                "talk to a human",
                "speak to a human",
                "connect me to a human",
                "connect me to a human agent",
                "please connect me to a human agent",
                "talk to a human agent",
                "speak to a human agent",
                "makipag-usap sa human",
                "makipag-usap sa tao",
                "kausapin ang representative",
                "agent po",
            )
            return any(term in lowered for term in escalation_terms)

        if self.config.language_code == "id":
            escalation_terms = (
                "berbicara dengan petugas",
                "bicara dengan petugas",
                "berbicara dengan manusia",
                "agen manusia",
                "perwakilan manusia",
                "customer service",
                "bicara dengan agen",
                "ingin berbicara dengan petugas",
                "saya ingin berbicara dengan petugas",
                "ingin bicara dengan petugas",
                "tolong hubungkan saya dengan petugas",
                "hubungkan saya dengan petugas",
            )
            return any(term in lowered for term in escalation_terms)

        return False

    def _human_escalation_response(self) -> str:
        """Acknowledge escalation without falsely claiming a live transfer."""
        if self.config.language_code == "fil":
            return (
                "Naiintindihan ko. Kailangan mo ng tulong mula sa "
                "human representative. Hindi ako makakapaglipat ng "
                "tawag dito, pero maaari kang humiling ng human follow-up."
            )

        if self.config.language_code == "id":
            return (
                "Baik, Anda ingin berbicara dengan petugas. "
                "Saya tidak dapat mentransfer panggilan secara langsung "
                "di sini, tetapi Anda dapat meminta tindak lanjut "
                "dari perwakilan manusia."
            )

        return self.config.fallback_message

    def respond(self, message: str) -> str:
        """Return a localized, grounded response or a safe fallback."""
        if not message or not message.strip():
            return self.config.fallback_message

        if self.config.language_code == "fil":
            message = normalize_filipino_transcript(message)

        lowered = message.strip().lower()

        # Priority 1: honor explicit requests for a human first.
        # This does not perform a real call transfer or create a callback.
        if self._human_escalation_requested(lowered):
            return self._human_escalation_response()

        # Priority 2: handle sector-specific questions safely.
        # The current Q2 knowledge base contains business-loan information,
        # not verified life-insurance or consumer-finance product terms.
        if self.config.language_code == "fil":
            insurance_terms = (
                "life insurance",
                "bancassurance",
                "insurance coverage",
                "policy benefits",
                "beneficiary",
                "rider",
                "premium",
                "coverage",
                "life policy",
                "insurance policy",
            )

            if any(term in lowered for term in insurance_terms):
                return (
                    "Salamat sa iyong tanong tungkol sa life insurance. "
                    "Wala sa kasalukuyang knowledge base ang beripikadong "
                    "detalye tungkol sa coverage, premium, policy benefits, "
                    "o beneficiary. Hindi ako magbibigay ng hindi "
                    "nakumpirmang impormasyon. Maaari kang humiling ng "
                    "follow-up mula sa isang human representative."
                )

        if self.config.language_code == "id":
            finance_terms = (
                "consumer financing",
                "consumer finance",
                "multifinance",
                "pembiayaan",
                "cicilan",
                "angsuran",
                "tenor",
                "denda",
                "jatuh tempo",
                "uang muka",
                "biaya administrasi",
                "biaya pembiayaan",
                "jumlah cicilan",
            )

            if any(term in lowered for term in finance_terms):
                return (
                    "Terima kasih atas pertanyaan Anda tentang pembiayaan. "
                    "Knowledge base saat ini belum memiliki informasi "
                    "terverifikasi tentang cicilan, tenor, biaya, denda, "
                    "atau persyaratan produk pembiayaan konsumen. Saya tidak "
                    "akan menebak detail tersebut. Anda dapat meminta "
                    "tindak lanjut dari perwakilan manusia."
                )

        # Priority 3: validate the detected language.
        detected_config = get_bot_config(message)

        # Permit known Filipino eligibility/document intents when ASR
        # has weakened language markers.
        if detected_config is None:
            known_filipino_intent = (
                self.config.language_code == "fil"
                and any(
                    term in lowered
                    for term in (
                        "gaano na katagal",
                        "katagal dapat",
                        "dokumentong kailangan",
                        "mga dokumento",
                        "dokumento",
                    )
                )
            )

            if not known_filipino_intent:
                return self.config.fallback_message

        elif detected_config.language_code != self.config.language_code:
            return self.config.fallback_message

        # Priority 4: Filipino business-loan intents.
        if self.config.language_code == "fil":
            if any(
                term in lowered
                for term in (
                    "gaano na katagal",
                    "katagal dapat",
                    "ilang buwan",
                    "edad ng negosyo",
                    "operasyon",
                )
            ):
                return (
                    "Ang negosyo ay kailangang may hindi bababa sa "
                    "24 na buwan ng tuloy-tuloy na operasyon, ayon "
                    "sa eligibility requirement."
                )

            if any(
                term in lowered
                for term in (
                    "dokumentong kailangan",
                    "mga dokumento",
                    "dokumento",
                    "documents",
                    "requirements",
                )
            ):
                return (
                    "Karaniwang kailangan ang identity proof, PAN o "
                    "naaangkop na tax identification, business proof "
                    "o registration kung naaangkop, at recent business "
                    "bank statements o iba pang hinihinging financial records."
                )

            if any(
                term in lowered
                for term in (
                    "interest rate",
                    "rate ngayon",
                    "kasalukuyang rate",
                    "magkano ang rate",
                    "pricing",
                )
            ):
                return (
                    "Ang kasalukuyang live interest rate ay hindi "
                    "available sa knowledge base. Maaari kitang "
                    "tulungan na mag-request ng human follow-up "
                    "para sa current pricing."
                )

            if any(term in lowered for term in ("kumusta", "hello", "hi")):
                return self.config.greeting

            if any(
                term in lowered
                for term in ("business loan", "pautang", "negosyo")
            ):
                return (
                    "Sige. Maaari kitang tulungan sa mga pangunahing "
                    "impormasyon tungkol sa business loan."
                )

            return self.config.fallback_message

        # Priority 5: Indonesian business-loan intents.
        if self.config.language_code == "id":
            if any(
                term in lowered
                for term in (
                    "berapa lama",
                    "sudah berjalan",
                    "minimal berapa",
                    "lama usaha",
                    "beroperasi",
                    "kelayakan",
                )
            ):
                return (
                    "Usaha harus telah beroperasi secara berkelanjutan "
                    "selama minimal 24 bulan sesuai dengan persyaratan "
                    "kelayakan."
                )

            if any(
                term in lowered
                for term in ("dokumen", "diperlukan", "persyaratan")
            ):
                return (
                    "Dokumen yang biasanya diperlukan meliputi "
                    "identitas, PAN atau identifikasi pajak yang berlaku, "
                    "bukti usaha atau pendaftaran jika diperlukan, serta "
                    "rekening koran bisnis terbaru atau dokumen keuangan "
                    "lain yang diminta."
                )

            if any(
                term in lowered
                for term in (
                    "suku bunga",
                    "bunga saat ini",
                    "bunga sekarang",
                    "harga saat ini",
                    "pricing",
                )
            ):
                return (
                    "Suku bunga saat ini tidak tersedia dalam knowledge "
                    "base. Saya dapat membantu mengatur tindak lanjut "
                    "dengan perwakilan untuk informasi harga terkini."
                )

            if any(term in lowered for term in ("halo", "hai", "hello")):
                return self.config.greeting

            if any(
                term in lowered
                for term in (
                    "pinjaman bisnis",
                    "pinjaman",
                    "usaha saya",
                    "butuh pinjaman",
                )
            ):
                return (
                    "Tentu. Saya dapat membantu memberikan informasi "
                    "dasar mengenai pinjaman bisnis."
                )

            return self.config.fallback_message

        return self.config.fallback_message
