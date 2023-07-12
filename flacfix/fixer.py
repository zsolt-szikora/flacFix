import glob
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

from pydub import AudioSegment

CORRECTION_MS = 2_000


def do_fix_flac_files():
    root_folder = _read_root_folder()
    if not root_folder:
        print("No root folder selected, exiting")
        exit(-1)
    os.makedirs(root_folder + "_fixed", exist_ok=True)
    _process(root_folder, root_folder)


def _read_root_folder():
    root = Tk()
    root.withdraw()
    return askdirectory(initialdir="/home/zsolt/audio-test/")


def _process(root, path):
    for s in _subdirectories(path):
        _process(root, s)
        _fix_input_folder(root, s)


def _subdirectories(path):
    """Yield directory names not starting with '.' under given path."""
    for entry in os.scandir(path):
        if not entry.name.startswith('.') and entry.is_dir():
            yield path + "/" + entry.name


def _fix_input_folder(root_folder, input_folder):
    flac_files = sorted(glob.glob(input_folder + "/*.flac"))
    durations, merged_audio = _merge_flac_files(flac_files)
    print(f"Input_folder: {input_folder}, sum of durations: {len(merged_audio)} ms")

    segment_start = 0
    for file in flac_files:
        segment_end = segment_start + durations[file] - (CORRECTION_MS if segment_start == 0 else 0)
        fixed_segment = merged_audio[segment_start:segment_end]
        os.makedirs(input_folder.replace(root_folder, root_folder + "_fixed"), exist_ok=True)
        output_file = file.replace(root_folder, root_folder + "_fixed")
        fixed_segment.export(output_file, format="flac")
        print(f"Output file: {output_file}, duration: {len(fixed_segment)}")
        segment_start = segment_end


def _merge_flac_files(flac_files):
    durations = {}
    merged_audio = AudioSegment.empty()
    for file in flac_files:
        audio = AudioSegment.from_file(file, format="flac")
        durations[file] = len(audio)
        print(f"Input file: {file}, duration: {durations[file]} ms")
        merged_audio += audio
    return durations, merged_audio
