"""Fix encoding issues in agent files — byte-level replacement."""
files = [
    'D:/AI_Office/backend/app/agents/ba_agent.py',
    'D:/AI_Office/backend/app/agents/qa_agent.py',
]

# Mojibake em-dash: Thai char โ (U+0E42) + Euro sign (U+20AC) in UTF-8
MOJIBAKE      = b'\xe0\xb9\x82\xe2\x82\xac'

# Curly quote bytes (UTF-8)
RIGHT_DQUOTE  = b'\xe2\x80\x9d'   # "
LEFT_DQUOTE   = b'\xe2\x80\x9c'   # "
RIGHT_SQUOTE  = b'\xe2\x80\x99'   # '
LEFT_SQUOTE   = b'\xe2\x80\x98'   # '

BOM           = b'\xef\xbb\xbf'
ASCII_QUOTE   = b'\x22'           # "

for path in files:
    with open(path, 'rb') as f:
        data = f.read()

    fixed = data

    # Step 1: mojibake immediately followed by any closing quote
    #         (the mojibake + its "closing curly quote" combo = the mangled em dash)
    fixed = fixed.replace(MOJIBAKE + RIGHT_DQUOTE, b'--')
    fixed = fixed.replace(MOJIBAKE + ASCII_QUOTE,  b'--')
    # Step 2: remaining standalone mojibake
    fixed = fixed.replace(MOJIBAKE, b'--')

    # Step 3: BOM
    fixed = fixed.replace(BOM, b'')

    # Step 4: remaining curly/smart quotes → ASCII
    fixed = fixed.replace(LEFT_DQUOTE,  b'"')
    fixed = fixed.replace(RIGHT_DQUOTE, b'"')
    fixed = fixed.replace(LEFT_SQUOTE,  b"'")
    fixed = fixed.replace(RIGHT_SQUOTE, b"'")

    with open(path, 'wb') as f:
        f.write(fixed)

    remaining = sum(fixed.count(s) for s in [MOJIBAKE, LEFT_DQUOTE, RIGHT_DQUOTE, LEFT_SQUOTE, RIGHT_SQUOTE, BOM])
    print(f'Fixed {path} — remaining problem sequences: {remaining}')
