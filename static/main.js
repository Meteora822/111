// 全局变量：当前选择的年月
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth() + 1; // JavaScript 月份从0开始
let selectedYear = currentYear; // 用于年度统计

// 初始化选择器
function initSelectors() {
  // 生成月份选择器选项（最近24个月）
  const monthSelector = document.getElementById('monthSelector');
  monthSelector.innerHTML = '';
  const now = new Date();
  for(let i = 23; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const year = d.getFullYear();
    const month = d.getMonth() + 1;
    const value = `${year}-${month.toString().padStart(2, '0')}`;
    const text = `${year}年${month}月`;
    const option = new Option(text, value, false, year === currentYear && month === currentMonth);
    monthSelector.add(option);
  }
  
  // 生成年份选择器选项（最近5年）
  const yearSelector = document.getElementById('yearSelector');
  yearSelector.innerHTML = '';
  const currentYearNum = now.getFullYear();
  for(let i = 4; i >= 0; i--) {
    const year = currentYearNum - i;
    const option = new Option(`${year}年`, year, false, year === selectedYear);
    yearSelector.add(option);
  }
}

async function fetchRecords(start, end){
  let q = [];
  if(start) q.push('start='+start);
  if(end) q.push('end='+end);
  const url = '/api/records' + (q.length?('?'+q.join('&')):'');
  console.log('正在获取记录:', url);
  try {
    const res = await fetch(url);
    if(!res.ok) {
      console.error('获取记录失败:', res.status);
      return [];
    }
    const data = await res.json();
    console.log('获取到记录数:', data.length);
    return data;
  } catch(e) {
    console.error('获取记录异常:', e);
    return [];
  }
}

function renderTable(data){
  const tbody = document.querySelector('#recordTable tbody');
  tbody.innerHTML = '';
  
  if(data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--muted-foreground);padding:2rem;">暂无记录</td></tr>';
    return;
  }
  
  data.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${r.id}</td><td>${r.type === 'income' ? '收入' : '支出'}</td><td>¥${parseFloat(r.amount).toFixed(2)}</td><td>${r.category}</td><td>${r.date}</td><td>${r.note || '-'}</td><td><button data-id="${r.id}" class="del">删除</button></td>`;
    tbody.appendChild(tr);
  });
  
  // 为所有删除按钮添加事件监听
  document.querySelectorAll('.del').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = e.target.dataset.id;
      if(confirm('确定要删除这条记录吗？')) {
        await deleteRecord(id);
      }
    });
  });
}

async function deleteRecord(id){
  try {
    const res = await fetch(`/api/record/${id}`, {method:'DELETE'});
    if(res.ok){
      await refresh();
    } else {
      alert('删除失败');
    }
  } catch(e) {
    console.error('删除失败:', e);
    alert('删除失败，请检查网络连接');
  }
}

async function refresh(){
  console.log('开始刷新数据...');
  const start = document.querySelector('#start').value;
  const end = document.querySelector('#end').value;
  const data = await fetchRecords(start, end);
  renderTable(data);
  
  try {
    const statsUrl = '/api/stats' + (start||end?('?'+(start?('start='+start):'') + (end?('&end='+end):'')) : '');
    console.log('正在获取统计:', statsUrl);
    const statsRes = await fetch(statsUrl);
    if(!statsRes.ok) {
      console.error('获取统计失败:', statsRes.status);
      return;
    }
    const stats = await statsRes.json();
    console.log('统计数据:', stats);
    
    // 渲染日统计图表
    renderDailyChart(stats.daily_stats);
    
    // 渲染分类图表和列表
    renderCategoryStats(stats.by_category);
  } catch(e) {
    console.error('获取统计异常:', e);
  }
  
  // 获取并更新月度统计（独立调用，使用当前选择的年月）
  await refreshMonthSummary();
  
  // 获取并更新年度统计
  await refreshYearSummary();
}

async function refreshMonthSummary() {
  try {
    const url = `/api/stats?year=${currentYear}&month=${currentMonth}`;
    const res = await fetch(url);
    if(!res.ok) {
      console.error('获取月度统计失败:', res.status);
      return;
    }
    const stats = await res.json();
    updateMonthSummaryCard(stats.month_summary);
  } catch(e) {
    console.error('获取月度统计异常:', e);
  }
}

async function refreshYearSummary() {
  try {
    const url = `/api/year-stats?year=${selectedYear}`;
    const res = await fetch(url);
    if(!res.ok) {
      console.error('获取年度统计失败:', res.status);
      return;
    }
    const stats = await res.json();
    updateYearSummaryCard(stats);
  } catch(e) {
    console.error('获取年度统计异常:', e);
  }
}

function updateMonthSummaryCard(summary) {
  const balance = summary.balance || 0;
  const income = summary.income || 0;
  const expense = summary.expense || 0;
  
  // 更新选择器的值
  const value = `${summary.year}-${summary.month.toString().padStart(2, '0')}`;
  document.getElementById('monthSelector').value = value;
  
  document.getElementById('monthBalance').textContent = 
    (balance >= 0 ? '+' : '') + '¥' + balance.toFixed(2);
  document.getElementById('monthIncome').textContent = '¥' + income.toFixed(2);
  document.getElementById('monthExpense').textContent = '¥' + expense.toFixed(2);
  
  // 根据结余调整卡片颜色
  const cards = document.querySelectorAll('.summary-card');
  if(cards[0]) {
    if(balance >= 0) {
      cards[0].style.background = 'linear-gradient(135deg, var(--primary) 0%, oklch(0.5680 0.0778 65.5444) 100%)';
    } else {
      cards[0].style.background = 'linear-gradient(135deg, oklch(0.5471 0.1438 32.9149) 0%, oklch(0.4971 0.1438 32.9149) 100%)';
    }
  }
}

function updateYearSummaryCard(summary) {
  const balance = summary.balance || 0;
  const income = summary.income || 0;
  const expense = summary.expense || 0;
  
  // 更新选择器的值
  document.getElementById('yearSelector').value = summary.year;
  
  document.getElementById('yearBalance').textContent = 
    (balance >= 0 ? '+' : '') + '¥' + balance.toFixed(2);
  document.getElementById('yearIncome').textContent = '¥' + income.toFixed(2);
  document.getElementById('yearExpense').textContent = '¥' + expense.toFixed(2);
  
  // 根据结余调整卡片颜色
  const cards = document.querySelectorAll('.summary-card');
  if(cards[1]) {
    if(balance >= 0) {
      cards[1].style.background = 'linear-gradient(135deg, oklch(0.5604 0.0624 68.5805) 0%, oklch(0.4851 0.0570 72.6827) 100%)';
    } else {
      cards[1].style.background = 'linear-gradient(135deg, oklch(0.5471 0.1438 32.9149) 0%, oklch(0.4471 0.1438 32.9149) 100%)';
    }
  }
}

document.getElementById('recordForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const f = e.target;
  
  // 验证表单
  if(!f.amount.value || parseFloat(f.amount.value) <= 0) {
    alert('请输入有效的金额');
    return;
  }
  if(!f.category.value.trim()) {
    alert('请输入分类');
    return;
  }
  if(!f.date.value) {
    alert('请选择日期');
    return;
  }
  
  const payload = {
    type: f.type.value,
    amount: f.amount.value,
    category: f.category.value.trim(),
    date: f.date.value,
    note: f.note.value.trim()
  };
  
  try {
    const res = await fetch('/api/record', {
      method:'POST', 
      headers:{'Content-Type':'application/json'}, 
      body: JSON.stringify(payload)
    });
    
    if(res.ok){
      f.reset();
      await refresh();
      alert('添加成功！');
    } else {
      const err = await res.json();
      alert('新增失败: ' + (err.error || '未知错误'));
    }
  } catch(e) {
    console.error('提交失败:', e);
    alert('提交失败，请检查网络连接');
  }
});

document.getElementById('filterBtn').addEventListener('click', async ()=>{ await refresh(); });

async function renderChart(by_category){
  // 此函数已弃用，由 renderExpensePieChart 和 renderIncomePieChart 替代
  renderExpensePieChart(by_category);
  renderIncomePieChart(by_category);
}

function renderDailyChart(daily_stats) {
  if(!daily_stats || Object.keys(daily_stats).length === 0) {
    return;
  }
  
  const dates = Object.keys(daily_stats).sort();
  const incomeData = dates.map(d => daily_stats[d].income || 0);
  const expenseData = dates.map(d => daily_stats[d].expense || 0);
  const labels = dates.map(d => d.substring(5)); // 只显示月-日
  
  const ctx = document.getElementById('dailyChart').getContext('2d');
  if(window._daily) window._daily.destroy();
  
  window._daily = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: '支出',
          data: expenseData,
          backgroundColor: 'oklch(0.5471 0.1438 32.9149 / 0.7)',
          borderColor: 'oklch(0.5471 0.1438 32.9149)',
          borderWidth: 1
        },
        {
          label: '收入',
          data: incomeData,
          backgroundColor: 'oklch(0.6180 0.0778 65.5444 / 0.7)',
          borderColor: 'oklch(0.6180 0.0778 65.5444)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: 'oklch(0.3760 0.0225 64.3434)',
            font: { family: "'Libre Baskerville', serif" }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': ¥' + context.parsed.y.toFixed(2);
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '¥' + value;
            },
            color: 'oklch(0.5391 0.0387 71.1655)'
          },
          grid: {
            color: 'oklch(0.8606 0.0321 84.5881)'
          }
        },
        x: {
          ticks: {
            color: 'oklch(0.5391 0.0387 71.1655)'
          },
          grid: {
            display: false
          }
        }
      }
    }
  });
}

// 分类图标映射
const categoryIcons = {
  '餐饮': '🍽️',
  '交通': '🚗',
  '购物': '🛍️',
  '娱乐': '🎮',
  '医疗': '🏥',
  '教育': '📚',
  '住房': '🏠',
  '工资': '💰',
  '兼职': '💼',
  '投资': '📈',
  '其他': '📌',
  '测试': '🧪'
};

function getCategoryIcon(category) {
  return categoryIcons[category] || '📌';
}

// 当前显示的分类类型
let currentCategoryType = 'expense'; // 'expense' 或 'income'

function renderCategoryStats(by_category) {
  renderPieChart(by_category, currentCategoryType);
  renderCategoryList(by_category, currentCategoryType);
}

function renderPieChart(by_category, type) {
  const canvas = document.getElementById('pieChart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  if(window._pie) window._pie.destroy();
  
  const data = by_category.filter(x => x.type === type);
  
  if(data.length === 0) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#999';
    ctx.textAlign = 'center';
    ctx.font = '14px Arial';
    ctx.fillText(type === 'expense' ? '暂无支出数据' : '暂无收入数据', canvas.width/2, canvas.height/2);
    return;
  }
  
  const labels = data.map(x => x.category);
  const values = data.map(x => Math.abs(x.total));
  
  // 根据类型选择配色
  const colors = type === 'expense' ? [
    'oklch(0.65 0.20 25)',   // 橙红
    'oklch(0.70 0.18 40)',   // 橙色
    'oklch(0.72 0.15 60)',   // 金黄
    'oklch(0.65 0.18 15)',   // 深红
    'oklch(0.68 0.16 50)',   // 琥珀
    'oklch(0.60 0.20 30)',   // 褐色
    'oklch(0.70 0.12 70)',   // 浅黄
    'oklch(0.63 0.19 20)',   // 砖红
  ] : [
    'oklch(0.65 0.18 160)',  // 青色
    'oklch(0.60 0.20 200)',  // 蓝色
    'oklch(0.65 0.16 180)',  // 天蓝
    'oklch(0.70 0.15 140)',  // 薄荷绿
    'oklch(0.58 0.18 220)',  // 深蓝
    'oklch(0.68 0.14 170)',  // 浅青
    'oklch(0.62 0.17 190)',  // 海蓝
    'oklch(0.66 0.16 150)',  // 碧绿
  ];
  
  window._pie = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors.slice(0, values.length),
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const value = context.parsed;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percent = ((value / total) * 100).toFixed(1);
              return context.label + ': ¥' + value.toFixed(2) + ' (' + percent + '%)';
            }
          }
        }
      }
    }
  });
}

function renderCategoryList(by_category, type) {
  const data = by_category.filter(x => x.type === type);
  const listDiv = document.getElementById('categoryList');
  
  if(!listDiv) return;
  
  if(!data || data.length === 0) {
    listDiv.innerHTML = '<div style="text-align:center;color:#999;padding:2rem;">' + 
      (type === 'expense' ? '暂无支出数据' : '暂无收入数据') + '</div>';
    return;
  }
  
  const total = data.reduce((sum, item) => sum + item.total, 0);
  
  const colors = type === 'expense' ? [
    'oklch(0.65 0.20 25)',
    'oklch(0.70 0.18 40)',
    'oklch(0.72 0.15 60)',
    'oklch(0.65 0.18 15)',
    'oklch(0.68 0.16 50)',
    'oklch(0.60 0.20 30)',
    'oklch(0.70 0.12 70)',
    'oklch(0.63 0.19 20)',
  ] : [
    'oklch(0.65 0.18 160)',
    'oklch(0.60 0.20 200)',
    'oklch(0.65 0.16 180)',
    'oklch(0.70 0.15 140)',
    'oklch(0.58 0.18 220)',
    'oklch(0.68 0.14 170)',
    'oklch(0.62 0.17 190)',
    'oklch(0.66 0.16 150)',
  ];
  
  const listHtml = data.map((item, index) => {
    const percent = ((item.total / total) * 100).toFixed(1);
    const color = colors[index % colors.length];
    return `
      <div class="category-item">
        <div class="category-icon" style="background: ${color}">
          ${getCategoryIcon(item.category)}
        </div>
        <div class="category-info">
          <div class="category-name">${item.category}</div>
          <div class="category-percent">${percent}%</div>
        </div>
        <div class="category-amount">¥${item.total.toFixed(2)}</div>
      </div>
    `;
  }).join('');
  
  listDiv.innerHTML = listHtml;
}

// 初始化加载
initSelectors();
refresh();

// 月份导航按钮事件
document.getElementById('prevMonth').addEventListener('click', async () => {
  currentMonth--;
  if(currentMonth < 1) {
    currentMonth = 12;
    currentYear--;
  }
  await refreshMonthSummary();
});

document.getElementById('nextMonth').addEventListener('click', async () => {
  currentMonth++;
  if(currentMonth > 12) {
    currentMonth = 1;
    currentYear++;
  }
  await refreshMonthSummary();
});

// 年份导航按钮事件
document.getElementById('prevYear').addEventListener('click', async () => {
  selectedYear--;
  await refreshYearSummary();
});

document.getElementById('nextYear').addEventListener('click', async () => {
  selectedYear++;
  await refreshYearSummary();
});

// 月份选择器事件
document.getElementById('monthSelector').addEventListener('change', async (e) => {
  const [year, month] = e.target.value.split('-');
  currentYear = parseInt(year);
  currentMonth = parseInt(month);
  await refreshMonthSummary();
});

// 年份选择器事件
document.getElementById('yearSelector').addEventListener('change', async (e) => {
  selectedYear = parseInt(e.target.value);
  await refreshYearSummary();
});

// 分类统计切换按钮事件
document.getElementById('btnExpense').addEventListener('click', async () => {
  currentCategoryType = 'expense';
  document.getElementById('btnExpense').classList.add('active');
  document.getElementById('btnIncome').classList.remove('active');
  await refresh();
});

document.getElementById('btnIncome').addEventListener('click', async () => {
  currentCategoryType = 'income';
  document.getElementById('btnIncome').classList.add('active');
  document.getElementById('btnExpense').classList.remove('active');
  await refresh();
});
