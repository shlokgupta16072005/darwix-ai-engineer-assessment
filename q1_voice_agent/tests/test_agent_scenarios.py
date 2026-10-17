import pytest

from q1_voice_agent.app.agent import ConversationAgent


class FakeClient:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.calls = []

    def generate_response(
        self,
        user_message,
        conversation_context=None,
    ):
        self.calls.append(
            {
                "user_message": user_message,
                "conversation_context": conversation_context,
            }
        )

        if not self.responses:
            return "I can help with your question."

        response = self.responses.pop(0)

        if isinstance(response, Exception):
            raise response

        return response


def test_agent_returns_response_and_stores_history():
    client = FakeClient(["I can explain the application process."])
    agent = ConversationAgent(client=client)

    response = agent.respond("  How do I apply?  ")

    assert response == "I can explain the application process."
    assert agent.get_history() == [
        ("How do I apply?", "I can explain the application process.")
    ]
    assert agent.turn_count() == 1


def test_agent_passes_previous_turns_as_context():
    client = FakeClient(["First answer.", "Second answer."])
    agent = ConversationAgent(client=client)

    agent.respond("What is the application process?")
    agent.respond("Which documents should I prepare?")

    context = client.calls[1]["conversation_context"]
    assert "User: What is the application process?" in context
    assert "Assistant: First answer." in context


def test_agent_rejects_empty_user_message():
    agent = ConversationAgent(client=FakeClient())

    with pytest.raises(ValueError, match="cannot be empty"):
        agent.respond("   ")

    assert agent.turn_count() == 0


def test_agent_rejects_empty_client_response():
    agent = ConversationAgent(client=FakeClient(["   "]))

    with pytest.raises(RuntimeError, match="empty response"):
        agent.respond("How do I apply?")

    assert agent.turn_count() == 0


def test_agent_propagates_client_failure_without_storing_turn():
    agent = ConversationAgent(
        client=FakeClient([RuntimeError("Client unavailable")])
    )

    with pytest.raises(RuntimeError, match="Client unavailable"):
        agent.respond("How do I apply?")

    assert agent.turn_count() == 0


def test_agent_limits_stored_history():
    agent = ConversationAgent(
        client=FakeClient(["Answer one.", "Answer two.", "Answer three."]),
        max_turns=2,
    )

    agent.respond("Question one")
    agent.respond("Question two")
    agent.respond("Question three")

    assert agent.turn_count() == 2
    assert agent.get_history() == [
        ("Question two", "Answer two."),
        ("Question three", "Answer three."),
    ]


def test_agent_reset_clears_history():
    agent = ConversationAgent(client=FakeClient(["Answer."]))
    agent.respond("Hello")

    agent.reset()

    assert agent.get_history() == []
    assert agent.turn_count() == 0


def test_agent_rejects_nonpositive_max_turns():
    with pytest.raises(ValueError, match="max_turns"):
        ConversationAgent(client=FakeClient(), max_turns=0)


@pytest.mark.parametrize(
    "customer_message",
    [
        "I am worried about the loan terms.",
        "I do not know which documents I need.",
        "Your information seems inconsistent.",
        "Can I speak to a human representative?",
        "Tell me something unrelated to loans.",
    ],
)
def test_agent_safely_passes_scenario_messages_to_client(customer_message):
    client = FakeClient(["I will help using the available information."])
    agent = ConversationAgent(client=client)

    response = agent.respond(customer_message)

    assert response
    assert client.calls[0]["user_message"] == customer_message
    assert agent.turn_count() == 1
