"""
Local end-to-end voice loop with evidence recording.

Pipeline:
Microphone -> Local STT -> Q2 RAG -> Local TTS

Each session stores customer audio, assistant audio, and
structured transcript/evidence metadata.
"""

import json
import wave
from datetime import datetime, timezone
from pathlib import Path

from q1_voice_agent.app.agent import ConversationAgent
from q1_voice_agent.app.rag_client import RAGClient
from q1_voice_agent.app.local_stt import LocalSTT
from q1_voice_agent.app.local_tts import LocalTTS
from q1_voice_agent.app.microphone import MicrophoneInput


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class LocalVoiceLoop:
    """Run the voice agent and record evidence for each turn."""

    def __init__(self, recording_seconds: int = 5) -> None:
        self.microphone = MicrophoneInput(
            recording_seconds=recording_seconds
        )
        self.stt = LocalSTT()
        self.rag_client = RAGClient()
        self.agent = ConversationAgent(client=self.rag_client)
        self.tts = LocalTTS()

        self.session_dir = None
        self.transcript_path = None
        self.transcript = {
            "project": "Darwix AI Engineer Assessment - Q1",
            "session_started_utc": None,
            "pipeline": ["microphone", "local_stt", "q2_rag", "local_tts"],
            "turns": [],
        }

    def _start_session(self) -> None:
        """Create a new, timestamped local evidence directory."""

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.session_dir = (
            PROJECT_ROOT
            / "q1_voice_agent"
            / "evidence"
            / "recorded_calls"
            / f"session_{timestamp}"
        )
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self.transcript_path = self.session_dir / "transcript.json"
        self.transcript["session_started_utc"] = (
            datetime.now(timezone.utc).isoformat()
        )
        self.transcript["turns"] = []

        self._save_transcript()

        print(f"\nEvidence directory: {self.session_dir}")

    def _save_transcript(self) -> None:
        """Write the transcript after each completed turn."""

        if self.transcript_path is None:
            return

        self.transcript["session_updated_utc"] = (
            datetime.now(timezone.utc).isoformat()
        )

        self.transcript_path.write_text(
            json.dumps(self.transcript, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _save_customer_audio(audio, output_path: Path) -> None:
        """Save raw microphone PCM bytes as a valid WAV file."""

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(audio.channels)
            wav_file.setsampwidth(audio.sample_width)
            wav_file.setframerate(audio.sample_rate)
            wav_file.writeframes(audio.audio_bytes)

    def run_once(self) -> str:
        """Record one customer utterance and respond."""

        print("\nListening...")
        audio = self.microphone.record_once()

        if self.session_dir is None:
            self._start_session()

        turn_number = len(self.transcript["turns"]) + 1
        turn_prefix = f"turn_{turn_number:02d}"

        customer_audio_path = self.session_dir / (
            f"{turn_prefix}_customer.wav"
        )
        self._save_customer_audio(audio, customer_audio_path)

        print("Transcribing...")
        user_text = self.stt.transcribe_bytes(
            audio.audio_bytes,
            sample_rate=audio.sample_rate,
            channels=audio.channels,
            sample_width=audio.sample_width,
        )

        if not user_text:
            print("No speech detected.")
            self.transcript["turns"].append({
                "turn": turn_number,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "customer_transcript": "",
                "status": "no_speech_detected",
                "customer_audio": customer_audio_path.name,
                "assistant_audio": None,
                "assistant_response": None,
                "rag_mode": None,
                "sources": [],
            })
            self._save_transcript()
            return ""

        print(f"USER: {user_text}")

        response = self.agent.respond(user_text)
        print(f"ASSISTANT: {response}")

        rag_result = self.rag_client.last_result
        source_records = []

        for source in rag_result.get("sources", []):
            source_records.append({
                "source": source.get("source"),
                "category": source.get("category"),
                "score": source.get("score"),
            })

        assistant_audio_path = self.session_dir / (
            f"{turn_prefix}_assistant.wav"
        )
        assistant_audio_name = None

        try:
            self.tts.save(response, str(assistant_audio_path))

            if (
                assistant_audio_path.exists()
                and assistant_audio_path.stat().st_size > 44
            ):
                assistant_audio_name = assistant_audio_path.name
            else:
                print(
                    "[WARNING] TTS did not produce a usable audio file."
                )
        except Exception as error:
            print(f"[WARNING] Could not save assistant audio: {error}")

        # Play the response as before, even if saving the clip failed.
        self.tts.speak(response)

        self.transcript["turns"].append({
            "turn": turn_number,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "customer_transcript": user_text,
            "assistant_response": response,
            "status": "completed",
            "customer_audio": customer_audio_path.name,
            "assistant_audio": assistant_audio_name,
            "rag_mode": rag_result.get("mode", "unknown"),
            "sources": source_records,
        })

        self._save_transcript()
        print(f"Evidence saved: {self.transcript_path}")

        return response

    def run(self, turns: int = 3) -> None:
        """Run a multi-turn conversation and save its evidence."""

        if turns <= 0:
            raise ValueError("turns must be greater than zero.")

        self._start_session()

        print("\n========================================")
        print(" Darwix Voice Assistant - Local Demo")
        print("========================================")
        print(f"Conversation turns: {turns}")

        for turn_number in range(1, turns + 1):
            print(f"\n--- Turn {turn_number}/{turns} ---")

            response = self.run_once()

            if not response:
                print("Ending conversation.")
                break

            if any(
                phrase in response.lower()
                for phrase in ["goodbye", "thank you for using"]
            ):
                print("Conversation ended.")
                break

        print("\nConversation history:")
        for index, (user_message, assistant_message) in enumerate(
            self.agent.get_history(),
            start=1,
        ):
            print(f"{index}. USER: {user_message}")
            print(f"   ASSISTANT: {assistant_message}")

        print(f"\nTotal turns stored: {self.agent.turn_count()}")
        print(f"Evidence directory: {self.session_dir}")
        print(f"Transcript: {self.transcript_path}")


if __name__ == "__main__":
    voice_loop = LocalVoiceLoop(recording_seconds=5)
    voice_loop.run(turns=3)
