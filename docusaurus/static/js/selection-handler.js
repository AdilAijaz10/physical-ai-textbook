// Selection handler for capturing selected text to pass to the RAG query
// This will be used by the RagChatbot component to get selected text context

class TextSelectionHandler {
  constructor() {
    this.selectedText = null;
    this.init();
  }

  init() {
    // Add event listener for when text is selected
    document.addEventListener('mouseup', this.handleTextSelection.bind(this));
    document.addEventListener('touchend', this.handleTextSelection.bind(this));
  }

  handleTextSelection() {
    // Get the currently selected text
    const selection = window.getSelection();
    this.selectedText = selection.toString().trim();

    // Optionally store the selected text in a data attribute for other components to access
    if (this.selectedText) {
      document.body.setAttribute('data-selected-text', this.selectedText);
    } else {
      document.body.removeAttribute('data-selected-text');
    }
  }

  getSelectedText() {
    // Get selected text either from our stored value or directly from the window
    const directSelection = window.getSelection().toString().trim();
    return directSelection || this.selectedText || null;
  }

  // Method to clear the selected text
  clearSelection() {
    this.selectedText = null;
    document.body.removeAttribute('data-selected-text');
  }

  // Method to get the selected text range for more advanced processing
  getSelectionRange() {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      return selection.getRangeAt(0);
    }
    return null;
  }
}

// Initialize the text selection handler when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.ragSelectionHandler = new TextSelectionHandler();
});

// Export for use in modules if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TextSelectionHandler;
}