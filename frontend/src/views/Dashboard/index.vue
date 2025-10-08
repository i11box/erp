<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" v-loading="loading">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#409EFF"><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ dashboardData.inventory.total_products }}</div>
              <div class="stat-label">商品总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" v-loading="loading">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#F56C6C"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ dashboardData.inventory.low_stock_products }}</div>
              <div class="stat-label">库存不足</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" v-loading="loading">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#67C23A"><Sell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">¥{{ formatNumber(dashboardData.sales.today) }}</div>
              <div class="stat-label">今日销售</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" v-loading="loading">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40" color="#E6A23C"><ShoppingCart /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">¥{{ formatNumber(dashboardData.purchases.today) }}</div>
              <div class="stat-label">今日采购</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>库存不足警告</span>
              <el-button type="primary" size="small" @click="$router.push('/inventory')">
                查看详情
              </el-button>
            </div>
          </template>
          <el-table :data="lowStockItems" style="width: 100%">
            <el-table-column prop="product.name" label="商品名称" />
            <el-table-column prop="quantity" label="当前库存" width="100" />
            <el-table-column prop="product.reorder_level" label="预警值" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag
                  :type="scope.row.quantity === 0 ? 'danger' : 'warning'"
                  size="small"
                >
                  {{ scope.row.quantity === 0 ? '缺货' : '库存不足' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="lowStockItems.length === 0" class="empty-state">
            <el-empty description="暂无库存不足商品" :image-size="80" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>系统概览</span>
              <el-button type="primary" size="small" @click="$router.push('/analytics')">
                查看分析
              </el-button>
            </div>
          </template>
          <div class="overview-content">
            <div class="overview-item">
              <div class="overview-label">客户总数</div>
              <div class="overview-value">{{ dashboardData.counts.customers }}</div>
            </div>
            <div class="overview-item">
              <div class="overview-label">供应商总数</div>
              <div class="overview-value">{{ dashboardData.counts.suppliers }}</div>
            </div>
            <div class="overview-item">
              <div class="overview-label">库存总价值</div>
              <div class="overview-value">¥{{ formatNumber(dashboardData.inventory.total_inventory_value) }}</div>
            </div>
            <div class="overview-item">
              <div class="overview-label">本月销售</div>
              <div class="overview-value">¥{{ formatNumber(dashboardData.sales.month) }}</div>
            </div>
            <div class="overview-item">
              <div class="overview-label">本月采购</div>
              <div class="overview-value">¥{{ formatNumber(dashboardData.purchases.month) }}</div>
            </div>
            <div class="overview-item">
              <div class="overview-label">缺货商品</div>
              <div class="overview-value">{{ dashboardData.inventory.out_of_stock_items }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 销售趋势 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card v-loading="loading">
          <template #header>
            <span>销售趋势</span>
          </template>
          <div ref="salesChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Box, Goods, ShoppingCart, Sell, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/services/api'

// Reactive data
const loading = ref(false)
const salesChartRef = ref<HTMLElement>()
let salesChart: echarts.ECharts | null = null

// Dashboard data
const dashboardData = ref({
  sales: {
    today: 0,
    month: 0,
    year: 0
  },
  purchases: {
    today: 0,
    month: 0
  },
  inventory: {
    total_products: 0,
    low_stock_products: 0,
    out_of_stock_products: 0,
    total_inventory_value: 0
  },
  counts: {
    customers: 0,
    suppliers: 0
  }
})

const lowStockItems = ref<any[]>([])

// Load dashboard data
const loadDashboardData = async () => {
  loading.value = true
  try {
    console.log('正在加载仪表板数据...')
    const response = await api.get('/analytics/dashboard')
    console.log('仪表板数据响应:', response)

    // Handle response data structure
    if (response && typeof response === 'object') {
      dashboardData.value = {
        sales: {
          today: response.sales_today || 0,
          month: response.sales_month || 0,
          year: response.sales_year || 0
        },
        purchases: {
          today: response.purchases_today || 0,
          month: response.purchases_month || 0
        },
        inventory: {
          total_products: response.total_products || 0,
          low_stock_products: response.low_stock_products || 0,
          out_of_stock_products: response.out_of_stock_products || 0,
          total_inventory_value: response.total_inventory_value || 0
        },
        counts: {
          customers: response.total_customers || 0,
          suppliers: response.total_suppliers || 0
        }
      }
    } else {
      // Set default values if no data
      dashboardData.value = {
        sales: { today: 0, month: 0, year: 0 },
        purchases: { today: 0, month: 0 },
        inventory: {
          total_products: 0,
          low_stock_products: 0,
          out_of_stock_products: 0,
          total_inventory_value: 0
        },
        counts: { customers: 0, suppliers: 0 }
      }
    }

    console.log('仪表板数据加载成功:', dashboardData.value)
  } catch (error: any) {
    console.error('加载仪表板数据失败:', error)
    ElMessage.error(`加载仪表板数据失败: ${error.response?.data?.detail || error.message || '未知错误'}`)

    // Set default values on error
    dashboardData.value = {
      sales: { today: 0, month: 0, year: 0 },
      purchases: { today: 0, month: 0 },
      inventory: {
        total_products: 0,
        low_stock_products: 0,
        out_of_stock_products: 0,
        total_inventory_value: 0
      },
      counts: { customers: 0, suppliers: 0 }
    }
  } finally {
    loading.value = false
  }
}

// Load low stock items
const loadLowStockItems = async () => {
  try {
    const response = await api.get('/inventory/low-stock', {
      params: { limit: 5 }
    })
    lowStockItems.value = response
  } catch (error) {
    console.error('加载库存不足商品失败:', error)
  }
}

// Load sales chart
const loadSalesChart = async () => {
  try {
    console.log('正在加载销售图表数据...')
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 7) // 最近7天

    const response = await api.get('/analytics/sales-report', {
      params: {
        start_date: formatDate(startDate),
        end_date: formatDate(endDate),
        group_by: 'day'
      }
    })

    console.log('销售图表数据响应:', response)

    if (salesChart && response && Array.isArray(response)) {
      const option = {
        title: { text: '最近7天销售趋势', left: 'center' },
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>销售额: ¥{c}'
        },
        xAxis: {
          type: 'category',
          data: response.map((item: any) => formatChartDate(item.period || item.date))
        },
        yAxis: {
          type: 'value',
          name: '销售额 (¥)'
        },
        series: [{
          data: response.map((item: any) => item.total_amount || 0),
          type: 'line',
          smooth: true,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ])
          },
          lineStyle: {
            color: '#409EFF',
            width: 2
          },
          itemStyle: {
            color: '#409EFF'
          }
        }]
      }
      salesChart.setOption(option)
      console.log('销售图表更新成功')
    } else {
      console.log('无销售数据或图表未初始化')
      // 创建空数据的图表
      if (salesChart) {
        const option = {
          title: { text: '最近7天销售趋势', left: 'center' },
          xAxis: { type: 'category', data: [] },
          yAxis: { type: 'value', name: '销售额 (¥)' },
          series: [{ data: [], type: 'line' }]
        }
        salesChart.setOption(option)
      }
    }
  } catch (error: any) {
    console.error('加载销售图表失败:', error)
    ElMessage.error(`加载销售图表失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
  }
}

// Initialize chart
const initChart = () => {
  if (salesChartRef.value) {
    salesChart = echarts.init(salesChartRef.value)
  }
}

// Utility functions
const formatNumber = (num: number): string => {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0]
}

const formatChartDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(async () => {
  await nextTick()
  initChart()

  // Load all data
  await Promise.all([
    loadDashboardData(),
    loadLowStockItems(),
    loadSalesChart()
  ])

  // Handle window resize
  window.addEventListener('resize', () => {
    salesChart?.resize()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  height: 120px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overview-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.overview-item {
  text-align: center;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.overview-item:hover {
  background-color: #e9ecef;
}

.overview-label {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 8px;
}

.overview-value {
  font-size: 20px;
  font-weight: 600;
  color: #495057;
}

.empty-state {
  padding: 20px 0;
  text-align: center;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #fafafa;
}

:deep(.el-loading-mask) {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .overview-content {
    grid-template-columns: 1fr;
  }

  .stat-number {
    font-size: 24px;
  }
}
</style>