<template>
  <div class="suppliers">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>供应商管理</span>
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            添加供应商
          </el-button>
        </div>
      </template>

      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索供应商名称、联系人或电话"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadSuppliers" style="margin-left: 10px">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-table
        :data="suppliers"
        style="width: 100%; margin-top: 20px;"
        empty-text="暂无供应商数据"
      >
        <el-table-column prop="name" label="供应商名称" min-width="150">
          <template #default="scope">
            <el-text type="primary" style="cursor: pointer">{{ scope.row.name }}</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="contact_person" label="联系人" width="120" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editSupplier(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="deleteSupplier(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: center;"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingSupplier ? '编辑供应商' : '添加供应商'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="supplierFormRef"
        :model="supplierForm"
        :rules="supplierRules"
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="supplierForm.name"
            placeholder="请输入供应商名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input
            v-model="supplierForm.contact_person"
            placeholder="请输入联系人姓名"
            maxlength="50"
          />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input
            v-model="supplierForm.phone"
            placeholder="请输入联系电话"
            maxlength="20"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="supplierForm.email"
            placeholder="请输入邮箱地址"
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input
            v-model="supplierForm.address"
            type="textarea"
            :rows="3"
            placeholder="请输入详细地址"
            maxlength="255"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSupplier" :loading="saving">
          {{ editingSupplier ? '更新' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Plus, Search, Edit, Delete, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import api from '@/services/api'
import type { Supplier, SupplierForm } from '@/services/types'

// Reactive data
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingSupplier = ref(false)
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// Form ref
const supplierFormRef = ref<FormInstance>()

// Form data
const supplierForm = reactive<SupplierForm>({
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  address: ''
})

// Suppliers list
const suppliers = ref<Supplier[]>([])

// Form validation rules
const supplierRules: FormRules = {
  name: [
    { required: true, message: '请输入供应商名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

// Load suppliers
const loadSuppliers = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchText.value || undefined
    }

    const response = await api.get('/suppliers', { params })
    suppliers.value = response
    // Note: The API should return paginated data, but for now we assume it returns an array
    total.value = response.length
  } catch (error) {
    ElMessage.error('加载供应商列表失败')
  } finally {
    loading.value = false
  }
}

// Handle search
const handleSearch = () => {
  currentPage.value = 1
  loadSuppliers()
}

// Handle pagination
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadSuppliers()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  loadSuppliers()
}

// Open add dialog
const openAddDialog = () => {
  editingSupplier.value = false
  showDialog.value = true
}

// Edit supplier
const editSupplier = (supplier: Supplier) => {
  editingSupplier.value = true
  Object.assign(supplierForm, supplier)
  showDialog.value = true
}

// Delete supplier
const deleteSupplier = async (supplier: Supplier) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除供应商"${supplier.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.delete(`/suppliers/${supplier.id}`)
    ElMessage.success('删除成功')
    loadSuppliers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// Save supplier
const saveSupplier = async () => {
  if (!supplierFormRef.value) return

  try {
    await supplierFormRef.value.validate()
    saving.value = true

    if (editingSupplier.value) {
      await api.put(`/suppliers/${editingSupplier.value.id}`, supplierForm)
      ElMessage.success('更新成功')
    } else {
      await api.post('/suppliers', supplierForm)
      ElMessage.success('添加成功')
    }

    showDialog.value = false
    loadSuppliers()
  } catch (error: any) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error(editingSupplier.value ? '更新失败' : '添加失败')
    }
  } finally {
    saving.value = false
  }
}

// Reset form
const resetForm = () => {
  if (supplierFormRef.value) {
    supplierFormRef.value.resetFields()
  }
  Object.assign(supplierForm, {
    name: '',
    contact_person: '',
    phone: '',
    email: '',
    address: ''
  })
  editingSupplier.value = false
}

// Format date
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadSuppliers()
})
</script>

<style scoped>
.suppliers {
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

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background-color: #fafafa;
}

:deep(.el-table__row) {
  transition: background-color 0.2s;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-pagination) {
  justify-content: center;
}

:deep(.el-loading-mask) {
  border-radius: 8px;
}

:deep(.el-dialog) {
  border-radius: 12px;
}

:deep(.el-dialog__header) {
  padding: 20px 24px 10px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 10px 24px 20px;
  border-top: 1px solid #ebeef5;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  border-radius: 6px;
}

:deep(.el-textarea__inner) {
  border-radius: 6px;
}

:deep(.el-button) {
  border-radius: 6px;
  transition: all 0.3s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .search-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  :deep(.el-table) {
    font-size: 12px;
  }

  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
}
</style>