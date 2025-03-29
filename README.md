# Siren
Audio splitting and sheet music transcription tool

## Runnning the Program
Run the main script `siren.py` with the following flags:
- `-input` followed by your input `.wav` audio file.
- `-output` followed by your output directory.
- `-source` followed by each desired isolated track, from the list:
    - vocals
    - bass
    - drums
    - brass
    - synth
    - guitar

An example call to this program that seeks to isolate the drums and synth from a stem would be:
```
python3 siren.py -input mixed.wav\
                 -output isolated_sources/\
                 -source drums\
                         synth    
```

## Project Fles

### siren.py

Main script that is to be solely interfaced with as specified above.

### waveform.py

Performs all `.wav` file handling in terms of reading from and writing to.

### flags.py

Handles all command-line flag parsing to assist with program interfacing