def decimal_to_alphabet(value):
    buffer = ""

    while value > 0:
        remainder = (value - 1) % 26
        letter = chr(65 + remainder)
        buffer = letter + buffer
        value = (value - 1) // 26
    return buffer


def alphabet_to_decimal(value):
    result = 0
    for letter in value:
        result *= 26
        result += ord(letter) - 65 + 1
    return result


if __name__ == "__main__":
    assert decimal_to_alphabet(1) == "A", decimal_to_alphabet(1)
    assert decimal_to_alphabet(26) == "Z", decimal_to_alphabet(26)
    assert decimal_to_alphabet(26 + 1) == "AA", decimal_to_alphabet(26 + 1)
    assert decimal_to_alphabet(26 * 2) == "AZ", decimal_to_alphabet(26 * 2)
    assert decimal_to_alphabet(26 * 2 + 1) == "BA", decimal_to_alphabet(26 * 2 + 1)
    for i in range(1, 100000):
        alpha = decimal_to_alphabet(i)
        decimal = alphabet_to_decimal(alpha)
        assert i == decimal, f"i='{i}', alpha='{alpha}', decimal='{decimal}'"
