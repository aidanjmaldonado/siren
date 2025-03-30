import struct
import numpy as np
import matplotlib.pyplot as plt
import sys

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

        sys.stdout.write(f"[Debug] =::::= Reading file - {input_directory}\n")

        self.input_directory = input_directory

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
            self.data_size = self.find_data_block_size(file)
            self.bit_rate = self.bits_per_sample * self.sample_rate
            self.num_samples = self.data_size // (self.bytes_per_sample * self.audio_channels)

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
            for sample_number in range(self.num_samples):
                for channel_number in range(self.audio_channels):
                    start = (sample_number * self.audio_channels + channel_number) * self.bytes_per_sample
                    sample = struct.unpack(self.sample_format, raw_data[start:start + self.bytes_per_sample])[0]
                    self.amplitudes[sample_number, channel_number] = sample

        # Report file information
        sys.stdout.write(f"File information:\n")
        sys.stdout.write(f"Sample Rate:        {self.sample_rate}\n")
        sys.stdout.write(f"Bits Per Sample     {self.bits_per_sample}\n")
        sys.stdout.write(f"Bit Rate            {self.bit_rate}\n")  
        data_size_mb = self.data_size / (1024 * 1024)
        sys.stdout.write(f"Data size           {self.data_size} ({data_size_mb:.2f} mb)\n")
        sys.stdout.write(f"Number of samples:  {len(self.amplitudes)}\n")
        sys.stdout.write(f"Audio Channels:     {self.audio_channels}\n\n")

    def find_data_block_size(self, file) -> int:
        '''
        Skip through a .wav file to locate the b'data' block id and return its size
        ''' 
        sys.stdout.write(f"[Debug] ::: Seeking data block size\n")
        SEEK_CUR = 1
        FILESIZE_MAX = 4294967295

        while True:
            block_id = file.read(4)
            if not block_id:
                raise ValueError("End of file. Data block not found")
            
            # Read current block size
            block_size = struct.unpack('<I', file.read(4))[0]

            if block_id == b'data':
                self.data_id = block_id
                if block_size == FILESIZE_MAX:
                    raise ValueError("Error reading file.")
                return block_size
            else:
                # Skip to the end of the current block
                file.seek(block_size, SEEK_CUR)
    
    def split(self, output_directory, sources):
       '''
       For each desired source, write a new .wav file containing the isolated track
       '''
       sys.stdout.write("[Debug] =::::= Splitting track\n")
       for source in sources:
            
            isolated_amplitudes = self.isolate(source)

            sys.stdout.write(f"[Debug] ::: Writing to file - {output_directory}{source}.wav\n")
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
                for frame in isolated_amplitudes:
                    for sample in frame:
                        file.write(struct.pack(self.sample_format, int(sample)))
                file.flush()
                
                # Report file confirmation
                sys.stdout.write(f"File successfully saved as: {output_directory}{source}.wav\n")

    def isolate(self, source) -> np.array:
        '''
        Isolate desired source from original amplitudes array
        '''
        sys.stdout.write(f"[Debug] ::: Isolating {source}\n")
        
        # TO-DO
        return self.amplitudes
