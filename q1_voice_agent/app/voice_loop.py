"""
Local end-to-end voice loop for the Q1 voice agent.

Pipeline:
Microphone -> Local STT -> ConversationAgent -> Local TTS

Uses the Q2 RAGClient so voice responses are grounded
in the NovaFin knowledge base.
"""

from q1_voice_agent.app.agent import ConversationAgent
from q1_voice_agent.app.rag_client import RAGClient
from q1_voice_agent.app.local_stt import LocalSTT
from q1_voice_agent.app.local_tts import LocalTTS
from q1_voice_agent.app.microphone import MicrophoneInput


class LocalVoiceLoop:
    """Run the complete offline voice-agent pipeline."""

    def __init__(self, recording_seconds: int = 5) -> None:
        self.microphone = MicrophoneInput(
            recording_seconds=recording_seconds
        )

        self.stt = LocalSTT()

        self.agent = ConversationAgent(
            client=RAGClient()
        )

        self.tts = LocalTTS()

    def run_once(self) -> str:
        """Record one utterance and generate a spoken response."""

        print("\nListening...")

        audio = self.microphone.record_once()

        print("Transcribing...")

        user_text = self.stt.transcribe_bytes(
            audio.audio_bytes,
            sample_rate=audio.sample_rate,
            channels=audio.channels,
            sample_width=audio.sample_width,
        )

        if not user_text:
            print("No speech detected.")
            return ""

        print(f"USER: {user_text}")

        response = self.agent.respond(user_text)

        print(f"ASSISTANT: {response}")

        self.tts.speak(response)

        return response

    def run(self, turns: int = 3) -> None:
        """Run multiple voice turns in one conversation."""

        if turns <= 0:
            raise ValueError("turns must be greater than zero.")

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
                word in response.lower()
                for word in ["goodbye", "thank you for using"]
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


if __name__ == "__main__":
    voice_loop = LocalVoiceLoop(recording_seconds=5)
    voice_loop.run(turns=3)