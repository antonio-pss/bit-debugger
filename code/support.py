from settings import *


def import_image(*path, frmt='png', alpha=True):
    full_path = join(*path) + f'.{frmt}'
    return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()


def import_folder(*path):
    frames = []
    for folder_path, sub_folders, file_names in walk(join(*path)):
        for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
            full_path = join(folder_path, file_name)
            surf = pygame.image.load(full_path).convert_alpha()
            frames.append(surf)

    return frames


def audio_importer(*path):
    audio_dict = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            full_path = join(folder_path, file_name)
            audio_dict[file_name.split('.')[0]] = pygame.mixer.Sound(full_path)
    return audio_dict


def sql_importer(command):
    conn = psycopg2.connect('host=localhost dbname=windows user=postgres password=123456')
    cur = conn.cursor()
    cur.execute(command)
    records = cur.fetchall()
    columns = [column[0] for column in cur.description]
    return [dict(zip(columns, row)) for row in records]
