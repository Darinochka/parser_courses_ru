from bs4 import BeautifulSoup
import requests
from langdetect import detect
import toml
import json
from os.path import dirname, realpath, join

PROJECT_DIR = join(dirname(realpath(__file__)), "..")
CONFIG_PATH = join(PROJECT_DIR, "config.toml")
config = toml.load(CONFIG_PATH)

#erfe
def write_courses(file_path, soup, begin_course=0):
    """ 
    Записывает курсы из soup в файл file_path.json
    начиная с begin_course курса
    """
    courses = []
    for j in range(begin_course, len(soup)):
        cdesc = soup[j].get_text() # description of the course

        if detect(cdesc[0:cdesc.find('(')-1]) == 'ru':
            try:
                ctitle = cdesc.split('(')[0].strip()
                curl = f"https://www.coursera.org{soup[j].get('href')}"
                cauthor = cdesc.split('(')[1][:-1].strip()

                courses.append({
                    "title": ctitle, 
                    "url" : curl, 
                    "author": str(cauthor)
                })
            except:
                continue

    if courses: # если не пустой
        courses_to_json(file_path, courses)

def courses_to_json(file_path, courses: dict):
    """
    Дописывает в файл file_path.json курсы
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

        try:
            for course in courses:
                data["courses"].append(course)
        except KeyError:
            data["courses"] = courses
    
        with open(file_path, 'w') as fw:
            json.dump(data, fw)

def get_soup_courses(page: int):
    """
    Возвращает soup курсов на странице page
    """
    url = "https://www.coursera.org/directory/courses?page=" + str(page)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # код для выделения cписка курсов на странице
    code_html = "MuiTypography-root MuiLink-root MuiLink-underlineHover css-19sqvu6 MuiTypography-colorPrimary"
    st = soup.find_all('a', class_=code_html)
    return st

def get_count_pages():
    """
    Возвращает количество страниц с курсами
    """
    url = "https://www.coursera.org/directory/courses"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # код для полосы прокрутки курсов по их номеру
    code_html = "MuiTypography-root MuiLink-root MuiLink-underlineHover box number css-bu128x MuiTypography-colorPrimary"
    count_pages = int(soup.find_all('a',class_=code_html)[-1].get_text())
    return count_pages
