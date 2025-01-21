import logging
import logging.handlers
from json import loads
from multiprocessing import Pool, cpu_count, Queue, Process, Manager
from os import walk, rename, path
from pathlib import Path
from queue import Empty
from subprocess import run, PIPE
from typing import Tuple, Dict, Set


def setup_logger(queue: Queue, log_level: int) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    if not logger.handlers:
        queue_handler = logging.handlers.QueueHandler(queue)
        logger.addHandler(queue_handler)
    return logger


def logger_process(queue: Queue, log_level: int, log_file: str):
    try:
        log_dir = path.dirname(path.abspath(log_file))
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        root_logger = logging.getLogger()
        if not root_logger.handlers:
            root_logger.addHandler(logging.FileHandler(log_file))
            root_logger.addHandler(logging.StreamHandler())

        while True:
            try:
                record = queue.get()
                if record is None:
                    break
                logger = logging.getLogger(record.name)
                logger.handle(record)
            except Empty:
                continue
            except Exception as e:
                print(f'Error in logger process: {str(e)}')
    except Exception as e:
        print(f'Error setting up logger process: {str(e)}')


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


def process_video(args: Tuple[Path, Path, Dict[Path, str], Queue, int]) -> bool:
    input_path, output_path, filename_mapping, log_queue, log_level = args
    logger = setup_logger(log_queue, log_level)

    try:
        output_path = output_path.with_suffix(".mp4")

        try:
            width, height = get_video_resolution(str(input_path))
            scale_filter = "1920:1080" if width > 1920 or height > 1080 else "iw:ih"
            logger.info(f"Original resolution for {input_path}: {width}x{height}")
            logger.info(f"Using scale filter: {scale_filter}")
        except Exception as e:
            logger.warning(f"Could not get resolution for {input_path}, using original: {str(e)}")
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
            logger.error(f"FFmpeg error for {input_path}: {result.stderr}")
            return False

        if output_path in filename_mapping:
            new_path = output_path.parent / f"{filename_mapping[output_path]}.mp4"
            rename(output_path, new_path)
            logger.info(f"Restored original filename: {new_path}")

        logger.info(f"Successfully processed: {input_path}")
        return True

    except Exception as e:
        logger.error(f"Error processing {input_path}: {str(e)}")
        return False


class VideoCompressor:
    def __init__(self, input_dir: str, processes: int = None, log_level: int = logging.INFO):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(f"{input_dir}_compressed")
        self.filename_mapping: Dict[Path, str] = dict()
        self.processes = processes if processes is not None else cpu_count()
        self.log_level = log_level
        self.log_queue = Manager().Queue()

        self.log_file = path.join(path.dirname(path.abspath(input_dir)), "video_processing.log")

        if not isinstance(self.processes, int):
            raise TypeError("processes parameter must be an integer")
        if self.processes < 1:
            raise ValueError("processes parameter must be greater than or equal to 1")

        self.logger_process = Process(
            target=logger_process,
            args=(self.log_queue, self.log_level, self.log_file)
        )
        self.logger_process.start()

        self.logger = setup_logger(self.log_queue, self.log_level)
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
            self.logger.info(f"Using {self.processes} processes for processing")

            self.create_directory_structure()

            process_args = [(input_path, output_path, self.filename_mapping, self.log_queue, self.log_level)
                            for input_path, output_path in video_files]

            with Pool(processes=self.processes) as pool:
                results = pool.map(process_video, process_args)

            failed_count = len([result for result in results if not result])
            if failed_count > 0:
                self.logger.error(f"Failed to process {failed_count} video files")

        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            raise
        finally:
            self.log_queue.put(None)
            self.logger_process.join()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Video Processing Script")
    parser.add_argument("input_dir", help="Input directory containing video files")
    parser.add_argument("--processes", type=int, default=1,
                        help="Number of processing processes (default: 1). Use None for all available CPUs")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    processor = VideoCompressor(
        args.input_dir,
        processes=args.processes,
        log_level=logging.DEBUG if args.debug else logging.INFO
    )

    try:
        processor.process_all_videos()
        print("Processing complete. Check video_processing.log for details.")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    # e.g.: python video_compressor.py "absolute-path" --processes 4 --debug
    main()
