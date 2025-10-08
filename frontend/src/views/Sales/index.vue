<template>
  <div class="sales">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>销售管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            创建销售订单
          </el-button>
        </div>
      </template>

      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索订单号或客户"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="订单状态" style="width: 150px; margin-left: 10px" @change="handleSearch">
          <el-option label="全部" value="" />
          <el-option label="待处理" value="pending" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px; margin-left: 10px"
          @change="handleSearch"
        />
      </div>

      <el-table :data="sales" style="width: 100%; margin-top: 20px;" v-loading="loading">
        <el-table-column prop="order_number" label="订单号" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="order_date" label="订单日期">
          <template #default="scope">
            {{ formatDate(scope.row.order_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额">
          <template #default="scope">
            ¥{{ (scope.row.total_amount || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button size="small" @click="viewSale(scope.row)">查看</el-button>
            <el-button size="small" @click="editSale(scope.row)" v-if="scope.row.status === 'pending'">编辑</el-button>
            <el-button size="small" type="success" @click="updateStatus(scope.row, 'completed')" v-if="scope.row.status === 'pending'">完成</el-button>
            <el-button size="small" type="danger" @click="updateStatus(scope.row, 'cancelled')" v-if="scope.row.status === 'pending'">取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :small="false"
          :disabled="loading"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑销售订单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑销售订单' : '创建销售订单'"
      width="900px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户" prop="customer_id">
              <el-select v-model="form.customer_id" placeholder="请选择客户" style="width: 100%">
                <el-option
                  v-for="customer in customers"
                  :key="customer.id"
                  :label="customer.name"
                  :value="customer.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="订单日期" prop="order_date">
              <el-date-picker
                v-model="form.order_date"
                type="date"
                placeholder="选择订单日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>

        <el-divider content-position="left">销售商品</el-divider>

        <el-form-item>
          <el-button type="primary" @click="addSaleItem">
            <el-icon><Plus /></el-icon>
            添加商品
          </el-button>
        </el-form-item>

        <el-table :data="form.items" style="width: 100%">
          <el-table-column label="商品" width="200">
            <template #default="scope">
              <el-select v-model="scope.row.product_id" placeholder="选择商品" style="width: 100%" @change="handleProductChange(scope.$index)">
                <el-option
                  v-for="product in products"
                  :key="product.id"
                  :label="`${product.name} (${product.sku}) - 库存: ${product.stock}${product.unit}`"
                  :value="product.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="120">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.quantity"
                :min="1"
                :max="getMaxQuantity(scope.$index)"
                style="width: 100%"
                @change="calculateItemTotal(scope.$index)"
              />
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.unit_price"
                :precision="2"
                :step="0.1"
                :min="0"
                style="width: 100%"
                @change="calculateItemTotal(scope.$index)"
              />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120">
            <template #default="scope">
              ¥{{ (scope.row.quantity * scope.row.unit_price || 0).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="scope">
              <el-button size="small" type="danger" @click="removeSaleItem(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-row style="margin-top: 20px;">
          <el-col :span="24" style="text-align: right;">
            <span style="font-size: 16px; font-weight: bold;">总计：¥{{ (totalAmount || 0).toFixed(2) }}</span>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看销售订单详情对话框 -->
    <el-dialog v-model="detailVisible" title="销售订单详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ selectedSale?.order_number }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ selectedSale?.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="订单日期">{{ selectedSale?.order_date ? formatDate(selectedSale.order_date) : '-' }}</el-descriptions-item>
        <!-- <el-descriptions-item label="订单日期">{{ formatDate(selectedSale?.order_date) }}</el-descriptions-item> -->
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(selectedSale?.status??'')">
            {{ getStatusText(selectedSale?.status??'') }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ (selectedSale?.total_amount || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ selectedSale?.notes || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">销售商品明细</el-divider>

      <el-table :data="selectedSaleItems" style="width: 100%">
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="product_sku" label="SKU" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="unit_price" label="单价">
          <template #default="scope">
            ¥{{ (scope.row.unit_price || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_price" label="小计">
          <template #default="scope">
            ¥{{ (scope.row.total_price || 0).toFixed(2) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()

interface Sale {
  id: number
  order_number: string
  customer_id: number
  customer_name: string
  order_date: string
  total_amount: number
  status: string
  notes?: string
}

interface SaleItem {
  product_id: number | null
  product_name: string
  product_sku: string
  quantity: number
  unit_price: number
  total_price: number
}

interface Customer {
  id: number
  name: string
}

interface Product {
  id: number
  name: string
  sku: string
  stock: number
  unit: string
  price: number
}

const sales = ref<Sale[]>([])
const customers = ref<Customer[]>([])
const products = ref<Product[]>([])
const selectedSale = ref<Sale | null>(null)
const selectedSaleItems = ref<SaleItem[]>([])

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const dateRange = ref<[Date, Date] | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const formRef = ref<FormInstance>()
const form = reactive({
  id: 0,
  customer_id: null,
  order_date: new Date(),
  notes: '',
  items: [] as SaleItem[]
})

const rules: FormRules = {
  customer_id: [
    { required: true, message: '请选择客户', trigger: 'change' }
  ],
  order_date: [
    { required: true, message: '请选择订单日期', trigger: 'change' }
  ]
}

const totalAmount = computed(() => {
  return form.items.reduce((sum, item) => sum + (item.quantity * item.unit_price || 0), 0)
})

const getSales = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value || undefined
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }

    const response = await api.get('/sales', { params })
    
    // Handle both array and paginated response
    if (Array.isArray(response)) {
      sales.value = response
      total.value = response.length
    } else if (response && Array.isArray(response.items)) {
      sales.value = response.items
      total.value = response.total || response.items.length
    } else {
      sales.value = []
      total.value = 0
    }
  } catch (error: any) {
    console.error('获取销售订单列表失败:', error)
    // Check if it's an auth error
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(`获取销售订单列表失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
    }
    sales.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const getCustomers = async () => {
  try {
    const response = await api.get('/customers')
    customers.value = response.data || response || []
  } catch (error) {
    console.error('获取客户列表失败:', error)
  }
}

const getProducts = async () => {
  try {
    const response = await api.get('/products')
    products.value = response.data || response || []
  } catch (error) {
    console.error('获取商品列表失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  getSales()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  getSales()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getSales()
}

const showAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editSale = async (sale: Sale) => {
  isEdit.value = true
  try {
    const token = authStore.token
    const response = await fetch(`/api/sales/${sale.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      Object.assign(form, {
        id: data.id,
        customer_id: data.customer_id,
        order_date: new Date(data.order_date),
        notes: data.notes || '',
        items: data.items
      })
      dialogVisible.value = true
    }
  } catch (error) {
    console.error('获取销售订单详情失败:', error)
    ElMessage.error('获取销售订单详情失败')
  }
}

const viewSale = async (sale: Sale) => {
  try {
    const token = authStore.token
    const response = await fetch(`/api/sales/${sale.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      selectedSale.value = data
      selectedSaleItems.value = data.items
      detailVisible.value = true
    }
  } catch (error) {
    console.error('获取销售订单详情失败:', error)
    ElMessage.error('获取销售订单详情失败')
  }
}

const resetForm = () => {
  Object.assign(form, {
    id: 0,
    customer_id: null,
    order_date: new Date(),
    notes: '',
    items: []
  })
  formRef.value?.clearValidate()
}

const addSaleItem = () => {
  form.items.push({
    product_id: null,
    product_name: '',
    product_sku: '',
    quantity: 1,
    unit_price: 0,
    total_price: 0
  })
}

const removeSaleItem = (index: number) => {
  form.items.splice(index, 1)
}

const handleProductChange = (index: number) => {
  const item = form.items[index]
  const product = products.value.find(p => p.id === item.product_id)
  if (product) {
    item.product_name = product.name
    item.product_sku = product.sku
    item.unit_price = product.price
    if (item.quantity > product.stock) {
      item.quantity = product.stock
      ElMessage.warning(`库存不足，已调整为最大库存数量 ${product.stock}`)
    }
  }
  calculateItemTotal(index)
}

const getMaxQuantity = (index: number) => {
  const item = form.items[index]
  const product = products.value.find(p => p.id === item.product_id)
  return product ? product.stock : 999999
}

const calculateItemTotal = (index: number) => {
  const item = form.items[index]
  item.total_price = item.quantity * item.unit_price
}

const handleSubmit = async () => {
  if (!formRef.value) return

  if (form.items.length === 0) {
    ElMessage.error('请至少添加一个销售商品')
    return
  }

  // 检查库存
  for (const item of form.items) {
    const product = products.value.find(p => p.id === item.product_id)
    if (product && item.quantity > product.stock) {
      ElMessage.error(`商品 "${product.name}" 库存不足，当前库存: ${product.stock}`)
      return
    }
  }

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const token = authStore.token
        const url = isEdit.value ? `/api/sales/${form.id}` : '/api/sales/'
        const method = isEdit.value ? 'PUT' : 'POST'

        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            customer_id: form.customer_id,
            order_date: form.order_date.toISOString().split('T')[0],
            notes: form.notes,
            items: form.items
          })
        })

        if (response.ok) {
          ElMessage.success(isEdit.value ? '销售订单更新成功' : '销售订单创建成功')
          dialogVisible.value = false
          getSales()
        } else {
          const error = await response.json()
          ElMessage.error(error.detail || '操作失败')
        }
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const updateStatus = async (sale: Sale, status: string) => {
  try {
    const token = authStore.token
    const response = await fetch(`/api/sales/${sale.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ status })
    })

    if (response.ok) {
      ElMessage.success('订单状态更新成功')
      getSales()
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '状态更新失败')
    }
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败')
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'completed': return 'success'
    case 'cancelled': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '待处理'
    case 'completed': return '已完成'
    case 'cancelled': return '已取消'
    default: return status
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  getSales()
  getCustomers()
  getProducts()
})

onBeforeUnmount(() => {
  // 清理组件状态
  loading.value = false
  submitting.value = false
  dialogVisible.value = false
  detailVisible.value = false
  isEdit.value = false
})
</script>

<style scoped>
.sales {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>