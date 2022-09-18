from parser_coursera import *
import os.path

def check_new_courses(file_path, last_page):
    """
    Ищет новые курсы на последней странице и если они появились
    добавляет их в файл file_path
    """
    with open(file_path,'r') as f:
        data = json.load(f)
        last_course = data["courses"][-1]

    soup = get_soup_courses(last_page)

    for ncourse in range(len(soup)):
        cdesc = soup[ncourse].get_text()
        ctitle = cdesc.split('(')[0].strip()
        curl = f"https://www.coursera.org{soup[ncourse].get('href')}"
        cauthor = cdesc.split('(')[1][:-1].strip()

        curr_course = {
            "title": ctitle, 
            "url" : curl, 
            "author": str(cauthor)
        }
        if curr_course == last_course:
            break;

    write_courses(file_path, soup, ncourse+1)

def check_new_pages(file_path, new_count, old_count):
    """
    Случай, когда появились новые страницы.
    Тогда надо каждую страницу парсить и из нее добавлять новые курсы в файл
    сохранив при этом остальные
    """
    if new_count > old_count:
        for i in range(old_count+1, new_count+1):
            soup = get_soup_courses(i)
            write_courses(file_path, soup)

def parser_new_courses(file_path, old_count):
    """
    Парсит новые курсы\страницы.
    Последняя распарсенная страница old_count, 
    а запись идет в файл file_path
    """
    # проверяем наличие новых курсов на последней странице
    check_new_courses(file_path, old_count)

    # проверяем наличие новых страниц
    new_count = get_count_pages()
    check_new_pages(file_path, new_count, old_count)

    # меняем номер последней страницы
    with open(file_path,'r') as f:
        data = json.load(f)
        data["count_pages"] = new_count

        with open(file_path, 'w') as fw:
            json.dump(data, fw)

def main():
    file_path = config["saving_path"] + "coursera_courses.json"

    # сначала проверяем, существует ли файл и парсились ли данные до этого
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        # получаем последнюю страницу, которую мы знаем
        with open(file_path, 'r') as f:
            data = json.load(f)
            old_count = data["count_pages"]
            parser_new_courses(file_path, old_count)
    else:
        # файл не существует или пустой, значит надо парсить все страницы
        count_pages = get_count_pages()
        with open(file_path, 'w') as f:
            json.dump({"count_pages": count_pages}, f)
        
        for i in range(1, count_pages+1):
            soup = get_soup_courses(i)
            write_courses(file_path, soup)

if __name__ == "__main__":
    main()
