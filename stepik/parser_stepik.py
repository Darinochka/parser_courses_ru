import requests
import json
import toml
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from bs4 import BeautifulSoup
import numpy as np
from os.path import dirname, realpath, join
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

PROJECT_DIR = join(dirname(realpath(__file__)), "..")
CONFIG_PATH = join(PROJECT_DIR, "config.toml")
config = toml.load(CONFIG_PATH)

cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
browser = webdriver.Firefox(capabilities=cap, executable_path=config['geckodriver_path'])
browser.get("https://stepik.org")

def get_assesment(url):
    """
    Код для получения оценки курса
    url : ссылка на курс
    """
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    code_html = "course-promo-summary__average"
    score = soup.find('span', class_=code_html)

    if score is None:
        return np.nan
    return str(score.contents[0]).strip()

def get_last_page(file_path):
    """
    Возвращает последнюю страницу ("last_page")
    в файле file_path
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
        last_page = data["last_page"]
    return last_page

def check_new_page(page):
    """
    Проверяет наличие следующей странице после page
    """
    url = f"https://stepik.org/api/courses?page={page}"
    has_next = requests.get(url).json()['meta']['has_next']
    return has_next

def upd_last_page(file_path, page):
    """
    Обновляет последнюю страницу в файле, то есть ее номер
    и курсы которые появились на ней
    page : последняя страница
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

    url = f"https://stepik.org/api/courses?page={page}"
    courses = requests.get(url).json()['courses']
    ids = [course['id'] for course in courses]
    titles = [course['title'] for course in courses]
    langs = [course['language'] for course in courses]
    learners = [course['learners_count'] for course in courses]

    
    with open(file_path, 'r') as f:
        for i in range(len(ids)):
            try:
               if langs[i] == 'ru' and detect(titles[i]) == 'ru' and int(learners[i]) >= 1000:
                    curl = f"https://stepik.org/course/{ids[i]}/promo"
                    data["courses"].append({
                    "title": titles[i], 
                    "url": curl,
                    "score" : get_assesment(curl),
                    "number of students" : learners[i]
                })
            except LangDetectException:
                continue
        
    with open(file_path, 'w') as f:
        json.dump(data, f)

def pars_new_pages(file_path, page):
    """
    Парсит курсы начиная со страницы page, 
    а также записывает их в файл file_path вместе с последней
    страницей
    """
    with open(file_path,'r') as f:
        data = json.load(f)
        has_next = True
        courses = []

        while has_next:
            page += 1
            url = 'https://stepik.org/api/courses?page={}'.format(page)
            courses = requests.get(url).json()['courses']
            has_next = requests.get(url).json()['meta']['has_next']
            page_inf = [(course['id'], course['title'], course['language'], course['learners_count']) for course in courses]

            for i in page_inf:
                try:
                    if i[2] == 'ru' and detect(i[1]) == 'ru' and int(i[3]) >= 1000:
                        curl = f"https://stepik.org/course/{i[0]}/promo"
                        data["courses"].append({
                            "title": i[1], 
                            "url": curl,
                            "score" : get_assesment(curl),
                            "number of students" : i[3],
                        })
                        with open(file_path, 'w') as f:
                            data["last_page"] = page
                            json.dump(data, f)
                except LangDetectException:
                    continue

def first_pars(file_path):
    """
    Полностью парсит все страницы и записывает данные о курсах
    в файл. Также записывает последнюю распарсенную страницу.
    """
    data = {"last_page": 0, "courses": []}
    has_next = True
    page = 0
    while has_next:
        page += 1
        url = f"https://stepik.org/api/courses?page={page}"
        courses = requests.get(url).json()['courses']
        has_next = requests.get(url).json()['meta']['has_next']
        page_inf = [(course['id'], course['title'], course['language'], course['learners_count']) for course in courses]

        for i in page_inf:
            try:
                if i[2] == 'ru' and detect(i[1]) == 'ru' and int(i[3]) >= 1000:
                    curl = f"https://stepik.org/course/{i[0]}/promo"
                    data["courses"].append({
                        "title": i[1], 
                        "url": curl,
                        "score" : get_assesment(curl),
                        "number of students" : i[3],
                    })
                    with open(file_path, 'w') as f:
                        data["last_page"] = page
                        json.dump(data, f)
            except LangDetectException:
                pass