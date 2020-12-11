import spacy
import pandas as import pd

nlp = spacy.load('en_core_web_lg')
text = ()
doc = nlp(text)

# Get the entities, labels and explanation to the labels
table = []
for ent in doc.ents:
    table.append([ent.text,ent.label_,spacy.explain(ent.label_)])
    
# Creat a dataframe from the list created above
df2 = pd.DataFrame(table, columns=['Entity', 'Label','Label_Description']).sort_values(by=['Label'])
print(df2.shape)

# To filter for location, person, date and org
df3= df2[df2['Label'].isin(['GPE','ORG','PERSON','DATE'])]
print(df3.shape)

df4=df3.drop_duplicates(subset=None, keep='first',inplace= False)
print(df4.shape)
df4