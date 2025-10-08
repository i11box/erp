<template>
  <div class="inventory">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>库存管理</span>
              <div>
                <el-button type="warning" @click="getLowStockInventory">
                  <el-icon><Warning /></el-icon>
                  库存预警
                </el-button>
                <el-button type="danger" @click="getOutOfStockInventory">
                  <el-icon><CircleClose /></el-icon>
                  缺货商品
                </el-button>
                <el-button type="primary" @click="showAdjustDialog">
                  <el-icon><Edit /></el-icon>
                  库存调整
                </el-button>
              </div>
            </div>
          </template>

          <div class="search-bar">
            <el-input
              v-model="searchQuery"
              placeholder="搜索商品名称或SKU"
              style="width: 300px"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="info" style="margin-left: 10px" @click="getInventorySummary">
              <el-icon><DataLine /></el-icon>
              库存汇总
            </el-button>
          </div>

          <el-table :data="inventory" style="width: 100%; margin-top: 20px;" v-loading="loading">
            <el-table-column prop="product_name" label="商品名称" />
            <el-table-column prop="product_sku" label="SKU" />
            <el-table-column prop="product_category" label="分类" />
            <el-table-column prop="quantity" label="当前库存">
              <template #default="scope">
                <el-tag :type="getStockStatusType(scope.row.quantity, scope.row.min_stock)">
                  {{ scope.row.quantity }} {{ scope.row.unit }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="min_stock" label="最低库存">
              <template #default="scope">
                {{ scope.row.min_stock }} {{ scope.row.unit }}
              </template>
            </el-table-column>
            <el-table-column prop="unit_cost" label="单位成本">
              <template #default="scope">
                ¥{{ scope.row.unit_cost.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_value" label="库存价值">
              <template #default="scope">
                ¥{{ (scope.row.quantity * scope.row.unit_cost).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="adjustStock(scope.row)">调整</el-button>
                <el-button size="small" type="info" @click="viewMovements(scope.row)">记录</el-button>
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
      </el-col>
    </el-row>

    <!-- 库存汇总对话框 -->
    <el-dialog v-model="summaryVisible" title="库存汇总" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="商品种类">{{ summary.total_products }}</el-descriptions-item>
        <el-descriptions-item label="总库存数量">{{ summary.total_quantity }}</el-descriptions-item>
        <el-descriptions-item label="库存总价值">¥{{ summary.total_value.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="低库存商品">{{ summary.low_stock_count }}</el-descriptions-item>
        <el-descriptions-item label="缺货商品">{{ summary.out_of_stock_count }}</el-descriptions-item>
        <el-descriptions-item label="正常商品">{{ summary.normal_stock_count }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 库存调整对话框 -->
    <el-dialog v-model="adjustDialogVisible" title="库存调整" width="500px">
      <el-form
        ref="adjustFormRef"
        :model="adjustForm"
        :rules="adjustRules"
        label-width="80px"
      >
        <el-form-item label="商品">
          <el-input v-model="adjustForm.product_name" readonly />
        </el-form-item>
        <el-form-item label="当前库存">
          <el-input :value="`${adjustForm.current_quantity} ${adjustForm.unit}`" readonly />
        </el-form-item>
        <el-form-item label="调整类型" prop="adjustment_type">
          <el-radio-group v-model="adjustForm.adjustment_type">
            <el-radio label="increase">增加</el-radio>
            <el-radio label="decrease">减少</el-radio>
            <el-radio label="set">设置为</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="调整数量" prop="adjustment_quantity">
          <el-input-number
            v-model="adjustForm.adjustment_quantity"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="调整原因" prop="reason">
          <el-select v-model="adjustForm.reason" placeholder="请选择调整原因" style="width: 100%">
            <el-option label="盘盈" value="盘盈" />
            <el-option label="盘亏" value="盘亏" />
            <el-option label="损坏" value="损坏" />
            <el-option label="退货" value="退货" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="adjustForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="adjustDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAdjustSubmit" :loading="adjustSubmitting">
            确认调整
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 库存变动记录对话框 -->
    <el-dialog v-model="movementsVisible" title="库存变动记录" width="800px">
      <el-table :data="movements" v-loading="movementsLoading" style="width: 100%">
        <el-table-column prop="movement_type" label="变动类型">
          <template #default="scope">
            <el-tag :type="getMovementType(scope.row.movement_type)">
              {{ scope.row.movement_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="created_at" label="时间">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Warning, CircleClose, Edit, DataLine } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

interface InventoryItem {
  id: number
  product_id: number
  product_name: string
  product_sku: string
  product_category: string
  quantity: number
  min_stock: number
  unit: string
  unit_cost: number
}

interface InventoryMovement {
  id: number
  product_id: number
  movement_type: string
  quantity: number
  reason: string
  notes?: string
  created_at: string
}

interface InventorySummary {
  total_products: number
  total_quantity: number
  total_value: number
  low_stock_count: number
  out_of_stock_count: number
  normal_stock_count: number
}

const inventory = ref<InventoryItem[]>([])
const movements = ref<InventoryMovement[]>([])
const summary = ref<InventorySummary>({
  total_products: 0,
  total_quantity: 0,
  total_value: 0,
  low_stock_count: 0,
  out_of_stock_count: 0,
  normal_stock_count: 0
})

const loading = ref(false)
const movementsLoading = ref(false)
const adjustSubmitting = ref(false)
const summaryVisible = ref(false)
const adjustDialogVisible = ref(false)
const movementsVisible = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const adjustFormRef = ref<FormInstance>()
const adjustForm = reactive({
  product_id: 0,
  product_name: '',
  current_quantity: 0,
  unit: '',
  adjustment_type: 'increase',
  adjustment_quantity: 0,
  reason: '',
  notes: ''
})

const adjustRules: FormRules = {
  adjustment_type: [
    { required: true, message: '请选择调整类型', trigger: 'change' }
  ],
  adjustment_quantity: [
    { required: true, message: '请输入调整数量', trigger: 'blur' },
    { type: 'number', min: 0, message: '调整数量必须大于等于0', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请选择调整原因', trigger: 'change' }
  ]
}

const getInventory = async () => {
  loading.value = true
  try {
    const token = authStore.token
    const response = await fetch(`/api/inventory/?skip=${(currentPage.value - 1) * pageSize.value}&limit=${pageSize.value}&search=${searchQuery.value}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      inventory.value = data
      total.value = data.length
    } else {
      ElMessage.error('获取库存列表失败')
    }
  } catch (error) {
    console.error('获取库存列表失败:', error)
    ElMessage.error('获取库存列表失败')
  } finally {
    loading.value = false
  }
}

const getLowStockInventory = async () => {
  loading.value = true
  try {
    const token = authStore.token
    const response = await fetch('/api/inventory/low-stock', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      inventory.value = data
      total.value = data.length
      if (data.length === 0) {
        ElMessage.success('所有商品库存充足')
      } else {
        ElMessage.warning(`发现 ${data.length} 个库存不足的商品`)
      }
    } else {
      ElMessage.error('获取库存预警商品失败')
    }
  } catch (error) {
    console.error('获取库存预警商品失败:', error)
    ElMessage.error('获取库存预警商品失败')
  } finally {
    loading.value = false
  }
}

const getOutOfStockInventory = async () => {
  loading.value = true
  try {
    const token = authStore.token
    const response = await fetch('/api/inventory/out-of-stock', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      inventory.value = data
      total.value = data.length
      if (data.length === 0) {
        ElMessage.success('没有缺货商品')
      } else {
        ElMessage.warning(`发现 ${data.length} 个缺货商品`)
      }
    } else {
      ElMessage.error('获取缺货商品失败')
    }
  } catch (error) {
    console.error('获取缺货商品失败:', error)
    ElMessage.error('获取缺货商品失败')
  } finally {
    loading.value = false
  }
}

const getInventorySummary = async () => {
  try {
    const token = authStore.token
    const response = await fetch('/api/inventory/summary', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      summary.value = data
      summaryVisible.value = true
    } else {
      ElMessage.error('获取库存汇总失败')
    }
  } catch (error) {
    console.error('获取库存汇总失败:', error)
    ElMessage.error('获取库存汇总失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  getInventory()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  getInventory()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getInventory()
}

const showAdjustDialog = () => {
  if (inventory.value.length === 0) {
    ElMessage.warning('请先选择要调整库存的商品')
    return
  }
  resetAdjustForm()
  adjustDialogVisible.value = true
}

const adjustStock = (item: InventoryItem) => {
  adjustForm.product_id = item.product_id
  adjustForm.product_name = item.product_name
  adjustForm.current_quantity = item.quantity
  adjustForm.unit = item.unit
  adjustDialogVisible.value = true
}

const resetAdjustForm = () => {
  Object.assign(adjustForm, {
    product_id: 0,
    product_name: '',
    current_quantity: 0,
    unit: '',
    adjustment_type: 'increase',
    adjustment_quantity: 0,
    reason: '',
    notes: ''
  })
  adjustFormRef.value?.clearValidate()
}

const handleAdjustSubmit = async () => {
  if (!adjustFormRef.value) return

  await adjustFormRef.value.validate(async (valid) => {
    if (valid) {
      adjustSubmitting.value = true
      try {
        const token = authStore.token
        const response = await fetch('/api/inventory/adjust', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            product_id: adjustForm.product_id,
            adjustment_type: adjustForm.adjustment_type,
            adjustment_quantity: adjustForm.adjustment_quantity,
            reason: adjustForm.reason,
            notes: adjustForm.notes
          })
        })

        if (response.ok) {
          ElMessage.success('库存调整成功')
          adjustDialogVisible.value = false
          getInventory()
        } else {
          const error = await response.json()
          ElMessage.error(error.detail || '调整失败')
        }
      } catch (error) {
        console.error('调整失败:', error)
        ElMessage.error('调整失败')
      } finally {
        adjustSubmitting.value = false
      }
    }
  })
}

const viewMovements = async (item: InventoryItem) => {
  movementsLoading.value = true
  movementsVisible.value = true
  try {
    const token = authStore.token
    const response = await fetch(`/api/inventory/movements/?product_id=${item.product_id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      movements.value = data
    } else {
      ElMessage.error('获取库存变动记录失败')
    }
  } catch (error) {
    console.error('获取库存变动记录失败:', error)
    ElMessage.error('获取库存变动记录失败')
  } finally {
    movementsLoading.value = false
  }
}

const getStockStatusType = (quantity: number, minStock: number) => {
  if (quantity === 0) return 'danger'
  if (quantity < minStock) return 'warning'
  return 'success'
}

const getMovementType = (type: string) => {
  switch (type) {
    case 'purchase': return 'success'
    case 'sale': return 'danger'
    case 'adjustment': return 'warning'
    default: return 'info'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  getInventory()
})
</script>

<style scoped>
.inventory {
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