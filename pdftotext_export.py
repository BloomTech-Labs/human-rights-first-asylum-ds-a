# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %%
get_ipython().system('pip install pdfminer.six')


# %%
get_ipython().system('pip install nbconvert')


# %%
from pdfminer.high_level import extract_text


# %%
with open('/Users/edwinapalmer/Desktop/human-rights-first-asylim-ds-b/app/173103309-Benjamin-Luis-Garcia-A098-237-658-BIA-Jan-21-2011.pdf','rb') as f:
    text = extract_text(f)


# %%
print(text)


# %%



