import streamlit as st
import io
import base64
from PIL import Image
import time

# Set page configuration
st.set_page_config(
    page_title="AI Content Generator Demo",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
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
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #667eea;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #5a6fd8;
        border: none;
    }
    
    .upload-section {
        border: 2px dashed #cccccc;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .generation-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def create_download_link(content, filename, content_type="application/octet-stream"):
    """
    Creates a download link for content.
    
    Args:
        content: The content to download (bytes or file-like object)
        filename: Name for the downloaded file
        content_type: MIME type of the content
    
    Returns:
        HTML string for download link
    """
    if isinstance(content, str):
        # If content is a string (like base64), convert to bytes
        b64 = content
    else:
        # If content is bytes, encode to base64
        b64 = base64.b64encode(content).decode()
    
    href = f'<a href="data:{content_type};base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def simulate_generation(content_type="image", delay=2):
    """
    Simulates AI generation process with a progress bar.
    In a real app, this would call your AI generation API.
    
    Args:
        content_type: Type of content to generate ("image" or "video")
        delay: Simulation delay in seconds
    
    Returns:
        Simulated generated content
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f'Generating {content_type}... {i+1}%')
        time.sleep(delay/100)  # Simulate processing time
    
    status_text.text(f'{content_type.title()} generation complete!')
    progress_bar.empty()
    status_text.empty()
    
    # Return placeholder content (in real app, return actual generated content)
    if content_type == "image":
        # Create a simple placeholder image
        img = Image.new('RGB', (512, 512), color='lightblue')
        return img
    else:  # video
        return "video_placeholder.mp4"  # In real app, return actual video file

# Main header
st.markdown('<div class="main-header"><h1>🎨 AI Content Generator Demo</h1><p>Create amazing content with AI-powered tools</p></div>', unsafe_allow_html=True)

# Create two columns
left_col, right_col = st.columns(2)

# LEFT COLUMN - Banner/Short-form Content Generator
with left_col:
    st.markdown('<div class="column-header"><h2>📱 Banner & Short-form Generator</h2></div>', unsafe_allow_html=True)
    
    # Content type selection menu
    st.subheader("Content Type")
    content_type = st.selectbox(
        "Select content type:",
        ["🎯 Banner", "📱 Short-form Video"],
        key="left_content_type"
    )
    
    # Text input for content description
    st.subheader("Content Description")
    left_text_input = st.text_area(
        "Describe what you want to generate:",
        placeholder="e.g., Create a promotional banner for a coffee shop with warm colors and cozy atmosphere...",
        height=100,
        key="left_text_input"
    )
    
    # Image upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("📸 Add Reference Image (Optional)")
    left_uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png', 'webp'],
        key="left_file_uploader",
        help="Upload a reference image to guide the generation"
    )
    
    # Display uploaded image if any
    if left_uploaded_file is not None:
        left_image = Image.open(left_uploaded_file)
        st.image(left_image, caption="Reference Image", use_column_width=True)
        st.success(f"✅ Uploaded: {left_uploaded_file.name}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generation button
    st.markdown('<div class="generation-section">', unsafe_allow_html=True)
    if st.button("🚀 Generate Content", key="left_generate", type="primary"):
        if left_text_input.strip():
            # Determine output type based on selection
            output_type = "video" if "Video" in content_type else "image"
            
            # Simulate generation process
            with st.spinner(f'Generating {output_type}...'):
                generated_content = simulate_generation(output_type)
            
            # Store in session state for persistence
            st.session_state[f'left_generated_{output_type}'] = generated_content
            st.success(f"✨ {output_type.title()} generated successfully!")
        else:
            st.error("⚠️ Please enter a content description first!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Output display section
    st.subheader("Generated Output")
    
    # Display generated image
    if 'left_generated_image' in st.session_state:
        st.image(st.session_state['left_generated_image'], caption="Generated Image", use_column_width=True)
        
        # Create download button for image
        img_buffer = io.BytesIO()
        st.session_state['left_generated_image'].save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Image",
            data=img_bytes,
            file_name="generated_banner.png",
            mime="image/png",
            key="left_download_image"
        )
    
    # Display generated video placeholder
    if 'left_generated_video' in st.session_state:
        st.info("🎥 Video generated! (Demo placeholder)")
        st.video("https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4")  # Demo video
        
        # Download button for video (placeholder)
        st.download_button(
            label="📥 Download Video",
            data=b"video_placeholder_data",  # In real app, use actual video data
            file_name="generated_video.mp4",
            mime="video/mp4",
            key="left_download_video"
        )

# RIGHT COLUMN - Image Generator/Editor
with right_col:
    st.markdown('<div class="column-header"><h2>🖼️ Image Generator & Editor</h2></div>', unsafe_allow_html=True)
    
    # Text input for image generation
    st.subheader("Image Generation Prompt")
    right_text_input = st.text_area(
        "Describe the image you want to generate:",
        placeholder="e.g., A beautiful sunset over mountains with vibrant orange and purple colors...",
        height=100,
        key="right_text_input"
    )
    
    # Image upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("📸 Upload Image to Edit")
    right_uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png', 'webp'],
        key="right_file_uploader",
        help="Upload an image to edit or use as reference"
    )
    
    # Display uploaded image if any
    if right_uploaded_file is not None:
        right_image = Image.open(right_uploaded_file)
        st.image(right_image, caption="Uploaded Image", use_column_width=True)
        st.success(f"✅ Uploaded: {right_uploaded_file.name}")
        
        # Image editing options
        st.subheader("Editing Options")
        edit_option = st.selectbox(
            "Choose editing action:",
            ["Generate Similar", "Style Transfer", "Background Removal", "Color Enhancement"],
            key="edit_option"
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generation button
    st.markdown('<div class="generation-section">', unsafe_allow_html=True)
    if st.button("🎨 Generate/Edit Image", key="right_generate", type="primary"):
        if right_text_input.strip() or right_uploaded_file is not None:
            # Simulate generation process
            with st.spinner('Processing image...'):
                generated_image = simulate_generation("image")
            
            # Store in session state
            st.session_state['right_generated_image'] = generated_image
            st.success("✨ Image processed successfully!")
        else:
            st.error("⚠️ Please enter a prompt or upload an image first!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Output display section
    st.subheader("Generated/Edited Output")
    
    if 'right_generated_image' in st.session_state:
        st.image(st.session_state['right_generated_image'], caption="Generated/Edited Image", use_column_width=True)
        
        # Create download button for image
        img_buffer = io.BytesIO()
        st.session_state['right_generated_image'].save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Image",
            data=img_bytes,
            file_name="generated_image.png",
            mime="image/png",
            key="right_download_image"
        )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🚀 Built with Streamlit | 🎨 AI Content Generator Demo</p>
        <p><em>This is a demonstration interface. In a production app, connect to actual AI generation APIs.</em></p>
    </div>
    """, 
    unsafe_allow_html=True
)
