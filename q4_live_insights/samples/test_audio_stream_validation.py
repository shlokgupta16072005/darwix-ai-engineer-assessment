from app.audio_stream import AudioStreamBuffer

buffer = AudioStreamBuffer()

cases = [
    ("empty", b""),
    ("wrong type", "not bytes"),
]

for name, data in cases:
    try:
        buffer.add_chunk(data)
        print(f"{name}: FAIL - input was accepted")
    except (TypeError, ValueError):
        print(f"{name}: PASS - invalid input rejected")
