import collections
import os


class ShannonFanoNode:
    def __init__(self):
        self.symbol = None
        self.left = None
        self.right = None
        self.code = ''


def shannon_fano_tree(symbols, frequencies):
    if len(symbols) == 0:
        return None

    if len(symbols) == 1:
        node = ShannonFanoNode()
        node.symbol = symbols[0]
        return node

    total_sum = sum(frequencies[s] for s in symbols)
    partial_sum = 0

    for i in range(len(symbols)):
        partial_sum += frequencies[symbols[i]]
        if partial_sum >= total_sum / 2:
            break

    left_symbols = symbols[:i + 1]
    right_symbols = symbols[i + 1:]

    node = ShannonFanoNode()
    node.left = shannon_fano_tree(left_symbols, frequencies)
    node.right = shannon_fano_tree(right_symbols, frequencies)

    return node


def build_shannon_fano_codes(root, prefix, result):
    if root is None:
        return

    if root.symbol is not None:
        result[root.symbol] = prefix

    build_shannon_fano_codes(root.left, prefix + '0', result)
    build_shannon_fano_codes(root.right, prefix + '1', result)


def encode(text, codes):
    return ''.join(codes[byte] for byte in text)


def decode(encoded_text, root):
    decoded_bytes = bytearray()
    current_node = root

    for bit in encoded_text:
        if bit == '0':
            current_node = current_node.left
        elif bit == '1':
            current_node = current_node.right

        if current_node.left is None and current_node.right is None:
            decoded_bytes.append(current_node.symbol)
            current_node = root

    return bytes(decoded_bytes)


def compress_file(input_file, output_file):
    with open(input_file, 'rb') as file:
        text = file.read()

    frequencies = collections.Counter(text)
    symbols = sorted(frequencies, key=frequencies.get, reverse=True)

    root = shannon_fano_tree(symbols, frequencies)
    codes = {}
    build_shannon_fano_codes(root, '', codes)
    encoded_text = encode(text, codes)

    encoded_data = bytearray()
    padded_info = 8 - len(encoded_text) % 8
    encoded_text += '0' * padded_info

    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i + 8]
        encoded_data.append(int(byte, 2))

    with open(output_file, 'wb') as file:
        file.write(len(codes).to_bytes(2, 'big'))  # Записываем кол-во уникальных символов
        file.write(padded_info.to_bytes(1, 'big'))  # Записываем кол-во добавочных битов
        for symbol in codes:
            file.write(symbol.to_bytes(1, 'big'))
            code_len = len(codes[symbol])
            file.write(code_len.to_bytes(1, 'big'))
            file.write(int(codes[symbol], 2).to_bytes((code_len + 7) // 8, 'big'))
        file.write(encoded_data)


def decompress_file(input_file, output_file):
    with open(input_file, 'rb') as file:
        len_codes = int.from_bytes(file.read(2), 'big')  # Читаем кол-во уникальных символов
        padded_info = int.from_bytes(file.read(1), 'big')  # Читаем кол-во добавочных битов

        codes = {}
        reverse_codes = {}
        for _ in range(len_codes):
            symbol = file.read(1)[0]
            code_len = int.from_bytes(file.read(1), 'big')
            code = int.from_bytes(file.read((code_len + 7) // 8), 'big')
            bin_code = bin(code)[2:].rjust(code_len, '0')
            codes[symbol] = bin_code
            reverse_codes[bin_code] = symbol

        encoded_data = file.read()

    bit_string = ''.join(f'{byte:08b}' for byte in encoded_data)
    bit_string = bit_string[:-padded_info]

    root = ShannonFanoNode()

    for symbol, code in reverse_codes.items():
        current_node = root
        for bit in code:
            if bit == '0':
                if current_node.left is None:
                    current_node.left = ShannonFanoNode()
                    current_node = current_node.left
            else:
                if current_node.right is None:
                    current_node.right = ShannonFanoNode()
                current_node = current_node.right
        current_node.symbol = symbol

    decoded_bytes = decode(bit_string, root)

    with open(output_file, 'wb') as file:
        file.write(decoded_bytes)


if __name__ == "__main__":
    choice = input("Введите 'c' для сжатия и 'd' для разархивации: ").strip().lower()

    if choice == 'c':
        input_file = input("Введите путь к исходному файлу: ").strip('\"')
        output_file = input("Введите путь для сохранения сжатого файла, включая имя файла: ").strip('\"')
        compress_file(input_file, output_file)
        print("Сжатие завершено.")
    elif choice == 'd':
        input_file = input("Введите путь к сжатому файлу: ").strip('\"')
        output_file = input("Введите путь для сохранения разархивированного файла, включая имя файла: ").strip('\"')
        decompress_file(input_file, output_file)
        print("Разархивация завершена.")
    else:
        print("Неверный выбор.")