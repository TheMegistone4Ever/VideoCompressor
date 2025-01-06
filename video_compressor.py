import logging
from json import loads
from os import walk
from pathlib import Path
from shutil import copy2
from subprocess import run, PIPE
from typing import List, Tuple


def sanitize_filename(filename: str) -> str:
    return filename.replace(" ", "_")


def get_video_resolution(video_path: str) -> Tuple[int, int]:
    """Get the width and height of a video file using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json",
            str(video_path)
        ]

        result = run(cmd, stdout=PIPE, stderr=PIPE, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"ffprobe error: {result.stderr}")

        stream = loads(result.stdout)["streams"][0]
        return stream["width"], stream["height"]
    except Exception as e:
        raise RuntimeError(f"Error getting video resolution: {str(e)}")


class VideoCompressor:
    def __init__(self, input_dir: str, log_level: int = logging.INFO):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(f"{input_dir}_compressed")

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("video_processing.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        self.video_extensions = {".mp4", ".mkv"}

    def create_directory_structure(self) -> None:
        try:
            if not self.input_dir.exists():
                raise FileNotFoundError(f"Input directory \"{self.input_dir}\" does not exist")

            self.output_dir.mkdir(parents=True, exist_ok=True)

            for dir_path, _, _ in walk(self.input_dir):
                relative_path = Path(dir_path).relative_to(self.input_dir)
                new_dir = self.output_dir / relative_path
                new_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {new_dir}")

        except Exception as e:
            self.logger.error(f"Error creating directory structure: {str(e)}")
            raise

    def process_video(self, input_path: Path, output_path: Path) -> bool:
        try:
            output_path = output_path.with_suffix(".mp4")

            try:
                width, height = get_video_resolution(str(input_path))
                scale_filter = "1920:1080" if width > 1920 or height > 1080 else "iw:ih"
                self.logger.info(f"Original resolution for {input_path}: {width}x{height}")
                self.logger.info(f"Using scale filter: {scale_filter}")
            except Exception as e:
                self.logger.warning(f"Could not get resolution for {input_path}, using original: {str(e)}")
                scale_filter = "iw:ih"

            ffmpeg_cmd = [
                "ffmpeg",
                "-i", str(input_path),
                "-vcodec", "libx265",
                "-vf", f"scale={scale_filter}",
                "-r", "30",
                "-y",
                str(output_path)
            ]

            result = run(
                ffmpeg_cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self.logger.error(f"FFmpeg error for {input_path}: {result.stderr}")
                return False

            self.logger.info(f"Successfully processed: {input_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error processing {input_path}: {str(e)}")
            return False

    def find_video_files(self) -> List[Tuple[Path, Path]]:
        video_files = []

        for dir_path, _, files in walk(self.input_dir):
            dir_path = Path(dir_path)
            relative_path = dir_path.relative_to(self.input_dir)

            for file in files:
                if Path(file).suffix.lower() in self.video_extensions:
                    input_path = dir_path / file
                    output_path = self.output_dir / relative_path / file
                    video_files.append((input_path, output_path))

        return video_files

    def process_all_videos(self) -> None:
        try:
            self.create_directory_structure()
            video_files = self.find_video_files()

            if not video_files:
                self.logger.warning("No video files found in input directory")
                return

            self.logger.info(f"Found {len(video_files)} video files to process")

            for input_path, output_path in video_files:
                try:
                    temp_input = input_path.with_name(sanitize_filename(input_path.name))
                    temp_output = output_path.with_name(sanitize_filename(output_path.name))

                    if " " in input_path.name:
                        copy2(input_path, temp_input)
                    else:
                        temp_input = input_path

                    success = self.process_video(temp_input, temp_output)

                    if success:
                        if " " in output_path.name:
                            temp_output.rename(output_path)

                    if temp_input != input_path and temp_input.exists():
                        temp_input.unlink()

                except Exception as e:
                    self.logger.error(f"Error processing {input_path}: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            raise


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Video Processing Script")
    parser.add_argument("input_dir", help="Input directory containing video files")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    processor = VideoCompressor(
        args.input_dir,
        log_level=logging.DEBUG if args.debug else logging.INFO
    )

    try:
        processor.process_all_videos()
        print("Processing complete. Check video_processing.log for details.")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
