import os, re
import pandas as pd
from glob import iglob as glob

SPEAKER_re = re.compile(r'Name: (.*) ; Gender: (.*) ; Race: \s*(.*) ; Dialogue: (.*)')

data_dir = "../data/output_clean"
channels = ["CNN", "FOX", "MSNBC"]

processed = []
for c in channels:
    d = os.path.join(data_dir, c)
    shows = os.listdir(d)
    
    for s in shows:
        episodes = os.path.join(d, s, "*.txt")
        for e in glob(episodes):
            with open(e) as inpt:
                lines = inpt.readlines()
                
                # Keep only those that have speaker annotations
                # Split into name, gender, race and dialogue
                for l in lines:
                    m = SPEAKER_re.match(l)
                    if m:
                        name, gender, race, dialogue = m.groups()
                        processed.append((c, s, e, name, gender, race, dialogue.strip()))

data = pd.DataFrame.from_records(processed, columns = ['channel', 'show', 'episode', 'name', 'gender', 'race', 'text'])

data.to_csv("../data/preprocessed.tsv", sep = "\t", index = False)