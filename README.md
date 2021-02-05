# Process Playlist

A simple Python script to convert AudioVAULT AVScheduler EVT playlist files into CSV files for uploading to NPR Composer.

## Install

    pip install -r requirements.txt
    python -m PyInstaller --windowed --noconsole --onefile gui.spec

## Usage

Run the executable with the GUI from the dist folder or run from the command line:

    python process_playlist.py soure_file_name.EVT