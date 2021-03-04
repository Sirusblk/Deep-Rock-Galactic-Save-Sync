#!/usr/bin/env python3

import configparser
import os.path
import re

from string import ascii_uppercase


class SaveSyncer():
    def __init__(self):
        self.config = configparser.ConfigParser()

        self.config['General'] = {}
        self.config.read('config.ini')
        if 'SteamPath' not in self.config['General']:
            self.find_steam_path()
        if 'SteamSaveName' not in self.config['General']:
            self.find_steam_save_name()
        if 'WinStorePath' not in self.config['General']:
            self.find_winstore_path()
        if 'WinStoreSaveName' not in self.config['General']:
            self.find_winstore_save_name()


    def find_steam_path(self):
        for drive_letter in ascii_uppercase:
            path = drive_letter + ':\\Program Files (x86)\\Steam\\steamapps\\common\\Deep Rock Galactic\\FSD\\Saved\\SaveGames'
            path2 = drive_letter + ':\\SteamLibrary\\steamapps\\common\\Deep Rock Galactic\\FSD\\Saved\\SaveGames'
            if os.path.isdir(path):
                self.config['General']['SteamPath'] = path
                return True
            if os.path.isdir(path2):
                self.config['General']['SteamPath'] = path2
                return True

        return False


    def find_steam_save_name(self):
        save_subfolder = self.config['General']['SteamPath']
        save_file_candidates = [f for f in os.listdir(save_subfolder) if f.endswith('.sav') and os.path.isfile(os.path.join(save_subfolder, f))]
        self.config['General']['SteamSaveName'] = self.find_save_name(save_subfolder, save_file_candidates)
        return True


    def find_winstore_path(self):
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
                self.config['General']['WinStorePath'] = save_subfolder
                return True

        return False


    def find_winstore_save_name(self):
        save_pattern = '([0-F]){32}'
        save_subfolder = self.config['General']['WinStorePath']

        save_file_candidates = [f for f in os.listdir(save_subfolder) if re.match(save_pattern, f) and os.path.isfile(os.path.join(save_subfolder, f))]
        self.config['General']['WinStoreSaveName'] = self.find_save_name(save_subfolder, save_file_candidates)
        return True


    def find_save_name(self, save_subfolder, save_file_candidates):
        latest_modify_time = 0
        latest_save_file = ''
        for save_file in save_file_candidates:
            modify_time = os.stat(os.path.join(save_subfolder, save_file)).st_mtime

            if modify_time > latest_modify_time:
                modify_time = latest_modify_time
                latest_save_file = save_file

        return latest_save_file


    def save_config(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)


def main():
    syncer = SaveSyncer()
    syncer.save_config()


if __name__ == '__main__':
    main()
