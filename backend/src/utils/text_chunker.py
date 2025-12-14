from typing import List, Dict, Any
import re


class TextChunker:
    """Utility for chunking text into smaller pieces for embedding"""

    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk(self, text: str, source_path: str = None) -> List[Dict[str, Any]]:
        """
        Chunk text into smaller pieces with overlap
        """
        if not text:
            return []

        # Split text into sentences to avoid breaking them
        sentences = self._split_into_sentences(text)

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for sentence in sentences:
            # If adding this sentence would exceed the chunk size
            if len(current_chunk) + len(sentence) > self.max_chunk_size:
                # If the current chunk is not empty, save it
                if current_chunk.strip():
                    chunks.append({
                        "content": current_chunk.strip(),
                        "source_path": source_path,
                        "chunk_index": chunk_index
                    })
                    chunk_index += 1

                # Start a new chunk with potential overlap
                # Add overlap from the end of the previous chunk
                if self.overlap > 0 and chunks:
                    last_chunk_content = chunks[-1]["content"]
                    overlap_text = self._get_overlap_text(last_chunk_content)
                    current_chunk = overlap_text + sentence
                else:
                    current_chunk = sentence
            else:
                # Add sentence to current chunk
                current_chunk += sentence

        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "source_path": source_path,
                "chunk_index": chunk_index
            })

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences while preserving the sentence structure
        """
        # Use regex to split on sentence endings but keep the punctuation
        sentence_endings = re.compile(r'([.!?]+["\']*)\s+')
        parts = sentence_endings.split(text)

        # Reconstruct sentences by pairing text with their ending punctuation
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            if i + 1 < len(parts):
                sentence = parts[i] + parts[i + 1]
                sentences.append(sentence)
            elif i < len(parts):
                # Handle the last part if it doesn't have a sentence ending
                sentences.append(parts[i])

        # Add any remaining text that wasn't processed
        if len(parts) % 2 == 1 and parts[-1].strip():
            sentences.append(parts[-1])

        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _get_overlap_text(self, text: str) -> str:
        """
        Get the last few words from text for overlap
        """
        words = text.split()
        overlap_words = words[-(self.overlap // 5):]  # Rough approximation
        return " ".join(overlap_words) + " "