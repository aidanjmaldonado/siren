import struct
import numpy as np
import os

class Waveform():
    '''
    Open a .wav audio file and read binary information to extract data.
    .wav formatted files are comprised of 3 main data blocks:
        - RIFF Block: (File type information)
            - 'RIFF'               (4 Bytes)
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

        with open(input_directory, 'rb') as file:
            # RIFF Block
            self.riff_id = file.read(4)
            self.file_size = struct.unpack('<I', file.read(4))[0] # Number of bytes in file, excluding 'RIFF' and file size itself (includes 'WAVE')
            self.wave_id = file.read(4)

            # fmt Block
            self.fmt_id = file.read(4)
            self.fmt_size = struct.unpack('<I', file.read(4))[0]
            self.audio_format = struct.unpack('<H', file.read(2))[0]
            self.audio_channels = struct.unpack('<H', file.read(2))[0]
            self.sample_rate = struct.unpack('<I', file.read(4))[0]
            self.byte_rate = struct.unpack('<I', file.read(4))[0]
            self.block_align = struct.unpack('<H', file.read(2))[0]
            self.bits_per_sample = struct.unpack('<H', file.read(2))[0]
            self.bytes_per_sample = self.bits_per_sample // 8
            if self.bits_per_sample not in [8, 16, 32]:
                raise ValueError("Error: Only 8, 16, and 32 bit wav files are supported")

            # Determine sample format and numpy dtype
            if self.bits_per_sample == 8:
                self.sample_format = '<B'
            if self.bits_per_sample == 16:
                self.sample_format = '<h'
            elif self.bits_per_sample == 32:
                self.sample_format = '<i'  

            # Data Block
            self.data_size = self.find_data_block(file)
            self.bit_rate = self.bits_per_sample * self.sample_rate
            self.num_samples = self.data_size // (self.bits_per_sample * self.audio_channels)

            # Determine sample format and numpy dtype
            if self.bits_per_sample == 8:
                self.amplitudes = np.empty((self.num_samples, self.audio_channels), dtype=np.uint8)
            if self.bits_per_sample == 16:
                self.amplitudes = np.empty((self.num_samples, self.audio_channels), dtype=np.int16)
            elif self.bits_per_sample == 32:
                self.amplitudes = np.empty((self.num_samples, self.audio_channels), dtype=np.int32)

            # Read raw data
            raw_data = file.read(self.data_size)

            # Read from file data into each channel's amplitude array
            for i in range(self.num_samples):
                for channel in range(self.audio_channels):
                    start = (i * self.audio_channels + channel) * self.bytes_per_sample
                    sample = struct.unpack(self.sample_format, raw_data[start:start + self.bytes_per_sample])[0]
                    self.amplitudes[i, channel] = sample

        # Print file information
        print(f"{input_directory} information:")
        print(f"Sample Rate:        {self.sample_rate}")
        print(f"Bits Per Sample     {self.bits_per_sample}")
        print(f"Bit Rate            {self.bit_rate}")  
        data_size_mb = self.data_size / (1024 * 1024)
        print(f"Data size           {self.data_size} ({data_size_mb:.2f} mb)")
        print(f"Number of samples:  {len(self.amplitudes)}")
        print(f"Audio Channels:     {self.audio_channels}\n")

    def find_data_block(self, file):
        '''
        Skip through a .wav file to locate the b'data' block id and return its size
        ''' 
        SEEK_CUR = 1
        MAX_INT = 4294967295

        while True:
            block_id = file.read(4)
            if not block_id:
                raise ValueError("End of file. Data block not found")
            
            # Read current block size
            block_size = struct.unpack('<I', file.read(4))[0]

            if block_id == b'data':
                self.data_id = block_id
                if block_size == MAX_INT:
                    raise ValueError("Error reading file.")
                return block_size
            else:
                file.seek(block_size, SEEK_CUR) # Skip to the end of the current block