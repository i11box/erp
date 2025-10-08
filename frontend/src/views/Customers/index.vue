<template>
  <div class="customers">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>客户管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加客户
          </el-button>
        </div>
      </template>

      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索客户名称或联系人"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-table :data="customers" style="width: 100%; margin-top: 20px;" v-loading="loading">
        <el-table-column prop="name" label="客户名称" />
        <el-table-column prop="contact_person" label="联系人" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="address" label="地址" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editCustomer(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCustomer(scope.row)">删除</el-button>
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

    <!-- 添加/编辑客户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑客户' : '添加客户'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="客户名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="form.contact_person" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" type="textarea" placeholder="请输入地址" />
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
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

interface Customer {
  id: number
  name: string
  contact_person: string
  phone: string
  email: string
  address: string
}

const customers = ref<Customer[]>([])
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
  contact_person: '',
  phone: '',
  email: '',
  address: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  contact_person: [
    { required: true, message: '请输入联系人', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const getCustomers = async () => {
  loading.value = true
  try {
    const token = authStore.token
    const response = await fetch(`/api/customers/?skip=${(currentPage.value - 1) * pageSize.value}&limit=${pageSize.value}&search=${searchQuery.value}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      customers.value = data
      total.value = data.length
    } else {
      ElMessage.error('获取客户列表失败')
    }
  } catch (error) {
    console.error('获取客户列表失败:', error)
    ElMessage.error('获取客户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  getCustomers()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  getCustomers()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getCustomers()
}

const showAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editCustomer = (customer: Customer) => {
  isEdit.value = true
  Object.assign(form, customer)
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(form, {
    id: 0,
    name: '',
    contact_person: '',
    phone: '',
    email: '',
    address: ''
  })
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const token = authStore.token
        const url = isEdit.value ? `/api/customers/${form.id}` : '/api/customers/'
        const method = isEdit.value ? 'PUT' : 'POST'

        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            name: form.name,
            contact_person: form.contact_person,
            phone: form.phone,
            email: form.email,
            address: form.address
          })
        })

        if (response.ok) {
          ElMessage.success(isEdit.value ? '客户更新成功' : '客户创建成功')
          dialogVisible.value = false
          getCustomers()
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

const deleteCustomer = (customer: Customer) => {
  ElMessageBox.confirm(
    `确定要删除客户 "${customer.name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const token = authStore.token
      const response = await fetch(`/api/customers/${customer.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        ElMessage.success('客户删除成功')
        getCustomers()
      } else {
        const error = await response.json()
        ElMessage.error(error.detail || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  getCustomers()
})
</script>

<style scoped>
.customers {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
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