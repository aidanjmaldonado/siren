import sys
import os

class Flags():
    def __init__(self) -> None:

        sys.stdout.write("[Debug] =::::= Parsing Flags\n")
        self.input = None
        self.output = None
        self.source = []
        self.args = sys.argv[1:]
        self.valid_instruments = ['bass', 'guitar', 'vocals', 'drums', 'synth', 'brass']

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

        if self.input == None:
            raise TypeError("Invalid input argument. Use '-input input.wav")
        if self.output == None:
            raise TypeError("Invalid output argument. Use '-output [directory]")
        if self.source == []:
            raise TypeError("Invalid source argument. Use '-source [instrument_i] (for all i)")

        # Report processed flags
        sys.stdout.write(f"Sys - Input file:         {self.input}\n")
        sys.stdout.write(f"Sys - Output directory:   {self.output}\n")
        sys.stdout.write(f"Sys - Sampled sources:   {self.source}\n\n")