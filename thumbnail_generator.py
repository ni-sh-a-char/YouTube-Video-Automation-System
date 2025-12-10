"""
Thumbnail Generator - Creates eye-catching YouTube thumbnails automatically
Uses PIL and text overlay for viral-optimized thumbnails
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from typing import Tuple, Optional
import textwrap

class ThumbnailGenerator:
    """Generate viral YouTube thumbnails"""
    
    # Standard YouTube thumbnail size
    THUMB_WIDTH = 1280
    THUMB_HEIGHT = 720
    
    def __init__(self):
        """Initialize thumbnail generator"""
        self.colors = {
            'red': '#FF0000',
            'blue': '#0066FF',
            'yellow': '#FFFF00',
            'white': '#FFFFFF',
            'black': '#000000',
            'green': '#00DD00',
            'orange': '#FF6600',
            'purple': '#9933FF'
        }

    def create_solid_background(self, color: str = 'red') -> Image.Image:
        """Create solid color background"""
        rgb = tuple(int(self.colors.get(color, '#FF0000').lstrip('#')[i:i+2], 16) 
                   for i in (0, 2, 4))
        return Image.new('RGB', (self.THUMB_WIDTH, self.THUMB_HEIGHT), rgb)

    def create_gradient_background(self, color1: str = 'blue', color2: str = 'purple') -> Image.Image:
        """Create gradient background"""
        rgb1 = tuple(int(self.colors.get(color1, '#0066FF').lstrip('#')[i:i+2], 16) 
                    for i in (0, 2, 4))
        rgb2 = tuple(int(self.colors.get(color2, '#9933FF').lstrip('#')[i:i+2], 16) 
                    for i in (0, 2, 4))
        
        image = Image.new('RGB', (self.THUMB_WIDTH, self.THUMB_HEIGHT))
        draw = ImageDraw.Draw(image)
        
        for y in range(self.THUMB_HEIGHT):
            r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * y / self.THUMB_HEIGHT)
            g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * y / self.THUMB_HEIGHT)
            b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * y / self.THUMB_HEIGHT)
            draw.line([(0, y), (self.THUMB_WIDTH, y)], fill=(r, g, b))
        
        return image

    def add_text(self, image: Image.Image, text: str, font_size: int = 80,
                 font_color: str = 'white', position: str = 'center') -> Image.Image:
        """Add main text to thumbnail"""
        
        draw = ImageDraw.Draw(image)
        
        # Try to load a bold font, fall back to default
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Word wrap text
        max_width = self.THUMB_WIDTH - 40
        wrapped_lines = []
        for line in text.split('\n'):
            wrapped_lines.extend(textwrap.wrap(line, width=15))
        
        text_to_draw = '\n'.join(wrapped_lines[:3])  # Max 3 lines
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text_to_draw, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        if position == 'center':
            x = (self.THUMB_WIDTH - text_width) // 2
            y = (self.THUMB_HEIGHT - text_height) // 2
        elif position == 'top':
            x = (self.THUMB_WIDTH - text_width) // 2
            y = 40
        elif position == 'bottom':
            x = (self.THUMB_WIDTH - text_width) // 2
            y = self.THUMB_HEIGHT - text_height - 40
        else:
            x, y = 40, 40
        
        # Add shadow for better readability
        rgb = tuple(int(self.colors.get(font_color, '#FFFFFF').lstrip('#')[i:i+2], 16) 
                   for i in (0, 2, 4))
        
        # Draw shadow
        draw.text((x+4, y+4), text_to_draw, font=font, fill=(0, 0, 0), anchor=None)
        
        # Draw main text
        draw.text((x, y), text_to_draw, font=font, fill=rgb, anchor=None)
        
        return image

    def add_number_badge(self, image: Image.Image, number: str,
                        position: str = 'top-left', bg_color: str = 'red',
                        size: int = 100) -> Image.Image:
        """Add number badge (for ranking videos)"""
        
        draw = ImageDraw.Draw(image)
        
        # Create circle badge
        rgb = tuple(int(self.colors.get(bg_color, '#FF0000').lstrip('#')[i:i+2], 16) 
                   for i in (0, 2, 4))
        
        if position == 'top-left':
            x, y = 30, 30
        elif position == 'top-right':
            x, y = self.THUMB_WIDTH - size - 30, 30
        elif position == 'bottom-left':
            x, y = 30, self.THUMB_HEIGHT - size - 30
        else:  # bottom-right
            x, y = self.THUMB_WIDTH - size - 30, self.THUMB_HEIGHT - size - 30
        
        # Draw circle
        draw.ellipse([(x, y), (x + size, y + size)], fill=rgb)
        
        # Draw number
        try:
            font = ImageFont.truetype("arial.ttf", int(size * 0.6))
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), number, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x + (size - text_width) // 2
        text_y = y + (size - text_height) // 2
        
        draw.text((text_x, text_y), number, font=font, fill=(255, 255, 255))
        
        return image

    def add_border(self, image: Image.Image, color: str = 'yellow',
                  thickness: int = 15) -> Image.Image:
        """Add bold border to thumbnail"""
        
        draw = ImageDraw.Draw(image)
        rgb = tuple(int(self.colors.get(color, '#FFFF00').lstrip('#')[i:i+2], 16) 
                   for i in (0, 2, 4))
        
        # Draw border
        for i in range(thickness):
            draw.rectangle(
                [(i, i), (self.THUMB_WIDTH - i, self.THUMB_HEIGHT - i)],
                outline=rgb,
                width=1
            )
        
        return image

    def generate_ranking_thumbnail(self, title: str, number: int,
                                   color: str = 'red') -> Image.Image:
        """Generate thumbnail for ranking videos (Top 10, etc)"""
        
        # Start with gradient background
        image = self.create_gradient_background(color, 'black')
        
        # Add border
        image = self.add_border(image, color='yellow', thickness=20)
        
        # Add main text
        image = self.add_text(image, title, font_size=70,
                            font_color='white', position='center')
        
        # Add number badge
        image = self.add_number_badge(image, str(number), position='top-left',
                                     bg_color=color, size=120)
        
        return image

    def generate_tutorial_thumbnail(self, title: str, subtitle: str = "") -> Image.Image:
        """Generate thumbnail for tutorial videos"""
        
        # Blue gradient background
        image = self.create_gradient_background('blue', 'purple')
        
        # Add text
        if subtitle:
            image = self.add_text(image, title, font_size=75,
                                font_color='white', position='top')
            image = self.add_text(image, subtitle, font_size=50,
                                font_color='yellow', position='bottom')
        else:
            image = self.add_text(image, title, font_size=85,
                                font_color='white', position='center')
        
        # Add border
        image = self.add_border(image, color='cyan', thickness=15)
        
        return image

    def generate_controversy_thumbnail(self, title: str) -> Image.Image:
        """Generate thumbnail for controversial/viral videos"""
        
        # Red background
        image = self.create_solid_background('red')
        
        # Add bold text
        image = self.add_text(image, title, font_size=90,
                            font_color='white', position='center')
        
        # Add yellow border for contrast
        image = self.add_border(image, color='yellow', thickness=20)
        
        return image

    def generate_from_image(self, image_path: str, title: str = "",
                          opacity: float = 0.4) -> Image.Image:
        """Create thumbnail from an existing image"""
        
        try:
            # Load and resize image
            background = Image.open(image_path)
            background = background.resize((self.THUMB_WIDTH, self.THUMB_HEIGHT))
            
            # Add dark overlay for text readability
            overlay = Image.new('RGBA', (self.THUMB_WIDTH, self.THUMB_HEIGHT),
                              (0, 0, 0, int(255 * opacity)))
            background = background.convert('RGBA')
            background = Image.alpha_composite(background, overlay)
            background = background.convert('RGB')
            
            # Add text if provided
            if title:
                image = self.add_text(background, title, font_size=80,
                                    font_color='white', position='center')
            else:
                image = background
            
            return image
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return self.create_solid_background('red')

    def save_thumbnail(self, image: Image.Image, output_path: str) -> bool:
        """Save thumbnail to file"""
        
        try:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            image.save(output_path, quality=95)
            print(f"✅ Thumbnail saved: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to save thumbnail: {e}")
            return False


class ThumbnailTemplates:
    """Pre-built templates for different video types"""
    
    @staticmethod
    def top_10_template(title: str, number: int, color: str = 'red') -> Image.Image:
        """Template for 'Top 10' style videos"""
        generator = ThumbnailGenerator()
        return generator.generate_ranking_thumbnail(title, number, color)

    @staticmethod
    def tutorial_template(title: str, subtitle: str = "") -> Image.Image:
        """Template for tutorial videos"""
        generator = ThumbnailGenerator()
        return generator.generate_tutorial_thumbnail(title, subtitle)

    @staticmethod
    def controversy_template(title: str) -> Image.Image:
        """Template for viral/controversy videos"""
        generator = ThumbnailGenerator()
        return generator.generate_controversy_thumbnail(title)


if __name__ == "__main__":
    generator = ThumbnailGenerator()
    
    # Example 1: Top 10 ranking
    thumb1 = generator.generate_ranking_thumbnail(
        "Python Mistakes",
        10,
        color='red'
    )
    generator.save_thumbnail(thumb1, 'thumbnails/top_10_example.jpg')
    
    # Example 2: Tutorial
    thumb2 = generator.generate_tutorial_thumbnail(
        "Learn Python",
        "Complete Guide"
    )
    generator.save_thumbnail(thumb2, 'thumbnails/tutorial_example.jpg')
    
    # Example 3: Controversy
    thumb3 = generator.generate_controversy_thumbnail(
        "Stop Using\nPython NOW!"
    )
    generator.save_thumbnail(thumb3, 'thumbnails/viral_example.jpg')
    
    print("\n✅ Sample thumbnails generated in 'thumbnails/' directory")
