# .str files are made of layers, which are each made up of several keyframes
# by multiplying the start time of each keyframe by a constant, animations can be interpolated to a different speed
# haven't tried this with a scaling factor of less than 1, might not work or cause strange behavior

SCALING_FACTOR = 2 # Keyframe times multiplied by 2, resulting in 50% speed

import os, sys, glob

def multiply_int(f):
    try:
        num = int.from_bytes(f.read(4), 'little')
        bytes = int.to_bytes(round(num * SCALING_FACTOR), 4, 'little')

        # reading moves stream position forward, moving back four bytes to write 
        f.seek(-4, os.SEEK_CUR)
        f.write(bytes)
        return

    except:
        print(f'Error occured while writing file {f.name()} at location: {hex(f.tell())}')

def interpolate_str(path):
    with open(path, 'rb+') as f:
        f.seek(0xC) # total frame count
        multiply_int(f)

        layer_count = int.from_bytes(f.read(4), 'little')

        f.seek(24, os.SEEK_CUR) # aligning to start of first layer
        
        for layer in range(layer_count - 1):
            texture_count = int.from_bytes(f.read(4), 'little') 
            
            # layers begin with list of texture names
            f.seek(texture_count * 128, os.SEEK_CUR)

            keyframe_count = int.from_bytes(f.read(4), 'little')
            for keyframe in range(keyframe_count):
                multiply_int(f) # first keyframe comes right after count
                f.seek(120, os.SEEK_CUR) # next is 120 bytes later
            
    return
        
if __name__ == '__main__':
    path = input('Please enter a file or folder path:')

    if not os.path.exists(path):
        print('Path is not valid')
        sys.exit(1)

    if os.path.isfile(path) and path.endswith('.str'):
        try:
            interpolate_str(path)
            print('Successfully interpolated file')

        except:
            print('Interpolation failed')
        
        sys.exit(0)

    for file in glob.glob(os.path.join(path, '**/*'), recursive=True):
        if os.path.isfile(file) and file.endswith('.str'):
            try:
                interpolate_str(file)
                print(f'Successfully interpolated file: {file}')

            except:
                print(f'Interpolation failed at file: {file}')
                sys.exit(1)
