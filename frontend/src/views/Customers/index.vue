<template>
  <div class="customers">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>客户管理</span>
          <el-button type="primary">
            <el-icon><Plus /></el-icon>
            添加客户
          </el-button>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input
          placeholder="搜索客户名称或联系人"
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-table :data="customers" style="width: 100%; margin-top: 20px;">
        <el-table-column prop="name" label="客户名称" />
        <el-table-column prop="contact_person" label="联系人" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="address" label="地址" />
        <el-table-column label="操作" width="200">
          <template #default>
            <el-button size="small">编辑</el-button>
            <el-button size="small" type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'

const customers = ref([
  {
    id: 1,
    name: '客户A',
    contact_person: '王五',
    phone: '13800138002',
    email: 'wangwu@example.com',
    address: '广州市天河区'
  }
])
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
</style>