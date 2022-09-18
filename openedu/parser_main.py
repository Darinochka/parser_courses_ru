import json
import os.path
from parser_openedu import *


def main():
    file_path = config["saving_path"] + "openedu_courses.json"

    # сначала проверяем, существует ли файл и парсились ли данные до этого
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r') as f:
            data = json.load(f)
            old_num_course = data["count_courses"]
            new_num_course = get_count_courses()

        # если появились новые курсы
        if new_num_course > old_num_course:
            data["count_courses"] = new_num_course
            data["courses"] = parser_courses()
    
    else:
        with open(file_path, 'w') as f:
            data = dict()
            data["count_courses"] = get_count_courses()
            data["courses"] = parser_courses()
    
    with open(file_path, 'w') as f:
        json.dump(data, f)

if __name__=="__main__":
    main()