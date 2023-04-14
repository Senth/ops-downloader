from pathlib import Path

import ffmpeg

from ..core.episode import Episode


class Encoder:
    def __init__(self) -> None:
        pass

    def rerender(self, episode: Episode) -> None:
        in_file = episode.file

        out_file = episode.filename
        stream = ffmpeg.input(episode.file)
        stream = ffmpeg.output(
            stream,
            out_file,
            vcodec="copy",
            acodec="copy",
            metadata=f"title={episode.title}",
        )
        stream.run()

        # Delete the infile
        in_file.unlink(missing_ok=True)

        episode.file = Path(out_file)

        pass
