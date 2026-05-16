"""Image processing utilities"""

import os
import base64


def find_image_path(image_id, base_path):
    """
    Find the full path to an image by searching through subfolders
    
    Args:
        image_id: Image ID string
        base_path: Base directory path to search
        
    Returns:
        Full path to image file or None if not found
    """
    if not image_id:
        return None
    
    image_filename = f"{image_id}.jpg"
    
    try:
        for root, dirs, files in os.walk(base_path):
            if image_filename in files:
                full_path = os.path.join(root, image_filename)
                return full_path
        return None
    except Exception as e:
        print(f"Error searching for image {image_filename}: {e}")
        return None


def image_to_base64(image_path):
    """
    Convert image to base64 string for web display
    
    Args:
        image_path: Path to image file
        
    Returns:
        Base64 encoded data URL string or None
    """
    try:
        if not image_path or not os.path.exists(image_path):
            return None
            
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/jpeg;base64,{img_b64}"
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None


def validate_image(image_path):
    """
    Validate if image file exists and is readable
    
    Args:
        image_path: Path to image file
        
    Returns:
        Boolean indicating if image is valid
    """
    return image_path and os.path.exists(image_path) and os.path.isfile(image_path)