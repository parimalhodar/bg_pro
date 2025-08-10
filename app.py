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

# Enhanced Custom CSS with Mobile-First Design and Advanced Color Effects
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* CSS Variables for consistent theming */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --success-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --dark-gradient: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        --light-gradient: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --text-light: #9ca3af;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-card: rgba(255, 255, 255, 0.95);
        --border-color: rgba(255, 255, 255, 0.2);
        --shadow-light: 0 4px 20px rgba(0, 0, 0, 0.08);
        --shadow-medium: 0 8px 30px rgba(0, 0, 0, 0.12);
        --shadow-heavy: 0 15px 50px rgba(0, 0, 0, 0.15);
        --border-radius: 16px;
        --border-radius-sm: 12px;
        --border-radius-lg: 24px;
    }
    
    /* Main app container with enhanced background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    /* Enhanced main container */
    .main .block-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
        background: transparent;
    }
    
    /* Glassmorphism card effect */
    .card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-medium);
        margin-bottom: 2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        border-radius: var(--border-radius) var(--border-radius) 0 0;
    }
    
    .card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-heavy);
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    /* Enhanced buttons with gradient effects */
    .stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: var(--border-radius-sm);
        padding: 1rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        width: 100%;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-light);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover,
    .stButton > button:focus {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
        background: var(--secondary-gradient);
        outline: none;
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-light);
    }
    
    /* Header with enhanced styling */
    .header {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-medium);
        z-index: 100;
    }
    
    .header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        animation: rotate 10s linear infinite;
    }
    
    @keyframes rotate {
        to { transform: rotate(360deg); }
    }
    
    .header > * {
        position: relative;
        z-index: 2;
    }
    
    .header h1 {
        font-size: clamp(1.8rem, 5vw, 3rem);
        font-weight: 700;
        font-family: 'Poppins', sans-serif;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .header p {
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        color: var(--text-secondary);
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        line-height: 1.3;
    }
    
    h2 {
        font-size: clamp(1.5rem, 3vw, 2rem);
        background: var(--dark-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h3 {
        font-size: clamp(1.3rem, 2.5vw, 1.8rem);
        color: var(--primary-color);
    }
    
    h4 {
        font-size: clamp(1.1rem, 2vw, 1.5rem);
        color: var(--secondary-color);
    }
    
    /* Enhanced form elements */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--border-radius-sm);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        outline: none;
    }
    
    /* Enhanced radio buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.7);
        border-radius: var(--border-radius-sm);
        padding: 1rem;
        gap: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .stRadio > div > label {
        background: rgba(255, 255, 255, 0.9);
        border-radius: var(--border-radius-sm);
        padding: 0.8rem 1.2rem;
        margin: 0.3rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        font-weight: 500;
        color: var(--text-primary);
    }
    
    .stRadio > div > label:hover {
        background: var(--accent-gradient);
        color: white;
        transform: translateX(5px);
    }
    
    /* Enhanced checkboxes */
    .stCheckbox > label {
        font-weight: 500;
        color: var(--text-primary);
        cursor: pointer;
    }
    
    /* Enhanced sliders */
    .stSlider > div > div > div > div {
        background: var(--primary-gradient);
    }
    
    /* Enhanced file uploader */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.8);
        border: 2px dashed var(--primary-color);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stFileUploader > div:hover {
        border-color: var(--secondary-color);
        background: rgba(255, 255, 255, 0.9);
        transform: scale(1.02);
    }
    
    /* Enhanced images */
    .stImage img {
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-light);
        transition: all 0.3s ease;
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
    .stImage img:hover {
        transform: scale(1.05);
        box-shadow: var(--shadow-medium);
        border-color: var(--primary-color);
    }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Enhanced expander */
    .streamlit-expanderHeader {
        background: var(--accent-gradient);
        color: white;
        border-radius: var(--border-radius-sm);
        font-weight: 600;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 0 0 var(--border-radius-sm) var(--border-radius-sm);
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-top: none;
    }
    
    /* Enhanced progress bar */
    .stProgress > div > div > div > div {
        background: var(--success-gradient);
        border-radius: 10px;
    }
    
    /* Enhanced info/warning/error messages */
    .stAlert {
        border-radius: var(--border-radius-sm);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Enhanced footer */
    .footer {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        padding: 2.5rem 2rem;
        text-align: center;
        margin-top: 3rem;
        box-shadow: var(--shadow-medium);
    }
    
    .footer h4 {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }
    
    .footer p {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.8;
    }
    
    /* Loading spinner */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    /* Hover effects for interactive elements */
    .element-container:hover {
        transition: all 0.3s ease;
    }
    
    /* Enhanced mobile responsiveness */
    @media (max-width: 768px) {
        :root {
            --border-radius: 12px;
            --border-radius-sm: 8px;
            --border-radius-lg: 16px;
        }
        
        .main .block-container {
            padding: 0.5rem;
        }
        
        .card {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border-radius: var(--border-radius);
        }
        
        .header {
            padding: 2rem 1.5rem;
            border-radius: var(--border-radius);
        }
        
        .header h1 {
            font-size: clamp(1.5rem, 6vw, 2.5rem);
            line-height: 1.2;
        }
        
        .header p {
            font-size: clamp(0.9rem, 3vw, 1.1rem);
        }
        
        .stButton > button {
            padding: 0.8rem 1.5rem;
            font-size: 0.9rem;
            border-radius: var(--border-radius-sm);
        }
        
        .stImage img {
            max-width: 100%;
            height: auto;
            border-radius: var(--border-radius-sm);
        }
        
        .stColumn {
            padding: 0.5rem 0;
        }
        
        .stRadio > div {
            padding: 0.8rem;
            gap: 0.8rem;
        }
        
        .stRadio > div > label {
            padding: 0.6rem 1rem;
            margin: 0.2rem 0;
            font-size: 0.9rem;
        }
        
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            font-size: 16px; /* Prevents zoom on iOS */
            border-radius: var(--border-radius-sm);
        }
        
        .footer {
            padding: 2rem 1.5rem;
            margin-top: 2rem;
        }
        
        .footer h4 {
            font-size: 1.3rem;
        }
        
        .footer p {
            font-size: 0.9rem;
        }
    }
    
    /* Ultra mobile (small phones) */
    @media (max-width: 480px) {
        .main .block-container {
            padding: 0.25rem;
        }
        
        .card {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .header {
            padding: 1.5rem 1rem;
        }
        
        .stButton > button {
            padding: 0.7rem 1rem;
            font-size: 0.85rem;
        }
        
        .stRadio > div > label {
            padding: 0.5rem 0.8rem;
            font-size: 0.85rem;
        }
        
        .footer {
            padding: 1.5rem 1rem;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #f9fafb;
            --text-secondary: #d1d5db;
            --text-light: #9ca3af;
            --bg-primary: rgba(17, 24, 39, 0.95);
            --bg-secondary: rgba(31, 41, 55, 0.95);
            --bg-card: rgba(31, 41, 55, 0.95);
            --border-color: rgba(75, 85, 99, 0.3);
        }
        
        .stApp {
            background: linear-gradient(135deg, #1f2937 0%, #374151 50%, #4b5563 100%);
        }
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .card {
            border: 2px solid var(--primary-color);
            background: var(--bg-primary);
        }
        
        .header {
            border: 2px solid var(--primary-color);
            background: var(--bg-primary);
        }
    }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Print styles */
    @media print {
        .stApp {
            background: white;
            color: black;
        }
        
        .card, .header, .footer {
            background: white;
            box-shadow: none;
            border: 1px solid #ccc;
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
        <p>Transform your images with professional background removal and stunning studio effects.</p>
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
                    st.image(selected_background, caption=f"{style_choice} Preview", width=150)
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
                                st.image(selected_background, caption="Selected Background", width=150)
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
                    st.image(selected_background, caption="Generated Background", width=150)

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
                        st.image(selected_background, caption="Custom Background", width=150)
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
                        st.image(orig_img, width=150)
                
                with col2:
                    st.markdown("**Processed**")
                    st.image(final_image, width=150)
                    
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
