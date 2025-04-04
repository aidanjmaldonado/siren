import numpy as np

class Decomposer():
    '''
    Isolate desired source from original amplitudes array
    '''
    def __init__(self) -> None:
        pass

    def decompose(self, amplitudes, source) -> np.array:
        if source == "bass":
            isolated_amplitudes = self.isolate_bass(amplitudes)
        if source == "guitar":
            isolated_amplitudes = self.isolate_bass(amplitudes)
        if source == "vocals":
            isolated_amplitudes = self.isolate_bass(amplitudes)
        if source == "drums":
            isolated_amplitudes = self.isolate_bass(amplitudes)
        if source == "synth":
            isolated_amplitudes = self.isolate_bass(amplitudes)
        if source == "brass":
            isolated_amplitudes = self.isolate_bass(amplitudes)

        return isolated_amplitudes

    def isolate_bass(self, amplitudes) -> np.array:
        """
        To-do
        """
        return amplitudes

    def isolate_guitar(self, amplitudes) -> np.array:
        """
        To-do
        """
        return amplitudes

    def isolate_vocals(self, amplitudes) -> np.array:
        """
        To-do
        """
        return amplitudes

    def isolate_drums(self, amplitudes) -> np.array:
        """
        To-do
        """
        return amplitudes

    def isolate_synth(self, amplitudes) -> np.array:
        """
        To-do
        """
        return amplitudes

    def isolate_brass(self, amplitudes) -> np.array:
        """
        To-do
        """
        return amplitudes