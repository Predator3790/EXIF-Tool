import argparse
import csv
from pathlib import Path
from colorama import Fore, just_fix_windows_console
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS


def DMS_to_DD(degrees: float, minutes: float, seconds: float, negative=False):
    """Convert Degrees, Minutes, Seconds (DMS) format to Decimal Degrees (DD) format."""
    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
    decimal_degrees = decimal_degrees * -1 if negative else decimal_degrees
    return decimal_degrees

def get_EXIF(img_path):
    """Get EXIF data from an image and return it as a dictionary."""
    img_path = Path(img_path).absolute()
    
    try:
        exif = dict()
        img = Image.open(img_path)

        try:
            exif_encoded = img._getexif()
        except AttributeError:
            exif_encoded = img.getexif()
        
        for key, value in exif_encoded.items():
            key = TAGS.get(key)
            if key == 'GPSInfo':
                """
                value[1] = GPSLatitudeRef: N / S
                value[2] = GPSLatitude: (degrees, minutes, seconds)
                value[3] = GPSLongitudeRef: E / W
                value[4] = GPSLongitude: (degrees, minutes, seconds)
                """
                # Check if GPS coordinates are present
                if 1 in value and 2 in value and 3 in value and 4 in value:
                    latitude = DMS_to_DD(*map(float, value[2]), True if value[1] == 'S' else False)
                    longitude = DMS_to_DD(*map(float, value[4]), True if value[3] == 'W' else False)
                    exif[key] = f"https://maps.google.com/?q={latitude},{longitude}"
            else:
                if not isinstance(value, bytes):
                    exif[key] = value
        return exif
    # img.getexif() => there is no EXIF data
    except AttributeError:
        return dict()
    # Image.open() => file doesn't exist
    except FileNotFoundError:
        return dict()
    # Image.open() => file type is not supported
    except UnidentifiedImageError:
        return dict()

def remove_EXIF(img_path):
    """Remove EXIF data from an image and return the new image path."""
    img_path = Path(img_path).absolute()
    img = Image.open(img_path)
    img_data = list(img.getdata())
    img_no_exif = Image.new(img.mode, img.size)
    img_no_exif.putdata(img_data)
    img_no_exif_path = img_path.with_stem(f"{img_path.stem}_noEXIF")
    img_no_exif.save(img_no_exif_path)
    return img_no_exif_path

def save_EXIF(img_path):
    """Get and save the EXIF data in an excel file and return its path."""
    img_path = Path(img_path).absolute()
    exif_data = get_EXIF(img_path)
    csv_path = img_path.with_suffix('.csv')
    with open(csv_path, 'w', encoding='utf-8', errors='replace', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('File', img_path))
        for key, value in exif_data.items():
            writer.writerow((key, value))
    return csv_path


if __name__ == '__main__':
    # Get arguments
    modes = ('show', 'remove', 'save')
    parser = argparse.ArgumentParser(usage=f"{Path(__file__).name} [-h] \u007b{','.join(modes)}\u007D (-f FILE [FILE ...] | -d DIRECTORY [DIRECTORY ...])")
    parser.add_argument('mode', choices=modes, help="select between show in terminal, remove or save file's EXIF data")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--directories', nargs='+', type=Path, help="select directories containing the image files. Script does not work recursively", metavar='DIRECTORY')
    group.add_argument('-f', '--files', nargs='+', type=Path, help="select image files to work with", metavar='FILE')
    
    # Set arguments
    args = parser.parse_args()
    mode = args.mode
    if args.directories is None:
        files = [file.absolute() for file in args.files]
    elif args.files is None:
        files = [file.absolute() for directory in args.directories for file in directory.iterdir() if file.is_file()]

    # Make colorama module work in Windows
    just_fix_windows_console()

    for image in files:
        
        # Check if image exists
        if not image.is_file():
            print(f"{Fore.RED}{image}{Fore.WHITE}: file does not exist{Fore.RESET}")
            continue
        
        # Check if image is supported by Pillow
        try:
            img = Image.open(image)
            exif_data = img._getexif()
        except AttributeError:
            exif_data = img.getexif()
        except:
            print(f"{Fore.RED}{image}{Fore.WHITE}: file type not supported{Fore.RESET}")
            continue
        
        # Check if image contains EXIF data
        if exif_data is None or exif_data == dict():
            print(f"{Fore.RED}{image}{Fore.WHITE}: no EXIF data{Fore.RESET}")
            continue

        # Show EXIF data
        if mode == 'show':
            print(f"{Fore.GREEN}{image}{Fore.WHITE}:{Fore.RESET}")
            for key, value in get_EXIF(image).items():
                print(f"\t{Fore.WHITE}{key}: {value}{Fore.RESET}")
        # Remove EXIF data
        elif mode == 'remove':
            no_exif = remove_EXIF(image)
            print(f"{Fore.GREEN}{image}{Fore.WHITE}: {no_exif}{Fore.RESET}")
        # Save EXIF data
        elif mode == 'save':
            csv_file = save_EXIF(image)
            print(f"{Fore.GREEN}{image}{Fore.WHITE}: {csv_file}{Fore.RESET}")
