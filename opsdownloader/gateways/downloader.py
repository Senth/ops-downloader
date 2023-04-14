from pathlib import Path

from yt_dlp import YoutubeDL

from ..core.episode import Episode


class Downloader:
    opts = {
        "outtmpl": "tmp.%(ext)s",  # Set the output file name format
        "merge_output_format": "mkv",  # Set the output format
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",  # Set the format for the streams
    }

    def __init__(self) -> None:
        pass

    def download(self, episode: Episode) -> None:
        yt = YoutubeDL(Downloader.opts)
        yt.download([episode.ops.download_url])
        episode.file = Downloader._rename_file(episode)

    @staticmethod
    def _rename_file(episode: Episode) -> Path:
        file = Path("tmp.mkv")

        new_name = episode.filename.replace(".mp4", ".mkv")
        return file.rename(new_name)
