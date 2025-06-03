import os
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
from tqdm import tqdm

def download_and_resize_image(url, target_size=(105, 158)):
    """
    Download image from URL and resize it to target dimensions while maintaining aspect ratio
    Netflix uses approximately 105x158 for their compact poster view
    """
    try:
        # Download image
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
            
        # Open image
        img = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate dimensions for resizing while maintaining aspect ratio
        original_width, original_height = img.size
        target_width, target_height = target_size
        
        # Calculate resize dimensions
        ratio = min(target_width/original_width, target_height/original_height)
        new_size = (int(original_width * ratio), int(original_height * ratio))
        
        # Resize with high quality
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Create new image with padding if necessary
        new_img = Image.new('RGB', target_size, (0, 0, 0))
        
        # Calculate position to paste resized image
        paste_x = (target_width - new_size[0]) // 2
        paste_y = (target_height - new_size[1]) // 2
        
        # Paste resized image
        new_img.paste(img, (paste_x, paste_y))
        
        return new_img
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

def process_all_posters():
    """
    Process all posters from the posters CSV file
    """
    # Create output directory if it doesn't exist
    output_dir = 'data/processed_posters'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Load posters data
        posters_df = pd.read_csv('data/posters_with_titles.csv')
        
        print(f"Processing {len(posters_df)} posters...")
        
        # Process each poster
        processed_count = 0
        for idx, row in tqdm(posters_df.iterrows(), total=len(posters_df)):
            title = row['title']
            poster_url = row['poster']
            
            if pd.isna(poster_url):
                continue
                
            # Create safe filename
            safe_title = "".join(x for x in title if x.isalnum() or x in (' ', '-', '_')).rstrip()
            output_path = os.path.join(output_dir, f"{safe_title}.jpg")
            
            # Skip if already processed
            if os.path.exists(output_path):
                processed_count += 1
                continue
            
            # Process image
            processed_img = download_and_resize_image(poster_url)
            if processed_img:
                processed_img.save(output_path, 'JPEG', quality=95)
                processed_count += 1
        
        print(f"\nSuccessfully processed {processed_count} posters")
        print(f"Posters saved to: {output_dir}")
        
    except Exception as e:
        print(f"Error processing posters: {str(e)}")

if __name__ == "__main__":
    process_all_posters() 