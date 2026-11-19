import re
from pathlib import Path
from datetime import datetime


# Read original journal
journal = Path("textfile.txt").read_text(encoding="utf-8")


# Match date headings
date_pattern = re.compile(
    r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
    r"\s+•\s+(\d{1,2}-\d{1,2}-\d{4})\s*$"
)


entries = []
current_entry = []
current_date = None


# Extract individual journal entries
for line in journal.splitlines(keepends=True):

    match = date_pattern.match(line.strip())

    if match:
        if current_date is not None:
            entries.append((current_date, current_entry))

        current_date = datetime.strptime(
            match.group(2), "%m-%d-%Y"
        )

        current_entry = [line.strip()]

    else:
        if current_date is not None:
            current_entry.append(line.rstrip("\r\n"))


# Save final entry
if current_date is not None:
    entries.append((current_date, current_entry))


# Sort newest to oldest
entries.sort(key=lambda entry: entry[0], reverse=True)


# Convert text into RTF-compatible text
def rtf_escape(text):

    result = []

    for char in text:

        if char in "\\{}":
            result.append("\\" + char)

        elif char == "\t":
            result.append("\\tab ")

        elif ord(char) < 128:
            result.append(char)

        else:
            # Encode Unicode characters for RTF
            encoded = char.encode("utf-16-le")

            for i in range(0, len(encoded), 2):
                code = int.from_bytes(encoded[i:i+2], "little")

                if code >= 32768:
                    code -= 65536

                result.append(f"\\u{code}?")

    return "".join(result)


# Generate RTF document
rtf_content = [
    r"{\rtf1\ansi\deff0",
    r"{\fonttbl{\f0 .AppleSystemUIFont;}}",
    r"\f0\fs26 "
]


for date, lines in entries:
    # First line is the date heading
    heading = lines[0]

    # Actual bold formatting
    rtf_content.append(
        r"\b " + rtf_escape(heading) + r"\b0\par "
    )

    # Remaining lines are the journal entry
    for line in lines[1:]:
        if line.lstrip().startswith("⁃"):
            bullet_text = line.lstrip()[1:].strip()

            rtf_content.append(
                r"\li0\fi0 " + rtf_escape("–   " + bullet_text) + r"\par "
            )
        else:
            rtf_content.append(
                r"\li0\fi0 " + rtf_escape(line.strip()) + r"\par "
            )


rtf_content.append("}")


# Export RTF file
Path("journal_newest_first.rtf").write_text(
    "".join(rtf_content),
    encoding="ascii"
)


# Validation
print(f"Total entries: {len(entries)}")

if entries:
    print(f"Newest entry: {entries[0][0].date()}")
    print(f"Oldest entry: {entries[-1][0].date()}")

print("RTF journal successfully generated!")