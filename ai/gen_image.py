import requests
import os
import time
from PIL import Image, ImageDraw, ImageFont

def gen_image(prompt, image_path, height=1920, width=1080):
    """
    Generate an image using Pollinations.ai API.
    Falls back to a placeholder image if API fails.
    """
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Construct URL
            style = "cinematic, hyperrealistic, 4k, high quality, professional lighting"
            full_prompt = f"{prompt}, {style}"
            encoded_prompt = requests.utils.quote(full_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
            # Use model that is less likely to timeout if possible, or just default
            
            print(f"[*] Generating image via Pollinations (Attempt {attempt+1}/{max_retries}): {prompt[:30]}...")
            
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                if os.path.getsize(image_path) > 1024:
                    print(f"[OK] Image saved to {image_path}")
                    return
                else:
                    print(f"[!] Image saved but too small, retrying...")
            else:
                print(f"[!] Failed to generate image. Status: {response.status_code}")
                
        except Exception as e:
            print(f"[!] Error generating image: {e}")
        
        time.sleep(5)  # Increased wait time for rate limits/server load

    # Fallback: Generate placeholder image with better aesthetics
    print(f"⚠️  Failed to generate image from API. Creating placeholder for: {image_path}")
    try:
        # Create a gradient-like or solid professional background (Dark Grey/Blue)
        img = Image.new('RGB', (width, height), color=(25, 30, 40)) 
        d = ImageDraw.Draw(img)
        
        # Try to load a font
        try:
            # Try to use a standard font likely to be on Windows/Linux
            font = ImageFont.truetype("arial.ttf", 80)
        except OSError:
            font = ImageFont.load_default()
            
        # Draw text (centered)
        text = prompt[:100] + "..." if len(prompt) > 100 else prompt
        
        # Calculate text position (rough centering)
        text_bbox = d.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        
        d.text((x, y), text, fill=(200, 200, 200), font=font)
        d.text((x+2, y+2), text, fill=(0, 0, 0), font=font) # Shadow for readability
        
        img.save(image_path)
        print(f"[OK] Placeholder image saved to {image_path}")
        
    except Exception as e:
        print(f"❌ Critical Error: Could not create placeholder image: {e}")
        img = Image.new('RGB', (width, height), color='black')
        img.save(image_path)

def gen_thumbnail(prompt, image_path, text_overlay):
    """
    Generate a high-quality YouTube thumbnail with text overlay.
    """
    width, height = 1280, 720 # Standard thumbnail 16:9
    enhanced_prompt = f"YouTube thumbnail for {prompt}, high contrast, 8k resolution, vibrant, clickbait, stunning visuals, cinematic lighting"
    
    # Retry logic same as gen_image
    max_retries = 3
    for attempt in range(max_retries):
        try:
            encoded_prompt = requests.utils.quote(enhanced_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
            
            print(f"[*] Generating thumbnail: {prompt[:30]}...")
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                # Add Text Overlay
                try:
                    img = Image.open(image_path)
                    d = ImageDraw.Draw(img)
                    
                    # Font setup
                    try:
                        font_size = 80
                        font = ImageFont.truetype("arialbd.ttf", font_size) # Bold Arial
                    except:
                        font = ImageFont.load_default()
                    
                    # Wrap text
                    words = text_overlay.split()
                    lines = []
                    current_line = []
                    for word in words:
                        current_line.append(word)
                        # Check width
                        line_str = " ".join(current_line)
                        bbox = d.textbbox((0,0), line_str, font=font)
                        if (bbox[2] - bbox[0]) > (width - 100):
                            current_line.pop()
                            lines.append(" ".join(current_line))
                            current_line = [word]
                    lines.append(" ".join(current_line))
                    
                    # Draw text with shadow/outline
                    # Position: Centered, slightly lower
                    y_start = (height - (len(lines) * 90)) / 2
                    
                    for i, line in enumerate(lines):
                        bbox = d.textbbox((0,0), line, font=font)
                        line_w = bbox[2] - bbox[0]
                        x_pos = (width - line_w) / 2
                        y_pos = y_start + (i * 90)
                        
                        # Black outline/shadow
                        stroke_width = 3
                        for dx in range(-stroke_width, stroke_width+1):
                            for dy in range(-stroke_width, stroke_width+1):
                                d.text((x_pos+dx, y_pos+dy), line, font=font, fill="black")
                        
                        # Main text (Yellow or White)
                        d.text((x_pos, y_pos), line, font=font, fill="#FFD700") # Gold color
                    
                    img.save(image_path)
                    print(f"[OK] Thumbnail enhanced with text: {image_path}")
                    return

                except Exception as e:
                    print(f"[!] Partial Error adding text to thumbnail: {e}")
                    # Determine if we keep the image without text or not. 
                    # If image is saved, just return, text is bonus.
                    return
            
        except Exception as e:
            print(f"[!] Error generating thumbnail: {e}")
        time.sleep(3)
    
    # Fallback
    print("⚠️  Failed to generate thumbnail. Creating simple text placeholder.")
    try:
        img = Image.new('RGB', (width, height), color=(200, 50, 50)) # Red background
        d = ImageDraw.Draw(img)
        d.text((100, 300), text_overlay, fill="white")
        img.save(image_path)
    except:
        pass