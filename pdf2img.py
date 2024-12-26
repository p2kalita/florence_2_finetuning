import os
from pdf2image import convert_from_path
 
def process_pdf_folder(input_folder):
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        return
 
    # Create a 'jpg' folder inside the input folder
    jpg_folder = os.path.join(input_folder, "jpg")
    os.makedirs(jpg_folder, exist_ok=True)
 
    # Process each PDF file in the input folder
    pdf_files = sorted([file for file in os.listdir(input_folder) if file.lower().endswith(".pdf")])
 
    for file in pdf_files:
        pdf_name = os.path.splitext(file)[0]
        pdf_path = os.path.join(input_folder, file)
 
        # Create a folder for the current PDF inside the 'jpg' folder
        pdf_output_folder = os.path.join(jpg_folder, pdf_name)
        os.makedirs(pdf_output_folder, exist_ok=True)
 
        # Convert the PDF to images
        try:
            images = convert_from_path(pdf_path, dpi=300)
            print(f"Processing '{file}'...")
 
            # Save each page as an image in sorted order
            for i, image in enumerate(images):
                image_filename = f"{pdf_name}_{i + 1:03d}.jpg"  
                image_path = os.path.join(pdf_output_folder, image_filename)
                image.save(image_path, "JPEG")
 
            print(f"Saved images for '{file}' in '{pdf_output_folder}'.")
        except Exception as e:
            print(f"Error processing '{file}': {str(e)}")
 
# Example usage
input_folder = r"C:\\projects\\vlm\\gemini\\pdf"
process_pdf_folder(input_folder)