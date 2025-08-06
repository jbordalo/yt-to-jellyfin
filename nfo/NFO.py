from nfo.templates import *
import os

class VideoNFOWriter:


    def __init__(self, title: str, base_path: str):
        self.title = title
        self.episodes = []
        self.base_path = base_path


    def add_episode(self, title: str, description: str, upload_date: str):
        self.episodes.append((title, description, upload_date))


    def __main_nfo(self) -> str:
        return show_template.format(title=self.title)


    def write(self):
        with open(os.path.join(self.base_path, self.title, "tvshow.nfo"), "w") as f:
            f.write(self.__main_nfo())

        for k, (title, description, upload_date) in enumerate(self.episodes): 
            number = k+1
            with open(os.path.join(self.base_path, self.title, f"Episode {number}.nfo"), "w") as f:
                f.write(episode_template.format(title=title, description=description, number=number, date=upload_date))
