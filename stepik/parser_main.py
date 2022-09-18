from parser_stepik import get_last_page, check_new_page, upd_last_page, pars_new_pages, first_pars, config
import os.path

def main():
    file_path = config["saving_path"] + "stepik_courses.json"

    # сначала проверяем, существует ли файл и парсились ли данные до этого
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        # получаем последнюю распарсенную страницу
        page = get_last_page(file_path)
        if check_new_page(page): # если существует новая после текущей
            upd_last_page(file_path, page)
            pars_new_pages(file_path, page)
        else:
            upd_last_page(file_path, page)
    else:
        first_pars(file_path) 

if __name__ == "__main__":
    main()