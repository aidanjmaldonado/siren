from waveform import Waveform
from flags import Flags
import matplotlib.pyplot as plt

def main():
    # Contains input, output, and source
    argument_flags = Flags()

    # Create waveform from input
    waveform = Waveform(argument_flags.input)

    # Split tracks and save output
    waveform.split(argument_flags.output, argument_flags.source)

    # Test plot
    if waveform.audio_channels > 1:
        fig, axs = plt.subplots(waveform.audio_channels, 1, figsize=(10, 8))    
        for channel_number in range(waveform.audio_channels):
            axs[channel_number].plot(waveform.amplitudes[:, channel_number], linewidth=0.5)
            axs[channel_number].set_title(f'Channel {channel_number+1}')
    else:
        plt.plot(waveform.amplitudes, linewidth=0.5)
        plt.title(f'Channel 1')
    plt.show()

if __name__ == "__main__":
    main()