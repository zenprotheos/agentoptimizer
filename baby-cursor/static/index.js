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
    this.selectedAgent = 'oneshot_agent'; // Default agent
    this.monacoEditor = null;
  }

  async init() {
    console.log('Initializing Baby Cursor...');
    if (this.isLoading) return;
    this.isLoading = true;
    
    try {
      await this.initializeMonaco();
      await this.loadAgents();
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

  async initializeMonaco() {
    return new Promise((resolve) => {
      require.config({ paths: { vs: 'https://unpkg.com/monaco-editor@0.45.0/min/vs' } });
      require(['vs/editor/editor.main'], () => {
        this.monacoEditor = monaco.editor.create(document.getElementById('editor'), {
          value: '',
          language: 'plaintext',
          theme: 'vs-dark',
          automaticLayout: true,
          fontSize: 13,
          fontFamily: 'SF Mono, Monaco, Inconsolata, "Roboto Mono", Consolas, "Courier New", monospace',
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          wordWrap: 'on',
          tabSize: 2,
          insertSpaces: true
        });
        
        // Listen for content changes
        this.monacoEditor.onDidChangeModelContent(() => {
          if (this.activePath) {
            this.unsavedChanges.add(this.activePath);
            this.renderTabs();
            this.renderFileTree();
          }
        });
        
        resolve();
      });
    });
  }

  async loadAgents() {
    try {
      console.log('Loading agents...');
      const response = await fetch('/api/agents');
      if (!response.ok) throw new Error(`Failed to fetch agents: ${response.status}`);
      const agents = await response.json();
      
      const agentSelect = document.getElementById('agent-select');
      if (agentSelect) {
        // Clear existing options
        agentSelect.innerHTML = '';
        
        // Add agents to dropdown
        agents.forEach(agent => {
          const option = document.createElement('option');
          option.value = agent.value;
          option.textContent = agent.label;
          agentSelect.appendChild(option);
        });
        
        // Set default selection
        this.selectedAgent = agents.length > 0 ? agents[0].value : 'oneshot_agent';
        agentSelect.value = this.selectedAgent;
      }
      
      console.log('Agents loaded successfully:', agents.length);
    } catch (error) {
      console.error('Failed to load agents:', error);
      this.showToast(`Failed to load agents: ${error.message}`, 'error');
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
    
    treeContainer.innerHTML = '<div style="color: var(--cursor-text-muted); font-size: 12px;">Loading...</div>';
    
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
            folderHeader.className = 'cursor-pointer py-1 px-2 rounded text-sm flex items-center hover:bg-opacity-10 hover:bg-white';
            folderHeader.style.marginLeft = `${level * 12}px`;
            folderHeader.style.color = 'var(--cursor-text-primary)';
            folderHeader.innerHTML = `
              <span class="mr-1" style="color: var(--cursor-text-secondary);">${isCollapsed ? '▶' : '▼'}</span>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" class="mr-1" style="color: var(--cursor-accent);">
                <path d="M6.5 1h3l.5.5v1h3.5l.5.5v9l-.5.5h-11l-.5-.5v-10l.5-.5H6.5zM2 2v9h12V4H8.5l-.5-.5v-1H2z"/>
              </svg>
              <span>${this.escapeHtml(folder.name)}</span>
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
            const isUnsaved = this.unsavedChanges.has(file.path);
            fileEl.className = 'cursor-pointer py-1 px-2 rounded text-sm flex items-center hover:bg-opacity-10 hover:bg-white';
            fileEl.style.marginLeft = `${level * 12}px`;
            fileEl.style.color = isUnsaved ? 'var(--cursor-warning)' : 'var(--cursor-text-primary)';
            
            const fileIcon = this.getFileIcon(file.path);
            fileEl.innerHTML = `
              ${fileIcon}
              <span>${this.escapeHtml(file.path.split('/').pop())}${isUnsaved ? ' •' : ''}</span>
            `;
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
        treeContainer.innerHTML = '<div style="color: var(--cursor-error); font-size: 12px;">Error loading files</div>';
      }
    }, 10);
  }

  getFileIcon(path) {
    const ext = path.split('.').pop()?.toLowerCase();
    const iconColor = 'var(--cursor-text-secondary)';
    
    switch (ext) {
      case 'js':
        return `<svg width="16" height="16" viewBox="0 0 16 16" fill="${iconColor}" class="mr-1"><path d="M1 8.5c0-1.5.5-2.5 1.5-3s2-.5 3.5-.5h1v1H6c-1 0-1.5.5-1.5 1.5S5 9 6 9h1v1H6c-1.5 0-2.5-.5-3.5-1.5S1 10 1 8.5z"/></svg>`;
      case 'py':
        return `<svg width="16" height="16" viewBox="0 0 16 16" fill="${iconColor}" class="mr-1"><path d="M8 1c3.9 0 7 3.1 7 7s-3.1 7-7 7-7-3.1-7-7 3.1-7 7-7z"/></svg>`;
      case 'md':
        return `<svg width="16" height="16" viewBox="0 0 16 16" fill="${iconColor}" class="mr-1"><path d="M2 3h12v10H2V3zm1 1v8h10V4H3z"/></svg>`;
      case 'json':
        return `<svg width="16" height="16" viewBox="0 0 16 16" fill="${iconColor}" class="mr-1"><path d="M6 2.5V2h-.5a1 1 0 0 0-1 1v.5a1 1 0 0 1-1 1H3a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1h.5a1 1 0 0 1 1 1v.5a1 1 0 0 0 1 1H6v-.5a1 1 0 0 1 1-1h.5a1 1 0 0 0 1-1v-1a1 1 0 0 0-1-1H7a1 1 0 0 1-1-1z"/></svg>`;
      default:
        return `<svg width="16" height="16" viewBox="0 0 16 16" fill="${iconColor}" class="mr-1"><path d="M2 2h8l4 4v8H2V2zm8 0v4h4l-4-4z"/></svg>`;
    }
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
      const isActive = this.activePath === path;
      const hasUnsavedChanges = this.unsavedChanges.has(path);
      
      tab.className = `px-3 py-2 cursor-pointer text-sm flex items-center border-r`;
      tab.style.borderColor = 'var(--cursor-border)';
      tab.style.backgroundColor = isActive ? 'var(--cursor-bg-primary)' : 'var(--cursor-bg-secondary)';
      tab.style.color = 'var(--cursor-text-primary)';
      
      const fileName = path.split('/').pop();
      
      tab.innerHTML = `
        <span class="file-name ${hasUnsavedChanges ? 'text-yellow-400' : ''}" data-path="${path}">
          ${this.escapeHtml(fileName)}${hasUnsavedChanges ? ' •' : ''}
        </span>
        <button class="close-tab ml-2 text-xs hover:bg-opacity-20 hover:bg-white rounded p-1" data-path="${path}" style="color: var(--cursor-text-secondary);">×</button>
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
    const editorContainer = document.getElementById('editor');
    
    if (!placeholder || !editorContainer || !this.monacoEditor) return;
    
    if (this.activePath && this.files.has(this.activePath)) {
      const file = this.files.get(this.activePath);
      placeholder.classList.add('hidden');
      editorContainer.classList.remove('hidden');
      
      // Set content and language
      this.monacoEditor.setValue(file.content);
      const language = this.getLanguageFromPath(this.activePath);
      monaco.editor.setModelLanguage(this.monacoEditor.getModel(), language);
      
      // Focus editor after a brief delay
      setTimeout(() => this.monacoEditor.focus(), 50);
    } else {
      placeholder.classList.remove('hidden');
      editorContainer.classList.add('hidden');
    }
  }

  getLanguageFromPath(path) {
    const ext = path.split('.').pop()?.toLowerCase();
    const languageMap = {
      'py': 'python',
      'js': 'javascript',
      'ts': 'typescript',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'md': 'markdown',
      'yml': 'yaml',
      'yaml': 'yaml',
      'xml': 'xml',
      'sh': 'shell',
      'bash': 'shell',
      'sql': 'sql',
      'php': 'php',
      'cpp': 'cpp',
      'c': 'c',
      'java': 'java',
      'go': 'go',
      'rs': 'rust',
      'rb': 'ruby'
    };
    return languageMap[ext] || 'plaintext';
  }

  async saveFile(path = null, showToast = true) {
    const targetPath = path || this.activePath;
    if (!targetPath || this.isLoading || !this.monacoEditor) return;
    
    const content = this.monacoEditor.getValue();
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
    const agentSelect = document.getElementById('agent-select');
    if (!input || this.isLoading) return;
    
    const message = input.value.trim();
    if (!message) return;

    this.selectedAgent = agentSelect?.value || 'oneshot_agent';
    this.addMessage('user', message);
    input.value = '';
    this.isLoading = true;

    try {
      const requestBody = {
        message: message,
        agent_name: this.selectedAgent
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
    
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'flex gap-3 mb-4';
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium';
    
    // Message content
    const messageContent = document.createElement('div');
    messageContent.className = 'flex-1 min-w-0';
    
    // Message header with role and timestamp
    const messageHeader = document.createElement('div');
    messageHeader.className = 'flex items-center gap-2 mb-1';
    
    const roleName = document.createElement('span');
    roleName.className = 'text-sm font-medium';
    roleName.style.color = 'var(--cursor-text-primary)';
    
    const timestamp = document.createElement('span');
    timestamp.className = 'text-xs';
    timestamp.style.color = 'var(--cursor-text-secondary)';
    timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Message body
    const messageBody = document.createElement('div');
    messageBody.className = 'text-sm leading-relaxed';
    messageBody.style.color = 'var(--cursor-text-primary)';
    
    if (role === 'user') {
      avatar.style.backgroundColor = 'var(--cursor-accent)';
      avatar.style.color = 'white';
      avatar.textContent = 'You';
      roleName.textContent = 'You';
      
      // User messages with slight background
      messageBody.className += ' px-3 py-2 rounded-lg';
      messageBody.style.backgroundColor = 'var(--cursor-bg-secondary)';
      messageBody.style.border = '1px solid var(--cursor-border)';
    } else {
      avatar.style.backgroundColor = 'var(--cursor-bg-tertiary)';
      avatar.style.color = 'var(--cursor-text-primary)';
      avatar.style.border = '1px solid var(--cursor-border)';
      avatar.innerHTML = '🤖';
      roleName.textContent = this.selectedAgent ? this.selectedAgent.replace('_', ' ').toUpperCase() : 'ASSISTANT';
      
      // Assistant messages with markdown-like styling
      messageBody.style.whiteSpace = 'pre-wrap';
      messageBody.style.wordBreak = 'break-word';
    }
    
    // Process content for basic markdown-like formatting
    if (role === 'assistant') {
      messageBody.innerHTML = this.formatAssistantMessage(content);
    } else {
      messageBody.textContent = content;
    }
    
    // Assemble the message
    messageHeader.appendChild(roleName);
    messageHeader.appendChild(timestamp);
    messageContent.appendChild(messageHeader);
    messageContent.appendChild(messageBody);
    messageWrapper.appendChild(avatar);
    messageWrapper.appendChild(messageContent);
    
    messagesContainer.appendChild(messageWrapper);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Limit message history
    const messages = messagesContainer.children;
    if (messages.length > 50) {
      messagesContainer.removeChild(messages[0]);
    }
  }

  formatAssistantMessage(content) {
    // Basic markdown-like formatting
    let formatted = this.escapeHtml(content);
    
    // Code blocks
    formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<div class="bg-gray-800 rounded-md p-3 my-2 text-sm font-mono overflow-x-auto">
        ${lang ? `<div class="text-xs text-gray-400 mb-2">${lang}</div>` : ''}
        <pre style="color: #e5e7eb; margin: 0;">${code.trim()}</pre>
      </div>`;
    });
    
    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 rounded text-sm font-mono" style="background-color: var(--cursor-bg-tertiary); color: var(--cursor-accent);">$1</code>');
    
    // Bold text
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic text
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
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
    
    // Enter to send message and auto-resize
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
      // Auto-resize functionality
      const autoResize = () => {
        messageInput.style.height = 'auto';
        const newHeight = Math.min(messageInput.scrollHeight, 120); // Max height of 120px
        messageInput.style.height = newHeight + 'px';
      };

      messageInput.addEventListener('input', autoResize);
      messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });

      // Initial resize
      autoResize();
    }

    // Agent selection
    const agentSelect = document.getElementById('agent-select');
    if (agentSelect) {
      agentSelect.addEventListener('change', (e) => {
        this.selectedAgent = e.target.value;
        console.log('Selected agent:', this.selectedAgent);
      });
    }
  }

  showToast(message, type = 'info') {
    // Remove existing toasts
    document.querySelectorAll('.toast').forEach(t => t.remove());
    
    const toast = document.createElement('div');
    toast.className = 'toast fixed top-4 right-4 p-3 rounded shadow-lg z-50 text-sm max-w-xs';
    
    let bgColor;
    switch (type) {
      case 'error':
        bgColor = 'var(--cursor-error)';
        break;
      case 'success':
        bgColor = 'var(--cursor-success)';
        break;
      default:
        bgColor = 'var(--cursor-accent)';
    }
    
    toast.style.backgroundColor = bgColor;
    toast.style.color = 'white';
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