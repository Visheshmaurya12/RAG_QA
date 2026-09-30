
from pathlib import Path
import fitz
import json

# 1. Define the input and output folders
input_folder = Path("data/raw_pdfs")
output_folder = Path("data/extracted_text")

# 2. Create the output folder if it does not exist
output_folder.mkdir(parents=True, exist_ok=True)

# 3. Find every PDF in the input folder
pdf_files = list(input_folder.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found in data/raw_pdfs/")
    
# 4. Process each PDF separately
for pdf_path in pdf_files:
    pages_data = []

    # Open the PDF
    with fitz.open(pdf_path) as document:

        # 5. Read every page separately
        for page_index, page in enumerate(document):
            text = page.get_text("text")

            # 6. Store text with its original page number
            pages_data.append({
                "document_id": pdf_path.stem,
                "source": pdf_path.name,
                "page_number": page_index + 1,
                "text": text.strip()
            })

    # 7. Save extracted pages as a JSON file
    output_file = output_folder / f"{pdf_path.stem}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(pages_data, file, ensure_ascii=False, indent=2)

    # 8. Display a summary
    extracted_pages = sum(1 for item in pages_data if item["text"])
    print(f"Processed: {pdf_path.name}")
    print(f"Total pages: {len(pages_data)}")
    print(f"Pages containing text: {extracted_pages}")
    print(f"Saved to: {output_file}")