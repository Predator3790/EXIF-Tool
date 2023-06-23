# EXIF Tool

Show in terminal, remove or save image's EXIF data.

## Installation

```shell
pip install -r requirements.txt
```

## Usage

> :warning: Script only works with [Pillow's image file formats](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html) that are able to work with EXIF data.

Basic format:

```shell
python exif.py {show,remove,save} (-f FILE [FILE ...] | -d DIRECTORY [DIRECTORY ...])
```

Working with image files:

```shell
python exif.py {show,remove,save} -f file1 file2 file3
```

Working with directories containing image files (not recursively):

```shell
python exif.py {show,remove,save} -d dir1 dir2 dir3
```

## Examples

Try these examples using the [samples directory](./samples/) by your own!

**Show** the EXIF data in terminal:

```shell
python exif.py show -d samples
```

**Remove** the EXIF data from a file:

```shell
python exif.py remove -d samples
```

**Save** the stored EXIF data in a Comma Separated Values (*.csv*) file:

```shell
python exif.py save -d samples
```

## Credits

Image samples provided from [Exif Samples](https://github.com/ianare/exif-samples) by [ianaré sévi](https://github.com/ianare) and his [contributors](https://github.com/ianare/exif-samples/graphs/contributors).
