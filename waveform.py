import struct
import numpy as np
import sys
from decompose import Decomposer

class Waveform():
    '''
    Open a .wav audio file and read binary information to extract data.
    .wav formatted files are comprised of 3 main data blocks:
        - RIFF Block: (File type information)
            - 'RIFF'              (4 Bytes)
            - File Size           (4 Bytes)
            - 'WAVE'              (4 Bytes)
        - fmt Block: (Song-encoding information)
            - 'fmt'               (4 Bytes)
            - Block Size          (4 Bytes)
            - Audio Format        (1 Byte - PCM (Pulse Code Modulation), 2 Bytes - ?)
            - Sample Rate         (4 Bytes) (Number of audio samples per second, kHz)
            - Byte Rate           (4 Bytes) (Bitrate / 8) [Bitrate is Bits Per Sample * Sample Rate, aka # of Bits / Second of Audio]
            - Block Align         (2 Bytes)
            - Bits Per Sample     (2 Bytes) (# of bits per audio sample)
        - Data Block: (Song data)
            - 'data'              (4 Bytes)
            - Data Size           (4 bytes)
            - Amplitudes          (Data Size)
    '''
    def __init__(self, input_directory) -> None:

        sys.stdout.write(f"[Info] =::::= Reading file - {input_directory}\n")

        self.input_directory = input_directory

        with open(input_directory, 'rb') as file:
            # RIFF Block
            self.riff_id, self.file_size = self.jump_to(b'RIFF', file)
            self.wave_id = file.read(4)

            # fmt Block
            self.fmt_id, self.fmt_size = self.jump_to(b'fmt ', file)
            self.audio_format = struct.unpack('<H', file.read(2))[0]
            self.audio_channels = struct.unpack('<H', file.read(2))[0]
            self.sample_rate = struct.unpack('<I', file.read(4))[0]
            self.byte_rate = struct.unpack('<I', file.read(4))[0]
            self.block_align = struct.unpack('<H', file.read(2))[0]
            self.bits_per_sample = struct.unpack('<H', file.read(2))[0]
            self.bytes_per_sample = self.bits_per_sample // 8
            if self.bits_per_sample not in [8, 16, 32]:
                raise ValueError(f"Error: Bits Per Sample of {self.bits_per_sample} not supported. Only 8, 16, and 32 bit wav files are supported")

            # Data Block
            self.data_id, self.data_size = self.jump_to(b'data', file)
            self.bit_rate = self.bits_per_sample * self.sample_rate
            self.num_samples = self.data_size // (self.bytes_per_sample * self.audio_channels)

            # Determine sample format and numpy dtype
            if self.bits_per_sample == 8:
                self.sample_format = '<B'
                self.amplitudes = np.empty((self.num_samples, self.audio_channels), dtype=np.uint8)
            if self.bits_per_sample == 16:
                self.sample_format = '<h'
                self.amplitudes = np.empty((self.num_samples, self.audio_channels), dtype=np.int16)
            elif self.bits_per_sample == 32:
                self.sample_format = '<i'
                self.amplitudes = np.empty((self.num_samples, self.audio_channels), dtype=np.int32)

            # Read raw data
            sys.stdout.write("[DEBUG] ::::  Reading data block - Status: ")
            sys.stdout.flush()
            raw_data = file.read(self.data_size)

            # Read from file data into each channel's amplitude array
            for sample_number in range(self.num_samples):
                for channel_number in range(self.audio_channels):
                    start = (sample_number * self.audio_channels + channel_number) * self.bytes_per_sample
                    sample = struct.unpack(self.sample_format, raw_data[start:start + self.bytes_per_sample])[0]
                    self.amplitudes[sample_number, channel_number] = sample
            sys.stdout.write("Finished\n")

        # Report file information
        data_size_mb = self.data_size / (1024 * 1024)
        sys.stdout.write(f"[Info]  ::::  File information:\n")
        sys.stdout.write(f"Sample Rate:        {self.sample_rate}\n")
        sys.stdout.write(f"Bits Per Sample:    {self.bits_per_sample}\n")
        sys.stdout.write(f"Bit Rate:           {self.bit_rate}\n")  
        sys.stdout.write(f"Data size:          {self.data_size} ({data_size_mb:.2f} mb)\n")
        sys.stdout.write(f"Number of samples:  {len(self.amplitudes)}\n")
        sys.stdout.write(f"Audio Channels:     {self.audio_channels}\n\n")

    def jump_to(self, block, file) -> tuple[bytes, int]:
        '''
        Skip through a .wav file to locate a desired block
        Returns the block id and correspoding block size
        ''' 
        SEEK_CUR = 1
        sys.stdout.write(f"[Debug] ::::  Seeking {block} block - Status: ")
        sys.stdout.flush()

        while True:
            block_id = file.read(4)

            # If invalid block_id read, or end of file
            if not block_id:
                sys.stdout.write("Error\n")
                raise ValueError("End of file. {block} block not found")
            
            # Read current block size
            block_size = struct.unpack('<I', file.read(4))[0]

            # If target
            if block_id == block:
                sys.stdout.write("Found\n")
                return block_id, block_size

            else:
                # Skip to the end of the current block
                file.seek(block_size, SEEK_CUR)
    
    def split(self, output_directory, sources) -> None:
        '''
        For each desired source, write a new .wav file containing the isolated track
        '''
        sys.stdout.write("[Info] =::::= Splitting track\n")

        # Create decomposer object
        decomposer = Decomposer()
              
        for source in sources:
            
            self.isolated_amplitudes = decomposer.decompose(self.amplitudes, source)

            sys.stdout.write(f"[Debug] ::::  Writing to file - {output_directory}{source}.wav - Status: ")
            sys.stdout.flush()
            with open(f'{output_directory}{source}.wav', 'wb') as file:
                # RIFF Block
                file.write(b'RIFF')
                file.write(struct.pack('<I', self.file_size))
                file.write(b'WAVE')

                # fmt Block
                file.write(b'fmt ')
                file.write(struct.pack('<I', self.fmt_size))
                file.write(struct.pack('<H', self.audio_format))
                file.write(struct.pack('<H', self.audio_channels))
                file.write(struct.pack('<I', self.sample_rate))
                file.write(struct.pack('<I', self.byte_rate))
                file.write(struct.pack('<H', self.block_align))
                file.write(struct.pack('<H', self.bits_per_sample))

                # data Block
                file.write(b'data')
                file.write(struct.pack('<I', self.data_size))

                # Write isolated amplitudes
                for frame in self.isolated_amplitudes:
                    for sample in frame:
                        file.write(struct.pack(self.sample_format, int(sample)))
                file.flush()
                
                # Report file confirmation
                sys.stdout.write(f"Success\n")