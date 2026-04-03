from PIL import Image

img = Image.open('figs/imgs/video_category.png')
print("Mode:", img.mode)

# If it's RGBA, get bounding box of non-transparent pixels
if img.mode == 'RGBA':
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    if bbox:
        img = img.crop(bbox)
        print("Cropped by alpha, new size:", img.size)
        img.save('figs/imgs/video_category_cropped.png')
