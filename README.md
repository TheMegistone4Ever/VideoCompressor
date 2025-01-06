# Video Processing Automation Tool

###### &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; — by [Mykyta Kyselov (TheMegistone4Ever)](https://github.com/TheMegistone4Ever).

A robust Python-based video processing automation tool that handles batch compression and resizing of video files while
preserving directory structures.

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
video collections.

### 1.2 Features

- Automatic directory structure replication
- Batch video processing with FFmpeg
- Smart filename handling
- Comprehensive logging system
- Progress tracking
- Error recovery and reporting

## 2. System Requirements

### 2.1 Software Dependencies

- Python 3.8 or higher
- FFmpeg

### 2.2 Hardware Requirements

- Minimum 4GB RAM
- Storage space: 2x the size of input videos
- Multi-core processor recommended

## 3. Installation

### 3.1 Setting Up Dependencies

1. Install Python 3.8+

2. Install FFmpeg

3. Install Python dependencies if needed

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

### 4.3 Examples

1. Process a single directory:
   ```bash
   python video_compressor.py ~/Videos/vacation
   ```

2. Process with detailed logging:
   ```bash
   python video_compressor.py ~/Videos/vacation --debug
   ```

## 5. Project Structure

### 5.1 Core Components

- `video_compressor.py`: Main script containing the VideoProcessor class
- `video_processing.log`: Processing log file

### 5.2 File Organization

```
video-processor/
├── video_processor.py
├── README.md
├── LICENSE.md
├── .gitignore
└── logs/
    └── video_processing.log
```

## 6. Technical Details

### 6.1 Processing Pipeline

1. Directory structure replication
2. Video file identification
3. Filename sanitization
4. FFmpeg processing
5. Output file management

### 6.2 Error Handling

- Comprehensive logging
- Graceful failure recovery
- Temporary file cleanup
- Input validation

## 7. Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 8. License

The project is licensed under the [CC BY-NC 4.0 License](LICENSE.md).
