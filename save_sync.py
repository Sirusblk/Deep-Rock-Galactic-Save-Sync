#!/usr/bin/env python3

import configparser
import datetime
import os.path
import re
import shutil

from string import ascii_uppercase


CONFIG = configparser.ConfigParser()

def init_config():
    CONFIG['General'] = {}
    CONFIG.read('config.ini')
    if 'SteamPath' not in CONFIG['General']:
        find_steam_path()
    if 'WinStorePath' not in CONFIG['General']:
        find_winstore_path()

    find_steam_save_name()
    find_winstore_save_name()


def find_steam_path():
    for drive_letter in ascii_uppercase:
        path = drive_letter + ':\\Program Files (x86)\\Steam\\steamapps\\common\\Deep Rock Galactic\\FSD\\Saved\\SaveGames'
        path2 = drive_letter + ':\\SteamLibrary\\steamapps\\common\\Deep Rock Galactic\\FSD\\Saved\\SaveGames'
        if os.path.isdir(path):
            CONFIG['General']['SteamPath'] = path
            return True
        if os.path.isdir(path2):
            CONFIG['General']['SteamPath'] = path2
            return True

    return False


def find_steam_save_name():
    save_subfolder = CONFIG['General']['SteamPath']
    save_file_candidates = [f for f in os.listdir(save_subfolder) if f.endswith('.sav') and os.path.isfile(os.path.join(save_subfolder, f))]
    CONFIG['General']['SteamSaveName'] = find_save_name(save_subfolder, save_file_candidates)
    return True


def find_winstore_path():
    save_dir_pattern = '([0-F]){16}_([0-F]){32}'
    save_pattern = '([0-F]){32}'

    for drive_letter in ascii_uppercase:
        user = os.getlogin()
        general_path = drive_letter + ':\\Users\\' + user + '\\AppData\\Local\\Packages'

        if os.path.isdir(general_path):
            dev_candidates = [d for d in os.listdir(general_path) if d.startswith('CoffeeStainStudios.DeepRockGalactic_') and os.path.isdir(os.path.join(general_path, d))]
            dev_folder = os.path.join(general_path, dev_candidates[0], 'SystemAppData\\wgs')

            save_folder_candidates = [d for d in os.listdir(dev_folder) if re.match(save_dir_pattern, d) and os.path.isdir(os.path.join(dev_folder, d))]
            save_folder = os.path.join(dev_folder, save_folder_candidates[0])

            save_subfolder_candidates = [d for d in os.listdir(save_folder) if re.match(save_pattern, d) and os.path.isdir(os.path.join(save_folder, d))]
            save_subfolder = os.path.join(save_folder, save_subfolder_candidates[0])
            CONFIG['General']['WinStorePath'] = save_subfolder
            return True

    return False


def find_winstore_save_name():
    save_pattern = '([0-F]){32}'
    save_subfolder = CONFIG['General']['WinStorePath']

    save_file_candidates = [f for f in os.listdir(save_subfolder) if re.match(save_pattern, f) and os.path.isfile(os.path.join(save_subfolder, f))]
    CONFIG['General']['WinStoreSaveName'] = find_save_name(save_subfolder, save_file_candidates)
    return True


def find_save_name(save_subfolder, save_file_candidates):
    latest_modify_time = 0
    latest_save_file = ''
    for save_file in save_file_candidates:
        modify_time = os.stat(os.path.join(save_subfolder, save_file)).st_mtime

        if modify_time > latest_modify_time:
            latest_modify_time = modify_time
            latest_save_file = save_file

    return latest_save_file


def update_timestamps():
    CONFIG['General']['SteamSaveDate'] = get_modify_datetime(
        os.path.join(
            CONFIG['General']['SteamPath'],
            CONFIG['General']['SteamSaveName']
        )
    )
    CONFIG['General']['WinStoreSaveDate'] = get_modify_datetime(
        os.path.join(
            CONFIG['General']['WinStorePath'],
            CONFIG['General']['WinStoreSaveName']
        )
    )


def get_modify_datetime(filepath):
    if os.path.isfile(filepath):
        return datetime.datetime.fromtimestamp(os.stat(filepath).st_mtime).isoformat()

    print('Error: Cannot find modify time')
    return ''


def save_config():
    with open('config.ini', 'w') as configfile:
        CONFIG.write(configfile)


def backup_saves():
    backup_folder_name = 'backups'
    steam_folder_name = 'Steam'
    winstore_folder_name = 'WinStore'
    timestamp = datetime.datetime.today().strftime("%Y-%m-%dT%H.%M.%S")
    steam_backup_path = os.path.join(backup_folder_name, timestamp, steam_folder_name)
    winstore_backup_path = os.path.join(backup_folder_name, timestamp, winstore_folder_name)

    if not os.path.exists(steam_backup_path):
        os.makedirs(steam_backup_path)
    if not os.path.exists(winstore_backup_path):
        os.makedirs(winstore_backup_path)

    steam_save_backup_path = os.path.join(steam_backup_path, CONFIG['General']['SteamSaveName'])
    winstore_save_backup_path = os.path.join(winstore_backup_path, CONFIG['General']['WinStoreSaveName'])

    shutil.copy(
        os.path.join(CONFIG['General']['SteamPath'], CONFIG['General']['SteamSaveName']),
        steam_save_backup_path)
    shutil.copy(
        os.path.join(CONFIG['General']['WinStorePath'], CONFIG['General']['WinStoreSaveName']),
        winstore_save_backup_path)

    # Change modification time on save file backups
    if (CONFIG['General']['SteamSaveDate'] !=''):
        steam_save_mtime = datetime.datetime.fromisoformat(CONFIG['General']['SteamSaveDate']).timestamp()
        os.utime(steam_save_backup_path, times=(steam_save_mtime, steam_save_mtime))
    if (CONFIG['General']['WinStoreSaveDate'] !=''):
        winstore_save_mtime = datetime.datetime.fromisoformat(CONFIG['General']['WinStoreSaveDate']).timestamp()
        os.utime(winstore_save_backup_path, times=(winstore_save_mtime, winstore_save_mtime))


def main():
    init_config()
    update_timestamps()
    save_config()
    backup_saves()


if __name__ == '__main__':
    main()
