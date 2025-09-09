#!/bin/bash

# 并发爬坡测试脚本
PAYLOAD_FILE="$1"
LOG_FILE="$2"

echo "并发c | RPS | P95(ms) | 错误率(%)" >> "$LOG_FILE"
echo "------|-----|--------|----------" >> "$LOG_FILE"

# 并发阶梯: 1, 2, 5, 10, 20, 50, 100, 150, 200, 300
CONCURRENCY_LEVELS=(1 2 5 10 20 50 100 150 200 300)

for c in "${CONCURRENCY_LEVELS[@]}"; do
    requests=$((c * 200))
    
    echo "测试并发 c=$c, 请求数=$requests..." >&2
    
    # 运行测试并提取关键数据
    result=$(python simple_load_test.py "$PAYLOAD_FILE" "$c" "$requests" 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        # 使用grep和awk提取数据
        rps=$(echo "$result" | grep "RPS" | grep -o '[0-9]*\.[0-9]*' | head -1)
        p95=$(echo "$result" | grep "P95:" | grep -o '[0-9]*\.[0-9]*' | head -1)
        error_rate=$(echo "$result" | grep "错误率" | grep -o '[0-9]*\.[0-9]*' | head -1)
        
        # 如果提取失败，设置默认值
        rps=${rps:-"0.00"}
        p95=${p95:-"999.99"}
        error_rate=${error_rate:-"100.00"}
        
        printf "%6d | %5s | %8s | %8s\n" "$c" "$rps" "$p95" "$error_rate" >> "$LOG_FILE"
    else
        printf "%6d | ERROR | ERROR  | ERROR\n" "$c" >> "$LOG_FILE"
    fi
    
    # 短暂休息避免系统过载
    sleep 2
done

echo "并发爬坡测试完成，结果保存到: $LOG_FILE" >&2
