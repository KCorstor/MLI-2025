def decrypt_message(ciphertext, shift):
    decrypted = []
    for char in ciphertext:
        if char.isalpha():
            shift_char = chr(((ord(char) - 65 - shift) % 26) + 65)
            decrypted.append(shift_char)
        else:
            decrypted.append(char)
    return f"Unencrypted message: {''.join(decrypted)}"
