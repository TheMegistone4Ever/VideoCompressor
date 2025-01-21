import logging
from json import loads
from os import walk, rename
from pathlib import Path
from subprocess import run, PIPE
from typing import Tuple, Dict, Set


def sanitize_filename(filename: str) -> str:
    return filename.replace(" ", "_")


def get_video_resolution(video_path: str) -> Tuple[int, int]:
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
        self.filename_mapping: Dict[Path, str] = dict()

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("video_processing.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        self.video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}

    def create_directory_structure(self) -> None:
        try:
            if not self.input_dir.exists():
                raise FileNotFoundError(f"Input directory \"{self.input_dir}\" does not exist")

            self.output_dir.mkdir(parents=True, exist_ok=True)

            for dir_path, _, _ in walk(self.input_dir):
                new_dir = self.output_dir / Path(dir_path).relative_to(self.input_dir)
                new_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {new_dir}")

        except Exception as e:
            self.logger.error(f"Error creating directory structure: {str(e)}")
            raise

    def restore_original_filename(self, output_path: Path) -> None:
        try:
            if output_path in self.filename_mapping:
                new_path = output_path.parent / f"{self.filename_mapping[output_path]}.mp4"
                rename(output_path, new_path)
                self.logger.info(f"Restored original filename: {new_path}")
                del self.filename_mapping[output_path]
        except Exception as e:
            self.logger.error(f"Error restoring original filename for {output_path}: {str(e)}")

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

            result = run(ffmpeg_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"FFmpeg error for {input_path}: {result.stderr}")
                return False

            self.restore_original_filename(output_path)
            self.logger.info(f"Successfully processed: {input_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error processing {input_path}: {str(e)}")
            return False

    def find_video_files(self) -> Set[Tuple[Path, Path]]:
        video_files = set()
        for dir_path, _, files in walk(self.input_dir):
            for file in files:
                if Path(file).suffix.lower() in self.video_extensions:
                    input_file = Path(dir_path) / file
                    sanitized_file = sanitize_filename(file)
                    output_file = self.output_dir / Path(dir_path).relative_to(self.input_dir) / sanitized_file
                    self.filename_mapping[output_file.with_suffix(".mp4")] = Path(file).stem
                    video_files.add((input_file, output_file))
        return video_files

    def process_all_videos(self) -> None:
        try:
            video_files = self.find_video_files()

            if not video_files:
                self.logger.warning(f"No video files found in input directory. "
                                    f"Extensions supported: {self.video_extensions}")
                return

            self.logger.info(f"Found {len(video_files)} video files to process")

            self.create_directory_structure()
            for input_path, output_path in video_files:
                try:
                    success = self.process_video(input_path, output_path)

                    if not success:
                        self.logger.error(f"Failed to process {input_path}")

                except Exception as e:
                    self.logger.error(f"Error processing {input_path}: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            raise


def main() -> None:
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
    # python video_compressor.py "absolute-path" --debug
    main()
