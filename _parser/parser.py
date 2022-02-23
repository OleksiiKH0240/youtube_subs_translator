from os.path import join

from youtube_transcript_api import YouTubeTranscriptApi
import os
from Benchmarks_funcs.Benchmarks import benchmark
from config_paths import get_paths


class Parser:
    def __init__(self, download_path: str = ""):
        print('Start Parser')
        self.download_path = download_path
        if download_path:
            if ":" not in download_path:
                # relative path (path started from _parser folder)
                self.download_path = join(get_paths(["parser"])[0], download_path)
            if not os.path.exists(self.download_path):
                os.mkdir(self.download_path)

        self.file_name_pattern = 'parsed_file_id='

    def get_id_from_link(self, link):
        video_id = ""
        if "youtube" in link:
            video_id = [i[2:] for i in link[link.index('?') + 1:].split('&') if 'v=' in i][0]
        elif "youtu.be" in link:
            video_id = link[link.index("youtu.be") + len("youtu.be/"):]

        return video_id

    @benchmark
    def parse(self, pers_id, video_link=None):
        print(f'start parse link: {video_link}')
        if video_link:
            sub_strs = []
            video_id: str = self.get_id_from_link(video_link)
            try:
                parse_list = YouTubeTranscriptApi.get_transcript(video_id, languages=('en',))
            except Exception as e:
                print(e)
                print('subtitles not founded')
                return sub_strs
            sub_strs = [i['text'] + '\n' for i in parse_list]
            if self.download_path:
                with open(self.download_path + f'\\{self.file_name_pattern}{pers_id}.txt', 'w', encoding="utf-8") as f:
                    f.writelines("\n".join(sub_strs) + "\n")
            else:
                return [i[:-1] for i in sub_strs]


class SubsNotFoundException(Exception):
    def __init__(self, message: str = None):
        self.msg = message

    def __str__(self):
        return self.msg + "; " + "Subtitles is not found"


if __name__ == '__main__':
    p = Parser('Temp_parsers_files')
    print(p.parse(1234, video_link='https://www.youtube.com/watch?v=m-kQXpKG0Iw'))
