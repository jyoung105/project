import streamlit as st
import io
import base64
from PIL import Image
import time
import os
import tempfile
import replicate
import requests

# API Key configuration
# These should be set as environment variables or Streamlit secrets
FAL_API_KEY = st.secrets.get("FAL_API_KEY") or os.getenv("FAL_API_KEY")
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
REPLICATE_API_TOKEN = st.secrets.get("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_TOKEN")

# Configure Replicate client
if REPLICATE_API_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# Set page configuration
st.set_page_config(
    page_title="AI Content Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .column-header {
        text-align: center;
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    .input-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 1.5rem;
    }
    
    .result-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #667eea;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1rem;
        font-weight: 600;
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        background-color: #5a6fd8;
        border: none;
    }
    
    .download-button {
        margin-top: 1rem;
    }
    
    .aspect-ratio-info {
        background-color: #e3f2fd;
        padding: 0.5rem;
        border-radius: 5px;
        margin-top: 0.5rem;
        font-size: 0.9em;
        color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_keys():
    """
    Check if required API keys are configured.
    
    Returns:
        tuple: (bool, str) - (keys_available, error_message)
    """
    missing_keys = []
    if not FAL_API_KEY:
        missing_keys.append("FAL_API_KEY")
    if not GOOGLE_API_KEY:
        missing_keys.append("GOOGLE_API_KEY")
    if not REPLICATE_API_TOKEN:
        missing_keys.append("REPLICATE_API_TOKEN")
    
    if missing_keys:
        return False, f"Missing API keys: {', '.join(missing_keys)}"
    return True, ""

def save_uploaded_file(uploaded_file):
    """
    Save an uploaded file to a temporary location and return the path.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        str: Path to the saved temporary file
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def process_api_output(output, content_type="image"):
    """
    Process the output from Replicate API.
    
    Args:
        output: The output from Replicate API
        content_type: Type of content ("image" or "video")
    
    Returns:
        Processed content (PIL Image for images, URL for videos)
    """
    try:
        if content_type == "image":
            # Handle different output formats
            if isinstance(output, str):
                # If it's a URL, download the image
                response = requests.get(output)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                return image
            elif isinstance(output, list) and len(output) > 0:
                # If it's a list, take the first item
                url = str(output[0])
                response = requests.get(url)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                return image
            elif hasattr(output, 'url'):
                # If it has a URL attribute
                response = requests.get(output.url)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                return image
            else:
                st.error(f"Unexpected output format: {type(output)}")
                return None
        else:
            # For video, return the URL or first item
            if isinstance(output, str):
                return output
            elif isinstance(output, list) and len(output) > 0:
                return str(output[0])
            elif hasattr(output, 'url'):
                return output.url
            else:
                st.error(f"Unexpected output format: {type(output)}")
                return None
                
    except Exception as e:
        st.error(f"Error processing API output: {str(e)}")
        return None

def generate_banner(text, image_path, aspect_ratio="vertical"):
    """
    Generate a banner using Replicate API.
    
    Args:
        text: User's text description
        image_path: Path to the reference image
        aspect_ratio: Aspect ratio for the banner
    
    Returns:
        Generated banner content or None if failed
    """
    try:
        # Check API keys
        keys_ok, error_msg = check_api_keys()
        if not keys_ok:
            st.error(f"API Configuration Error: {error_msg}")
            return None
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Initializing banner generation...")
        progress_bar.progress(10)
        
        # Open the image file
        with open(image_path, "rb") as image_file:
            status_text.text("Calling AI Agent...")
            progress_bar.progress(30)
            
            # Call Replicate API for banner generation
            output = replicate.run(
                "smoretalk/banner-agent:3c5abcaa3101f9e9b216ae60d89aeca98f5223dacd8399613504f1aebc32cfea",
                input={
                    "text": text,
                    "image": image_file,
                    "f_api_key": FAL_API_KEY,
                    "g_api_key": GOOGLE_API_KEY,
                    "aspect_ratio": aspect_ratio
                }
            )
            
            progress_bar.progress(90)
            status_text.text("Processing results...")
            
        # Process the API output
        processed_output = process_api_output(output, "image")
        
        progress_bar.progress(100)
        status_text.text("Banner generation complete!")
        
        # Clean up progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return processed_output
        
    except Exception as e:
        st.error(f"Error generating banner: {str(e)}")
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_text' in locals():
            status_text.empty()
        return None

def generate_short_form_video(text, image_path):
    """
    Generate a short-form video using Replicate API.
    
    Args:
        text: User's text description
        image_path: Path to the reference image
    
    Returns:
        Generated video content or None if failed
    """
    try:
        # Check API keys
        keys_ok, error_msg = check_api_keys()
        if not keys_ok:
            st.error(f"API Configuration Error: {error_msg}")
            return None
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Initializing video generation...")
        progress_bar.progress(10)
        
        # Open the image file
        with open(image_path, "rb") as image_file:
            status_text.text("Calling AI Agent...")
            progress_bar.progress(30)
            
            # Call Replicate API for short-form video generation
            output = replicate.run(
                "smoretalk/short-form-agent:c712a086199c854d29172eb9434c34ba812d2312c414ca0466ea3acc30e14029",
                input={
                    "text": text,
                    "image": image_file,
                    "f_api_key": FAL_API_KEY,
                    "g_api_key": GOOGLE_API_KEY
                }
            )
            
            progress_bar.progress(90)
            status_text.text("Processing results...")
            
        # Process the API output
        processed_output = process_api_output(output, "video")
        
        progress_bar.progress(100)
        status_text.text("Video generation complete!")
        
        # Clean up progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return processed_output
        
    except Exception as e:
        st.error(f"Error generating video: {str(e)}")
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_text' in locals():
            status_text.empty()
        return None

def edit_image(text, image_path):
    """
    Edit an image using Replicate API.
    
    Args:
        text: User's editing instructions
        image_path: Path to the image to edit
    
    Returns:
        Edited image content or None if failed
    """
    try:
        # Check API keys
        keys_ok, error_msg = check_api_keys()
        if not keys_ok:
            st.error(f"API Configuration Error: {error_msg}")
            return None
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Initializing image editing...")
        progress_bar.progress(10)
        
        # Open the image file
        with open(image_path, "rb") as image_file:
            status_text.text("Calling AI Agent...")
            progress_bar.progress(30)
            
            # Call Replicate API for image editing
            output = replicate.run(
                "smoretalk/edit-agent:155b8d038510340657a71cd97fccdfdd27bf8d60a3165a1db5b662954508bc63",
                input={
                    "text": text,
                    "image": image_file,
                    "f_api_key": FAL_API_KEY,
                    "g_api_key": GOOGLE_API_KEY
                }
            )
            
            progress_bar.progress(90)
            status_text.text("Processing results...")
            
        # Process the API output
        processed_output = process_api_output(output, "image")
        
        progress_bar.progress(100)
        status_text.text("Image editing complete!")
        
        # Clean up progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return processed_output
        
    except Exception as e:
        st.error(f"Error editing image: {str(e)}")
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_text' in locals():
            status_text.empty()
        return None

def cleanup_temp_file(file_path):
    """
    Clean up temporary files.
    
    Args:
        file_path: Path to the temporary file to delete
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        st.warning(f"Could not clean up temporary file: {str(e)}")

# Main header
st.markdown('<div class="main-header"><h1>🎨 AI Content Generator</h1><p>Create banners, videos, and edit images with AI</p></div>', unsafe_allow_html=True)

# Check API key configuration and show warning if needed
keys_ok, error_msg = check_api_keys()
if not keys_ok:
    st.error(f"""
    ⚠️ **API Configuration Required**
    
    {error_msg}
    
    **Setup Instructions:**
    1. Create a `.streamlit/secrets.toml` file in your project directory
    2. Add your API keys as shown in the template
    3. Restart the application
    
    **OR** set environment variables:
    - `REPLICATE_API_TOKEN`
    - `FAL_API_KEY`
    - `GOOGLE_API_KEY`
    """)
    st.info("💡 The app interface will work, but generation will fail without proper API keys.")

# Create two columns
left_col, right_col = st.columns(2)

# LEFT COLUMN - Generate Banner or Short-form Video
with left_col:
    st.markdown('<div class="column-header"><h2>🎬 Generate Banner or Short-form Video</h2></div>', unsafe_allow_html=True)
    
    # Input Container
    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.subheader("📝 Input Requirements")
        
        # Content type selection
        content_type = st.selectbox(
            "Select content type:",
            ["Banner", "Short-form Video"],
            key="left_content_type"
        )
        
        # Text input (required)
        st.markdown("**Text Description** *(Required)*")
        left_text_input = st.text_area(
            "Describe what you want to generate:",
            placeholder="e.g., Create a promotional banner for a coffee shop with warm colors and cozy atmosphere...",
            height=100,
            key="left_text_input",
            help="This field is required - describe your vision clearly!"
        )
        
        # Image picker (required)
        st.markdown("**Reference Image** *(Required)*")
        left_uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="left_file_uploader",
            help="Upload a reference image to guide the generation"
        )
        
        # Display uploaded image preview
        if left_uploaded_file is not None:
            left_image = Image.open(left_uploaded_file)
            st.image(left_image, caption=f"Reference Image: {left_uploaded_file.name}", width=200)
        
        # Aspect ratio selection (required)
        st.markdown("**Aspect Ratio** *(Required)*")
        aspect_ratio = st.selectbox(
            "Choose aspect ratio:",
            ["Vertical", "Square", "Horizontal"],
            key="aspect_ratio",
            help="Select the aspect ratio for your content"
        )
        
        # Show aspect ratio info
        aspect_info = {
            "Vertical": "9:16 ratio - Perfect for mobile content, stories",
            "Square": "1:1 ratio - Great for social media posts",
            "Horizontal": "16:9 ratio - Ideal for banners, landscape content"
        }
        if aspect_ratio:
            st.markdown(f'<div class="aspect-ratio-info">ℹ️ {aspect_info[aspect_ratio]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Generation button
    generate_disabled = not (left_text_input.strip() and left_uploaded_file is not None)
    
    if st.button("🚀 Generate Content", key="left_generate", type="primary", disabled=generate_disabled):
        if not generate_disabled:
            # Save the uploaded file temporarily
            temp_image_path = save_uploaded_file(left_uploaded_file)
            
            try:
                # Determine output type and aspect ratio
                output_type = "video" if content_type == "Short-form Video" else "banner"
                aspect_key = aspect_ratio.lower() if aspect_ratio else "square"
                
                # Call the appropriate API
                if content_type == "Short-form Video":
                    generated_content = generate_short_form_video(left_text_input, temp_image_path)
                else:  # Banner
                    generated_content = generate_banner(left_text_input, temp_image_path, aspect_key)
                
                # Store in session state if generation was successful
                if generated_content is not None:
                    st.session_state[f'left_generated_{output_type}'] = generated_content
                    st.session_state['left_generated_aspect_ratio'] = aspect_key
                    st.session_state['left_generated_content_type'] = content_type
                    st.success(f"✨ {content_type} generated successfully!")
                else:
                    st.error(f"Failed to generate {content_type.lower() if content_type else 'content'}. Please try again.")
                    
            finally:
                # Clean up temporary file
                cleanup_temp_file(temp_image_path)
    
    if generate_disabled:
        st.warning("⚠️ Please fill in all required fields (Text, Image, Aspect Ratio)")
    
    # Result Preview Container
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.subheader("🎯 Result Preview")
    
    # Display generated banner
    if 'left_generated_banner' in st.session_state:
        st.markdown("**Generated Banner:**")
        st.image(st.session_state['left_generated_banner'], caption=f"Banner ({st.session_state.get('left_generated_aspect_ratio', 'square')} aspect ratio)", use_container_width=True)
        
        # Download button for banner
        img_buffer = io.BytesIO()
        st.session_state['left_generated_banner'].save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Banner",
            data=img_bytes,
            file_name=f"banner_{st.session_state.get('left_generated_aspect_ratio', 'square')}.png",
            mime="image/png",
            key="left_download_banner"
        )
    
    # Display generated video
    elif 'left_generated_video' in st.session_state:
        st.markdown("**Generated Short-form Video:**")
        
        # Get the video URL
        video_url = st.session_state['left_generated_video']
        
        # Display video info
        st.info(f"🎥 Video generated ({st.session_state.get('left_generated_aspect_ratio', 'square')} aspect ratio)")
        
        if video_url:
            # Display the actual generated video
            st.video(video_url)
            
            # Download button for video
            try:
                # Try to get video data for download
                response = requests.get(video_url)
                response.raise_for_status()
                video_data = response.content
                
                st.download_button(
                    label="📥 Download Video",
                    data=video_data,
                    file_name=f"video_{st.session_state.get('left_generated_aspect_ratio', 'square')}.mp4",
                    mime="video/mp4",
                    key="left_download_video"
                )
            except Exception as e:
                st.warning(f"Could not prepare video for download: {str(e)}")
                st.markdown(f"**Direct Link**: [Download Video]({video_url})")
        else:
            st.error("Video URL not available")
    
    else:
        st.info("👆 Generate content above to see results here")
    
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN - Edit Image
with right_col:
    st.markdown('<div class="column-header"><h2>✏️ Edit Image</h2></div>', unsafe_allow_html=True)
    
    # Input Container
    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.subheader("📝 Input Requirements")
        
        # Text input (required)
        st.markdown("**Edit Instructions** *(Required)*")
        right_text_input = st.text_area(
            "Describe how you want to edit the image:",
            placeholder="e.g., Change the background to a sunset, enhance colors, remove the background, add vintage filter...",
            height=100,
            key="right_text_input",
            help="This field is required - describe your editing instructions clearly!"
        )
        
        # Image picker (required)
        st.markdown("**Image to Edit** *(Required)*")
        right_uploaded_file = st.file_uploader(
            "Choose an image file to edit",
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="right_file_uploader",
            help="Upload the image you want to edit"
        )
        
        # Display uploaded image preview
        if right_uploaded_file is not None:
            right_image = Image.open(right_uploaded_file)
            st.image(right_image, caption=f"Image to Edit: {right_uploaded_file.name}", width=200)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Edit button
    edit_disabled = not (right_text_input.strip() and right_uploaded_file is not None)
    
    if st.button("🎨 Edit Image", key="right_edit", type="primary", disabled=edit_disabled):
        if not edit_disabled:
            # Save the uploaded file temporarily
            temp_image_path = save_uploaded_file(right_uploaded_file)
            
            try:
                # Call the image editing API
                edited_image = edit_image(right_text_input, temp_image_path)
                
                # Store in session state if editing was successful
                if edited_image is not None:
                    st.session_state['right_edited_image'] = edited_image
                    st.success("✨ Image edited successfully!")
                else:
                    st.error("Failed to edit image. Please try again.")
                    
            finally:
                # Clean up temporary file
                cleanup_temp_file(temp_image_path)
    
    if edit_disabled:
        st.warning("⚠️ Please fill in all required fields (Edit Instructions, Image)")
    
    # Result Preview Container
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.subheader("🎯 Result Preview")
    
    # Display edited image
    if 'right_edited_image' in st.session_state:
        st.markdown("**Edited Image:**")
        st.image(st.session_state['right_edited_image'], caption="Edited Image", use_container_width=True)
        
        # Download button for edited image
        img_buffer = io.BytesIO()
        st.session_state['right_edited_image'].save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Edited Image",
            data=img_bytes,
            file_name="edited_image.png",
            mime="image/png",
            key="right_download_image"
        )
    else:
        st.info("👆 Edit an image above to see results here")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🚀 Built with Streamlit | 🎨 AI Content Generator</p>
        <p><em>This is a demonstration interface. In a production app, connect to actual AI generation APIs.</em></p>
    </div>
    """, 
    unsafe_allow_html=True
)
