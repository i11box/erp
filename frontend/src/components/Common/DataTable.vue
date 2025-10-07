<template>
  <div class="data-table">
    <div class="table-header" v-if="showHeader">
      <div class="table-title">
        <h3>{{ title }}</h3>
      </div>
      <div class="table-actions">
        <el-input
          v-if="showSearch"
          v-model="searchValue"
          placeholder="搜索..."
          style="width: 200px; margin-right: 10px;"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button
          v-if="showAddButton"
          type="primary"
          @click="$emit('add')"
        >
          <el-icon><Plus /></el-icon>
          {{ addButtonText }}
        </el-button>
      </div>
    </div>

    <el-table
      :data="data"
      :loading="loading"
      stripe
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="55"
      />
      
      <slot name="columns" />
      
      <el-table-column
        v-if="showActions"
        label="操作"
        width="150"
        fixed="right"
      >
        <template #default="scope">
          <el-button
            size="small"
            @click="$emit('edit', scope.row)"
          >
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="$emit('delete', scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="table-pagination" v-if="showPagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'

interface Props {
  data: any[]
  loading?: boolean
  title?: string
  showHeader?: boolean
  showSearch?: boolean
  showAddButton?: boolean
  addButtonText?: string
  showSelection?: boolean
  showActions?: boolean
  showPagination?: boolean
  total?: number
  currentPage?: number
  pageSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  title: '',
  showHeader: true,
  showSearch: true,
  showAddButton: true,
  addButtonText: '新增',
  showSelection: false,
  showActions: true,
  showPagination: true,
  total: 0,
  currentPage: 1,
  pageSize: 10
})

const emit = defineEmits<{
  add: []
  edit: [row: any]
  delete: [row: any]
  search: [keyword: string]
  'page-change': [page: number]
  'size-change': [size: number]
  'selection-change': [selection: any[]]
}>()

const searchValue = ref('')
const currentPage = ref(props.currentPage)
const pageSize = ref(props.pageSize)

const handleSearch = () => {
  emit('search', searchValue.value)
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  emit('page-change', page)
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  emit('size-change', size)
}

const handleSelectionChange = (selection: any[]) => {
  emit('selection-change', selection)
}

// Watch for prop changes
watch(() => props.currentPage, (newVal) => {
  currentPage.value = newVal
})

watch(() => props.pageSize, (newVal) => {
  pageSize.value = newVal
})
</script>

<style scoped>
.data-table {
  background: white;
  border-radius: 4px;
  padding: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-title h3 {
  margin: 0;
  color: #303133;
}

.table-actions {
  display: flex;
  align-items: center;
}

.table-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>