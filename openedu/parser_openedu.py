from bs4 import BeautifulSoup
import requests
import itertools 
import urllib.request
import toml
from os.path import dirname, realpath, join

PROJECT_DIR = join(dirname(realpath(__file__)), "..")
CONFIG_PATH = join(PROJECT_DIR, "config.toml")
config = toml.load(CONFIG_PATH)


def get_count_courses():
    """
    Возвращает количество курсов
    """
    url = "https://openedu.ru/course/"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    count_courses = soup.find('span',{'id': 'courses-found'}).get_text()
    count_courses = int(''.join(itertools.filterfalse(str.isalpha, count_courses)))
    return count_courses

def parser_courses():
    """
    Парсит страницу с курсами и возвращает dict курсов
    """
    soap = str(urllib.request.urlopen("https://openedu.ru/course/").read(),'utf-8')

    gr = soap.find(";\n  GROUPS")
    cs = soap.find('COURSES')
    unv = soap.find('UNIVERSITIES')

    dict_full = eval(str(soap[unv-1:gr]).translate({ord("'"): None})[15:])
    dict_uni = {} 
    for j in dict_full:
        dict_uni[j] = dict_full[j]['abbr']

    soap = soap[cs:unv].split(',')

    courses = []
    for line in soap:
        if '"title"' in line or '"url"' in line or '"uni"' in line:
            courses.append(line)
    courses[0] = courses[0].replace("COURSES = {", ' ')

    newcour = []
    for cs, j in enumerate(courses[::3]):
        courses[3*cs] = j[j.find('{') + 1 : ]
        newcour.append({
            "title": courses[3*cs][10:-1],
            "url": 'https://openedu.ru' + courses[3*cs + 2][9:-1],
            "author": dict_uni.get(courses[3*cs + 1][9:-1])
        })

    return newcour
