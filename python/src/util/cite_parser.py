# This class implements a simple key-based counter, often used
# for data exploration and wrangling.
# Chris Joakim, Microsoft

from src.util.counter import Counter

# STATES is used to filter the many citations to a managable set
STATES = {
    'ca': 'ca',
    'idaho': 'idaho',
    'me': 'me',
    'miss': 'miss',
    'neb': 'neb',
    'us': 'us',
    'wash': 'wash',
    'wa': 'wash',
    'wn': 'wash'
}  

class CiteParser:

    values_counter = Counter()  # used to observe facts about the data for __case_url logic

    def __init__(self):
        self.scrubbed_cite = None

    def parse(self, cite: str, file_name: str = None) -> str:
        """ Parse the given values into a URL string at https://static.case.law/ """
        concat_raw_values = "{}^{}".format(cite, file_name)
        self.increment(concat_raw_values)
        self.scrubbed_cite = self.scrub_cite(str(cite))
        url = None  # the return value for this method


        tokens = self.scrubbed_cite.split(' ')

        if len(tokens) == 3:
            dir = tokens[0].strip()
            state = self.translate_filter_state(tokens[1].strip())
            if state is not None:
                file = self.zero_pad_with_01_suffix(tokens[2].strip())
                if file_name is not None:
                    if '-' in file_name: # it has an -01, -02, ... suffix
                        pass
                    else:
                        file_name = "{}-01".format(file_name)
                    url = "https://static.case.law/{}/{}/cases/{}.json".format(
                        state, dir, file_name)
                else:
                    url = "https://static.case.law/{}/{}/cases/{}.json".format(
                        state, dir, file)
            
        elif len(tokens) == 4:
            # example url: https://static.case.law/wash-2d/58/cases/0569-01.json
            dir = tokens[0].strip()
            state = self.translate_filter_state(tokens[1].strip())
            if state is not None:
                dist = tokens[2].strip()
                file = self.zero_pad_with_01_suffix(tokens[3].strip())
                if file_name is not None:
                    if '-' in file_name: # it has an -01, -02, ... suffix
                        pass
                    else:
                        file_name = "{}-01".format(file_name)
                    url = "https://static.case.law/{}-{}/{}/cases/{}.json".format(
                        state, dist, dir, file_name)
                else:
                    url = "https://static.case.law/{}-{}/{}/cases/{}.json".format(
                        state, dist, dir, file)
        else:
            pass  # unknown format

        # capture the raw data and parsed url for analysis, then return the url
        self.increment("parsed | {} | {}".format(concat_raw_values, url))
        return url
    
    def scrub_cite(self, cite):
        """
        Scrub the cite string to remove extraneous characters
        and normalize to lowercase and stripped.
        """
        return cite.lower().replace('.', '').replace('(', '').replace(')', '').strip()
    
    def increment(self, key):
        CiteParser.values_counter.increment(key)

    def translate_filter_state(self, state):
        if state is not None:
            if state in STATES.keys():
                return STATES[state]
        
    def zero_pad_with_01_suffix(self, file):
        """
        Zero-pad the given number so that it has four digits,
        and append '-01' to the end.
        """
        if len(file) == 3:
            return '0{}-01'.format(file)
        elif len(file) == 2:
            return '00{}-01'.format(file)
        elif len(file) == 1:
            return '000{}-01'.format(file)
        else:
            return '{}-01'.format(file)
        