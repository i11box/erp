<template>
  <div class="purchases">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采购管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            创建采购订单
          </el-button>
        </div>
      </template>

      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索订单号或供应商"
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
      </div>

      <el-table :data="purchases" style="width: 100%; margin-top: 20px;" v-loading="loading">
        <el-table-column prop="order_number" label="订单号" />
        <el-table-column prop="supplier_name" label="供应商" />
        <el-table-column prop="order_date" label="订单日期">
          <template #default="scope">
            {{ formatDate(scope.row.order_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额">
          <template #default="scope">
            ¥{{ Number(scope.row.total_amount || 0).toFixed(2) }}
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
            <el-button size="small" @click="viewPurchase(scope.row)">查看</el-button>
            <el-button size="small" @click="editPurchase(scope.row)" v-if="scope.row.status === 'pending'">编辑</el-button>
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

    <!-- 添加/编辑采购订单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑采购订单' : '创建采购订单'"
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
            <el-form-item label="供应商" prop="supplier_id">
              <el-select v-model="form.supplier_id" placeholder="请选择供应商" style="width: 100%">
                <el-option
                  v-for="supplier in suppliers"
                  :key="supplier.id"
                  :label="supplier.name"
                  :value="supplier.id"
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

        <el-divider content-position="left">采购商品</el-divider>

        <el-form-item>
          <el-button type="primary" @click="addPurchaseItem">
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
                  :label="`${product.name} (${product.sku})`"
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
              <el-button size="small" type="danger" @click="removePurchaseItem(scope.$index)">删除</el-button>
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

    <!-- 查看采购订单详情对话框 -->
    <el-dialog v-model="detailVisible" title="采购订单详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ selectedPurchase?.order_number }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ selectedPurchase?.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="订单日期">{{ formatDate(selectedPurchase?.order_date) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(selectedPurchase?.status || '')">
            {{ getStatusText(selectedPurchase?.status || '') }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ (selectedPurchase?.total_amount || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ selectedPurchase?.notes || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">采购商品明细</el-divider>

      <el-table :data="selectedPurchaseItems" style="width: 100%">
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
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()

interface Purchase {
  id: number
  order_number: string
  supplier_id: number
  supplier_name: string
  order_date: string
  total_amount: number
  status: string
  notes?: string
}

interface PurchaseItem {
  product_id: number | null
  product_name: string
  product_sku: string
  quantity: number
  unit_price: number
  total_price: number
}

interface Supplier {
  id: number
  name: string
}

interface Product {
  id: number
  name: string
  sku: string
}

const purchases = ref<Purchase[]>([])
const suppliers = ref<Supplier[]>([])
const products = ref<Product[]>([])
const selectedPurchase = ref<Purchase | null>(null)
const selectedPurchaseItems = ref<PurchaseItem[]>([])

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 添加一个用于跟踪组件是否已卸载的ref
const isComponentMounted = ref(true)

const formRef = ref<FormInstance>()
const form = reactive({
  id: 0,
  supplier_id: null,
  order_date: new Date(),
  notes: '',
  items: [] as PurchaseItem[]
})

const rules: FormRules = {
  supplier_id: [
    { required: true, message: '请选择供应商', trigger: 'change' }
  ],
  order_date: [
    { required: true, message: '请选择订单日期', trigger: 'change' }
  ]
}

const totalAmount = computed(() => {
  return form.items.reduce((sum, item) => sum + (item.quantity * item.unit_price || 0), 0)
})

const getPurchases = async () => {
  // 检查组件是否仍然挂载
  if (!isComponentMounted.value) return;
  
  loading.value = true
  try {
    const response = await api.get('/purchases', {
      params: {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value,
        search: searchQuery.value || undefined,
        status: statusFilter.value || undefined
      }
    })
    
    // 检查组件是否仍然挂载
    if (!isComponentMounted.value) return;
    
    // Handle both array and paginated response
    if (Array.isArray(response)) {
      purchases.value = response
      total.value = response.length
    } else if (response && Array.isArray(response.items)) {
      purchases.value = response.items
      total.value = response.total || response.items.length
    } else {
      purchases.value = []
      total.value = 0
    }
  } catch (error: any) {
    // 检查组件是否仍然挂载
    if (!isComponentMounted.value) return;
    
    console.error('获取采购订单列表失败:', error)
    // Check if it's an auth error
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(`获取采购订单列表失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
    }
    purchases.value = []
    total.value = 0
  } finally {
    // 检查组件是否仍然挂载
    if (!isComponentMounted.value) return;
    loading.value = false
  }
}

const getSuppliers = async () => {
  try {
    const response = await api.get('/suppliers')
    suppliers.value = response.data || response || []
  } catch (error) {
    console.error('获取供应商列表失败:', error)
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
  getPurchases()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  getPurchases()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getPurchases()
}

const showAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editPurchase = async (purchase: Purchase) => {
  isEdit.value = true
  try {
    // 使用统一的api实例替代原生fetch
    const response = await api.get(`/purchases/${purchase.id}`)
    
    // 检查组件是否仍然挂载
    if (!isComponentMounted.value) return;
    
    Object.assign(form, {
      id: response.id,
      supplier_id: response.supplier_id,
      order_date: new Date(response.order_date),
      notes: response.notes || '',
      items: response.items
    })
    dialogVisible.value = true
  } catch (error) {
    // 检查组件是否仍然挂载
    if (!isComponentMounted.value) return;
    
    console.error('获取采购订单详情失败:', error)
    ElMessage.error('获取采购订单详情失败')
  }
}

const viewPurchase = async (purchase: Purchase) => {
  try {
    // 使用统一的api实例替代原生fetch
    const response = await api.get(`/purchases/${purchase.id}`)
    
    // 检查组件是否仍然挂载
    if (!isComponentMounted.value) return;
    
    selectedPurchase.value = response
    selectedPurchaseItems.value = response.items
    detailVisible.value = true
  } catch (error) {
    // 检查组件是否仍然挂载
    if (!isComponentMounted.value) return;
    
    console.error('获取采购订单详情失败:', error)
    ElMessage.error('获取采购订单详情失败')
  }
}

const resetForm = () => {
  Object.assign(form, {
    id: 0,
    supplier_id: null,
    order_date: new Date(),
    notes: '',
    items: []
  })
  formRef.value?.clearValidate()
}

const addPurchaseItem = () => {
  form.items.push({
    product_id: null,
    product_name: '',
    product_sku: '',
    quantity: 1,
    unit_price: 0,
    total_price: 0
  })
}

const removePurchaseItem = (index: number) => {
  form.items.splice(index, 1)
}

const handleProductChange = (index: number) => {
  const item = form.items[index]
  const product = products.value.find(p => p.id === item.product_id)
  if (product) {
    item.product_name = product.name
    item.product_sku = product.sku
  }
  calculateItemTotal(index)
}

const calculateItemTotal = (index: number) => {
  const item = form.items[index]
  item.total_price = item.quantity * item.unit_price
}

const handleSubmit = async () => {
  if (!formRef.value) return

  if (form.items.length === 0) {
    ElMessage.error('请至少添加一个采购商品')
    return
  }

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        let response;
        if (isEdit.value) {
          response = await api.put(`/purchases/${form.id}`, {
            supplier_id: form.supplier_id,
            order_date: form.order_date.toISOString().split('T')[0],
            notes: form.notes,
            items: form.items
          })
        } else {
          response = await api.post('/purchases/', {
            supplier_id: form.supplier_id,
            order_date: form.order_date.toISOString().split('T')[0],
            notes: form.notes,
            items: form.items
          })
        }
        
        // 检查组件是否仍然挂载
        if (!isComponentMounted.value) return;

        ElMessage.success(isEdit.value ? '采购订单更新成功' : '采购订单创建成功')
        dialogVisible.value = false
        getPurchases()
      } catch (error: any) {
        // 检查组件是否仍然挂载
        if (!isComponentMounted.value) return;
        
        console.error('操作失败:', error)
        ElMessage.error(error.response?.data?.detail || '操作失败')
      } finally {
        // 检查组件是否仍然挂载
        if (!isComponentMounted.value) return;
        submitting.value = false
      }
    }
  })
}

const updateStatus = async (purchase: Purchase, status: string) => {
  try {
    // 使用统一的api实例替代原生fetch
    await api.patch(`/purchases/${purchase.id}/status`, { status })
    
    // 检查组件是否仍然挂载
    if (!isComponentMounted.value) return;
    
    ElMessage.success('订单状态更新成功')
    getPurchases()
  } catch (error: any) {
    // 检查组件是否仍然挂载
    if (!isComponentMounted.value) return;
    
    console.error('状态更新失败:', error)
    ElMessage.error(error.response?.data?.detail || '状态更新失败')
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
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return 'Invalid Date'
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  isComponentMounted.value = true;
  getPurchases()
  getSuppliers()
  getProducts()
})

onBeforeUnmount(() => {
  // 标记组件已卸载
  isComponentMounted.value = false;
  
  // 清理组件状态
  loading.value = false
  submitting.value = false
  dialogVisible.value = false
  detailVisible.value = false
  isEdit.value = false
})
</script>

<style scoped>
.purchases {
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