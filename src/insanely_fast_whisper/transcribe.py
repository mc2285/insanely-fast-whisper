#!/usr/bin/python3

# https://github.com/Vaibhavs10/insanely-fast-whisper/blob/main/convert_output.py

import argparse
import json
import os
import subprocess


class TxtFormatter:
    @classmethod
    def preamble(cls):
        return ""

    @classmethod
    def format_chunk(cls, chunk, index):
        text = chunk['text']
        return f"{text}\n"


class SrtFormatter:
    @classmethod
    def preamble(cls):
        return ""

    @classmethod
    def format_seconds(cls, seconds):
        whole_seconds = int(seconds)
        milliseconds = int((seconds - whole_seconds) * 1000)

        hours = whole_seconds // 3600
        minutes = (whole_seconds % 3600) // 60
        seconds = whole_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    @classmethod
    def format_chunk(cls, chunk, index):
        text = chunk['text']
        start, end = chunk['timestamp'][0], chunk['timestamp'][1]
        start_format, end_format = cls.format_seconds(
            start), cls.format_seconds(end)
        return f"{index}\n{start_format} --> {end_format}\n{text}\n\n"


class VttFormatter:
    @classmethod
    def preamble(cls):
        return "WEBVTT\n\n"

    @classmethod
    def format_seconds(cls, seconds):
        whole_seconds = int(seconds)
        milliseconds = int((seconds - whole_seconds) * 1000)

        hours = whole_seconds // 3600
        minutes = (whole_seconds % 3600) // 60
        seconds = whole_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    @classmethod
    def format_chunk(cls, chunk, index):
        text = chunk['text']
        start, end = chunk['timestamp'][0], chunk['timestamp'][1]
        start_format, end_format = cls.format_seconds(
            start), cls.format_seconds(end)
        return f"{index}\n{start_format} --> {end_format}\n{text}\n\n"


def convert(input_path, output_format, output_dir, verbose):
    with open(input_path, 'r') as file:
        data = json.load(file)

    formatter_class = {
        'srt': SrtFormatter,
        'vtt': VttFormatter,
        'txt': TxtFormatter
    }.get(output_format)

    string = formatter_class.preamble()
    for index, chunk in enumerate(data['chunks'], 1):
        entry = formatter_class.format_chunk(chunk, index)

        if verbose:
            print(entry)

        string += entry

    with open(os.path.join(output_dir, f"output.{output_format}"), 'w', encoding='utf-8') as file:
        file.write(string)


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio file")
    parser.add_argument("input_file", help="Input audio file")
    parser.add_argument("-f", "--output_format", default="srt",
                        help="Format of the output file (default: srt)", choices=["txt", "vtt", "srt"])
    parser.add_argument("-o", "--output_dir", default=".",
                        help="Directory where the output file/s is/are saved")

    args = parser.parse_args()

    # Trabscribe with insanely-fast-whisper
    subprocess.run(["insanely-fast-whisper", "--file-name", args.input_file,
                   "--model-name", "openai/whisper-large-v3", "--transcript-path", "output.json"])

    convert("output.json", args.output_format, args.output_dir, False)


if __name__ == "__main__":
    # Example Usage:
    # python convert_output.py file.flac -f vtt -o /tmp/my/output/dir
    main()
