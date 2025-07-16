from jamdict import Jamdict
from jamdict.jmdict import JMDEntry
from dataclasses import dataclass
import csv
import re

jm = Jamdict()

POS_MAP = {
    "noun": "n",
    "adjectival nouns": "adj-no",
    "suru verb": "vs",
    "Godan verb": "u-v",
    "Ichidan verb": "ru-v",
    "adverb": "adv",
    "adjective": "adj",
    "pre-noun adjectival": "adj-pn",
    "interjection": "int",
    "conjunction": "conj",
    "expressions": "expr",
    "pronoun": "n",
    "verb": "v",
    "counter": "n",
    "numeric": "number",
    "prefix": "pref",
    "suffix": "suf",
    "'taru' adjective": "adj",
    "particle": "prt"
}

CAT_MAP = {
    "verbs": ["u-v", "ru-v", "v", "vs"],
    "nouns": ["n", "adj-no"],
    "adjectives": ["adj", "adj-pn"],
    "adverbs": ["adv"],
    "other": ["int", "conj", "expr", "number", "pref", "suf", "prt", "unknown"]
}

@dataclass
class JLPTWord:
    pos: str
    kanji: str
    kana: str
    meaning: str

def classify(word) -> tuple[str, JMDEntry]:
    entry: JMDEntry = next(jm.lookup_iter(word).entries, None)
    if entry is None:
        return "unknown", None
    sense = entry.senses[0]
    pos_desc: str = sense.pos[0]

    pos = next((pos for desc, pos in POS_MAP.items() if pos_desc.startswith(desc)), None)

    if pos is None:
        raise Exception(f"Unknown POS {pos_desc}: {word}")

    return pos, entry


def get_pos_words(fname: str) -> dict[str, list[JLPTWord]]:
    pos_words = { pos: [] for pos  in set(POS_MAP.values())}
    pos_words["unknown"] = []
    with open(fname) as f:
        reader = csv.reader(f)
        next(reader)
        for kanji, kana, meaning, _ in reader:
            word = kanji or kana
            pos, e = classify(word)

            if e is not None:
                gloss = e.senses[0].gloss
                count = min(len(gloss), 2)
                senses = [s.text for s in gloss[:count]]
                meaning = "; ".join(senses)

            pos_words[pos].append(
                JLPTWord(pos, kanji, kana, meaning)
            )
    return pos_words

NUM_TABLE = str.maketrans({
    chr(ord("0") + i): chr(ord("０") + i) for i in range(10)
})

def read_accents(fname: str):
    accent_map = {}
    with open(fname, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for kanji, kana, pitch in reader:
            pitch_map = accent_map.get(kanji, {})
            pitch_map[kana] = re.search(r"\d+", pitch).group(0)
            accent_map[kanji] = pitch_map
    return accent_map

def split_moras(kana: str):
    moras = []
    s = kana[0]
    for c in kana[1:]:
        if c in "ゃゅょャュョ":
            s += c
        else:
            moras.append(s)
            s = c
    moras += s
    return moras

if __name__ == "__main__":
    pos_words = get_pos_words("n2.csv")
    accents = read_accents("accents.txt")
    print('<html lang="ja">')
    print('''<head>
    <meta charset="UTF-8">
    <style>
        td {
            padding: .1em;
        }
        span {
            padding: 0 .1em;
            border: 1px grey;
        }
        .high {
            border-top-style: solid;
        }
        .low {
            border-bottom-style: solid;
        }
        .high + .low, .low + .high {
            border-left-style: solid;
        }
    </style>
    </head>''')
    print("<body>")
    for cat, pos_list in CAT_MAP.items():
        words: list[JLPTWord] = sum([pos_words[pos] for pos in pos_list], [])
        words.sort(key=lambda w: (w.kana, w.kanji))
        # print(cat.upper())
        print(f"<div>{cat.upper()}</div>")
        kanji_len = max(len(w.kanji) for w in words)
        kana_len = max(len(w.kana) for w in words) + 1
        n = len(words)
        n_len = len(str(n))
        print("<table>")
        for i, w in enumerate(words):
            index = str(i+1)
            moras = split_moras(w.kana)
            pitch_map = accents.get(w.kanji)
            pitch_str = "-"
            if pitch_map is not None:
                pitch = pitch_map.get(w.kana)
                if pitch is not None:
                    pitch_str = pitch
                    p = int(pitch)
                    n = len(moras)
                    if p == 0:
                        pitch_pattern = [0] + [1] * (n-1)
                    elif p == 1:
                        pitch_pattern = [1] + [0] * (n-1)
                    else:
                        pitch_pattern = [0] + [1] * (p-1) + [0] * (n-p)
            if pitch_pattern is None:
                kana = w.kana
            else:
                kana = "".join(f'<span class="{"high" if p == 1 else "low"}">{m}</span>' for m, p in zip(moras, pitch_pattern))
            # print(index_str + kanji_str, kana_str, pitch, w.meaning, sep="　")
            cells = "".join(f"<td>{t}</td>" for t in [index, w.kanji, kana, pitch_str, w.meaning])
            print(f"<tr>{cells}</tr>")
        print("</table>")
        print("</body>")
        print("</html>")
