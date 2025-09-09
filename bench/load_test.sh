#!/bin/bash

# 简化压测脚本 (Windows Git Bash环境)
# 用法: ./load_test.sh <payload_file> <concurrency> <total_requests> <duration_sec>

PAYLOAD_FILE="$1"
CONCURRENCY="${2:-1}"
TOTAL_REQUESTS="${3:-100}"
DURATION="${4:-0}"
BASE_URL="http://127.0.0.1:8000"

if [[ ! -f "$PAYLOAD_FILE" ]]; then
    echo "错误: 载荷文件 '$PAYLOAD_FILE' 不存在"
    exit 1
fi

echo "=== 压测参数 ==="
echo "载荷文件: $PAYLOAD_FILE"
echo "并发数: $CONCURRENCY"
echo "总请求数: $TOTAL_REQUESTS"
if [[ $DURATION -gt 0 ]]; then
    echo "持续时间: ${DURATION}秒"
fi
echo "目标URL: $BASE_URL/intent"
echo

# 临时结果文件
RESULTS_DIR="raw/temp_$$"
mkdir -p "$RESULTS_DIR"

# 统计变量
declare -a response_times=()
declare -a status_codes=()
declare -a response_headers=()

start_time=$(date +%s.%N)

# 执行测试函数
run_load_test() {
    local requests_per_worker=$((TOTAL_REQUESTS / CONCURRENCY))
    local remainder=$((TOTAL_REQUESTS % CONCURRENCY))
    
    echo "开始压测... (每个worker处理 $requests_per_worker 请求)"
    
    # 并发执行
    for ((i=1; i<=CONCURRENCY; i++)); do
        local worker_requests=$requests_per_worker
        if [[ $i -le $remainder ]]; then
            worker_requests=$((worker_requests + 1))
        fi
        
        {
            for ((j=1; j<=worker_requests; j++)); do
                local req_start=$(date +%s.%N)
                
                response=$(curl -s -w "%{http_code}|%{time_total}|%{header_json}" \
                    -H "Content-Type: application/json" \
                    -X POST \
                    --data @"$PAYLOAD_FILE" \
                    "$BASE_URL/intent" 2>/dev/null)
                
                local req_end=$(date +%s.%N)
                local req_time=$(echo "$req_end - $req_start" | bc -l 2>/dev/null || echo "0.001")
                
                # 解析curl输出
                if [[ "$response" =~ (.*)([0-9]{3})\|([0-9.]+)\|(.*) ]]; then
                    local body="${BASH_REMATCH[1]}"
                    local code="${BASH_REMATCH[2]}"
                    local curl_time="${BASH_REMATCH[3]}"
                    local headers="${BASH_REMATCH[4]}"
                    
                    echo "${code}|${curl_time}|${headers}" >> "$RESULTS_DIR/worker_$i.log"
                else
                    echo "000|${req_time}|" >> "$RESULTS_DIR/worker_$i.log"
                fi
                
                # 基于duration的退出条件
                if [[ $DURATION -gt 0 ]]; then
                    local current_time=$(date +%s.%N)
                    local elapsed=$(echo "$current_time - $start_time" | bc -l 2>/dev/null || echo "999")
                    if (( $(echo "$elapsed > $DURATION" | bc -l 2>/dev/null || echo "0") )); then
                        break 2
                    fi
                fi
            done
        } &
    done
    
    # 等待所有worker完成
    wait
}

# 基于duration的测试
run_duration_test() {
    echo "开始持续时间测试... (持续 $DURATION 秒)"
    
    for ((i=1; i<=CONCURRENCY; i++)); do
        {
            while true; do
                local current_time=$(date +%s.%N)
                local elapsed=$(echo "$current_time - $start_time" | bc -l 2>/dev/null || echo "999")
                if (( $(echo "$elapsed > $DURATION" | bc -l 2>/dev/null || echo "0") )); then
                    break
                fi
                
                local req_start=$(date +%s.%N)
                response=$(curl -s -w "%{http_code}|%{time_total}|%{header_json}" \
                    -H "Content-Type: application/json" \
                    -X POST \
                    --data @"$PAYLOAD_FILE" \
                    "$BASE_URL/intent" 2>/dev/null)
                
                local req_end=$(date +%s.%N)
                local req_time=$(echo "$req_end - $req_start" | bc -l 2>/dev/null || echo "0.001")
                
                if [[ "$response" =~ (.*)([0-9]{3})\|([0-9.]+)\|(.*) ]]; then
                    local code="${BASH_REMATCH[2]}"
                    local curl_time="${BASH_REMATCH[3]}"
                    local headers="${BASH_REMATCH[4]}"
                    echo "${code}|${curl_time}|${headers}" >> "$RESULTS_DIR/worker_$i.log"
                else
                    echo "000|${req_time}|" >> "$RESULTS_DIR/worker_$i.log"
                fi
            done
        } &
    done
    
    wait
}

# 执行测试
if [[ $DURATION -gt 0 ]]; then
    run_duration_test
else
    run_load_test
fi

end_time=$(date +%s.%N)
total_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "1.0")

echo "压测完成! 总耗时: ${total_time}秒"

# 统计结果
echo
echo "=== 结果统计 ==="

# 合并所有worker结果
cat "$RESULTS_DIR"/worker_*.log > "$RESULTS_DIR/all_results.log" 2>/dev/null

total_requests_actual=$(wc -l < "$RESULTS_DIR/all_results.log" 2>/dev/null || echo "0")
echo "实际完成请求数: $total_requests_actual"

if [[ $total_requests_actual -eq 0 ]]; then
    echo "错误: 没有成功的请求"
    rm -rf "$RESULTS_DIR"
    exit 1
fi

# 计算RPS
rps=$(echo "scale=2; $total_requests_actual / $total_time" | bc -l 2>/dev/null || echo "0.00")
echo "RPS (每秒请求数): $rps"

# 状态码分布
echo
echo "状态码分布:"
if command -v awk >/dev/null; then
    awk -F'|' '{count[$1]++} END {for (code in count) printf "%s: %d\n", code, count[code]}' "$RESULTS_DIR/all_results.log" | sort
else
    cut -d'|' -f1 "$RESULTS_DIR/all_results.log" | sort | uniq -c | sort -nr
fi

# 响应时间统计
echo
echo "响应时间统计 (秒):"
if command -v awk >/dev/null; then
    response_times=$(awk -F'|' '{if($2 > 0) print $2}' "$RESULTS_DIR/all_results.log")
    if [[ -n "$response_times" ]]; then
        echo "$response_times" | awk '{
            sum+=$1; count++; 
            if(count==1) min=max=$1
            if($1<min) min=$1
            if($1>max) max=$1
            times[count]=$1
        } END {
            if(count>0) {
                avg=sum/count
                printf "平均: %.3f秒\n", avg
                printf "最小: %.3f秒\n", min  
                printf "最大: %.3f秒\n", max
                
                # 简单百分位估算
                print "注: 详细百分位需要排序，这里显示基本统计"
            }
        }'
    fi
else
    echo "响应时间原始数据已保存到: $RESULTS_DIR/all_results.log"
fi

# 保留结果文件用于分析
echo
echo "详细结果保存在: $RESULTS_DIR/all_results.log"
echo "格式: 状态码|响应时间(秒)|响应头"
