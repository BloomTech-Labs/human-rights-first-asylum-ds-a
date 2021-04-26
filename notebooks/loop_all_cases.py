"""Returns list of cases mentioned in a given .txt document"""
import io, spacy

# Load all cases into a list, from a list of all of the cases' .txt files
case_names = []
with open('all_names.txt', encoding='utf8') as f:
    for line in f:
        case_names.append(line.strip())
nlp = spacy.load("en_core_web_sm")

# Loop over all cases
for m in range(0, len(case_names)):    
    print(case_names[m])
    full_text = ""
    with open(case_names[m], encoding='utf8') as f:
        for line in f:
            full_text+= line.strip() + ' '
    full_text = nlp(full_text)