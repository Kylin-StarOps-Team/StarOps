const { ipcRenderer } = require('electron');

class StarOpsRenderer {
    constructor() {
        this.currentView = 'chat';
        this.isProcessing = false;
        this.conversationHistory = [];
        this.sidebarVisible = false;
        this.currentConversationId = Date.now(); // 对话段ID
        this.debugSessions = []; // 调试会话记录
        this.isDataPanelOpen = false;
        this.isConsolePanelOpen = false;
        
        this.initializeApp();
        this.setupEventListeners();
        this.loadAppInfo();
    }

    initializeApp() {
        // 设置欢迎消息时间
        document.getElementById('welcomeTime').textContent = this.formatTime(new Date());
        
        // 加载初始报告
        this.loadWebReports();
        this.loadMysqlReports();
        
        console.log('StarOps应用已初始化');
    }

    setupEventListeners() {
        // 控制按钮
        document.getElementById('closeBtn').addEventListener('click', () => {
            ipcRenderer.invoke('close-main-window');
        });

        document.getElementById('minimizeBtn').addEventListener('click', () => {
            ipcRenderer.invoke('minimize-main-window');
        });

        document.getElementById('maximizeBtn').addEventListener('click', () => {
            ipcRenderer.invoke('maximize-main-window');
        });

        // 面板控制
        document.getElementById('toggleDataPanel').addEventListener('click', () => {
            this.toggleDataPanel();
        });

        document.getElementById('toggleConsolePanel').addEventListener('click', () => {
            this.toggleConsolePanel();
        });

        // 导航按钮
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.currentTarget.dataset.view;
                this.switchView(view);
            });
        });

        // 聊天功能
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('chatInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });

        document.getElementById('clearChatBtn').addEventListener('click', () => {
            this.clearChat();
        });

        // 历史管理按钮
        document.getElementById('historyBtn').addEventListener('click', () => {
            this.showHistoryModal();
        });

        // 报告刷新按钮
        document.getElementById('refreshWebReports').addEventListener('click', () => {
            this.loadWebReports();
        });

        document.getElementById('refreshMysqlReports').addEventListener('click', () => {
            this.loadMysqlReports();
        });

        // 示例查询点击事件
        this.setupExampleQueries();
    }

    setupExampleQueries() {
        // 为示例查询添加点击事件
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('query-example')) {
                const query = e.target.textContent.replace(/"/g, '');
                document.getElementById('chatInput').value = query;
                document.getElementById('chatInput').focus();
            }
        });
    }

    async loadAppInfo() {
        try {
            const appInfo = await ipcRenderer.invoke('get-app-info');
            // appVersion元素已移除，不再需要设置版本信息
            console.log('应用信息:', appInfo);
        } catch (error) {
            console.error('加载应用信息失败:', error);
        }
    }



    setupAutoResizeTextarea() {
        // 现在使用input，不需要自动调整高度
    }

    async sendMessage() {
        if (this.isProcessing) {
            return;
        }

        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) {
            return;
        }

        // 清空输入框
        input.value = '';

        // 添加用户消息
        this.addUserMessage(message);

        // 开始新的对话段
        this.currentConversationId = Date.now();
        
        // 显示思考动画
        this.showThinkingIndicator();

        // 设置处理状态
        this.setProcessingState(true);

        try {
            console.log('发送消息到智能监控系统:', message);
            
            // 调用智能监控并捕获调试信息
            const result = await ipcRenderer.invoke('call-smart-monitor', message, this.currentConversationId);
            
            console.log('收到智能监控系统响应:', result);
            
            // 显示思考完成
            this.showThinkingComplete();
            
            if (result.success) {
                // 记录AI分析数据
                if (result.debug_data && result.debug_data.length > 0) {
                    console.log('收到调试数据:', result.debug_data);
                    this.addDebugData(result.debug_data);
                }
                
                // 记录控制台输出
                if (result.console_output) {
                    console.log('收到控制台输出:', result.console_output);
                    this.addConsoleOutput(result.console_output);
                }
                
                // 显示历史保存状态
                if (result.data && result.data.history_count !== undefined) {
                    console.log(`✅ 对话历史已保存，当前包含 ${result.data.history_count} 轮对话`);
                }
                
                await this.handleSuccessResponse(result.data, message);
            } else {
                await this.handleErrorResponse(result.error, result.raw_output);
            }
        } catch (error) {
            console.error('发送消息失败:', error);
            this.addAssistantMessage(`❌ 系统错误: ${error.message}`);
        } finally {
            // 隐藏思考动画
            this.hideThinkingIndicator();
            this.setProcessingState(false);
        }
    }

    async handleSuccessResponse(data, originalMessage) {
        console.log('处理成功响应:', data);
        
        if (data.type === 'mcp_analysis') {
            // MCP协议分析结果
            const analysis = data.analysis;
            await this.addAssistantMessage(analysis);
            
        } else if (data.type === 'direct_answer') {
            // 直接回答
            await this.addAssistantMessage(data.answer);
            
        } else if (data.type === 'skywalking_direct_output') {
            // SkyWalking直接输出
            let responseMsg;
            if (data.mcp_result.status === 'success') {
                responseMsg = `✅ **SkyWalking分布式追踪分析已完成！**

📊 **分析结果已输出到控制台**，请查看终端窗口获取详细信息。

💡 **分析包含：**
- 微服务拓扑关系
- 异常检测结果  
- 根因分析报告
- 资源依赖关系

🎯 分析完成，等待您的下一个问题...`;
            } else {
                responseMsg = `❌ **SkyWalking分析执行失败**：${data.mcp_result.message || '未知错误'}

请检查SkyWalking服务状态和配置。`;
            }
            
            await this.addAssistantMessage(responseMsg);
        }

        // 保存到对话历史
        this.conversationHistory.push(
            { role: 'user', content: originalMessage },
            { role: 'assistant', content: data.analysis || data.answer || '分析完成' }
        );
    }

    async handleErrorResponse(error, rawOutput) {
        console.log('处理错误响应:', error, rawOutput);
        
        let errorMessage = `❌ **执行失败**: ${error}`;
        
        if (rawOutput) {
            errorMessage += `\n\n**原始输出:**\n\`\`\`\n${rawOutput}\n\`\`\``;
        }
        
        await this.addAssistantMessage(errorMessage);
    }

    addUserMessage(message) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageGroup = this.createMessageGroup('user', '您', message);
        messagesContainer.appendChild(messageGroup);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async addAssistantMessage(content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageGroup = this.createMessageGroup('assistant', 'StarOps助手', content);
        messagesContainer.appendChild(messageGroup);
        
        // 如果内容包含Markdown，进行渲染
        if (content.includes('**') || content.includes('```') || content.includes('*') || content.includes('-')) {
            await this.renderMarkdown(messageGroup.querySelector('.message-text'));
        }
        
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    createMessageGroup(type, sender, content) {
        const timestamp = this.formatTime(new Date());
        
        const messageGroup = document.createElement('div');
        messageGroup.className = 'message-group';
        
        messageGroup.innerHTML = `
            <div class="message ${type}-message">
                <div class="message-avatar">
                    ${this.getAvatarIcon(type)}
                </div>
                <div class="message-content">
                    <div class="message-text">
                        ${this.escapeHtml(content)}
                    </div>
                    <div class="message-time">${timestamp}</div>
                </div>
            </div>
        `;
        
        return messageGroup;
    }

    getAvatarIcon(type) {
        const icons = {
            user: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            assistant: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
            system: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'
        };
        return icons[type] || icons.assistant;
    }

    async renderMarkdown(contentElement) {
        try {
            const markdownText = contentElement.textContent;
            const htmlContent = marked.parse(markdownText);
            contentElement.innerHTML = htmlContent;
            
            // 高亮代码块
            contentElement.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });
        } catch (error) {
            console.error('Markdown渲染失败:', error);
        }
    }



    setProcessingState(isProcessing) {
        this.isProcessing = isProcessing;
        const sendBtn = document.getElementById('sendBtn');
        const statusIndicator = document.getElementById('statusIndicator'); // 可能为null
        
        if (sendBtn) {
            sendBtn.disabled = isProcessing;
        }
        
        if (statusIndicator) {
            if (isProcessing) {
                statusIndicator.textContent = '处理中...';
                statusIndicator.className = 'status-indicator processing';
            } else {
                statusIndicator.textContent = '就绪';
                statusIndicator.className = 'status-indicator ready';
            }
        }
        
        this.updateStatus(isProcessing ? '正在处理您的问题...' : '就绪', isProcessing ? 'processing' : 'ready');
    }

    showThinkingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        
        // 创建思考指示器
        const thinkingGroup = document.createElement('div');
        thinkingGroup.className = 'message-group';
        thinkingGroup.id = 'thinkingIndicatorGroup';
        
        thinkingGroup.innerHTML = `
            <div class="message assistant-message">
                <div class="message-avatar">
                    ${this.getAvatarIcon('assistant')}
                </div>
                <div class="message-content">
                    <div class="thinking-indicator show">
                        <div class="thinking-text">正在思考</div>
                        <div class="thinking-dots">
                            <div class="thinking-dot"></div>
                            <div class="thinking-dot"></div>
                            <div class="thinking-dot"></div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(thinkingGroup);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideThinkingIndicator() {
        const thinkingGroup = document.getElementById('thinkingIndicatorGroup');
        if (thinkingGroup) {
            const indicator = thinkingGroup.querySelector('.thinking-indicator');
            if (indicator) {
                indicator.classList.remove('show');
                setTimeout(() => {
                    thinkingGroup.remove();
                }, 300);
            }
        }
    }

    showThinkingComplete() {
        const thinkingGroup = document.getElementById('thinkingIndicatorGroup');
        if (thinkingGroup) {
            const indicator = thinkingGroup.querySelector('.thinking-indicator');
            if (indicator) {
                const thinkingText = indicator.querySelector('.thinking-text');
                if (thinkingText) {
                    thinkingText.textContent = '思考完成';
                    // 暂停一下再隐藏
                    setTimeout(() => {
                        this.hideThinkingIndicator();
                    }, 800);
                }
            }
        }
    }

    // 面板控制功能
    toggleDataPanel() {
        const panel = document.getElementById('dataPanel');
        this.isDataPanelOpen = !this.isDataPanelOpen;
        
        if (this.isDataPanelOpen) {
            panel.classList.add('open');
        } else {
            panel.classList.remove('open');
        }
    }

    toggleConsolePanel() {
        const panel = document.getElementById('consolePanel');
        this.isConsolePanelOpen = !this.isConsolePanelOpen;
        
        if (this.isConsolePanelOpen) {
            panel.classList.add('open');
        } else {
            panel.classList.remove('open');
        }
    }

    // 添加调试数据
    addDebugData(debugData) {
        console.log('添加调试数据:', debugData);
        
        // 查找现有会话或创建新会话
        let session = this.debugSessions.find(s => s.id === this.currentConversationId);
        if (!session) {
            session = {
                id: this.currentConversationId,
                timestamp: new Date(),
                data: []
            };
            this.debugSessions.unshift(session);
        }
        
        // 添加调试数据
        if (Array.isArray(debugData)) {
            debugData.forEach(item => {
                try {
                    // 尝试解析JSON
                    const parsedItem = typeof item === 'string' ? JSON.parse(item) : item;
                    session.data.push(parsedItem);
                } catch (e) {
                    // 如果不是JSON，直接添加
                    session.data.push(item);
                }
            });
        } else {
            session.data.push(debugData);
        }
        
        // 保持最多10个会话
        if (this.debugSessions.length > 10) {
            this.debugSessions = this.debugSessions.slice(0, 10);
        }
        
        this.updateDataPanel();
    }

    // 添加控制台输出
    addConsoleOutput(consoleOutput) {
        const existingSession = this.debugSessions.find(s => s.id === this.currentConversationId);
        if (existingSession) {
            existingSession.consoleOutput = consoleOutput;
        } else {
            const session = {
                id: this.currentConversationId,
                timestamp: new Date(),
                consoleOutput: consoleOutput
            };
            this.debugSessions.unshift(session);
        }
        
        this.updateConsolePanel();
    }

    // 更新数据面板
    updateDataPanel() {
        const content = document.getElementById('dataPanelContent');
        
        if (this.debugSessions.length === 0) {
            content.innerHTML = '<div class="panel-placeholder">暂无分析数据</div>';
            return;
        }
        
        const sessions = this.debugSessions.filter(s => s.data && s.data.length > 0);
        if (sessions.length === 0) {
            content.innerHTML = '<div class="panel-placeholder">暂无分析数据</div>';
            return;
        }
        
        const html = sessions.map(session => {
            // 为每个数据项创建单独的显示块
            const dataItems = session.data.map((item, index) => `
                <div class="data-item">
                    <div class="data-item-header">数据项 ${index + 1}</div>
                    <div class="json-data">${JSON.stringify(item, null, 2)}</div>
                </div>
            `).join('');
            
            return `
                <div class="data-session">
                    <div class="session-header">
                        会话 ${session.id} - ${this.formatTime(session.timestamp)} (${session.data.length} 项数据)
                    </div>
                    <div class="session-content">
                        ${dataItems}
                    </div>
                </div>
            `;
        }).join('');
        
        content.innerHTML = html;
    }

    // 更新控制台面板
    updateConsolePanel() {
        const content = document.getElementById('consolePanelContent');
        
        if (this.debugSessions.length === 0) {
            content.innerHTML = '<div class="panel-placeholder">暂无控制台输出</div>';
            return;
        }
        
        const sessions = this.debugSessions.filter(s => s.consoleOutput);
        if (sessions.length === 0) {
            content.innerHTML = '<div class="panel-placeholder">暂无控制台输出</div>';
            return;
        }
        
        const html = sessions.map(session => `
            <div class="console-session">
                <div class="session-header">
                    会话 ${session.id} - ${this.formatTime(session.timestamp)}
                </div>
                <div class="session-content">
                    <div class="console-output">${session.consoleOutput}</div>
                </div>
            </div>
        `).join('');
        
        content.innerHTML = html;
    }

    clearChat() {
        if (confirm('确定要清空当前对话吗？')) {
            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.innerHTML = `
                <div class="message-group">
                    <div class="message assistant-message">
                        <div class="message-avatar">
                            ${this.getAvatarIcon('assistant')}
                        </div>
                        <div class="message-content">
                            <div class="message-text">
                                对话已清空，您可以开始新的对话。
                            </div>
                            <div class="message-time">${this.formatTime(new Date())}</div>
                        </div>
                    </div>
                </div>
            `;
            
            this.conversationHistory = [];
            this.updateStatus('对话已清空');
        }
    }

    switchView(viewName) {
        // 更新导航按钮
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

        // 切换视图
        document.querySelectorAll('.view-content').forEach(view => {
            view.classList.remove('active');
        });
        
        const targetView = {
            'chat': 'chatView',
            'web-reports': 'webReportsView',
            'mysql-reports': 'mysqlReportsView'
        }[viewName];
        
        document.getElementById(targetView).classList.add('active');
        this.currentView = viewName;

        // 更新状态
        this.updateStatus(`已切换到${this.getViewDisplayName(viewName)}`);
    }

    getViewDisplayName(viewName) {
        const names = {
            'chat': 'AI对话',
            'web-reports': 'Web检测报告',
            'mysql-reports': 'MySQL优化报告'
        };
        return names[viewName] || viewName;
    }

    async loadWebReports() {
        try {
            this.updateStatus('正在加载Web检测报告...');
            const reports = await ipcRenderer.invoke('get-web-reports');
            this.renderWebReports(reports);
            this.updateStatus(`已加载${reports.length}个Web检测报告`);
        } catch (error) {
            console.error('加载Web报告失败:', error);
            this.updateStatus('加载Web报告失败', 'error');
        }
    }

    async loadMysqlReports() {
        try {
            this.updateStatus('正在加载MySQL优化报告...');
            const reports = await ipcRenderer.invoke('get-mysql-reports');
            this.renderMysqlReports(reports);
            this.updateStatus(`已加载${reports.length}个MySQL优化报告`);
        } catch (error) {
            console.error('加载MySQL报告失败:', error);
            this.updateStatus('加载MySQL报告失败', 'error');
        }
    }

    renderWebReports(reports) {
        const container = document.getElementById('webReportsGrid');
        
        if (reports.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M32 8L8 20L32 32L56 20L32 8Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M8 44L32 56L56 44" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M8 32L32 44L56 32" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                    </svg>
                    <h3>暂无Web检测报告</h3>
                    <p>请先进行Web配置检测以生成报告</p>
                </div>
            `;
            return;
        }

        container.innerHTML = reports.map(report => `
            <div class="report-card" onclick="window.staropsRenderer.openReport('${report.path}')">
                <div class="report-header">
                    <div class="report-icon web-report-icon">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M17 13V7C17 5.89543 16.1046 5 15 5H5C3.89543 5 3 5.89543 3 7V13C3 14.1046 3.89543 15 5 15H15C16.1046 15 17 14.1046 17 13Z" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M3 9H17" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                    </div>
                    <div class="report-title">
                        ${report.targetUrl ? `Web检测: ${this.truncateText(report.targetUrl, 25)}` : 'Web配置检测报告'}
                    </div>
                </div>
                <div class="report-details">
                    <div class="report-detail">生成时间: ${report.modifiedTime}</div>
                    <div class="report-detail">文件大小: ${this.formatFileSize(report.size)}</div>
                    <div class="report-detail">文件名: ${report.name}</div>
                </div>
                <div class="report-actions">
                    <button class="btn-report primary" onclick="event.stopPropagation(); window.staropsRenderer.openReport('${report.path}')">
                        打开报告
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderMysqlReports(reports) {
        const container = document.getElementById('mysqlReportsGrid');
        
        if (reports.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M8 16V12C8 9.79086 9.79086 8 12 8H52C54.2091 8 56 9.79086 56 12V16M8 16V52C8 54.2091 9.79086 56 12 56H52C54.2091 56 56 54.2091 56 52V16M8 16H56" stroke="currentColor" stroke-width="2"/>
                        <path d="M20 16V48M44 16V48" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    <h3>暂无MySQL优化报告</h3>
                    <p>请先进行MySQL配置优化检测以生成报告</p>
                </div>
            `;
            return;
        }

        container.innerHTML = reports.map(report => `
            <div class="report-card" onclick="window.staropsRenderer.openReport('${report.path}')">
                <div class="report-header">
                    <div class="report-icon mysql-report-icon">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M4 6V4C4 2.89543 4.89543 2 6 2H14C15.1046 2 16 2.89543 16 4V6M4 6V16C4 17.1046 4.89543 18 6 18H14C15.1046 18 16 17.1046 16 16V6M4 6H16" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M8 6V14M12 6V14" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                    </div>
                    <div class="report-title">
                        MySQL配置优化报告 #${report.detectionNum}
                    </div>
                </div>
                <div class="report-details">
                    <div class="report-detail">生成时间: ${report.modifiedTime}</div>
                    <div class="report-detail">文件大小: ${this.formatFileSize(report.size)}</div>
                    <div class="report-detail">优化建议: ${report.suggestionsCount || '多项'} 条</div>
                </div>
                <div class="report-actions">
                    <button class="btn-report primary" onclick="event.stopPropagation(); window.staropsRenderer.openReport('${report.path}')">
                        打开报告
                    </button>
                </div>
            </div>
        `).join('');
    }

    async openReport(filePath) {
        try {
            await ipcRenderer.invoke('open-report', filePath);
            this.updateStatus(`已打开报告: ${filePath.split('/').pop()}`);
        } catch (error) {
            console.error('打开报告失败:', error);
            this.updateStatus('打开报告失败', 'error');
        }
    }

    updateStatus(message, type = 'ready') {
        const statusElement = document.getElementById('statusText');
        
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `status-text ${type}`;
            
            // 3秒后恢复默认状态
            if (type !== 'ready') {
                setTimeout(() => {
                    statusElement.textContent = '就绪';
                    statusElement.className = 'status-text ready';
                }, 3000);
            }
        }
    }

    // 工具函数
    formatTime(date) {
        return date.toLocaleTimeString('zh-CN', { hour12: false });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 历史管理功能
    async showHistoryModal() {
        const modal = document.getElementById('historyModal');
        const historyCount = document.getElementById('historyCount');
        const historyPreview = document.getElementById('historyPreview');
        const historyContent = document.getElementById('historyContent');
        
        // 获取历史数据
        try {
            const response = await ipcRenderer.invoke('get-conversation-history');
            
            if (response.success) {
                const { conversation_count, summary } = response.data;
                historyCount.textContent = conversation_count;
                
                // 如果有历史记录，显示摘要
                if (conversation_count > 0) {
                    historyContent.textContent = summary;
                    historyPreview.style.display = 'block';
                } else {
                    historyPreview.style.display = 'none';
                }
            } else {
                historyCount.textContent = '获取失败';
                historyPreview.style.display = 'none';
            }
        } catch (error) {
            console.error('获取历史记录失败:', error);
            historyCount.textContent = '错误';
            historyPreview.style.display = 'none';
        }
        
        // 显示弹窗
        modal.style.display = 'flex';
        
        // 绑定事件（确保不重复绑定）
        this.bindHistoryModalEvents();
    }

    bindHistoryModalEvents() {
        const modal = document.getElementById('historyModal');
        const closeBtn = document.getElementById('closeHistoryModal');
        const viewBtn = document.getElementById('viewHistoryBtn');
        const exportBtn = document.getElementById('exportHistoryBtn');
        const clearBtn = document.getElementById('clearHistoryBtn');
        
        // 移除已有的事件监听器（如果存在）
        const newCloseBtn = closeBtn.cloneNode(true);
        closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
        
        const newViewBtn = viewBtn.cloneNode(true);
        viewBtn.parentNode.replaceChild(newViewBtn, viewBtn);
        
        const newExportBtn = exportBtn.cloneNode(true);
        exportBtn.parentNode.replaceChild(newExportBtn, exportBtn);
        
        const newClearBtn = clearBtn.cloneNode(true);
        clearBtn.parentNode.replaceChild(newClearBtn, clearBtn);
        
        // 关闭弹窗
        newCloseBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        // 点击背景关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
        
        // 查看历史
        newViewBtn.addEventListener('click', async () => {
            await this.viewHistory();
        });
        
        // 导出历史
        newExportBtn.addEventListener('click', async () => {
            await this.exportHistory();
        });
        
        // 清空历史
        newClearBtn.addEventListener('click', async () => {
            await this.clearHistory();
        });
    }

    async viewHistory() {
        try {
            const response = await ipcRenderer.invoke('get-conversation-history');
            
            if (response.success) {
                const { conversation_history } = response.data;
                
                if (conversation_history.length === 0) {
                    this.showNotification('暂无对话历史', 'info');
                    return;
                }
                
                // 显示完整历史
                const historyContent = document.getElementById('historyContent');
                let historyText = '';
                
                for (let i = 0; i < conversation_history.length; i += 2) {
                    if (i + 1 < conversation_history.length) {
                        const userMsg = conversation_history[i].content;
                        const assistantMsg = conversation_history[i + 1].content;
                        historyText += `问: ${userMsg}\n\n答: ${assistantMsg}\n\n${'='.repeat(50)}\n\n`;
                    }
                }
                
                historyContent.textContent = historyText;
                document.getElementById('historyPreview').style.display = 'block';
                this.showNotification('历史记录已显示', 'success');
            } else {
                this.showNotification(`获取历史失败: ${response.error}`, 'error');
            }
        } catch (error) {
            console.error('查看历史失败:', error);
            this.showNotification('查看历史失败', 'error');
        }
    }

    async exportHistory() {
        try {
            const response = await ipcRenderer.invoke('export-conversation-history');
            
            if (response.success) {
                const { filename, conversation_count } = response.data;
                this.showNotification(`历史已导出到: ${filename}，包含 ${conversation_count} 轮对话`, 'success');
            } else {
                this.showNotification(`导出失败: ${response.error}`, 'error');
            }
        } catch (error) {
            console.error('导出历史失败:', error);
            this.showNotification('导出历史失败', 'error');
        }
    }

    async clearHistory() {
        if (!confirm('确定要清空所有对话历史吗？此操作不可撤销。')) {
            return;
        }
        
        try {
            const response = await ipcRenderer.invoke('clear-conversation-history');
            
            if (response.success) {
                // 更新UI
                document.getElementById('historyCount').textContent = '0';
                document.getElementById('historyPreview').style.display = 'none';
                this.showNotification('对话历史已清空', 'success');
            } else {
                this.showNotification(`清空失败: ${response.error}`, 'error');
            }
        } catch (error) {
            console.error('清空历史失败:', error);
            this.showNotification('清空历史失败', 'error');
        }
    }

    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // 添加样式
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            z-index: 10001;
            animation: slideInRight 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        `;
        
        document.body.appendChild(notification);
        
        // 3秒后移除
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// 初始化应用
window.staropsRenderer = new StarOpsRenderer();

// 全局函数用于面板控制
window.toggleDataPanel = () => {
    window.staropsRenderer.toggleDataPanel();
};

window.toggleConsolePanel = () => {
    window.staropsRenderer.toggleConsolePanel();
};

// 导出到全局作用域以便在HTML中使用
window.staropsRenderer = window.staropsRenderer;