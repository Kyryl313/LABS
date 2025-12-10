import re

def generate_pairs(line):
    words = re.findall(r'\b[^\W_]+\b', line.lower(), flags=re.UNICODE)

    for i, word in enumerate(words):

        for j in range(len(word) - 1):
            yield word[j:j+2]

        if i < len(words) - 1:
            next_word = words[i + 1]
            if not (word.endswith('у') and next_word.startswith('н')):
                if word and next_word:
                    yield word[-1] + next_word[0]

def get_unique_first_three(generator):
    seen = []
    for pair in generator:
        if pair not in seen:
            seen.append(pair)
        if len(seen) == 3:
            break
    return seen


def main():
    filename = "laba_9.txt"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    print(f"Рядок {idx}: (пустий)")
                    continue
                gen = generate_pairs(line)
                first_three = get_unique_first_three(gen)
                print(f"Рядок {idx}: {first_three}")

    except FileNotFoundError:
        print(f"Файл '{filename}' не знайдено! Поклади laba_9.txt у ту ж папку.")


if __name__ == "__main__":
    main()
