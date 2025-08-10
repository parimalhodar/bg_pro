from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from typing import Any, Tuple

# Preset colors for studio backgrounds
COLOR_MAP = {
    "White": (255, 255, 255),
    "Light Blue": (135, 206, 250),
    "Light Gray": (200, 200, 200),
    "Pastel Pink": (255, 182, 193),
    "Pastel Green": (152, 251, 152),
    "Red": (220, 60, 60),
    "Royal Blue": (65, 105, 225),
    "Olive": (128, 128, 64),
    "Purple": (128, 0, 128),
    "Black": (10, 10, 10),
    "Navy Blue": (0, 0, 128),
    "Forest Green": (34, 139, 34),
    "Maroon": (128, 0, 0),
    "Teal": (0, 128, 128),
    "Orange": (255, 165, 0)
}

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def add_noise(image: Image.Image, amount: int = 6) -> Image.Image:
    """Add subtle noise to image for realistic texture"""
    arr = np.array(image, dtype=np.int16)
    noise = np.random.randint(-amount, amount + 1, arr.shape, dtype=np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def add_vignette(image: Image.Image, blur: int = 120, darkness: float = 0.5) -> Image.Image:
    """Add vignette effect to image"""
    w, h = image.size
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    max_r = int((w + h) / 2 * darkness)
    draw.ellipse((-max_r, -max_r, w + max_r, h + max_r), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return Image.composite(image, Image.new('RGB', (w, h), (0, 0, 0)), mask)  # type: ignore

def add_bokeh(image: Image.Image, count: int = 12, max_radius: int = 80, opacity: int = 50) -> Image.Image:
    """Add bokeh light effects to image"""
    draw = ImageDraw.Draw(image, 'RGBA')
    w, h = image.size
    for _ in range(count):
        x, y = np.random.randint(0, w), np.random.randint(0, h)
        r = np.random.randint(20, max_radius)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, opacity))
    return image

# Studio Background Styles

def solid_color_bg(color: Tuple[int, int, int], size: Tuple[int, int] = (800, 1000)) -> Image.Image:
    """Create a flat solid color background"""
    return Image.new('RGB', size, color=color)  # type: ignore

def passport_studio_bg(color: Tuple[int, int, int], size: Tuple[int, int] = (413, 531)) -> Image.Image:
    """Create passport-style studio background with subtle gradient and effects"""
    img = Image.new('RGB', size, color=color)  # type: ignore
    cx, cy = size[0] // 2, size[1] // 2
    max_r = max(size) // 1.2
    px: Any = img.load()
    
    # Create radial gradient
    for y in range(size[1]):
        for x in range(size[0]):
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            ratio = min(dist / max_r, 1)
            r = int(color[0] * (1 - ratio) + 255 * ratio * 0.18)
            g = int(color[1] * (1 - ratio) + 255 * ratio * 0.18)
            b = int(color[2] * (1 - ratio) + 255 * ratio * 0.18)
            px[x, y] = (r, g, b)
    
    # Add effects
    img = add_noise(img, amount=5)
    img = add_vignette(img, blur=80, darkness=0.5)
    return img

def portrait_studio_bg(color: Tuple[int, int, int], size: Tuple[int, int] = (800, 1000)) -> Image.Image:
    """Create portrait studio background with vertical gradient and professional effects"""
    img = Image.new('RGB', size, color=color)  # type: ignore
    px: Any = img.load()
    
    # Create vertical gradient
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(color[0] * (1 - ratio) + 235 * ratio)
        g = int(color[1] * (1 - ratio) + 235 * ratio)
        b = int(color[2] * (1 - ratio) + 235 * ratio)
        for x in range(size[0]):
            px[x, y] = (r, g, b)
    
    # Add professional effects
    img = add_noise(img, amount=7)
    img = add_vignette(img, blur=120, darkness=0.38)
    img = add_bokeh(img, count=12, max_radius=80, opacity=55)
    return img

def group_studio_bg(color: Tuple[int, int, int], size: Tuple[int, int] = (1600, 900)) -> Image.Image:
    """Create group photo studio background with wide format and subtle effects"""
    img = Image.new('RGB', size, color=color)  # type: ignore
    cx, cy = size[0] // 2, size[1] // 2
    max_r = max(size) // 1.6
    px: Any = img.load()
    
    # Create radial gradient from center
    for y in range(size[1]):
        for x in range(size[0]):
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            ratio = min(dist / max_r, 1)
            r = int(color[0] * (1 - ratio) + 210 * ratio)
            g = int(color[1] * (1 - ratio) + 210 * ratio)
            b = int(color[2] * (1 - ratio) + 210 * ratio)
            px[x, y] = (r, g, b)
    
    # Add subtle effects
    img = add_noise(img, amount=6)
    img = add_vignette(img, blur=140, darkness=0.35)
    return img

def professional_headshot_bg(color: Tuple[int, int, int], size: Tuple[int, int] = (600, 800)) -> Image.Image:
    """Create professional headshot background with sophisticated lighting"""
    img = Image.new('RGB', size, color=color)  # type: ignore
    cx, cy = size[0] // 2, size[1] // 3  # Focus light higher up
    max_r = max(size) // 1.8
    px: Any = img.load()
    
    # Create sophisticated gradient
    for y in range(size[1]):
        for x in range(size[0]):
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            ratio = min(dist / max_r, 1)
            
            # More sophisticated color blending
            highlight_factor = 0.25 if ratio < 0.3 else 0.1
            r = int(color[0] * (1 - ratio) + (255 * highlight_factor) * ratio)
            g = int(color[1] * (1 - ratio) + (255 * highlight_factor) * ratio)
            b = int(color[2] * (1 - ratio) + (255 * highlight_factor) * ratio)
            px[x, y] = (r, g, b)
    
    # Add professional effects
    img = add_noise(img, amount=4)
    img = add_vignette(img, blur=100, darkness=0.45)
    return img

# Map of available styles
STYLE_MAP = {
    "Solid Color": solid_color_bg,
    "Passport": passport_studio_bg,
    "Portrait": portrait_studio_bg,
    "Group Photo": group_studio_bg,
    "Professional Headshot": professional_headshot_bg
}

def generate_background(style: str, color_name: str = "White", custom_color_hex: str | None = None, size: Tuple[int, int] = (800, 1000)) -> Image.Image:
    """
    Generate a professional studio background
    
    Args:
        style (str): Background style from STYLE_MAP
        color_name (str): Color name from COLOR_MAP
        custom_color_hex (str): Custom hex color (optional)
        size (tuple): Background size (width, height)
    
    Returns:
        PIL.Image: Generated background image
    """
    # Determine color
    if custom_color_hex:
        color = hex_to_rgb(custom_color_hex)
    else:
        color = COLOR_MAP.get(color_name, (255, 255, 255))
    
    # Get background generation function
    func = STYLE_MAP.get(style, solid_color_bg)
    
    # Generate background
    return func(color, size=size)

# Convenience function for getting available options
def get_available_styles() -> list[str]:
    """Get list of available background styles"""
    return list(STYLE_MAP.keys())

def get_available_colors() -> list[str]:
    """Get list of available preset colors"""
    return list(COLOR_MAP.keys())

# Example usage and testing
if __name__ == "__main__":
    # Generate a sample background for testing
    bg = generate_background("Portrait", "Light Blue", size=(400, 500))
    bg.save("test_background.png")
    print("Test background saved as test_background.png")