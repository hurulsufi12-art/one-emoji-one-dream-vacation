"""One Emoji, One Dream Vacation — entry program.

Writes exactly one emoji (1-8 chars) to /output/entry.txt: the dream
vacation that most makes a stranger want to book the flight.
Stdlib only, deterministic.
"""
import os
import unicodedata

TEXT = "\U0001F3DD"  # desert island — beach + faraway place, a postcard


def check_gate(text):
    """Enforce the scorer's gate (RULES.txt) plus the task's own rule.

    Gate: UTF-8 text of 1-8 characters, not whitespace-only.
    Task: exactly ONE emoji, nothing else — no words, no caption,
    no explanation. Returns the text unchanged when it passes;
    raises SystemExit with a specific reason when it does not, so a
    bad entry fails loudly instead of being written.
    """
    if not isinstance(text, str):
        raise SystemExit("entry text is not a string")
    if not 1 <= len(text) <= 8:
        raise SystemExit("entry text violates the 1-8 char gate")
    if not text.strip() or text != text.strip() or "\n" in text:
        raise SystemExit("entry text is blank, padded or multi-line")
    if len(text) != 1 or unicodedata.category(text) not in ("So", "Sk", "Sm", "Sc"):
        raise SystemExit("entry text is not exactly one emoji")
    return text


def main():
    text = check_gate(TEXT)
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Write to a temp file in the same
    # directory, flush it to disk, then rename over the target.
    # Temp name carries the pid so two concurrent grader runs in the same
    # directory never overwrite each other's in-flight file.
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != text:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
