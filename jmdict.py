from jamdict import Jamdict
from jamdict.jmdict import JMDEntry
from dataclasses import dataclass
import csv

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
            pitch_map[kana] = pitch.split(",")[0]
            accent_map[kanji] = pitch_map
    return accent_map

def split_moras(kana: str):
    moras = []
    s = kana[0]
    for c in kana[1:]:
        if c in "ゃゅょャュョ":
            s += c
        else:
            moras += s
            s = c
    moras += s
    return moras

if __name__ == "__main__":
    pos_words = get_pos_words("n2.csv")
    accents = read_accents("accents.txt")
    for cat, pos_list in CAT_MAP.items():
        words: list[JLPTWord] = sum([pos_words[pos] for pos in pos_list], [])
        words.sort(key=lambda w: (w.kana, w.kanji))
        print(cat.upper())
        kanji_len = max(len(w.kanji) for w in words)
        kana_len = max(len(w.kana) for w in words)
        n = len(words)
        n_len = len(str(n))
        for i, w in enumerate(words):
            index_jap = str(i+1).translate(NUM_TABLE)
            index_str = index_jap.ljust(n_len, "　") + "　"
            kanji_str = w.kanji.ljust(kanji_len, "　")
            kana_str = w.kana.ljust(kana_len, "　")
            moras = "-".join(split_moras(w.kana))
            pitch_map = accents.get(w.kanji)
            if pitch_map is not None:
                pitch = pitch_map.get(w.kana)
            else:
                pitch = "-"
            print(index_str + kanji_str, kana_str, moras, pitch, w.meaning, sep="　")
        print()
