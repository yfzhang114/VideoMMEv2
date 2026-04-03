from PIL import Image
img = Image.open('figs/imgs/video_category.png')
alpha = img.split()[-1]
# Count pixels with alpha between 1 and 254 (indicates soft drop shadow or anti-aliasing)
data = alpha.getdata()
semi_transparent = sum(1 for a in data if 0 < a < 255)
print(f"Semi-transparent pixels: {semi_transparent} out of {len(data)}")
