// 实时数据看板JavaScript
let socket;
let stageChartInstance = null;
let workerChartInstance = null;
let trendChartInstance = null;

// 初始化WebSocket连接
function initWebSocket() {
    socket = io.connect(location.origin);

    socket.on('connect', () => {
        console.log('WebSocket连接成功');
        updateConnectionStatus(true);
        socket.emit('request_update');
    });

    socket.on('disconnect', () => {
        console.log('WebSocket断开连接');
        updateConnectionStatus(false);
    });

    socket.on('connected', (data) => {
        console.log('服务器响应:', data);
        if (data.status === 'error') {
            alert(data.message);
        }
    });

    socket.on('dashboard_update', (data) => {
        console.log('收到数据更新:', data);
        updateDashboard(data);
    });

    socket.on('error', (data) => {
        console.error('错误:', data.message);
        alert('数据获取失败: ' + data.message);
    });

    socket.on('new_alert', (alert) => {
        showAlertNotification(alert);
    });

    // 心跳检测
    setInterval(() => {
        if (socket.connected) {
            socket.emit('ping');
        }
    }, 30000);
}

// 更新连接状态
function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connection-status');
    if (connected) {
        statusEl.textContent = '已连接';
        statusEl.className = 'connection-status status-connected';
    } else {
        statusEl.textContent = '连接断开';
        statusEl.className = 'connection-status status-disconnected';
    }
}

// 更新看板数据
function updateDashboard(data) {
    // 更新核心指标
    if (data.metrics) {
        document.getElementById('total-prescriptions').textContent = data.metrics.total_prescriptions || 0;
        document.getElementById('today-prescriptions').textContent = data.metrics.today_prescriptions || 0;
        document.getElementById('pending-tasks').textContent = data.metrics.pending_tasks || 0;
        document.getElementById('completed-today').textContent = data.metrics.completed_today || 0;
    }

    // 更新图表
    if (data.stage_distribution) {
        updateStageChart(data.stage_distribution);
    }

    if (data.worker_efficiency) {
        updateWorkerChart(data.worker_efficiency);
    }

    if (data.hourly_stats) {
        updateTrendChart(data.hourly_stats);
    }

    // 更新时间戳
    if (data.timestamp) {
        const date = new Date(data.timestamp);
        document.getElementById('last-update-time').textContent =
            `最后更新: ${date.toLocaleString('zh-CN')}`;
    }
}

// 更新阶段分布饼图
function updateStageChart(distribution) {
    const ctx = document.getElementById('stageChart').getContext('2d');

    const chartData = {
        labels: ['待收方', '待配方', '待煎药'],
        datasets: [{
            data: [
                distribution.receive || 0,
                distribution.formulate || 0,
                distribution.decoction || 0
            ],
            backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 206, 86, 0.8)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)'
            ],
            borderWidth: 2
        }]
    };

    if (stageChartInstance) {
        stageChartInstance.data = chartData;
        stageChartInstance.update();
    } else {
        stageChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += context.parsed + ' 个任务';
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
}

// 更新工人效率柱状图
function updateWorkerChart(efficiency) {
    const ctx = document.getElementById('workerChart').getContext('2d');

    const labels = efficiency.map(w => w.name);
    const data = efficiency.map(w => w.completed_count);

    const chartData = {
        labels: labels,
        datasets: [{
            label: '完成任务数',
            data: data,
            backgroundColor: 'rgba(67, 233, 123, 0.8)',
            borderColor: 'rgba(67, 233, 123, 1)',
            borderWidth: 2
        }]
    };

    if (workerChartInstance) {
        workerChartInstance.data = chartData;
        workerChartInstance.update();
    } else {
        workerChartInstance = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// 更新趋势折线图
function updateTrendChart(stats) {
    const ctx = document.getElementById('trendChart').getContext('2d');

    const chartData = {
        labels: stats.hours || [],
        datasets: [{
            label: '完成任务数',
            data: stats.completed || [],
            borderColor: 'rgba(102, 126, 234, 1)',
            backgroundColor: 'rgba(102, 126, 234, 0.2)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }]
    };

    if (trendChartInstance) {
        trendChartInstance.data = chartData;
        trendChartInstance.update();
    } else {
        trendChartInstance = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// 显示告警通知
function showAlertNotification(alert) {
    const alertColor = alert.level === 'high' ? '#ef4444' : '#f59e0b';
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${alertColor};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        max-width: 400px;
        animation: slideIn 0.3s ease;
    `;
    notification.innerHTML = `
        <strong>${alert.type}</strong>
        <p style="margin: 8px 0 0 0;">${alert.message}</p>
        <button onclick="this.parentElement.remove()" style="
            background: rgba(255,255,255,0.3);
            border: none;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 8px;
        ">知道了</button>
    `;

    document.body.appendChild(notification);

    // 5秒后自动移除
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);

    // 播放提示音（如果需要）
    if (alert.level === 'high') {
        playAlertSound();
    }
}

// 播放告警提示音
function playAlertSound() {
    // 使用Web Audio API创建简单的提示音
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (e) {
        console.log('无法播放提示音:', e);
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    initWebSocket();
});
