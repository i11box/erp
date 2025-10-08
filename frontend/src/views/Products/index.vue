<template>
  <div class="products">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加商品
          </el-button>
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
        <el-button type="warning" style="margin-left: 10px" @click="getLowStockProducts">
          <el-icon><Warning /></el-icon>
          库存预警
        </el-button>
      </div>

      <el-table :data="products" style="width: 100%; margin-top: 20px;" v-loading="loading">
        <el-table-column prop="name" label="商品名称" />
        <el-table-column prop="sku" label="SKU" />
        <el-table-column prop="category" label="分类" />
        <el-table-column prop="price" label="售价">
          <template #default="scope">
            ¥{{ (scope.row.price || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="成本">
          <template #default="scope">
            ¥{{ (scope.row.cost || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="库存信息">
          <template #default="scope">
            <el-tag :type="scope.row.stock < scope.row.min_stock ? 'danger' : 'success'">
              {{ scope.row.stock }} {{ scope.row.unit }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editProduct(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteProduct(scope.row)">删除</el-button>
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

    <!-- 添加/编辑商品对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑商品' : '添加商品'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入商品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SKU" prop="sku">
              <el-input v-model="form.sku" placeholder="请输入SKU" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品分类" prop="category">
              <el-input v-model="form.category" placeholder="请输入商品分类" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="form.unit" placeholder="请输入单位" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="售价" prop="price">
              <el-input-number
                v-model="form.price"
                :precision="2"
                :step="0.1"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成本" prop="cost">
              <el-input-number
                v-model="form.cost"
                :precision="2"
                :step="0.1"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最低库存" prop="min_stock">
              <el-input-number
                v-model="form.min_stock"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="初始库存" prop="initial_stock">
              <el-input-number
                v-model="form.initial_stock"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入商品描述"
          />
        </el-form-item>
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
  </div> 
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Warning } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()

interface Product {
  id: number
  name: string
  sku: string
  category: string
  description?: string
  price: number
  cost: number
  unit: string
  min_stock: number
  stock: number
}

const products = ref<Product[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const formRef = ref<FormInstance>()
const form = reactive({
  id: 0,
  name: '',
  sku: '',
  category: '',
  description: '',
  price: 0,
  cost: 0,
  unit: '',
  min_stock: 10,
  initial_stock: 0
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  sku: [
    { required: true, message: '请输入SKU', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请输入商品分类', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请输入单位', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入售价', trigger: 'blur' },
    { type: 'number', min: 0, message: '售价必须大于等于0', trigger: 'blur' }
  ],
  cost: [
    { required: true, message: '请输入成本', trigger: 'blur' },
    { type: 'number', min: 0, message: '成本必须大于等于0', trigger: 'blur' }
  ]
}

const getProducts = async () => {
  loading.value = true
  try {
    console.log('正在获取商品列表...')
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const response = await api.get('/products', { params })
    console.log('商品数据响应:', response)

    // Handle both array and paginated response
    if (Array.isArray(response)) {
      products.value = response
      total.value = response.length
    } else if (response && Array.isArray(response.items)) {
      products.value = response.items
      total.value = response.total || response.items.length
    } else {
      products.value = []
      total.value = 0
    }

    console.log('商品数据加载成功:', products.value.length, '条记录')
  } catch (error: any) {
    console.error('获取商品列表失败:', error)
    ElMessage.error(`获取商品列表失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
    products.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const getLowStockProducts = async () => {
  loading.value = true
  try {
    const response = await api.get('/products/low-stock')
    products.value = response.data || response || []
    total.value = products.value.length
    if (products.value.length === 0) {
      ElMessage.success('所有商品库存充足')
    } else {
      ElMessage.warning(`发现 ${products.value.length} 个库存不足的商品`)
    }
  } catch (error: any) {
    console.error('获取库存预警商品失败:', error)
    ElMessage.error(`获取库存预警商品失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  getProducts()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  getProducts()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getProducts()
}

const showAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editProduct = (product: Product) => {
  isEdit.value = true
  Object.assign(form, {
    ...product,
    initial_stock: 0
  })
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(form, {
    id: 0,
    name: '',
    sku: '',
    category: '',
    description: '',
    price: 0,
    cost: 0,
    unit: '',
    min_stock: 10,
    initial_stock: 0
  })
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.put(`/products/${form.id}`, {
            name: form.name,
            sku: form.sku,
            category: form.category,
            description: form.description,
            price: form.price,
            cost: form.cost,
            unit: form.unit,
            min_stock: form.min_stock
          })
          ElMessage.success('商品更新成功')
        } else {
          await api.post('/products', {
            name: form.name,
            sku: form.sku,
            category: form.category,
            description: form.description,
            price: form.price,
            cost: form.cost,
            unit: form.unit,
            min_stock: form.min_stock,
            initial_stock: form.initial_stock
          })
          ElMessage.success('商品创建成功')
        }
        dialogVisible.value = false
        getProducts()
      } catch (error: any) {
        console.error('操作失败:', error)
        ElMessage.error(`操作失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
      } finally {
        submitting.value = false
      }
    }
  })
}

const deleteProduct = (product: Product) => {
  ElMessageBox.confirm(
    `确定要删除商品 "${product.name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await api.delete(`/products/${product.id}`)
      ElMessage.success('商品删除成功')
      getProducts()
    } catch (error: any) {
      console.error('删除失败:', error)
      ElMessage.error(`删除失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
    }
  })
}

onMounted(() => {
  getProducts()
})

onBeforeUnmount(() => {
  // 清理组件状态
  loading.value = false
  submitting.value = false
  dialogVisible.value = false
  isEdit.value = false
})
</script>

<style scoped>
.products {
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