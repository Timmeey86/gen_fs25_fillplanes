import os
import subprocess

# Test if the "magick" command is available
def check_imagemagick():
	try:
		subprocess.run(['magick', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return True
	except FileNotFoundError:
		print("ImageMagick 7+ is not installed or not found in the system PATH. Download it from https://imagemagick.org/script/download.php")
		return False

# Create a 1024x1024 PNG from a 512x512 DDS file by duplicating four tiles rather than stretching a single one
def resize_image(dds_file, output_file, isRgba=True):
	if isRgba:
		command = ['magick', '-size', '1024x1024', f'tile:{dds_file}', output_file]
	else:
		command = ['magick', '-size', '1024x1024', f'tile:{dds_file}', '-define', 'png:color-type=2', output_file]
	subprocess.run(command, check=True)

# Create a height map from the diffuse file
def convert_diffuse_to_heightmap(diffuse_file, heightmap_file):
	command = [
		'magick', diffuse_file,
		'-colorspace', 'Gray',
		'-auto-level',
		'-blur', '0x8',
		'-gamma', '2.0',
		heightmap_file
	]
	subprocess.run(command, check=True)

# Merges the height map and diffuse map into the blue channel of the normal map
def update_normal_map_blue_channel_to_fs25(normal_file, height_file, diffuse_file, new_normal_file):
	command = [
		'magick', normal_file,
		'(', '-clone', '0', '-channel', 'R', '-separate', '+channel', ')',
		'(', '-clone', '0', '-channel', 'G', '-separate', '+channel', ')',
		'(', '-clone', '0', '-channel', 'B', '-separate', '+channel',
			diffuse_file, '-compose', 'multiply', '-composite',
			height_file, '-compose', 'multiply', '-composite',
			'-evaluate', 'multiply', '0', # Remove shinyness
		')',
		'-delete', '0',
		'-combine', '-alpha', 'off', '-depth', '8', f'PNG24:{new_normal_file}'
	]
	subprocess.run(command, check=True)

# Merges the original normal map and height map into the diffuse map's alpha channel (this creates transparency)
def update_diffuse_map(diffuse_file, normal_file, height_file, new_diffuse_file):
	command = [
		'magick', diffuse_file,
		'(', '-clone', '0', '-channel', 'R', '-separate', '+channel', ')',
		'(', '-clone', '0', '-channel', 'G', '-separate', '+channel', ')',
		'(', '-clone', '0', '-channel', 'B', '-separate', '+channel', ')',
		'(', '-clone', '0', '-channel', 'A', '-separate', '+channel',
			normal_file, '-compose', 'multiply', '-composite',
			height_file, '-compose', 'multiply', '-composite',
		')',
		'-alpha', 'on',
		'-background', 'none',
		'-delete', '0',
		'-combine', '-depth', '8', f'PNG32:{new_diffuse_file}'
	]
	subprocess.run(command, check=True)

# Converts the height map into a 512x512 grayscale PNG file
def convert_height_to_grayscale(height_file, new_height_file):
	command = [
		'magick', height_file,
		'-resize', '512x512!',
		'-colorspace', 'Gray',
		'-depth', '8',
		'-define', 'png:color-type=0',  # grayscale, single channel
		new_height_file
	]
	subprocess.run(command, check=True)

def check_command_line_args():
	if len(os.sys.argv) != 3 or (len(os.sys.argv) == 2 and os.sys.argv[1] == '-h' or os.sys.argv[1] == '--help' or os.sys.argv[1] == '/h'):
		print(f"Usage: python {os.sys.argv[0]} <diffuse_file> <normal_file>.")
		print("    Mode1: If two DDS files are provided, it is assumed they are FS22 texture files.")
		print("    Mode2: If two PNG files are provided, it is assumed they are 1024x1024 PNG files.")
		os.sys.exit(1)

def get_fillplane_name():
	# Extract the fillplane name from the diffuse file path
	parts = os.path.splitext(os.path.basename(os.sys.argv[1]))
	return parts[0].replace("_diffuse", ""), parts[1]

# Mode 1: Convert FS22 DDS files to 1024x1024 PNGs
def convert_fs22_dds_to_1024_by_1024_pngs(fill_plane_name, diffuse_file, normal_file, tmp_dir):
	upscaled_diffuse = os.path.join(tmp_dir, f"{fill_plane_name}_diffuse.png")
	upscaled_normal = os.path.join(tmp_dir, f"{fill_plane_name}_normal.png")
	print("    Upscaling diffuse map to 1024x1024...")
	resize_image(diffuse_file, upscaled_diffuse, isRgba=True)
	print("    Upscaling normal map to 1024x1024...")
	resize_image(normal_file, upscaled_normal, isRgba=False)
	return upscaled_diffuse, upscaled_normal

# Mode 1 and 2: Convert 1024x1024 PNGs to FS25 textures
def convert_1024_by_1024_pngs_to_fs25_textures(fill_plane_name, diffuse_file, normal_file, height_file, out_dir):
	new_diffuse_file = os.path.join(out_dir, f"{fill_plane_name}_diffuse.png")
	new_normal_file = os.path.join(out_dir, f"{fill_plane_name}_normal.png")
	new_height_file = os.path.join(out_dir, f"{fill_plane_name}_height.png")

	print("    Updating alpha channel of diffuse map...")
	update_diffuse_map(diffuse_file, normal_file, height_file, new_diffuse_file)
	print("    Updating blue channel of normal map...")
	update_normal_map_blue_channel_to_fs25(normal_file, height_file, diffuse_file, new_normal_file)
	print("    Converting height map to grayscale...")
	convert_height_to_grayscale(height_file, new_height_file)

if __name__ == '__main__':
	check_command_line_args()
	print(f"{os.path.basename(os.sys.argv[0])} version 1.1")

	fill_plane_name, file_ext = get_fillplane_name()
	if not fill_plane_name:
		print("Fillplane name could not be determined from the first file argument. Make sure it ends with '_diffuse'.")
		os.sys.exit(1)

	tmp_dir = 'texture_convert_tmp'
	print(f"Creating temporary directory: {tmp_dir}")
	os.makedirs(tmp_dir, exist_ok=True)

	# Create a subdirectory next to the diffuse file
	out_dir = os.path.join(os.path.dirname(os.sys.argv[1]), "converted")
	print(f"Creating output directory: {out_dir}")
	os.makedirs(out_dir, exist_ok=True)

	diffuse_file = os.sys.argv[1]
	normal_file = os.sys.argv[2]
	
	if file_ext.lower() == '.png':
		print("PNG files were supplied")
		print("Creating height map file from diffuse file...")
		height_file = os.path.join(tmp_dir, f"{fill_plane_name}_height.png")
		convert_diffuse_to_heightmap(diffuse_file, height_file)

		print("Converting PNGs to FS25 textures...")
		convert_1024_by_1024_pngs_to_fs25_textures(fill_plane_name, diffuse_file, normal_file, height_file, out_dir)

	elif file_ext.lower() == '.dds':
		print("DDS files were supplied. Assuming FS22 textures.")

		print("Creating 1024x1024 PNGs from 512x512 DDS files...")
		upscaled_diffuse, upscaled_normal = convert_fs22_dds_to_1024_by_1024_pngs(fill_plane_name, diffuse_file, normal_file, tmp_dir)
		print("Creating height map file from diffuse file...")
		height_file = os.path.join(tmp_dir, f"{fill_plane_name}_height.png")
		convert_diffuse_to_heightmap(upscaled_diffuse, height_file)

		print("Converting PNGs to FS25 textures...")
		convert_1024_by_1024_pngs_to_fs25_textures(fill_plane_name, upscaled_diffuse, upscaled_normal, height_file, out_dir)

	else:
		print("This script only supports PNG or DDS files.")
		print(f"Fill Plane Name : {fill_plane_name}")
		print(f"File Extension : {file_ext}")
	
	#if os.path.exists(tmp_dir):
		# print("Cleaning up temporary directory...")
		# import shutil
		# try:
		# 	shutil.rmtree(tmp_dir)
		# except OSError as e:
		# 	print("Error: %s - %s." % (e.filename, e.strerror))
		
	print("All done. You can now drag the generated files onto the Giants Texture Tool in order to get FS25 DDS files.")
	