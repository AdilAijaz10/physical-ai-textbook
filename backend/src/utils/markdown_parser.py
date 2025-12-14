import re
from typing import Dict, Any, List


class MarkdownParser:
    """Utility for parsing Markdown content and extracting structure"""

    def __init__(self):
        pass

    def parse(self, markdown_content: str) -> str:
        """
        Parse markdown content and return plain text content
        This method extracts the main content while preserving structure
        """
        # Remove YAML frontmatter if present
        markdown_content = self._remove_frontmatter(markdown_content)

        # Extract main content (remove code blocks temporarily)
        code_blocks = []
        def replace_code_block(match):
            placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"
            code_blocks.append(match.group(0))
            return placeholder

        # Find and temporarily remove code blocks
        pattern = r'```[\s\S]*?```|`[^`]*`'
        markdown_content = re.sub(pattern, replace_code_block, markdown_content)

        # Remove markdown formatting but preserve the text
        plain_text = self._remove_markdown_formatting(markdown_content)

        # Put code blocks back
        for i, code_block in enumerate(code_blocks):
            placeholder = f"__CODE_BLOCK_{i}__"
            # For the plain text version, we'll include the code but without formatting
            code_content = self._extract_code_content(code_block)
            plain_text = plain_text.replace(placeholder, code_content)

        return plain_text.strip()

    def _remove_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from the beginning of the document"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2]
        return content

    def _remove_markdown_formatting(self, content: str) -> str:
        """Remove markdown formatting while preserving the text content"""
        # Remove headers but preserve the text
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)

        # Remove bold, italic formatting
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # **text**
        content = re.sub(r'\*(.*?)\*', r'\1', content)      # *text*
        content = re.sub(r'__(.*?)__', r'\1', content)      # __text__
        content = re.sub(r'_(.*?)_', r'\1', content)        # _text_
        content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)  # [text](link)

        # Remove image references
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)

        # Remove list markers
        content = re.sub(r'^\s*[\*\-\+]\s+', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)

        # Remove blockquotes
        content = re.sub(r'^\s*>\s*', '', content, flags=re.MULTILINE)

        # Remove horizontal rules
        content = re.sub(r'^\s*[\*\-\_]{3,}\s*$', '', content, flags=re.MULTILINE)

        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Multiple newlines to double newline
        content = re.sub(r'[ \t]+', ' ', content)      # Multiple spaces to single space

        return content.strip()

    def _extract_code_content(self, code_block: str) -> str:
        """Extract the actual code content from a code block"""
        # Remove the code fence (```language and ```)
        lines = code_block.split('\n')
        if len(lines) > 2:
            # Remove first and last lines (the fences)
            code_content = '\n'.join(lines[1:-1])
            return f" CODE: {code_content} "
        elif len(lines) == 1:
            # Inline code: remove backticks
            return code_block.strip('`')
        else:
            return code_block