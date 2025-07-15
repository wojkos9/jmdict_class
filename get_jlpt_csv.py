import pandas as pd
import sys

def get_level_csv(level: str):
    word_dfs = pd.read_html(f"https://en.wiktionary.org/wiki/Appendix:JLPT/{level.upper()}")
    level_df = pd.concat(word_dfs, ignore_index=True)
    level_df.to_csv(f"{level}.csv", index=False)

if __name__ == "__main__":
    get_level_csv(sys.argv[1])