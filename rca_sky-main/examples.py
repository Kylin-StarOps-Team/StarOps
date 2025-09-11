"""
示例配置和测试用例
"""

import json
from datetime import datetime, timedelta


# 模拟SkyWalking数据示例
def generate_sample_skywalking_data():
    """生成示例SkyWalking数据"""
    now = datetime.now()
    start_time = now - timedelta(minutes=15)
    
    sample_data = {
        "timestamp": now.isoformat(),
        "time_range": {
            "start": start_time.isoformat(),
            "end": now.isoformat()
        },
        "topology": {
            "nodes": [
                {"id": "user-service", "name": "user-service", "type": "USER", "isReal": True},
                {"id": "order-service", "name": "order-service", "type": "USER", "isReal": True},
                {"id": "payment-service", "name": "payment-service", "type": "USER", "isReal": True},
                {"id": "inventory-service", "name": "inventory-service", "type": "USER", "isReal": True},
                {"id": "notification-service", "name": "notification-service", "type": "USER", "isReal": True}
            ],
            "calls": [
                {"source": "user-service", "target": "order-service", "id": "1", "detectPoints": []},
                {"source": "order-service", "target": "payment-service", "id": "2", "detectPoints": []},
                {"source": "order-service", "target": "inventory-service", "id": "3", "detectPoints": []},
                {"source": "order-service", "target": "notification-service", "id": "4", "detectPoints": []}
            ]
        },
        "services": [
            {
                "service": {"id": "user-service", "name": "user-service"},
                "metrics": {
                    "service_cpm": {
                        "values": [{"values": [{"value": 120}, {"value": 115}, {"value": 130}]}]
                    },
                    "service_sla": {
                        "values": [{"values": [{"value": 99.8}, {"value": 99.5}, {"value": 99.9}]}]
                    },
                    "service_resp_time": {
                        "values": [{"values": [{"value": 200}, {"value": 180}, {"value": 220}]}]
                    }
                },
                "traces": [
                    {"duration": 200, "start": now.timestamp(), "isError": False, "traceIds": ["trace1"]},
                    {"duration": 180, "start": now.timestamp(), "isError": False, "traceIds": ["trace2"]}
                ],
                "instances": [{"id": "user-service-1", "name": "user-service-1"}]
            },
            {
                "service": {"id": "order-service", "name": "order-service"},
                "metrics": {
                    "service_cpm": {
                        "values": [{"values": [{"value": 80}, {"value": 85}, {"value": 75}]}]
                    },
                    "service_sla": {
                        "values": [{"values": [{"value": 98.5}, {"value": 97.8}, {"value": 98.2}]}]
                    },
                    "service_resp_time": {
                        "values": [{"values": [{"value": 500}, {"value": 1200}, {"value": 800}]}]
                    }
                },
                "traces": [
                    {"duration": 500, "start": now.timestamp(), "isError": False, "traceIds": ["trace3"]},
                    {"duration": 1200, "start": now.timestamp(), "isError": True, "traceIds": ["trace4"]},
                    {"duration": 800, "start": now.timestamp(), "isError": False, "traceIds": ["trace5"]}
                ],
                "instances": [{"id": "order-service-1", "name": "order-service-1"}]
            },
            {
                "service": {"id": "payment-service", "name": "payment-service"},
                "metrics": {
                    "service_cpm": {
                        "values": [{"values": [{"value": 60}, {"value": 65}, {"value": 58}]}]
                    },
                    "service_sla": {
                        "values": [{"values": [{"value": 99.2}, {"value": 99.0}, {"value": 99.5}]}]
                    },
                    "service_resp_time": {
                        "values": [{"values": [{"value": 300}, {"value": 320}, {"value": 280}]}]
                    }
                },
                "traces": [
                    {"duration": 300, "start": now.timestamp(), "isError": False, "traceIds": ["trace6"]},
                    {"duration": 320, "start": now.timestamp(), "isError": False, "traceIds": ["trace7"]}
                ],
                "instances": [{"id": "payment-service-1", "name": "payment-service-1"}]
            }
        ]
    }
    
    return sample_data


# 测试配置
def get_test_config():
    """获取测试配置"""
    return {
        "skywalking": {
            "base_url": "http://localhost:12800",
            "timeout": 30
        },
        "ollama": {
            "base_url": "http://localhost:11434",
            "model": "gemma3:12b-it-qat",
            "timeout": 600
        },
        "anomaly_detection": {
            "response_time_threshold": 1000,
            "error_rate_threshold": 5.0,
            "throughput_drop_threshold": 30.0,
            "time_window": 15,
            "algorithms": ["statistical", "isolation_forest", "z_score"]
        },
        "root_cause_analysis": {
            "max_depth": 5,
            "correlation_threshold": 0.7,
            "time_correlation_window": 5
        },
        "output": {
            "results_dir": "./test_results",
            "log_level": "INFO",
            "save_raw_data": True
        }
    }


if __name__ == "__main__":
    # 生成示例数据文件
    sample_data = generate_sample_skywalking_data()
    
    with open("sample_skywalking_data.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False, default=str)
    
    print("示例数据已生成: sample_skywalking_data.json")
    
    # 生成测试配置
    test_config = get_test_config()
    
    import yaml
    with open("test_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(test_config, f, default_flow_style=False, allow_unicode=True)
    
    print("测试配置已生成: test_config.yaml")
