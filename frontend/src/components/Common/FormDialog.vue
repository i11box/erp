<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    :width="width"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
      @submit.prevent="handleSubmit"
    >
      <slot name="form" :form-data="formData" />
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

interface Props {
  visible: boolean
  title: string
  width?: string
  formData: Record<string, any>
  rules?: FormRules
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: '500px',
  loading: false
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  submit: [formData: Record<string, any>]
  close: []
}>()

const formRef = ref<FormInstance>()

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    emit('submit', props.formData)
  } catch (error) {
    console.error('Form validation failed:', error)
  }
}

// Reset form when dialog closes
watch(() => props.visible, (newVal) => {
  if (!newVal && formRef.value) {
    formRef.value.resetFields()
  }
})
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>