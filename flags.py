import sys
import os

class Flags():
    def __init__(self) -> None:

        sys.stdout.write("[Info] =::::= Parsing flags\n")
        self.input = None
        self.output = None
        self.source = []
        self.valid_instruments = ['bass', 'guitar', 'vocals', 'drums', 'synth', 'brass']
        self.args = sys.argv[1:]
        if "-help" in self.args:
            sys.stdout.write(
'''
[Help] 
Run the main script siren.py with the following flags:
    -input  :: followed by your input .wav audio file.
    -output :: followed by your output directory.
    -source :: followed by each desired isolated track, from the list: [vocals, bass, drums, brass, synth, drums]\n
An example call to this program that seeks to isolate the drums and synth from a stem would be:
python3 siren.py -input mixed.wav -output isolated_sources/ -source drums synth\n\n''')
            sys.exit(0)

        # Parse each argument
        for index, arg in enumerate(self.args):

            if arg == "-input":
                if self.args[index+1].endswith(".wav"):
                    self.input = self.args[index+1]
                else:
                    raise TypeError("Invalid input argument. Use '-input input.wav")
                
            if arg == "-output":
                if os.path.isdir(self.args[index + 1]):
                    self.output = self.args[index+1]
                else:
                    raise TypeError ("Invalid output directory.")

            if arg == "-source":
                for instrument in self.args[index+1:]:
                    if instrument in self.valid_instruments:
                        self.source.append(instrument)
                    else:
                        raise TypeError("Invalid source argument. Please select from the list:\n - bass\n - guitar\n - vocals\n - drums\n - synth\n - brass")

        # Ensure all necessary flags were passed in
        if self.input == None:
            raise TypeError("Invalid input argument. Use '-input input.wav")
        if self.output == None:
            raise TypeError("Invalid output argument. Use '-output [directory]")
        if self.source == []:
            raise TypeError("Invalid source argument. Use '-source [instrument_i] (for all i)")

        # Report processed flags
        sys.stdout.write(f"Input file:         {self.input}\n")
        sys.stdout.write(f"Output directory:   {self.output}\n")
        sys.stdout.write(f"Sampled sources:    {self.source}\n\n")