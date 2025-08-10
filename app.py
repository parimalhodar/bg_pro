import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw
import io
import os
import zipfile
from streamlit_extras.add_vertical_space import add_vertical_space
import numpy as np
from typing import Optional, Tuple, List
import uuid

# Import from backgrounds module
try:
    from backgrounds import COLOR_MAP, generate_background, STYLE_MAP, get_available_styles, get_available_colors
    BACKGROUNDS_MODULE_AVAILABLE = True
except ImportError:
    BACKGROUNDS_MODULE_AVAILABLE = False
    st.error("backgrounds.py module not found. Please ensure backgrounds.py is in the same directory.")

# Fallback function for gradient background
def create_gradient_background(color1: Tuple[int, int, int], color2: Tuple[int, int, int], size: Tuple[int, int] = (800, 600)) -> Image.Image:
    img = Image.new('RGB', size, color=color1)  # type: ignore
    draw = ImageDraw.Draw(img)
    
    for i in range(size[1]):
        ratio = i / size[1]
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, i), (size[0], i)], fill=(r, g, b))
    
    return img

# Fallback function for pattern background
def create_pattern_background(size: Tuple[int, int] = (800, 600)) -> Image.Image:
    img = Image.new('RGB', size, color=(240, 240, 250))  # type: ignore
    draw = ImageDraw.Draw(img)
    
    for x in range(0, size[0], 50):
        for y in range(0, size[1], 50):
            draw.ellipse([x, y, x+20, y+20], fill=(200, 200, 230))
    
    return img

# Function to replace background
def replace_background(original_img: Image.Image, background_removed_img: Image.Image, new_background: Optional[Image.Image] = None, bg_color: Optional[Tuple[int, int, int]] = None) -> Image.Image:
    if bg_color:
        bg = Image.new('RGB', original_img.size, color=bg_color)  # type: ignore
    elif new_background:
        bg = new_background.resize(original_img.size, Image.Resampling.LANCZOS)
        if bg.mode != 'RGB':
            bg = bg.convert('RGB')
    else:
        return background_removed_img
    
    if background_removed_img.mode != 'RGBA':
        background_removed_img = background_removed_img.convert('RGBA')
    
    result = Image.new('RGB', original_img.size, color=(255, 255, 255))  # type: ignore
    result.paste(bg, (0, 0))
    result.paste(background_removed_img, (0, 0), background_removed_img)
    
    return result

# Custom CSS inspired by remove.bg
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* CSS Variables inspired by remove.bg */
    :root {
        --primary-color: #4A3AFF;
        --primary-dark: #3B2ECC;
        --text-primary: #1A1A1A;
        --text-secondary: #666666;
        --bg-primary: #FFFFFF;
        --bg-card: #F7F7F8;
        --border-color: #E5E5E5;
        --shadow-light: 0 4px 16px rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 6px 24px rgba(0, 0, 0, 0.15);
        --border-radius: 8px;
        --border-radius-lg: 12px;
    }

    /* Mobile-first base styles */
    .stApp {
        background: var(--bg-primary);
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        color: var(--text-primary);
        line-height: 1.6;
        padding: 0.5rem;
        box-sizing: border-box;
    }

    /* Main container */
    .main .block-container {
        max-width: 100%;
        margin: 0 auto;
        padding: 1rem;
        background: transparent;
    }

    /* Card */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-light);
        transition: box-shadow 0.3s ease;
    }

    .card:hover {
        box-shadow: var(--shadow-medium);
    }

    /* Radio buttons */
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        padding: 0.5rem;
        background: var(--bg-card);
        border-radius: var(--border-radius);
        border: 1px solid var(--border-color);
    }

    .stRadio label {
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        border-radius: var(--border-radius);
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        cursor: pointer;
        min-height: 48px;
        display: flex;
        align-items: center;
        box-shadow: var(--shadow-light);
    }

    .stRadio label:hover {
        border-color: var(--primary-color);
        transform: scale(1.02);
    }

    .stRadio input[type="radio"] {
        accent-color: var(--primary-color);
        width: 1.2rem;
        height: 1.2rem;
        margin-right: 0.75rem;
    }

    .stRadio input[type="radio"]:checked + div {
        background: var(--primary-color);
        color: var(--bg-primary);
        border-color: var(--primary-color);
        box-shadow: var(--shadow-medium);
    }

    /* Buttons */
    .stButton > button {
        background: var(--primary-color);
        color: var(--bg-primary);
        border: none;
        border-radius: var(--border-radius);
        padding: 0.8rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        width: 100%;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-light);
        text-transform: none;
        animation: fadeIn 0.5s ease-out;
    }

    .stButton > button:hover,
    .stButton > button:focus {
        background: var(--primary-dark);
        transform: scale(1.05);
        box-shadow: var(--shadow-medium);
        outline: none;
    }

    .stButton > button:active {
        transform: scale(1);
        box-shadow: var(--shadow-light);
    }

    /* Header */
    .header {
        background: var(--bg-primary);
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: var(--shadow-light);
        position: relative;
    }

    .header h1 {
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        animation: fadeIn 0.5s ease-out;
    }

    .header p {
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        color: var(--text-secondary);
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Output images */
    .stImage img {
        max-width: min(100%, 300px);
        height: auto;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-light);
        object-fit: contain;
        animation: fadeIn 0.5s ease-out;
    }

    /* Footer */
    .footer {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        padding: 1.5rem;
        margin-top: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-light);
        font-size: 0.9rem;
        color: var(--text-secondary);
    }

    .footer h4 {
        font-size: 1.1rem;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }

    /* Mobile-specific styles */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }

        .main .block-container {
            padding: 0.5rem;
        }

        .card {
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .stRadio > div {
            gap: 0.5rem;
            padding: 0.5rem;
        }

        .stRadio label {
            font-size: 0.9rem;
            padding: 0.5rem 0.75rem;
            min-height: 48px;
        }

        .stRadio input[type="radio"] {
            width: 1rem;
            height: 1rem;
            margin-right: 0.5rem;
        }

        .stButton > button {
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
        }

        .header {
            padding: 1rem;
        }

        .header h1 {
            font-size: clamp(1.5rem, 4vw, 2rem);
        }

        .header p {
            font-size: clamp(0.9rem, 2.5vw, 1rem);
        }

        .stImage img {
            max-width: min(100%, 200px);
            width: 100%;
        }

        .footer {
            padding: 1rem;
            font-size: 0.8rem;
        }

        .footer h4 {
            font-size: 1rem;
        }
    }

    /* PC-specific styles */
    @media (min-width: 769px) {
        .stApp {
            padding: 1rem;
        }

        .main .block-container {
            max-width: 900px;
            padding: 1.5rem;
        }

        .card {
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .stRadio > div {
            gap: 1rem;
            padding: 1rem;
        }

        .stRadio label {
            font-size: 1rem;
            padding: 0.75rem 1.5rem;
        }

        .stButton > button {
            padding: 0.8rem 2rem;
            font-size: 1rem;
        }

        .header {
            padding: 2.5rem;
        }

        .stImage img {
            max-width: min(100%, 400px);
        }
    }
</style>
""", unsafe_allow_html=True)

# Set page config
st.set_page_config(
    page_title="Pro Background Editor",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Header
with st.container():
    st.markdown("""
    <div class="header">
        <h1>🖼️ Pro Background Editor</h1>
        <p>Remove and replace backgrounds instantly with professional results.</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Settings")
    add_vertical_space(1)
    
    st.markdown("### About")
    st.markdown("Made with ❤️ by [Parimal Hodar]")
    if BACKGROUNDS_MODULE_AVAILABLE:
        st.success(f"✅ Studio Backgrounds: {len(get_available_styles())} styles, {len(get_available_colors())} colors")
    else:
        st.warning("⚠️ Studio Backgrounds Module Not Found")
    
    st.markdown("### Features")
    st.markdown("""
    - Professional studio backgrounds
    - Custom background upload
    - Batch processing
    - High-quality output
    - Mobile & desktop optimized
    """)

# Main content
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Background Options")
    bg_option: str = st.radio(
        "Choose background type:",
        ["Remove Only", "Studio Backgrounds", "Preset Backgrounds", "Custom Background"],
        help="Select the type of background for your processed images",
        key="bg_option"
    )

    # Background selection
    selected_background: Optional[Image.Image] = None
    background_color: Optional[Tuple[int, int, int]] = None
    style_choice: str = "Solid Color"
    selected_bg_file: Optional[str] = None

    # Track background selections for cache invalidation
    if "prev_style_choice" not in st.session_state:
        st.session_state.prev_style_choice = style_choice
    if "prev_color_choice" not in st.session_state:
        st.session_state.prev_color_choice = None
    if "prev_custom_color_hex" not in st.session_state:
        st.session_state.prev_custom_color_hex = None
    if "prev_selected_bg_file" not in st.session_state:
        st.session_state.prev_selected_bg_file = None
    if "prev_custom_bg" not in st.session_state:
        st.session_state.prev_custom_bg = None

    if bg_option == "Studio Backgrounds" and BACKGROUNDS_MODULE_AVAILABLE:
        with st.expander("Studio Background Settings", expanded=True):
            style_choice = st.selectbox(
                "Style:",
                get_available_styles(),
                help="Choose a professional studio background style",
                key="studio_style"
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                color_choice = st.selectbox(
                    "Preset color:",
                    get_available_colors(),
                    help="Select a preset color",
                    key="preset_color"
                )
            with col2:
                use_custom_color = st.checkbox("Use custom color", key="custom_color_check")
                custom_color_hex = st.color_picker("Custom color", "#FFFFFF", key="custom_color_picker") if use_custom_color else None
            
            # Clear cache if background settings change
            if (st.session_state.prev_style_choice != style_choice or
                st.session_state.prev_color_choice != color_choice or
                st.session_state.prev_custom_color_hex != custom_color_hex):
                st.cache_data.clear()
                st.session_state.prev_style_choice = style_choice
                st.session_state.prev_color_choice = color_choice
                st.session_state.prev_custom_color_hex = custom_color_hex
            
            try:
                selected_background = generate_background(
                    style=style_choice,
                    color_name=color_choice or "White",
                    custom_color_hex=custom_color_hex,
                    size=(800, 1000)
                )
                if selected_background:
                    st.image(selected_background, caption=f"{style_choice} Preview", width=200)
            except Exception as e:
                st.error(f"Error generating studio background: {str(e)}")

    elif bg_option == "Studio Backgrounds":
        with st.expander("Fallback Color Settings", expanded=True):
            color_option = st.selectbox(
                "Choose a color:",
                ["White", "Black", "Red", "Blue", "Green", "Yellow", "Purple", "Pink", "Custom"],
                index=0,
                key="fallback_color"
            )
            color_map = {
                "White": (255, 255, 255),
                "Black": (0, 0, 0),
                "Red": (255, 0, 0),
                "Blue": (0, 0, 255),
                "Green": (0, 255, 0),
                "Yellow": (255, 255, 0),
                "Purple": (128, 0, 128),
                "Pink": (255, 192, 203)
            }
            if color_option == "Custom":
                hex_color = st.color_picker("Pick a color", "#FFFFFF", key="custom_color")
                background_color = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))[:3]
            else:
                background_color = color_map[color_option]

    elif bg_option == "Preset Backgrounds":
        with st.expander("Preset Backgrounds", expanded=True):
            bg_folder = "backgrounds"
            if os.path.exists(bg_folder):
                bg_files = [f for f in os.listdir(bg_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                if bg_files:
                    selected_bg_file = st.selectbox("Choose a background:", bg_files, key="preset_bg")
                    if selected_bg_file:
                        try:
                            selected_background = Image.open(os.path.join(bg_folder, selected_bg_file))
                            if selected_background:
                                st.image(selected_background, caption="Selected Background", width=200)
                        except Exception as e:
                            st.error(f"Error loading background: {str(e)}")
                    # Clear cache if background file changes
                    if st.session_state.prev_selected_bg_file != selected_bg_file:
                        st.cache_data.clear()
                        st.session_state.prev_selected_bg_file = selected_bg_file
                else:
                    st.warning("No background images found in backgrounds folder. Create a 'backgrounds' folder with .png, .jpg, or .webp files.")
            else:
                st.warning("Backgrounds folder not found. Using generated backgrounds.")
                online_bg_option = st.selectbox(
                    "Generated background:",
                    ["Gradient Blue", "Gradient Purple", "Gradient Green", "Abstract Pattern"],
                    key="online_bg"
                )
                if online_bg_option == "Gradient Blue":
                    selected_background = create_gradient_background((100, 150, 255), (200, 220, 255))
                elif online_bg_option == "Gradient Purple":
                    selected_background = create_gradient_background((150, 100, 255), (220, 200, 255))
                elif online_bg_option == "Gradient Green":
                    selected_background = create_gradient_background((100, 255, 150), (200, 255, 220))
                else:
                    selected_background = create_pattern_background()
                if selected_background:
                    st.image(selected_background, caption="Generated Background", width=200)

    elif bg_option == "Custom Background":
        with st.expander("Custom Background", expanded=True):
            custom_bg = st.file_uploader(
                "Upload a background image",
                type=['png', 'jpg', 'jpeg', 'webp'],
                help="Upload your own background image",
                key="custom_bg"
            )
            if custom_bg:
                try:
                    selected_background = Image.open(custom_bg)
                    if selected_background:
                        st.image(selected_background, caption="Custom Background", width=200)
                    # Clear cache if custom background changes
                    if st.session_state.prev_custom_bg != custom_bg:
                        st.cache_data.clear()
                        st.session_state.prev_custom_bg = custom_bg
                except Exception as e:
                    st.error(f"Error loading custom background: {str(e)}. Ensure the file is a valid image (PNG, JPG, JPEG, or WEBP).")

    st.markdown("### Upload Images")
    col1, col2 = st.columns([3, 1])
    with col1:
        images = st.file_uploader(
            "Select images to process",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Upload one or more images for background removal and replacement",
            key="image_uploader"
        )
    with col2:
        resize_option = st.checkbox("Resize images", help="Reduce image size for faster processing", key="resize_option")
        max_width = None
        if resize_option:
            max_width = st.slider("Max width (px)", 200, 2000, 800, help="Set maximum width for resized images", key="resize_slider")
    
    if st.button("Reset All", key="reset_button"):
        st.cache_data.clear()  # Clear cache on reset
        st.rerun()  # type: ignore
    
    st.markdown('</div>', unsafe_allow_html=True)

# Cache image processing
@st.cache_data
def process_image(image_data: bytes, max_width: Optional[int], bg_option: str, _selected_background: Optional[Image.Image], background_color: Optional[Tuple[int, int, int]], style_choice: str) -> Tuple[str, bytes, Image.Image]:
    try:
        stream = io.BytesIO(image_data)
        stream.seek(0)
        with Image.open(stream) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            if max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            bg_removed = remove(img)
            if isinstance(bg_removed, Image.Image):
                output_image = bg_removed
            else:
                stream = io.BytesIO(bg_removed)
                stream.seek(0)
                output_image = Image.open(stream)
            
            if bg_option != "Remove Only":
                final_image = replace_background(img, output_image, _selected_background, background_color)
                output_format = "JPEG"
                file_extension = "jpg"
                mime_type = "image/jpeg"
            else:
                final_image = output_image
                output_format = "PNG"
                file_extension = "png"
                mime_type = "image/png"
            
            output_stream = io.BytesIO()
            if output_format == "PNG":
                final_image.save(output_stream, format="PNG")
            else:
                final_image.save(output_stream, format="JPEG", quality=95)
            
            output_stream.seek(0)
            base_name = "processed"
            style_name = style_choice.lower().replace(" ", "_")
            filename = f"{bg_option.lower().replace(' ', '_')}_{style_name}_{base_name}_{uuid.uuid4().hex[:8]}.{file_extension}"
            
            return filename, output_stream.getvalue(), final_image
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}. Ensure the file is a valid PNG, JPG, JPEG, or WEBP.")

# Process images
if images:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Processed Images")
    progress_bar = st.progress(0)
    processed_images = []
    
    with st.spinner("Processing images..."):
        for idx, image in enumerate(images):
            try:
                # Validate image file before processing
                stream = io.BytesIO(image.read())
                stream.seek(0)
                Image.open(stream).verify()  # Verify image is valid
                stream.seek(0)  # Reset stream position after verification
                
                # Use selected_background directly, as cache is cleared on changes
                filename, img_data, final_image = process_image(
                    stream.read(), max_width, bg_option, selected_background, background_color, style_choice
                )
                
                st.markdown(f"#### Image {idx + 1}: {image.name}")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Original**")
                    stream.seek(0)  # Reset stream for original image display
                    with Image.open(stream) as orig_img:
                        if max_width:
                            ratio = max_width / orig_img.width
                            new_height = int(orig_img.height * ratio)
                            orig_img = orig_img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                        st.image(orig_img, width=400)
                
                with col2:
                    st.markdown("**Processed**")
                    st.image(final_image, width=400)
                    
                    st.download_button(
                        label=f"Download Image {idx + 1}",
                        data=img_data,
                        file_name=filename,
                        mime="image/jpeg" if bg_option != "Remove Only" else "image/png",
                        key=f"download_{idx}_{uuid.uuid4()}"
                    )
                
                processed_images.append((filename, img_data))
                progress_bar.progress((idx + 1) / len(images))
            
            except Exception as e:
                st.error(f"Error processing image {idx + 1}: {str(e)}. Please ensure the image is a valid PNG, JPG, JPEG, or WEBP file.")
    
    if len(processed_images) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, img_data in processed_images:
                zip_file.writestr(filename, img_data)
        zip_buffer.seek(0)
        st.download_button(
            label="Download All Images as ZIP",
            data=zip_buffer.getvalue(),
            file_name="processed_images.zip",
            mime="application/zip",
            key=f"download_zip_{uuid.uuid4()}"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.info("👆 Upload images to start processing! Supported formats: PNG, JPG, JPEG, WEBP.")
    st.markdown("### How It Works")
    if BACKGROUNDS_MODULE_AVAILABLE:
        st.markdown("""
        - **Remove Only**: Outputs a transparent PNG with the background removed.
        - **Studio Backgrounds**: Professional studio effects (Solid Color, Passport, Portrait, Group Photo, Professional Headshot).
        - **Preset Backgrounds**: Choose from a library of preloaded backgrounds.
        - **Custom Background**: Upload your own background image.
        """)
    else:
        st.markdown("""
        - **Remove Only**: Outputs a transparent PNG.
        - **Studio Backgrounds**: Requires backgrounds.py for advanced effects.
        - **Preset Backgrounds**: Choose from a library or generated backgrounds.
        - **Custom Background**: Upload your own background image.
        """)
    st.markdown("### Tips for Best Results")
    st.markdown("""
    - Use high-contrast images for better subject separation.
    - Ensure good lighting on your subject.
    - Avoid complex backgrounds in original photos.
    - Choose studio colors that complement your subject.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
with st.container():
    st.markdown("""
    <div class="footer">
        <h4>About</h4>
        <p>Made with ❤️ by [Parimal Hodar]</p>
        <p>✅ Studio Backgrounds: 5 styles, 15 colors</p>
        <h4>Features</h4>
        <p>Professional studio backgrounds<br>Custom background upload<br>Batch processing<br>High-quality output<br>Mobile & desktop optimized</p>
    </div>
    """, unsafe_allow_html=True)
