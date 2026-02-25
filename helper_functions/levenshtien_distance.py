def levenshtein_distance(encoding1: str, encoding2: str) -> int:
    m, n = len(encoding1), len(encoding2)

    # Ensure encoding1 is the longer string (to use less memory)
    if n > m:
        encoding1, encoding2 = encoding2, encoding1
        m, n = n, m

    # Only keep two rows: previous and current
    previous_row = list(range(n + 1))
    current_row = [0] * (n + 1)

    for i in range(1, m + 1):
        current_row[0] = i
        for j in range(1, n + 1):
            cost = 0 if encoding1[i - 1] == encoding2[j - 1] else 1
            current_row[j] = min(
                previous_row[j] + 1,      # deletion
                current_row[j - 1] + 1,   # insertion
                previous_row[j - 1] + cost  # substitution
            )
        # Swap rows
        previous_row, current_row = current_row, previous_row

    return previous_row[n]

