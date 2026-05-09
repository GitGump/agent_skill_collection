# ECharts 图表配置参考

## 全局配色方案

```javascript
const COLORS = {
  primary: '#1a237e',    // 深蓝（主色）
  blue: '#1565c0',       // 蓝色
  lightBlue: '#42a5f5',  // 浅蓝
  paleBlue: '#90caf9',   // 淡蓝
  orange: '#ff6f00',     // 橙色（强调）
  amber: '#ffa726',      // 琥珀
  green: '#2e7d32',      // 成功绿
  lightGreen: '#66bb6a', // 浅绿
  red: '#c62828',        // 危险红
  lightRed: '#ef5350',   // 浅红
  yellow: '#f57c00',     // 警告黄
  gray: '#546e7a',       // 灰色
  lightGray: '#eceff1',  // 浅灰
};

const PALETTE = [
  '#1a237e', '#1565c0', '#42a5f5', '#90caf9',
  '#ff6f00', '#ffa726', '#66bb6a', '#ef5350'
];
```

---

## 图表1：渠道分布饼图

```javascript
const option_pie = {
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c}家 ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: '5%',
    top: 'center',
    textStyle: { fontSize: 12, color: '#333' }
  },
  series: [{
    name: '客户来源',
    type: 'pie',
    radius: ['40%', '70%'],  // 环形图
    center: ['40%', '50%'],
    data: [
      { value: 453, name: '企业微信' },
      // ... 其他渠道
    ],
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    },
    label: {
      show: true,
      formatter: '{b}\n{d}%',
      fontSize: 11
    },
    color: PALETTE
  }]
};
```

---

## 图表2：月度趋势柱状图

```javascript
const option_bar_monthly = {
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['1月', '2月', '3月', '4月'],
    axisLine: { lineStyle: { color: '#ccc' } },
    axisLabel: { color: '#666' }
  },
  yAxis: {
    type: 'value',
    name: '商机数量',
    nameTextStyle: { color: '#666' },
    axisLine: { show: false },
    splitLine: { lineStyle: { color: '#f0f0f0' } }
  },
  series: [
    {
      name: '试用',
      type: 'bar',
      stack: 'total',
      data: [165, 136, 229, 205],
      itemStyle: { color: '#1565c0', borderRadius: [0, 0, 0, 0] },
      label: { show: true, position: 'inside', color: '#fff', fontSize: 11 }
    },
    {
      name: '线索',
      type: 'bar',
      stack: 'total',
      data: [3, 0, 97, 119],
      itemStyle: { color: '#ff6f00', borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top', color: '#333', fontSize: 11 }
    }
  ],
  legend: { top: 0, right: 0 }
};
```

---

## 图表3：渠道跟进率对比条形图

```javascript
const option_follow_rate = {
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    formatter: params => params.map(p => `${p.name}: ${p.value}%`).join('<br/>')
  },
  xAxis: {
    type: 'value',
    max: 100,
    axisLabel: { formatter: '{value}%', color: '#666' },
    splitLine: { lineStyle: { color: '#f0f0f0' } }
  },
  yAxis: {
    type: 'category',
    data: ['APP', '小程序', '注册', '钉钉', '企业微信'],
    axisLabel: { color: '#333', fontSize: 12 }
  },
  series: [{
    type: 'bar',
    data: [
      { value: 96, itemStyle: { color: '#66bb6a' } },
      { value: 83, itemStyle: { color: '#66bb6a' } },
      { value: 78, itemStyle: { color: '#42a5f5' } },
      { value: 50, itemStyle: { color: '#ffa726' } },
      { value: 17, itemStyle: { color: '#ef5350' } },
    ],
    barMaxWidth: 30,
    label: {
      show: true,
      position: 'right',
      formatter: '{c}%',
      color: '#333',
      fontSize: 11
    }
  }]
};
```

---

## 图表4：转化率趋势折线图

```javascript
const option_line_trend = {
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    formatter: params => params.map(p => `${p.seriesName}: ${p.value}%`).join('<br/>')
  },
  legend: { top: 0, right: 0 },
  xAxis: {
    type: 'category',
    data: ['1月', '2月', '3月', '4月'],
    axisLine: { lineStyle: { color: '#ccc' } }
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLabel: { formatter: '{value}%', color: '#666' },
    splitLine: { lineStyle: { color: '#f0f0f0' } }
  },
  series: [
    {
      name: '试用转化率',
      type: 'line',
      data: [98.2, 100, 70.2, 63.3],
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { color: '#1565c0', width: 3 },
      itemStyle: { color: '#1565c0' },
      label: { show: true, formatter: '{c}%', position: 'top', fontSize: 11, color: '#1565c0' },
      areaStyle: { color: 'rgba(21, 101, 192, 0.1)' }
    },
    {
      name: '跟进率',
      type: 'line',
      data: [47.6, 36.8, 55.5, 48.1],
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { color: '#ff6f00', width: 3 },
      itemStyle: { color: '#ff6f00' },
      label: { show: true, formatter: '{c}%', position: 'top', fontSize: 11, color: '#ff6f00' },
      areaStyle: { color: 'rgba(255, 111, 0, 0.08)' }
    }
  ]
};
```

---

## 图表5：跟进次数分布

```javascript
const option_followup_dist = {
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['0次', '1次', '2次', '3次', '4次'],
    axisLabel: { color: '#333', fontSize: 12 }
  },
  yAxis: {
    type: 'value',
    name: '商机数量',
    axisLine: { show: false },
    splitLine: { lineStyle: { color: '#f0f0f0' } }
  },
  series: [{
    type: 'bar',
    data: [
      { value: 487, itemStyle: { color: '#ef5350' } },  // 零跟进（红色警示）
      { value: 311, itemStyle: { color: '#42a5f5' } },
      { value: 117, itemStyle: { color: '#66bb6a' } },
      { value: 28, itemStyle: { color: '#66bb6a' } },
      { value: 11, itemStyle: { color: '#66bb6a' } },
    ],
    barMaxWidth: 60,
    label: {
      show: true,
      position: 'top',
      color: '#333',
      fontSize: 12,
      fontWeight: 'bold'
    }
  }]
};
```

---

## 图表6：渠道效能矩阵散点图

```javascript
const option_matrix = {
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    formatter: params => {
      const d = params.data;
      return `<strong>${d.name}</strong><br/>商机量: ${d.value[0]}家<br/>转化率: ${d.value[1]}%<br/>跟进率: ${d.value[2]}%`;
    }
  },
  xAxis: {
    name: '商机量 (家)',
    nameLocation: 'middle',
    nameGap: 30,
    axisLine: { lineStyle: { color: '#ccc' } },
    splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } }
  },
  yAxis: {
    name: '转化率 (%)',
    nameLocation: 'middle',
    nameGap: 35,
    min: 0,
    max: 110,
    axisLine: { lineStyle: { color: '#ccc' } },
    splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } }
  },
  // 添加象限分隔线
  markLine: {
    silent: true,
    data: [
      { xAxis: 100, lineStyle: { color: '#ccc', type: 'dashed' } },  // 根据中位数调整
      { yAxis: 70, lineStyle: { color: '#ccc', type: 'dashed' } }
    ]
  },
  series: [{
    type: 'scatter',
    data: [
      {
        name: '企业微信',
        value: [453, 100, 17],
        symbolSize: 30,
        itemStyle: { color: '#ffa726' }  // 橙：优化对象
      },
      // ... 其他渠道
    ],
    label: {
      show: true,
      formatter: '{@[3]}',  // 显示渠道名
      position: 'top',
      fontSize: 11
    }
  }]
};
```

---

## 数据质量雷达图

```javascript
const option_radar = {
  backgroundColor: 'transparent',
  radar: {
    indicator: [
      { name: '手机号完整', max: 100 },
      { name: '需求填写', max: 100 },
      { name: '试用日期', max: 100 },
      { name: '跟进记录', max: 100 },
      { name: '渠道来源', max: 100 }
    ],
    splitLine: { lineStyle: { color: '#f0f0f0' } },
    axisLine: { lineStyle: { color: '#ddd' } }
  },
  series: [{
    type: 'radar',
    data: [{
      value: [47, 0.3, 77, 49, 100],
      name: '当前完整率',
      areaStyle: { color: 'rgba(21, 101, 192, 0.2)' },
      lineStyle: { color: '#1565c0', width: 2 },
      itemStyle: { color: '#1565c0' }
    }]
  }]
};
```

---

## HTML报告完整框架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>企业快管 · 商机管理月度分析报告</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <style>
    /* 基础样式 */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Microsoft YaHei', sans-serif; background: #f0f2f5; color: #1a1a2e; }

    /* 封面 */
    .cover {
      background: linear-gradient(135deg, #1a237e 0%, #283593 40%, #1565c0 100%);
      color: white; padding: 56px 60px 44px;
    }

    /* KPI卡片 */
    .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; padding: 28px 40px; }
    .kpi-card { background: white; border-radius: 12px; padding: 22px 24px; box-shadow: 0 2px 12px rgba(0,0,0,.06); }

    /* 图表区块 */
    .section { background: white; margin: 16px 40px; padding: 28px 32px; border-radius: 12px; }
    .section-title { font-size: 18px; font-weight: 700; color: #1a237e; margin-bottom: 20px; }

    /* 图表容器 */
    .chart { width: 100%; height: 320px; }
    .chart-lg { width: 100%; height: 400px; }
    .chart-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  </style>
</head>
<body>
  <!-- 封面 -->
  <div class="cover">
    <div class="cover-tag">BUSINESS INTELLIGENCE REPORT</div>
    <div class="cover-title">企业快管 · 商机管理数据分析报告</div>
    <div class="cover-sub">[时间范围] | 数据来源：商机管理系统</div>
    <div class="cover-meta">
      <span>📊 商机总量: [N]家</span>
      <span>📅 报告生成: [日期]</span>
      <span>🔍 分析维度: 获客·跟进·转化·渠道·数据质量</span>
    </div>
  </div>

  <!-- KPI卡片 -->
  <div class="kpi-row">
    <!-- 总商机、试用转化率、跟进率、零跟进率 -->
  </div>

  <!-- 各分析板块 -->
  <div class="section">
    <div class="section-title">📈 一、获客分析</div>
    <div class="chart-grid-2">
      <div id="chart-pie" class="chart"></div>
      <div id="chart-monthly" class="chart"></div>
    </div>
  </div>

  <!-- ... 更多板块 -->

  <script>
    // ECharts 初始化和配置代码
    // 参考上方各图表配置
  </script>
</body>
</html>
```
