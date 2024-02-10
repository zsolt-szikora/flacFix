import glob
import os
import yaml
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from pydub import AudioSegment


class _Fixer:
    correction_ms: int
    shorten_last_flac: bool
    root_folder: str
    folder_groups: [[str]]

    def __init__(self):
        pass

    def parse_settings(self):
        def _read_yaml_file():
            root = Tk()
            root.withdraw()
            return askopenfilename(filetypes=[("Yaml files", "*.yaml")])

        with open(_read_yaml_file(), "r") as stream:
            try:
                parsed = yaml.safe_load(stream)
                self.correction_ms = parsed["correction_ms"]
                self.shorten_last_flac = parsed["shorten_last_flac"]
                self.root_folder = parsed["root_folder"]
                self.folder_groups = parsed["folder_groups"]
            except yaml.YAMLError as exc:
                print(exc)

    def validate_folder_groups(self):
        for group in self.folder_groups:
            for folder in group:
                if Path(self.root_folder) in Path(folder).parents:
                    print(f"✅ validated folder {folder}")
                else:
                    raise Exception(f"Folder {folder} is not under root {self.root_folder}.")
        print()


    def do_fix(self):
        group_counter = 1
        for group in self.folder_groups:
            flac_files = self._extract_flac_files(group)
            print(f"Reading group {group_counter}")
            durations, merged_audio = self._merge_flac_files(flac_files)
            print(f"Group {group_counter}, sum of durations: {len(merged_audio)} ms")
            print(f"Writing Group {group_counter}")
            segment_start = 0
            for file in flac_files:
                is_first_segment = file == flac_files[0]
                is_last_segment = file == flac_files[-1]
                segment_end = (segment_start +
                               + durations[file]
                               - (self.correction_ms if is_first_segment else 0)
                               + (self.correction_ms if is_last_segment and not self.shorten_last_flac else 0))
                fixed_segment = merged_audio[segment_start:segment_end]
                segment_start = segment_end
                output_file = file.replace(self.root_folder, self.root_folder + "_fixed")
                output_path = os.path.dirname(os.path.abspath(output_file))
                Path(output_path).mkdir(parents=True, exist_ok=True)
                fixed_segment.export(output_file, format="flac")
                print(f"Output file: {output_file}, duration: {len(fixed_segment)}")
            print(f"Group {group_counter} done\n")
            group_counter += 1

    @staticmethod
    def _extract_flac_files(group):
        flac_files = []
        for folder in group:
            flac_files += sorted(glob.glob(folder + "/*.flac"))
        return flac_files

    @staticmethod
    def _merge_flac_files(flac_files):
        durations = {}
        merged_audio = AudioSegment.empty()
        for file in flac_files:
            audio = AudioSegment.from_file(file, format="flac")
            durations[file] = len(audio)
            print(f"Input file: {file}, duration: {durations[file]} ms")
            merged_audio += audio
        return durations, merged_audio


# ==================================================================
def do_fix_flac_files():
    f = _Fixer()
    f.parse_settings()
    f.validate_folder_groups()
    f.do_fix()
