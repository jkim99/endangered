import requests
from collections import OrderedDict
import json
from bs4 import BeautifulSoup
from IPython import embed
import time
from googlesearch import search


DEBUG = False
SLEEP = 10
INFO_PARSE_KEY = {'Status': 'status',
                  'Population': 'population',
                  'Habitats': 'habitats',
                 }


class Species(object):
    def __init__(self, *args, **kwargs):
        self.more = []
        self.env = []
        self.habitats = None
        self.construct(*args, **kwargs)

    def construct(self,
                  data=None,  # type: list
                  common_name=None,  # type: str
                  sci_name=None,  # type: str
                  status=None  # type: str
                 ):
        if data:
            self.common_name = data[0]
            self.sci_name = data[1]
            self.status = data[2]
        else:
            self.common_name = common_name
            self.sci_name = sci_name
            self.status = status

    def update(self,
               data=None,  # type: dict
               common_name=None,  # type: str
               sci_name=None,  # type: str
               status=None,  # type: str
               population=None, # type: str
               habitats=None,  # type: str
               more=None,  # type: str
              ):
        if data:
            self.update(**data)

        else:
            if common_name:
                self.common_name = common_name
            if sci_name:
                self.sci_name = sci_name
            if status:
                self.status = status
            if population:
                self.population = population
            if habitats:
                self.habitats = habitats
            if more:
                self.more.append(more)


def debug(s):
    if DEBUG:
        print(s)

def remove_tags(s):
    return BeautifulSoup(s, features="lxml").get_text()

def parse_all_species(s):
    f_index = s.index('<table')
    e_index = s.index('</table>') + 8
    return s[f_index:e_index]

def parse_species(s, name):
    debug('--{}--'.format(name))

    info = {}

    for key in INFO_PARSE_KEY:
        debug("Finding {} for {}".format(key, name))
        z = remove_tags(s).replace("  ", "").split("\n")
        for x in z:
            if x is '' or 'CR':
                z.remove(x)

        for x in z:
            if x is '':
                z.remove(x)
        try:
            f = z.index(key)
            info[INFO_PARSE_KEY[key]] = z[f+1]
        except:
            debug("Couldn't find {} for {}".format(key, name))

    return info

def duckduckgo(
               species=None,  # type: Species
               search=None,  # type: str
              ):
    new_info = {}
    if search:
        for key in INFO_PARSE_KEY:
            r = requests.get(url='https://duckduckgo.com/api/{}+{}'.format(search, search))
            time.sleep(SLEEP)
            if r.status_code == 200:
                answer = r.json['answer']
                if not answer:
                    answer = 'unknown'
                new_info[INFO_PARSE_KEY[key]] = answer

    if species:
        for key in INFO_PARSE_KEY:
            r = requests.get(url='https://duckduckgo.com/api/{}+{}'.format(species.common_name, search))
            time.sleep(SLEEP)
            if r.status_code == 200:
                answer = r.json['answer']
                if not answer:
                    answer = 'unknown'
                new_info[INFO_PARSE_KEY[key]] = answer

    return new_info


def get_more(species):
    for spec in species:
        name = spec.strip().replace(' ', '-').lower().replace('\'', '-')
        url = 'https://www.worldwildlife.org/species/{}'.format(name)
        r = requests.get(url=url)

        if r.status_code == 200:
            new_info = parse_species(r.text, name) 
        else:
            debug("Could not find more info from {}".format(url))
            new_info = duckduckgo(search=spec)

        species[spec].update(new_info)
        species[spec].update({'more': url})

def main():
    print('This program uses info from www.worldwildlife.org')
    species = {}
    r = requests.get(url='http://www.worldwildlife.org/species/directory?direction=desc&sort=extinction_status')
    html_data = parse_all_species(r.text)

    table_data = [[cell.text for cell in row("td")]
                         for row in BeautifulSoup(html_data, features="lxml")("tr")]
    for data in table_data:
        if data:
            s = Species(data=data)
            species.update({s.common_name: s})

    get_more(species)
    # print('Finding more data on duckduckgo...')
    # for spec in species.values():
    #     spec.update(duckduckgo(species=spec))
    for spec in species.values():
        print(spec.__dict__)

    for spec in species.values():
        if spec.habitats:
            for url in search(spec.habitats, stop=3):
                spec.env.append(url)
        # else:
        #     r = requests.get(url='http://duckduckgo.com/api/{}+habitats'.format(spec.common_name.replace(' ', '+')))
        #     for url in search(r.json['answer'], stop=3):
        #         spec.env.append(url)
    for spec in species.values():
        print(spec.__dict__)

if __name__ == '__main__':
    main()
