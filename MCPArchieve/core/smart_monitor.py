# -*- coding: utf-8 -*-
"""
智能监控器核心模块
"""

import json
import re
from .ai_model import OnlineModel
from .mcp_protocols import (
    WindowsIOMonitorProtocol, 
    PrometheusMonitorProtocol, 
    TrivySecurityProtocol,
    NodeExporterProtocol,
    BlackboxExporterProtocol,
    MysqldExporterProtocol,
    LokiPromtailProtocol,
    AutofixProtocol,
    WebScanProtocol,
    MySQLOptimizationProtocol,
    SkyWalkingProtocol,
    AnomalyPatternDetectionProtocol,
    FusionLLMAnomalyDetectionProtocol
)

class SmartMonitor:
    def __init__(self, api_key):
        self.model = OnlineModel(api_key)
        # MCP协议注册表
        self.mcp_protocols = {
            "WindowsIOMonitorProtocol": WindowsIOMonitorProtocol,
            "PrometheusMonitorProtocol": PrometheusMonitorProtocol,
            "TrivySecurityProtocol": TrivySecurityProtocol,
            "NodeExporterProtocol": NodeExporterProtocol,
            "BlackboxExporterProtocol": BlackboxExporterProtocol,
            "MysqldExporterProtocol": MysqldExporterProtocol,
            "LokiPromtailProtocol": LokiPromtailProtocol,
            "AutofixProtocol": AutofixProtocol,
            "WebScanProtocol": WebScanProtocol,
            "MySQLOptimizationProtocol": MySQLOptimizationProtocol,
            "SkyWalkingProtocol": SkyWalkingProtocol,
            "AnomalyPatternDetectionProtocol": AnomalyPatternDetectionProtocol,
            "FusionLLMAnomalyDetectionProtocol": FusionLLMAnomalyDetectionProtocol
        }
        # 对话历史管理
        self.conversation_history = []
        self.max_history_length = 3
    
    def _add_to_history(self, user_question, assistant_response):
        """添加对话到历史记录"""
        self.conversation_history.append({"role": "user", "content": user_question})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        # 限制历史长度
        if len(self.conversation_history) > self.max_history_length * 2:
            self.conversation_history = self.conversation_history[-(self.max_history_length * 2):]
    
    def _get_conversation_summary(self):
        """获取对话历史摘要"""
        if not self.conversation_history:
            return "暂无对话历史"
        
        summary = []
        for i in range(0, len(self.conversation_history), 2):
            if i + 1 < len(self.conversation_history):
                user_msg = self.conversation_history[i]["content"]
                assistant_msg = self.conversation_history[i + 1]["content"]
                summary.append(f"Q: {user_msg[:100]}...")
                summary.append(f"A: {assistant_msg[:100]}...")
        
        return "\n".join(summary[-10:])
    
    def _execute_mcp_protocol(self, protocol_name, params=None):
        """执行MCP协议"""
        if protocol_name in self.mcp_protocols:
            protocol_class = self.mcp_protocols[protocol_name]
            print(f"🔍 正在执行MCP协议: {protocol_name}")
            print(f"📋 参数: {params}")
            return protocol_class.execute(params)
        else:
            raise ValueError(f"未知的MCP协议: {protocol_name}")
    
    def _detect_mcp_call(self, response):
        """检测AI响应中的MCP调用指令"""
        mcp_call_pattern = r'\[MCP_CALL\](\{.*?\})\[/MCP_CALL\]'

        # print("debug - mcp_call_pattern", mcp_call_pattern)
        # print("debug - response", response)

        match = re.search(mcp_call_pattern, response, re.DOTALL)
        
        if match:
            try:
                call_data = json.loads(match.group(1))
                protocol_name = call_data.get("protocol")
                params = call_data.get("params", {})
                print(f"🔍 检测到MCP调用标签，协议: {protocol_name}")
                return protocol_name, params
            except json.JSONDecodeError as e:
                print(f"❌ MCP调用格式解析失败: {str(e)}")
                print(f"📄 原始JSON: {match.group(1)}")
                return None, None
        else:
            print("🔍 AI响应中未检测到MCP_CALL标签")
            print(f"📝 AI响应内容预览: {response[:200]}...")
        return None, None
    
    def smart_query(self, user_question):
        """智能查询：使用MCP格式进行函数调用，支持对话上下文"""
        print(f"❓ 用户问题：{user_question}")
        print("🤖 AI正在分析...")
        
        # 第一步：让AI判断是否需要调用MCP协议
        ai_response = self.model.ask(user_question, self.conversation_history)

        # print("debug - user_question", user_question)

        print(f"🔮 AI初步分析：{ai_response}")
        
        # 检测是否需要调用MCP协议
        protocol_name, params = self._detect_mcp_call(ai_response)
        
        final_response = ""
        
        if protocol_name:
            print(f"⚡ 检测到MCP协议调用：{protocol_name}")
            print(f"📊 协议参数：{params}")
            
            # 执行MCP协议获取数据
            try:
                print(f"🔧 开始执行MCP协议: {protocol_name}")
                mcp_result = self._execute_mcp_protocol(protocol_name, params)
                print("✅ MCP协议执行完成")
                
                # 对于SkyWalkingProtocol，脚本输出已实时显示，不需要重复输出
                if protocol_name == "SkyWalkingProtocol":
                    # 显示执行状态摘要
                    if mcp_result.get("status") == "success":
                        print(f"\n✅ SkyWalking分析执行成功")
                        print(f"📊 分析类型: {mcp_result.get('summary', {}).get('analysis_type', '微服务分布式追踪')}")
                        print(f"💡 结果说明: 详细分析结果已在上方实时输出中显示")
                    else:
                        print(f"\n❌ SkyWalking分析执行失败: {mcp_result.get('message', '未知错误')}")
                        if mcp_result.get("error"):
                            print(f"错误详情: {mcp_result['error']}")
                    
                    # 保存简单的响应到历史
                    simple_response = f"已执行SkyWalking分析，状态: {mcp_result.get('status', 'unknown')}"
                    self._add_to_history(user_question, simple_response)
                    
                    return {
                        "type": "skywalking_direct_output",
                        "protocol": protocol_name,
                        "params": params,
                        "mcp_result": mcp_result,
                        "message": "SkyWalking分析完成，结果已实时输出"
                    }
                else:
                    # 其他协议使用原有的AI分析逻辑
                    print("🧠 AI正在分析MCP数据...")
                    final_analysis = self.model.ask_with_data_analysis(mcp_result, user_question, self.conversation_history)
                    final_response = final_analysis
                    
                    # 保存到对话历史
                    self._add_to_history(user_question, final_analysis)
                    
                    return {
                        "type": "mcp_analysis",
                        "protocol": protocol_name,
                        "params": params,
                        "mcp_result": mcp_result,
                        "analysis": final_analysis
                    }
            except Exception as e:
                error_msg = f"MCP协议执行失败: {str(e)}"
                self._add_to_history(user_question, error_msg)
                return {
                    "type": "error", 
                    "message": error_msg
                }
        else:
            # 直接回答，不需要调用MCP协议
            final_response = ai_response
            self._add_to_history(user_question, ai_response)
            return {
                "type": "direct_answer",
                "answer": ai_response
            }
    
    def show_conversation_history(self):
        """显示对话历史"""
        print("\n📚 对话历史：")
        print("-" * 50)
        if not self.conversation_history:
            print("暂无对话历史")
        else:
            for i, msg in enumerate(self.conversation_history):
                role = "🤔 用户" if msg["role"] == "user" else "🤖 助手"
                print(f"{role}: {msg['content'][:150]}{'...' if len(msg['content']) > 150 else ''}")
        print("-" * 50) 