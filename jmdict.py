from jamdict import Jamdict
from jamdict.jmdict import JMDEntry
import csv

jm = Jamdict()
poss = {}

POS_TABLE = {
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
    "'taru' adjective": "adj",
    "particle": "prt"
}

SIMPLE_POS = {
    "verb": ["vs", "u-v", "ru-v", "v"],
    "noun": ["n", "adj-no"],
    "adjective": ["adj", "adj-pn"],
    "adverb": ["adv"]
}

SPOS_TABLE = {}

for spos, pos in SIMPLE_POS.items():
    for p in pos:
        SPOS_TABLE[p] = spos

other = []
for desc, pos in POS_TABLE.items():
    if pos not in SPOS_TABLE:
        other.append(pos)

other_name = "/".join(other)
for o in other:
    SPOS_TABLE[o] = other_name

print(SPOS_TABLE)

def get_pos(word):
    r: JMDEntry = next(jm.lookup_iter(word).entries, None)
    if r is None:
        return []
    return set(sum((s.pos for s in r.senses), []))

def classify(word):
    entry: JMDEntry = next(jm.lookup_iter(word).entries, None)
    if entry is None:
        return []
    sense = entry.senses[0]
    pos_desc: str = sense.pos[0]
    pos: str = None
    for desc, pos in POS_TABLE.items():
        if pos_desc.startswith(desc):
            spos = SPOS_TABLE[pos]
            return [(spos, ";".join(s.text for s in sense.gloss))]

    raise Exception(f"Unknown POS {pos_desc}: {word}")


with open("n3.csv") as f:
    reader = csv.reader(f)
    next(reader)
    for _, kanji, kana, *_ in reader:
        word = kanji or kana
        pos = classify(word)
        for p, s in pos:
            if not p in poss:
                poss[p] = []
            poss[p].append(f"{word}-{s}")
print(poss)