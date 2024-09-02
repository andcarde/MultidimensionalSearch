
# Characters Test

unicode_chars = set(chr(i) for i in range(0x110000))

upal = 0
upnal = 0
upnal_chars = ''
nupal = 0
nupnal = 0
surrogate = 0
try:
    for i, char in enumerate(unicode_chars):
        '''
        string += char
        if (i + 1) % 3 == 0:
            print(string)
            string = ''
            if (i + 1) % 9 == 0:
                print('\n')
        '''
        if char.isupper() and char.isalpha():
            # print(f'Upper Alpha: {char}')
            upal += 1
        elif char.isupper() and not char.isalpha():
            upnal += 1
            upnal_chars += char
            encode1 = char.encode('utf-8', 'ignore')
            encode2 = f'{ord(char):06X}'
            print(f'[WARNING] Char {upnal}: {char} Encode 1: {encode1} Encode 2: {encode2}')
        elif not char.isupper() and char.isalpha():
            # print(f'Not Upper Alpha: {char}')
            nupal += 1
        else:
            if ord(char) in range(0x00D800, 0x00E000):
                surrogate += 1
                encode1 = char.encode('utf-8', 'ignore')
                encode2 = f'{ord(char):05X}'
                # print(f'Surrogate {surrogate}: {encode1}, {encode2}')
            else:
                # print(f'Not Upper Not Alpha: {char}')
                pass
            nupnal += 1
except Exception as e:
    print(f'Exception: {str(e)}')
    print(f'Evaluated characters: {i + 1}')
print(f'Good Ending. Evaluated characters: {i + 1}')
print(f'Upper Alpha Amount: {upal}')
print(f'Upper Not Alpha Amount: {upnal}')
print(f'Not Upper Alpha Amount: {nupal}')
print(f'Not Upper Not Alpha Amount: {nupnal}')
checked = upal + upnal + nupal + nupnal
print(f'Characters Unicode Amount: {len(unicode_chars)}')
print(f'Characters Checked: {checked}')
print(f'Characters Not Checked: {len(unicode_chars) - checked}')
print(f'Characters Theoretically Possible: {16 ** 5 + 16 ** 4}')
print(f'Upper Not Alpha Characters: {upnal_chars}')

# Ejemplo de caracteres no alfabéticos que son mayúsculas

# chars = ['𝚨', 'Ⅎ', 'ᵁ', '𝒜', '₩', 'Ϯ', '⅛', '₠', 'ℤ', '✖', '➤']  # Agrega otros caracteres si es necesario
chars = [
    'Ⓡ', 'Ⓝ', 'Ⅹ', 'Ⓢ', 'Ⓨ', '🄹', '🆄', '🅞'
]

for char in chars:
    encode1 = char.encode('utf-8', 'ignore')
    encode2 = f'U+{ord(char):04X}'
    # print(f"Character: {char} Encode 1: {encode1} Encode 2: {encode2}")
    print(f"Character: {char}, isalpha: {char.isalpha()}, isupper: {char.isupper()},"
          f" not isalpha and isupper: {not char.isalpha() and char.isupper()}")