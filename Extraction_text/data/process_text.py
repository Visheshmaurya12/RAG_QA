import json
import re
import uuid
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def clean_text(text):
    # Remove repeated headers/footers based on observed patterns
    # Remove "RAG Dataset Notes | Academic Question Answering System\nPage X"
    text = re.sub(r'RAG Dataset Notes\s+\|\s+Academic Question Answering System\s+Page \d+\s+', '', text)
    # Remove unnecessary whitespace, while preserving paragraphs
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Clean leading/trailing whitespace
    return text.strip()

def main():
    input_dir = Path("data/extracted_text")
    cleaned_dir = Path("data/cleaned_text")
    chunks_dir = Path("data/processed_chunks")

    cleaned_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-3.5-turbo",
        chunk_size=400,
        chunk_overlap=60,
        add_start_index=True
    )

    stats = {
        "files_processed": 0,
        "pages_processed": 0,
        "chunks_created": 0,
        "empty_chunks": 0,
        "duplicate_chunks": 0,
        "validation_issues": []
    }

    seen_chunk_texts = set()

    for file_path in input_dir.glob("*.json"):
        stats["files_processed"] += 1
        with open(file_path, "r", encoding="utf-8") as f:
            pages = json.load(f)

        cleaned_pages = []
        document_id = None
        source = None
        
        full_text = ""
        page_mapping = []

        for page in pages:
            if not document_id:
                document_id = page.get("document_id", file_path.stem)
                source = page.get("source", file_path.name)
            
            stats["pages_processed"] += 1
            cleaned = clean_text(page["text"])
            
            # Save cleaned page for the cleaned dataset
            cleaned_page = {**page, "text": cleaned}
            cleaned_pages.append(cleaned_page)

            # Build full text for chunking and mapping
            start_idx = len(full_text)
            full_text += cleaned + "\n\n"
            end_idx = len(full_text)
            page_mapping.append((start_idx, end_idx, page.get("page_number", 1)))

        # Save cleaned text
        cleaned_file = cleaned_dir / file_path.name
        with open(cleaned_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_pages, f, ensure_ascii=False, indent=2)

        # Chunking
        doc = Document(page_content=full_text, metadata={"document_id": document_id, "source": source})
        split_docs = text_splitter.split_documents([doc])

        document_chunks = []
        last_found_idx = 0

        for doc_chunk in split_docs:
            chunk_text = doc_chunk.page_content.strip()
            
            if not chunk_text:
                stats["empty_chunks"] += 1
                stats["validation_issues"].append(f"Empty chunk found in {document_id}")
                continue
                
            if chunk_text in seen_chunk_texts:
                stats["duplicate_chunks"] += 1
                stats["validation_issues"].append(f"Duplicate chunk found in {document_id}")
            seen_chunk_texts.add(chunk_text)

            # Try to find actual index since Langchain sometimes returns -1 for start_index
            search_prefix = chunk_text[:100]
            found_idx = full_text.find(search_prefix, last_found_idx)
            if found_idx == -1:
                # Try shorter prefix in case of whitespace changes
                search_prefix = chunk_text[:50]
                found_idx = full_text.find(search_prefix, last_found_idx)
            if found_idx == -1:
                found_idx = full_text.find(search_prefix) # Search from beginning
                
            if found_idx != -1:
                start_idx = found_idx
                last_found_idx = found_idx + len(chunk_text) // 2
            else:
                start_idx = doc_chunk.metadata.get("start_index", -1)
                if start_idx == -1:
                    start_idx = last_found_idx

            end_idx = start_idx + len(chunk_text)
            
            page_start = None
            page_end = None
            
            for (p_start, p_end, p_num) in page_mapping:
                if p_start <= start_idx < p_end:
                    page_start = p_num
                if p_start < end_idx <= p_end:
                    page_end = p_num

            # Fallbacks
            if page_start is None and page_mapping:
                page_start = page_mapping[0][2]
            if page_end is None and page_mapping:
                page_end = page_mapping[-1][2]
                
            chunk_id = f"{document_id}_{uuid.uuid4().hex[:8]}"
            stats["chunks_created"] += 1
            
            chunk_data = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "source": source,
                "page_start": page_start,
                "page_end": page_end,
                "text": chunk_text
            }
            document_chunks.append(chunk_data)

        # Save chunks
        chunks_file = chunks_dir / f"{file_path.stem}_chunks.json"
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(document_chunks, f, ensure_ascii=False, indent=2)

    print("=== Processing Summary ===")
    print(f"Input files processed: {stats['files_processed']}")
    print(f"Pages processed:       {stats['pages_processed']}")
    print(f"Chunks created:        {stats['chunks_created']}")
    print(f"Empty chunks:          {stats['empty_chunks']}")
    print(f"Duplicate chunks:      {stats['duplicate_chunks']}")
    
    if stats["validation_issues"]:
        print(f"Validation issues:     {len(stats['validation_issues'])}")
        for issue in stats["validation_issues"][:5]:
            print(f"  - {issue}")
    else:
        print("Validation issues:     None")
        
    print(f"Outputs:")
    print(f"  Cleaned text:   {cleaned_dir}")
    print(f"  Processed text: {chunks_dir}")

if __name__ == "__main__":
    main()
