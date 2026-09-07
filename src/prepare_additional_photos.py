"""Optional asset preparation, requiring Pillow. Normal site builds use committed WebP files."""
from pathlib import Path
from PIL import Image, ImageOps, ImageCms
import argparse, io, json

parser = argparse.ArgumentParser()
parser.add_argument('upload_directory', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent
sources = json.loads((root/'src/additional-photo-sources.json').read_text())
assets = json.loads((root/'src/assets.json').read_text())
srgb = ImageCms.createProfile('sRGB')
for key, data in sources.items():
 with Image.open(args.upload_directory/data['uploaded_filename']) as original:
  image = ImageOps.exif_transpose(original).convert('RGB')
  profile = original.info.get('icc_profile')
  if profile:
   image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(profile)), srgb, outputMode='RGB')
  image.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
  small = image.copy()
  small.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
  for version, suffix, quality in [(image, '', 88), (small, '-small', 83)]:
   version.save(root/f'dist/assets/photos/{key}{suffix}.webp', 'WEBP', quality=quality, method=6)
  assets[key] = {'width':image.width, 'height':image.height, 'smallWidth':small.width, 'src':f'/assets/photos/{key}.webp', 'small':f'/assets/photos/{key}-small.webp'}
(root/'src/assets.json').write_text(json.dumps(assets, indent=2))
print(f'Prepared {len(sources)} photographs in sRGB; original uploads unchanged.')
