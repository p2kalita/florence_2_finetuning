from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from PIL import Image
import pandas as pd
import os
from tqdm import tqdm  # Import tqdm for progress display

# Initialize the Form Recognizer client
endpoint = "https://usi-ibbs.cognitiveservices.azure.com/"
key = "426a4dc22cb24d289fbfcac1d5db72da"
form_recognizer_client = FormRecognizerClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Function to compress images
def compress_image(image_path, output_path, quality=85):
    with Image.open(image_path) as img:
        img.save(output_path, format="JPEG", quality=quality)

# Function to extract header and footer
def extract_header_footer(image_path, header_height=300, footer_height=300):
    with Image.open(image_path) as img:
        width, height = img.size
        header = img.crop((0, 0, width, header_height))
        footer = img.crop((0, height - footer_height, width, height))
        
        return header, footer

# Function to process a single image and extract header/footer text
def process_image(image_path, form_recognizer_client, header_height=300, footer_height=300):
    try:
        # Compress the image (optional)
        compressed_image_path = f"{os.path.splitext(image_path)[0]}_compressed.jpg"
        compress_image(image_path, compressed_image_path)
        
        # Extract header and footer
        header, footer = extract_header_footer(compressed_image_path, header_height, footer_height)
        
        # Perform OCR on header and footer
        header_text, footer_text = "", ""
        for region, region_type in zip([header, footer], ["header", "footer"]):
            with open(compressed_image_path, "rb") as image:
                poller = form_recognizer_client.begin_recognize_content(image)
                pages = poller.result()
                extracted_text = "\n".join(line.text for page in pages for line in page.lines)
                if region_type == "header":
                    header_text = extracted_text
                else:
                    footer_text = extracted_text

        return header_text, footer_text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None, None

# Function to process a folder containing subfolders of document images
def process_folder(input_folder, form_recognizer_client):
    results = []
    # Collect all image files from subfolders
    image_files = [
        (os.path.join(root, file), os.path.basename(root))  # (file_path, folder_name)
        for root, _, files in os.walk(input_folder)
        for file in files if file.lower().endswith(('.tiff', '.jpg', '.jpeg', '.png'))
    ]
    
    # Process images with tqdm to show progress
    for image_path, folder_name in tqdm(image_files, desc="Processing Images", unit="image"):
        # Process the image and extract text
        header_text, footer_text = process_image(image_path, form_recognizer_client)
        
        if header_text or footer_text:
            results.append({
                "document": folder_name,
                "page_number": os.path.splitext(os.path.basename(image_path))[0],  # Extract page number from file name
                "header": header_text,
                "footer": footer_text
            })
    
    # Convert results to DataFrame
    df = pd.DataFrame(results)
    return df

# Input folder containing subfolders of images
input_folder = r"C:\projects\vlm\gemini\images"

# Process the folder and get the results in a DataFrame
df = process_folder(input_folder, form_recognizer_client)

# Output the results
print("Processing complete. Output DataFrame:")
print(df)

# Save the DataFrame to a CSV file
output_csv_path = os.path.join(input_folder, "output.csv")
df.to_csv(output_csv_path, index=False)
print("Results saved to:", output_csv_path)
