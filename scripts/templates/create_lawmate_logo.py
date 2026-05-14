"""
Create a professional Lawmate logo for documents
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create a professional logo
width, height = 400, 120
img = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(img)

# Draw a border/frame
border_color = (139, 69, 19)  # Brown
draw.rectangle([5, 5, width-5, height-5], outline=border_color, width=3)

# Draw scales of justice symbol (simplified)
scale_x = 60
scale_y = 60
# Draw base
draw.line([scale_x-20, scale_y+30, scale_x+20, scale_y+30], fill=border_color, width=3)
# Draw vertical line
draw.line([scale_x, scale_y-25, scale_x, scale_y+30], fill=border_color, width=3)
# Draw balance beam
draw.line([scale_x-25, scale_y-15, scale_x+25, scale_y-15], fill=border_color, width=2)
# Draw scales
draw.ellipse([scale_x-35, scale_y-5, scale_x-15, scale_y+5], outline=border_color, width=2)
draw.ellipse([scale_x+15, scale_y-5, scale_x+35, scale_y+5], outline=border_color, width=2)

# Add text "Lawmate"
try:
    # Try to use a nice font if available
    font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 40)
    font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 16)
except:
    # Fallback to default
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Draw main text
text_color = (139, 69, 19)
draw.text((110, 35), "Lawmate", fill=text_color, font=font_large)
draw.text((110, 75), "Legal Document System", fill=(100, 100, 100), font=font_small)

# Save
logo_path = "./Lawmate/Lawmate/public/lawmate-logo.png"
img.save(logo_path, 'PNG')
print(f"✅ Created professional logo: {logo_path}")

# Also save in data folder for backend use
backend_logo_path = "./data/lawmate-logo.png"
os.makedirs("./data", exist_ok=True)
img.save(backend_logo_path, 'PNG')
print(f"✅ Saved backend logo: {backend_logo_path}")
