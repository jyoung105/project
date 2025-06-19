# 🎨 AI Content Generator Demo

A beautiful Streamlit web application for generating AI-powered content including banners, short-form videos, and images.

## Features

### Left Panel - Banner & Short-form Generator
- Content type selection (Banner/Short-form Video)
- Text input for content description
- Optional reference image upload (.jpg, .png, .webp)
- AI content generation simulation
- Download generated content

### Right Panel - Image Generator & Editor
- Text prompts for image generation
- Image upload for editing
- Multiple editing options (Style Transfer, Background Removal, etc.)
- AI image processing simulation
- Download processed images

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## Requirements

- Python 3.7+
- Streamlit
- Pillow (PIL)

## Demo Features

- Interactive two-column layout
- File upload with format validation
- Progress bars for generation simulation
- Download functionality for generated content
- Responsive design with custom CSS
- Session state management

## Deployment

This app is ready for deployment on:
- Streamlit Cloud
- Heroku
- AWS/GCP/Azure
- Any server with Python support 