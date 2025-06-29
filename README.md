# Farming Simulator 25 Fill Plane Converter
## Purpose

This script allows you to do two things:

1. Convert a pair of FS22 512x512 Diffuse and 512x512 Normal Textures to FS25-compatible 1024x1024 PNG files with an auto-generated 512x512 height map. The textures will be tiled rather than stretched, so you'll get best results with seamless textures (as usual).
2. Convert any 1024x1024 Diffuse PNG and 1024x1024 Normal PNG to FS25-compatible PNG files with an auto-generated 512x512 height map.

The resulting files can be dragged onto the Giants Texture Tool in order to obtain FS25-compatible DDS files.

The script is intended for Fill Plane textures. Other textures might not be processed correctly.

## Preconditions

1. [Python 3+](https://www.python.org/downloads/)
2. [ImageMagick 7+](https://imagemagick.org/script/download.php)

Make sure both of these can be found in the system PATH. Reboot if necessary.

## How to use

Assuming the preconditions are fulfilled, download the newest zip from the [Releases](releases) section and extract it.
Then, simply select a diffuse and normal DDS or PNG file and drag them onto the convert_textures.bat
Alternatively, call `python gen_fs25_fillplanes.py <diffuse_file> <normal_file>` from the command line.

The script will place the converted textures in a "converted" subfolder next to the supplied diffuse file.

## Why do I need to install stuff first? Why is this not an executable?

The main design goal for this script is not ease of use, but rather adaptability. If you understand the multitude of ImageMagick's command line parameters, you can adapt the "command" arrays in the python script to make ImageMagick do what you want.

## Will the Textures be perfect?

No, they won't. But in some cases they might be just good enough, and in others they'll provide a good base you can continue from.

## How can I contribute?

If you've got a quick fix or improvement, simply fork and submit a pull request. If it's a larger operation it's best to create an issue first so other people know you're working on that already.

## Acknowledgements

Thanks to sablerock for showing me the manual process which led to the development of this automated script