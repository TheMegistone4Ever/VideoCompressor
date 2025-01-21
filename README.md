# Video Processing Automation Tool

###### &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; — by [Mykyta Kyselov (TheMegistone4Ever)](https://github.com/TheMegistone4Ever).

A robust Python-based video processing automation tool that handles batch compression and resizing of video files while
preserving directory structures.
This tool uses FFmpeg for efficient video processing and supports parallel processing
for improved performance.

## Table of Contents

1. [Introduction](#1-introduction)
    1. [Overview](#11-overview)
    2. [Features](#12-features)
2. [System Requirements](#2-system-requirements)
    1. [Software Dependencies](#21-software-dependencies)
    2. [Hardware Requirements](#22-hardware-requirements)
3. [Installation](#3-installation)
    1. [Setting Up Dependencies](#31-setting-up-dependencies)
    2. [Installing the Tool](#32-installing-the-tool)
4. [Usage](#4-usage)
    1. [Basic Usage](#41-basic-usage)
    2. [Advanced Options](#42-advanced-options)
    3. [Examples](#43-examples)
5. [Project Structure](#5-project-structure)
    1. [Core Components](#51-core-components)
    2. [File Organization](#52-file-organization)
6. [Technical Details](#6-technical-details)
    1. [Processing Pipeline](#61-processing-pipeline)
    2. [Error Handling](#62-error-handling)
7. [Contributing](#7-contributing)
8. [License](#8-license)

## 1. Introduction

### 1.1 Overview

The Video Processing Automation Tool is designed to streamline the process of batch video compression and resizing. It
automatically processes video files while maintaining original directory structures, making it ideal for managing large
video collections. The tool leverages FFmpeg for high-quality video processing and supports multicore processing for
enhanced performance.

### 1.2 Features

- Automatic directory structure replication
- Batch video processing with FFmpeg using H.265 codec
- Smart resolution management with configurable maximum dimensions
- Parallel processing support with a customizable process count
- Comprehensive logging system with debug options
- Progress tracking and detailed error reporting
- Automatic filename sanitization and restoration
- Support for multiple video formats (mp4, mkv, avi, mov, flv, wmv)

## 2. System Requirements

### 2.1 Software Dependencies

- Python 3.8 or higher
- FFmpeg with H.265 support
- FFprobe (typically included with FFmpeg)

### 2.2 Hardware Requirements

- Minimum 4GB RAM
- Storage space: 2x the size of input videos
- Multi-core processor recommended for parallel processing
- Additional CPU resources recommended for H.265 encoding

## 3. Installation

### 3.1 Setting Up Dependencies

1. Install Python 3.8+:
    - Download from [python.org](https://python.org)
    - Ensure Python is added to your system PATH

2. Install FFmpeg:
    - Windows: Download from [ffmpeg.org](https://ffmpeg.org)
    - Linux: `sudo apt-get install ffmpeg`
    - macOS: `brew install ffmpeg`

3. Install Python dependencies:
    - No additional Python packages required beyond a standard library

### 3.2 Installing the Tool

1. Clone the repository:
   ```bash
   git clone https://github.com/TheMegistone4Ever/VideoCompressor.git
   cd VideoCompressor
   ```

2. Make the script executable:
   ```bash
   chmod +x video_compressor.py
   ```

## 4. Usage

### 4.1 Basic Usage

Process videos in a directory:

```bash
python video_compressor.py /path/to/videos
```

### 4.2 Advanced Options

- Enable debug logging:
  ```bash
  python video_compressor.py /path/to/videos --debug
  ```

- Set custom maximum resolution:
  ```bash
  python video_compressor.py /path/to/videos --maxwidth 1280 --maxheight 720
  ```

- Specify the number of processing cores:
  ```bash
  python video_compressor.py /path/to/videos --processes 4
  ```

### 4.3 Examples

1. Process a single directory:
   ```bash
   python video_compressor.py ~/Videos/vacation
   ```

2. Process with detailed logging and custom resolution:
   ```bash
   python video_compressor.py ~/Videos/vacation --debug --maxwidth 1280 --maxheight 720
   ```

3. Process using all available CPU cores:
   ```bash
   python video_compressor.py ~/Videos/vacation --processes None
   ```

## 5. Project Structure

### 5.1 Core Components

- `video_compressor.py`: Main script containing the VideoProcessor class and processing logic
- `video_processing.log`: Detailed processing log file with operation history
- `LICENSE.md`: CC BY-NC 4.0 license details
- `README.md`: Project documentation

### 5.2 File Organization

```
video-processor/
├── video_compressor.py
├── README.md
├── LICENSE.md
├── .gitignore
└── video_processing.log
```

## 6. Technical Details

### 6.1 Processing Pipeline

1. Directory structure replication
2. Video file identification and format validation
3. Filename sanitization and mapping
4. Resolution analysis and scaling calculation
5. FFmpeg processing with H.265 encoding
6. Output file management and original filename restoration
7. Parallel processing coordination

### 6.2 Error Handling

- Comprehensive logging with configurable detail levels
- Graceful failure recovery with a process of isolation
- Automatic cleanup of incomplete operations
- Input validation and format verification
- Detailed error reporting with FFmpeg output capture

## 7. Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 8. License

The project is licensed under the [CC BY-NC 4.0 License](LICENSE.md).
