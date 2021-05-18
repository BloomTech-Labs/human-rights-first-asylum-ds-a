import pandas as pd
import numpy as np

def update_judges_table():
    """
    This function pulls information from multiple url's to create a table pupulated with information on all immigration judges. This table is saved in the current directory as 'jedges_courts.csv'. 
    """

    def get_courts(data):
        """This is inly a helper function"""
        courts = {i:str(j).split(' ')[-2] for i, j in 
                    zip(data[3]['State'], data[3]['Circuit assignment(s)']) if type(j) == str and i != 'District of Columbia'}

        for i, j in courts.items():
            if 'st' in j or 'nd' in j or 'rd' in j:
                courts[i] = j[-4:-1]

            elif '0th' in j or '1th' in j:
                courts[i] = j[-5:-1]

            elif 'th' in j:
                courts[i] = j[-4:-1]

        courts['District of Columbia'] = 'District of Columbia Circuit'

        # Following code saves a file to current directory, 
        # not necessary if only updating the judges table
        # 
        # with open('circuits_by_state_dict.csv', 'w') as f:
        #     f.write(f"{courts}")
        
        return courts
    

    url = 'https://en.wikipedia.org/wiki/United_States_courts_of_appeals'
    data = pd.read_html(url)
    courts = get_courts(data)

    def get_judges(tables):
        """This is only a helper function"""
        for i in tables:
            i.columns = i.iloc[0].values
            i.drop(0, inplace=True)
            i.reset_index(drop=True)

        df = tables[0]

        states = df.columns[0].replace('  ',' ').replace('|', '').split()

        for i in range(len(states)):
            
            if states[i].startswith('New') \
            or states[i].startswith('North') \
            or states[i].startswith('South') \
            or states[i].startswith('Puerto'):

                states[i] = states[i] + ' ' + states[i+1]
                states[i+1] = ''
            
            if states[i].startswith('Northern'):
                states[i] = states[i] + ' ' + states[i+2]
                states[i+2] = ''
        
        while '' in states:
            states.remove('')

        tables[0] = states

        judges = tables[1:]

        for s, j in zip(states, judges):
            j['State'] = s

        df = pd.concat(tables[1:], ignore_index=True)

        df.rename(columns = {'Court Administrator':'court_admin',
                            'Immigration Judges':'judges',
                            'Address':'court_address',
                            'Court':'court_name', 
                            'State':'court_state'}, inplace=True)

        df.dropna(axis=1, inplace=True)

        for i in range(len(df)):
            s = df.court_state[i] 
            if s in courts:
                df['court_circuit'] = courts[s]

        def jnames(names):
            return names.split('  ')

        df['judges'] = df['judges'].apply(jnames)

        return df
    

    url2 = 'https://www.justice.gov/eoir/eoir-immigration-court-listing#MP'
    tables = pd.read_html(url2)
    
    judges_courts = get_judges(tables)
    judges_courts.to_csv('judges_courts.csv', index=False)


def update_laws():
    """
    This function pulls information from the provided url and writes 'laws.text' into the current directory. 
    It is possible for the layout of the website to change, in which case this function will also need to be updated.
    """
    url ='https://en.wikipedia.org/wiki/List_of_United_States_immigration_laws'
    laws = pd.read_html(url)

    def cleanit(string):
        """This is only a helper function"""
        if 'Act ' in string:
            s = string[:string.find(' Act ')].strip()
            return s + ' Act'
        
        if 'Law ' in string:
            s = string[:string.find(' Law ')].strip()
            return s + ' Law'

        return string


    law = 'Name of legislation or case'

    laws = set(n for n in [cleanit(i) for i in laws[1][law] if type(i) == str] 
               if ' v. ' not in n)

    # Following code saves current immigration laws to current directory as
    # plain text, might need to change this if it is going into a db
    with open('immigration_laws.txt', 'w') as f:
        f.write(f'{laws}')