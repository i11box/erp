<template>
  <div class="analytics-page">
    <el-card class="page-header">
      <h2>统计分析</h2>
      <p>查看业务数据和趋势分析</p>
    </el-card>

    <div class="analytics-content">
      <el-row :gutter="20">
        <!-- 销售报表 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>销售趋势</span>
                <el-date-picker
                  v-model="salesDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  @change="loadSalesReport"
                />
              </div>
            </template>
            <div ref="salesChartRef" style="height: 300px"></div>
          </el-card>
        </el-col>

        <!-- 采购报表 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>采购趋势</span>
                <el-date-picker
                  v-model="purchaseDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  @change="loadPurchaseReport"
                />
              </div>
            </template>
            <div ref="purchaseChartRef" style="height: 300px"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <!-- 热销商品 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>热销商品排行</span>
            </template>
            <el-table :data="topProducts" style="width: 100%">
              <el-table-column prop="product_name" label="商品名称" />
              <el-table-column prop="total_quantity" label="销量" width="100" />
              <el-table-column prop="total_revenue" label="销售额" width="120">
                <template #default="scope">
                  ¥{{ (scope.row.total_revenue || 0).toFixed(2) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <!-- 重要客户 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>重要客户排行</span>
            </template>
            <el-table :data="topCustomers" style="width: 100%">
              <el-table-column prop="customer_name" label="客户名称" />
              <el-table-column prop="order_count" label="订单数" width="100" />
              <el-table-column prop="total_spent" label="消费金额" width="120">
                <template #default="scope">
                  ¥{{ (scope.row.total_spent || 0).toFixed(2) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <!-- 利润分析 -->
      <el-row style="margin-top: 20px">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>利润分析</span>
                <el-date-picker
                  v-model="profitDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  @change="loadProfitAnalysis"
                />
              </div>
            </template>
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="profit-item">
                  <div class="profit-label">销售收入</div>
                  <div class="profit-value revenue">¥{{ (profitAnalysis.sales_revenue || 0).toFixed(2) }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="profit-item">
                  <div class="profit-label">销售成本</div>
                  <div class="profit-value cost">¥{{ (profitAnalysis.sales_cost || 0).toFixed(2) }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="profit-item">
                  <div class="profit-label">毛利润</div>
                  <div class="profit-value gross-profit">¥{{ (profitAnalysis.gross_profit || 0).toFixed(2) }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="profit-item">
                  <div class="profit-label">净利润</div>
                  <div class="profit-value net-profit">¥{{ (profitAnalysis.net_profit || 0).toFixed(2) }}</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '@/services/api'

// Chart refs
const salesChartRef = ref<HTMLElement>()
const purchaseChartRef = ref<HTMLElement>()

// Date ranges
const salesDateRange = ref<[Date, Date]>()
const purchaseDateRange = ref<[Date, Date]>()
const profitDateRange = ref<[Date, Date]>()

// Data
const topProducts = ref<any[]>([])
const topCustomers = ref<any[]>([])
const profitAnalysis = reactive({
  sales_revenue: 0,
  sales_cost: 0,
  gross_profit: 0,
  net_profit: 0
})

// Charts
let salesChart: echarts.ECharts | null = null
let purchaseChart: echarts.ECharts | null = null

// Initialize charts
const initCharts = () => {
  if (salesChartRef.value) {
    salesChart = echarts.init(salesChartRef.value)
  }
  if (purchaseChartRef.value) {
    purchaseChart = echarts.init(purchaseChartRef.value)
  }
}

// Load sales report
const loadSalesReport = async () => {
  if (!salesDateRange.value) return

  try {
    const [start, end] = salesDateRange.value
    const response = await api.get('/analytics/sales-report', {
      params: {
        start_date: formatDate(start),
        end_date: formatDate(end),
        group_by: 'day'
      }
    })

    const data = response.data || response
    if (salesChart && Array.isArray(data)) {
      const option = {
        title: { text: '销售趋势' },
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: data.map((item: any) => item.period || item.date)
        },
        yAxis: { type: 'value' },
        series: [{
          data: data.map((item: any) => item.total_amount || 0),
          type: 'line',
          smooth: true,
          areaStyle: {}
        }]
      }
      salesChart.setOption(option)
    }
  } catch (error: any) {
    ElMessage.error(`加载销售报表失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
  }
}

// Load purchase report
const loadPurchaseReport = async () => {
  if (!purchaseDateRange.value) return

  try {
    const [start, end] = purchaseDateRange.value
    const response = await api.get('/analytics/purchase-report', {
      params: {
        start_date: formatDate(start),
        end_date: formatDate(end),
        group_by: 'day'
      }
    })

    const data = response.data || response
    if (purchaseChart && Array.isArray(data)) {
      const option = {
        title: { text: '采购趋势' },
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: data.map((item: any) => item.period || item.date)
        },
        yAxis: { type: 'value' },
        series: [{
          data: data.map((item: any) => item.total_amount || 0),
          type: 'line',
          smooth: true,
          areaStyle: {}
        }]
      }
      purchaseChart.setOption(option)
    }
  } catch (error: any) {
    ElMessage.error(`加载采购报表失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
  }
}

// Load top products
const loadTopProducts = async () => {
  try {
    const range = getDateRange()
    const response = await api.get('/analytics/top-products', {
      params: {
        start_date: formatDate(range.start),
        end_date: formatDate(range.end),
        limit: 10
      }
    })
    topProducts.value = response.data || response || []
  } catch (error: any) {
    ElMessage.error(`加载热销商品失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
  }
}

// Load top customers
const loadTopCustomers = async () => {
  try {
    const range = getDateRange()
    const response = await api.get('/analytics/top-customers', {
      params: {
        start_date: formatDate(range.start),
        end_date: formatDate(range.end),
        limit: 10
      }
    })
    topCustomers.value = response.data || response || []
  } catch (error: any) {
    ElMessage.error(`加载重要客户失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
  }
}

// Load profit analysis
const loadProfitAnalysis = async () => {
  // const dateRange = profitDateRange.value || getDateRange()
  let dateRange = profitDateRange.value
    ? { start: profitDateRange.value[0], end: profitDateRange.value[1] }
    : getDateRange()
  try {
    const response = await api.get('/analytics/profit-analysis', {
      params: {
        start_date: formatDate(dateRange.start),
        end_date: formatDate(dateRange.end)
      }
    })
    
    Object.assign(profitAnalysis, {
      sales_revenue: response.sales_revenue || 0,
      sales_cost: response.sales_cost || 0,
      gross_profit: response.gross_profit || 0,
      net_profit: response.net_profit || 0
    })
  } catch (error: any) {
    ElMessage.error(`加载利润分析失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
  }
}

// Utility functions
const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0]
}

const getDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setMonth(start.getMonth() - 1)
  return { start, end }
}

onMounted(() => {
  // Initialize date ranges
  const range = getDateRange()
  salesDateRange.value = [range.start, range.end]
  purchaseDateRange.value = [range.start, range.end]
  profitDateRange.value = [range.start, range.end]

  // Initialize charts
  initCharts()

  // Load data
  loadSalesReport()
  loadPurchaseReport()
  loadTopProducts()
  loadTopCustomers()
  loadProfitAnalysis()
})
</script>

<style scoped>
.analytics-page {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profit-item {
  text-align: center;
  padding: 20px;
}

.profit-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.profit-value {
  font-size: 24px;
  font-weight: 600;
}

.profit-value.revenue {
  color: #67C23A;
}

.profit-value.cost {
  color: #F56C6C;
}

.profit-value.gross-profit {
  color: #409EFF;
}

.profit-value.net-profit {
  color: #E6A23C;
}
</style>