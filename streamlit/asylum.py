import streamlit as st

import numpy as np
import pandas as pd

# SETUP
st.set_page_config(layout="wide")
st.title('Human Rights First Asylum')
st.markdown('### State of Aggregated Data')
st.markdown('---')
df: pd.DataFrame

# READ-IN CSV
df = (
    pd.read_csv('cases.csv')
      .fillna(value='')
      .set_index('date')
      .sort_index(ascending=False)
)

df.index = pd.to_datetime(df.index)
df = df.drop(['filename'], axis=1)

# UTIL
def getUnique(col):
    lsts = [a.split('; ') for a in df[col]]
    items = set([
        a
        for lst in lsts
        for a in lst
    ])
    items.discard('')
    return items

col1, col2 = st.beta_columns(2)

# UNIQUE TAGS IN EACH COLUMN
judges = getUnique('panel_members')
outcomes = getUnique('outcome')
countries = getUnique('country_of_origin')
application = getUnique('application')
protected_grounds = getUnique('protected_grounds')
based_violence = getUnique('based_violence')
keywords = getUnique('keywords')
references = getUnique('references')

# SIDEBAR
judge = st.sidebar.multiselect('BIA JUDGES: ', tuple(judges))
country = st.sidebar.multiselect('APPLICANT\'S COUNTRY OF ORIGIN: ',
                        tuple(countries))
applying = st.sidebar.multiselect('APPLYING FOR: ', tuple(application))

pg = st.sidebar.multiselect('APPLICANT\'S PROTECTED GROUNDS: ',
                    tuple(protected_grounds))
bv = st.sidebar.multiselect('VIOLENCE TYPE: ',
                    tuple(based_violence))
keyword = st.sidebar.multiselect('KEYWORDS: ', tuple(keywords))
reference = st.sidebar.multiselect('REFERENCES: ', tuple(references))

ref_ = {
    'Matter of AB, 27 I&N Dec. 316 (A.G. 2018)': 'Matter of AB',
    'Matter of L-E-A-, 27 I&N Dec. 581 (A.G. 2019)': 'Matter of L-E-A-'
}

ref = [ref_[r] for r in reference]

# DISPLAY CONDITIONS
display_df = df[
    df['panel_members'].str.contains('|'.join(judge))
    & df['country_of_origin'].str.contains('|'.join(country))
    & df['keywords'].str.contains('|'.join(keyword))
    & df['protected_grounds'].str.contains('|'.join(pg))
    & df['based_violence'].str.contains('|'.join(bv))
    & df['application'].str.contains('|'.join(applying))
    & df['references'].str.contains('|'.join(ref))
]

graphable_fields = [
    'outcome', 'country_of_origin', 
    'protected_grounds', 'based_violence',
    'references', 'panel_members', 'sex_of_applicant', 
    'year'
]

# UTIL
def getCount(col, normalize=False):
    if col == 'year':
        return display_df.index.year.value_counts()

    lsts = [a.split('; ') for a in display_df[col]]
    items = [
        a
        for lst in lsts
        for a in lst
    ]
    return pd.Series(items, name=col).value_counts(normalize=normalize)

# DISPLAYS
with col2:
    to_graph = st.selectbox('FIELD TO GRAPH: ', graphable_fields)
    st.write(f'Total Number of Cases Represented: {len(display_df)}')

with col1:
    st.bar_chart(getCount(to_graph), 
                 width=460, 
                 use_container_width=False)

display_df
