// Simple Baby Cursor IDE
class BabyCursor {
  constructor() {
    this.files = new Map();
    this.folders = new Map();
    this.activePath = null;
    this.openTabs = [];
    this.currentThread = { messages: [], run_id: null };
    this.isLoading = false;
    this.collapsedFolders = new Set();
    this.unsavedChanges = new Set();
  }

  async init() {
    console.log('Initializing Baby Cursor...');
    if (this.isLoading) return;
    this.isLoading = true;
    
    try {
      await this.loadFileTree();
      this.setupEventListeners();
      console.log('Baby Cursor initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Baby Cursor:', error);
      this.showToast('Failed to initialize application', 'error');
    } finally {
      this.isLoading = false;
    }
  }

  async loadFileTree() {
    try {
      console.log('Loading file tree...');
      const response = await fetch('/api/files');
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      const fileTree = await response.json();
      
      console.log('File tree loaded, processing...');
      this.processFileTree(fileTree);
      this.renderFileTree();
      console.log(`Processed ${this.files.size} files and ${this.folders.size} folders`);
    } catch (error) {
      console.error('Error loading file tree:', error);
      this.showToast('Failed to load file system', 'error');
    }
  }

  processFileTree(nodes) {
    this.files.clear();
    this.folders.clear();
    
    const processNode = (node, depth = 0) => {
      if (depth > 10) return; // Prevent infinite recursion
      
      try {
        if (node.type === 'folder') {
          this.folders.set(node.id, {
            ...node,
            children: node.children ? node.children.map(c => c.id) : []
          });
          
          if (node.children && Array.isArray(node.children)) {
            node.children.forEach(child => processNode(child, depth + 1));
          }
        } else if (node.type === 'file') {
          this.files.set(node.id, {
            path: node.id,
            content: '',
            loaded: false
          });
        }
      } catch (error) {
        console.warn('Error processing node:', node, error);
      }
    };
    
    if (Array.isArray(nodes)) {
      nodes.forEach(node => processNode(node));
    }
  }

  toggleFolder(folderId) {
    if (this.collapsedFolders.has(folderId)) {
      this.collapsedFolders.delete(folderId);
    } else {
      this.collapsedFolders.add(folderId);
    }
    this.renderFileTree();
  }

  renderFileTree() {
    const treeContainer = document.getElementById('file-tree');
    if (!treeContainer) {
      console.error('file-tree element not found!');
      return;
    }
    
    treeContainer.innerHTML = '<div class="text-gray-400 text-sm">Loading...</div>';
    
    // Use setTimeout to prevent blocking the UI
    setTimeout(() => {
      try {
        treeContainer.innerHTML = '';
        
        const renderNode = (nodeId, level = 0) => {
          if (level > 5) return; // Prevent deep nesting issues
          
          const folder = this.folders.get(nodeId);
          const file = this.files.get(nodeId);
          
          if (folder) {
            const isCollapsed = this.collapsedFolders.has(nodeId);
            const folderEl = document.createElement('div');
            
            // Folder header
            const folderHeader = document.createElement('div');
            folderHeader.className = 'cursor-pointer py-1 px-2 hover:bg-gray-700 rounded text-sm flex items-center';
            folderHeader.style.marginLeft = `${level * 12}px`;
            folderHeader.innerHTML = `
              <span class="mr-1">${isCollapsed ? '▶' : '▼'}</span>
              <span>📁 ${this.escapeHtml(folder.name)}</span>
            `;
            folderHeader.onclick = () => this.toggleFolder(nodeId);
            
            folderEl.appendChild(folderHeader);
            treeContainer.appendChild(folderEl);
            
            // Folder children (if not collapsed)
            if (!isCollapsed && folder.children && folder.children.length > 0 && level < 4) {
              folder.children.slice(0, 20).forEach(childId => renderNode(childId, level + 1));
            }
          } else if (file) {
            const fileEl = document.createElement('div');
            fileEl.className = `cursor-pointer py-1 px-2 hover:bg-gray-700 rounded text-sm ${
              this.unsavedChanges.has(file.path) ? 'text-yellow-400' : ''
            }`;
            fileEl.style.marginLeft = `${level * 12}px`;
            fileEl.innerHTML = `<span>📄 ${this.escapeHtml(file.path.split('/').pop())}${
              this.unsavedChanges.has(file.path) ? ' •' : ''
            }</span>`;
            fileEl.onclick = () => this.openFile(file.path);
            treeContainer.appendChild(fileEl);
          }
        };

        // Render root folders (limit to first 10)
        const rootFolders = Array.from(this.folders.values()).filter(f => !f.parent).slice(0, 10);
        rootFolders.forEach(f => renderNode(f.id));
        
        console.log('File tree rendered successfully');
      } catch (error) {
        console.error('Error rendering file tree:', error);
        treeContainer.innerHTML = '<div class="text-red-400 text-sm">Error loading files</div>';
      }
    }, 10);
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  async openFile(path) {
    if (this.isLoading) return;
    
    // Auto-save current file before switching
    if (this.activePath && this.unsavedChanges.has(this.activePath)) {
      await this.saveFile(this.activePath, false); // Silent save
    }
    
    try {
      console.log('Opening file:', path);
      const file = this.files.get(path);
      if (!file) {
        throw new Error(`File not found: ${path}`);
      }
      
      if (!file.loaded) {
        this.showToast('Loading file...', 'info');
        const response = await fetch(`/api/files/${encodeURIComponent(path)}`);
        if (!response.ok) throw new Error(`Failed to fetch file: ${response.status}`);
        const { content } = await response.json();
        file.content = content;
        file.loaded = true;
      }

      this.activePath = path;
      if (!this.openTabs.includes(path)) {
        this.openTabs.push(path);
        // Limit number of open tabs
        if (this.openTabs.length > 10) {
          const closedTab = this.openTabs.shift();
          this.unsavedChanges.delete(closedTab);
        }
      }
      
      this.renderTabs();
      this.renderEditor();
    } catch (error) {
      console.error('Error opening file:', error);
      this.showToast(`Failed to open file: ${path}`, 'error');
    }
  }

  closeFile(path) {
    // Auto-save before closing if there are unsaved changes
    if (this.unsavedChanges.has(path)) {
      this.saveFile(path, false); // Silent save
    }
    
    this.openTabs = this.openTabs.filter(p => p !== path);
    this.unsavedChanges.delete(path);
    
    if (this.activePath === path) {
      this.activePath = this.openTabs[this.openTabs.length - 1] || null;
    }
    this.renderTabs();
    this.renderEditor();
    this.renderFileTree(); // Update file tree to remove unsaved indicator
  }

  renderTabs() {
    const tabsContainer = document.getElementById('tabs');
    if (!tabsContainer) return;
    
    tabsContainer.innerHTML = '';
    
    this.openTabs.forEach(path => {
      const tab = document.createElement('div');
      tab.className = `px-3 py-2 cursor-pointer border-r border-gray-700 text-sm flex items-center ${
        this.activePath === path ? 'bg-gray-700' : 'hover:bg-gray-700'
      }`;
      
      const fileName = path.split('/').pop();
      const hasUnsavedChanges = this.unsavedChanges.has(path);
      
      tab.innerHTML = `
        <span class="file-name ${hasUnsavedChanges ? 'text-yellow-400' : ''}" data-path="${path}">
          ${this.escapeHtml(fileName)}${hasUnsavedChanges ? ' •' : ''}
        </span>
        <button class="close-tab ml-2 text-gray-400 hover:text-white text-xs" data-path="${path}">×</button>
      `;
      
      tabsContainer.appendChild(tab);
    });
    
    // Add event listeners
    requestAnimationFrame(() => {
      document.querySelectorAll('.file-name').forEach(el => {
        el.addEventListener('click', (e) => {
          this.setActiveFile(e.target.dataset.path);
        });
      });
      
      document.querySelectorAll('.close-tab').forEach(el => {
        el.addEventListener('click', (e) => {
          e.stopPropagation();
          this.closeFile(e.target.dataset.path);
        });
      });
    });
  }

  setActiveFile(path) {
    // Auto-save current file before switching
    if (this.activePath && this.unsavedChanges.has(this.activePath)) {
      this.saveFile(this.activePath, false); // Silent save
    }
    
    this.activePath = path;
    this.renderTabs();
    this.renderEditor();
  }

  renderEditor() {
    const placeholder = document.getElementById('editor-placeholder');
    const editor = document.getElementById('editor');
    
    if (!placeholder || !editor) return;
    
    if (this.activePath && this.files.has(this.activePath)) {
      const file = this.files.get(this.activePath);
      placeholder.classList.add('hidden');
      editor.classList.remove('hidden');
      editor.value = file.content;
      
      // Focus editor after a brief delay
      setTimeout(() => editor.focus(), 50);
    } else {
      placeholder.classList.remove('hidden');
      editor.classList.add('hidden');
    }
  }

  async saveFile(path = null, showToast = true) {
    const targetPath = path || this.activePath;
    if (!targetPath || this.isLoading) return;
    
    const editor = document.getElementById('editor');
    if (!editor) return;
    
    const content = editor.value;
    this.isLoading = true;
    
    try {
      await fetch(`/api/files/${encodeURIComponent(targetPath)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });
      
      const file = this.files.get(targetPath);
      if (file) {
        file.content = content;
      }
      this.unsavedChanges.delete(targetPath);
      this.renderTabs();
      this.renderFileTree();
      
      if (showToast) {
        this.showToast(`Saved ${targetPath}`, 'success');
      }
    } catch (error) {
      console.error('Error saving file:', error);
      if (showToast) {
        this.showToast(`Failed to save file: ${targetPath}`, 'error');
      }
    } finally {
      this.isLoading = false;
    }
  }

  async sendMessage() {
    const input = document.getElementById('message-input');
    if (!input || this.isLoading) return;
    
    const message = input.value.trim();
    if (!message) return;

    this.addMessage('user', message);
    input.value = '';
    this.isLoading = true;

    try {
      const requestBody = {
        message: message
      };
      
      // Only include run_id if it exists
      if (this.currentThread.run_id) {
        requestBody.run_id = this.currentThread.run_id;
      }
      
      console.log('Sending chat request:', requestBody);
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const result = await response.json();
      console.log('Chat response:', result);
      
      this.currentThread.run_id = result.run_id;
      this.addMessage('assistant', result.output || result.message || 'No response received');
      
    } catch (error) {
      console.error('Chat error:', error);
      this.addMessage('assistant', `Error: ${error.message}`);
    } finally {
      this.isLoading = false;
    }
  }

  addMessage(role, content) {
    const messagesContainer = document.getElementById('messages');
    if (!messagesContainer) return;
    
    const messageEl = document.createElement('div');
    messageEl.className = `p-2 my-2 rounded text-sm ${
      role === 'user' ? 'bg-blue-600 ml-4' : 'bg-gray-700 mr-4'
    }`;
    messageEl.textContent = content;
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Limit message history
    const messages = messagesContainer.children;
    if (messages.length > 50) {
      messagesContainer.removeChild(messages[0]);
    }
  }

  setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Save shortcut
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        this.saveFile();
      }
    });

    // Editor content change
    const editor = document.getElementById('editor');
    if (editor) {
      editor.addEventListener('input', (e) => {
        if (this.activePath && this.files.has(this.activePath)) {
          const file = this.files.get(this.activePath);
          file.content = e.target.value;
          this.unsavedChanges.add(this.activePath);
          this.renderTabs();
          this.renderFileTree();
        }
      });
      
      // Auto-save on blur (when focus leaves the editor)
      editor.addEventListener('blur', () => {
        if (this.activePath && this.unsavedChanges.has(this.activePath)) {
          this.saveFile(this.activePath, false); // Silent save
        }
      });
    }

    // Send message
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
      sendBtn.addEventListener('click', () => this.sendMessage());
    }
    
    // Enter to send message
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
      messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }
  }

  showToast(message, type = 'info') {
    // Remove existing toasts
    document.querySelectorAll('.toast').forEach(t => t.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast fixed top-4 right-4 p-3 rounded shadow-lg z-50 text-sm ${
      type === 'error' ? 'bg-red-600' : type === 'success' ? 'bg-green-600' : 'bg-blue-600'
    } text-white max-w-xs`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      if (document.body.contains(toast)) {
        document.body.removeChild(toast);
      }
    }, 3000);
  }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, initializing app...');
  window.app = new BabyCursor();
  window.app.init().catch(error => {
    console.error('Failed to initialize app:', error);
  });
}); 