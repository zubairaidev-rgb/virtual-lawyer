"""
Convert user's SVG logo to PNG for use in Word documents
"""
from PIL import Image
import cairosvg
import io
import os

svg_path = "/Users/mac/Downloads/Copy of Copy of Labor Law Thesis Defense by Slidesgo.pptx.svg"
png_output = "./data/user-logo.png"

try:
    # Convert SVG to PNG using cairosvg
    cairosvg.svg2png(url=svg_path, write_to=png_output, output_width=600)
    print(f"✅ Successfully converted SVG to PNG")
    print(f"   Input:  {svg_path}")
    print(f"   Output: {png_output}")
except Exception as e:
    print(f"❌ Error converting SVG: {e}")
    print("\nTrying alternative method...")

    # Fallback: Try with PIL if cairosvg fails
    try:
        # This won't work for complex SVGs but worth a try
        from wand.image import Image as WandImage

        with WandImage(filename=svg_path) as img:
            img.format = 'png'
            img.save(filename=png_output)
        print(f"✅ Converted using ImageMagick")
    except:
        print("❌ Could not convert logo. Will use default Lawmate logo instead.")
