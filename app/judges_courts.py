import pandas as pd
import numpy as np

def update_judges_table():
    """
    This function pulls information from multiple url's to create a 
<<<<<<< Updated upstream
    table pupulated with information on all immigration judges. This 
    table is saved in the current directory as 'jedges_courts.csv'. 
=======
    table populated with information on all immigration judges. This 
    table is saved in the current directory as 'judges_courts.csv'. 
>>>>>>> Stashed changes
    """
    def get_courts(data):
        """This is only a helper function"""
        courts = {i:str(j).split(' ')[-2] for i, j in 
                    zip(data[3]['State'], data[3]['Circuit assignment(s)']) 
                    if type(j) == str and i != 'District of Columbia'}

        for i, j in courts.items():
            if '0th' in j or '1th' in j:
                courts[i] = j[-5:-3]
            
            else:
                courts[i] = j[-4:-3]

        courts['District of Columbia'] = 'District of Columbia Circuit'

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

                states[i] = states[i] + ' ' + states[i + 1]
                states[i + 1] = ''
            
            if states[i].startswith('Northern'):
                states[i] = states[i] + ' ' + states[i + 2]
                states[i + 2] = ''
        
        while '' in states:
            states.remove('')

        tables[0] = states
        judges = tables[1:]

        for s, j in zip(states, judges):
            j['State'] = s

        df = pd.concat(tables[1:], ignore_index = True)
        df.rename(columns = {'Court Administrator':'court_admin',
                            'Immigration Judges':'judge',
                            'Address':'court_address',
                            'Court':'court_name', 
                            'State':'court_state'}, inplace = True)
        df.dropna(axis = 1, inplace = True)

        def get_circuit(state):
            if state in courts:
                return int(courts[state])

            if state == 'Northern Mariana Islands': 
                return 9
        
        
        def split_names(names):
            return names.split('  ')
        

        def split_address(address):
            return address.replace('  ', ',').split(',')


        def get_last_name(judge):
            return judge.split(',')[0]


        def get_first_name(judge):
            return judge.split(',')[1]


        def get_address(address_list):
            l = len(address_list)

            if l == 13: 
                return address_list[1]
            
            else: 
                return address_list[0]


        def get_city(address_list):
            l = len(address_list)

            if l == 3: 
                return address_list[-2]

            if l in range(4,8): 
                return address_list[-3]
            
            if l == 8: 
                return address_list[1]
            
            if l == 9 or l == 11 or l == 12: 
                return address_list[2]
            
            if l == 10 or l == 13:
                return address_list[3]


        def get_phone(address_list):
            l = len(address_list)

            if l == 3: 
                return None

            if l in range(4,8):
                return address_list[-1]

            if l == 8: 
                return address_list[3]
            
            if l == 9 or l == 11 or l == 12:
                return address_list[4]

            if l == 10 or l == 13:
                return address_list[5]


        def shorten_address(address):
            address = address.replace('Road', 'Rd')
            address = address.replace('Rd.', 'Rd')
            address = address.replace('Avenue', 'Ave')
            address = address.replace('Ave.', 'Ave')
            address = address.replace('Street', 'St')
            address = address.replace('St.', 'St')
            address = address.replace('Parkway', 'Pkwy')
            address = address.replace('Pkwy.', 'Pkwy')
            address = address.replace('Boulevard', 'Blvd')
            address = address.replace('Blvd.', 'Blvd')
            address = address.replace('Place', 'Pl')
            address = address.replace('Pl.', 'Pl')
            address = address.replace('Drive', 'Dr')
            address = address.replace('Dr.', 'Dr')
            address = address.replace('Turnpike', 'Tpke')
            address = address.replace('Tpke.', 'Tpke')
            address = address.replace('North', 'N')
            address = address.replace('N.', 'N')
            address = address.replace('East', 'E')
            address = address.replace('E.', 'E')
            address = address.replace('South', 'S')
            address = address.replace('S.', 'S')
            address = address.replace('West', 'W')
            address = address.replace('W.', 'W')

            return address

        df['court_circuit'] = df['court_state'].apply(get_circuit) 
        df['judge'] = df['judge'].apply(split_names)
        df['court_address'] = df['court_address'].apply(split_address)
        df['court_city'] = df['court_address'].apply(get_city)
        df['court_phone'] = df['court_address'].apply(get_phone)
        df['court_address'] = df['court_address'].apply(get_address)
        df['court_address'] = df['court_address'].apply(shorten_address)

        df = df.explode('judge', ignore_index=True)

        df['judge_last'] = df['judge'].apply(get_last_name)
        df['judge_first'] = df['judge'].apply(get_first_name)

        df.drop(columns='judge', inplace=True)
        
        cols = ['judge_last', 'judge_first', 'court_city', 
                'court_state', 'court_circuit', 'court_address', 
                'court_admin', 'court_phone']

        df = df[cols]

        return df


    url2 = 'https://www.justice.gov/eoir/eoir-immigration-court-listing#MP'
    tables = pd.read_html(url2)
    judges_courts = get_judges(tables)

    return judges_courts


def update_laws():
    """
    This function pulls information from the provided url and writes 
    'laws_filter.text' into the current directory. It is possible for 
    the layout of the website to change, in which case this function 
    will also need to be updated.
    """
    def cleanit(string):
        """This is only a helper function"""
        if 'Act ' in string:
            s = string[:string.find(' Act ')].strip()
            return s + ' Act'
        
        if 'Law ' in string:
            s = string[:string.find(' Law ')].strip()
            return s + ' Law'

        return string


    url ='https://en.wikipedia.org/wiki/List_of_United_States_immigration_laws'
    laws = pd.read_html(url)
    law = 'Name of legislation or case'

    laws = set(n for n in [cleanit(i) for i in laws[1][law] if type(i) == str] 
               if ' v. ' not in n)

    return laws