import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Supplier, SupplierForm, PaginatedResponse } from '@/services/types'
import api from '@/services/api'

export const useSuppliersStore = defineStore('suppliers', () => {
  const suppliers = ref<Supplier[]>([])
  const loading = ref(false)
  const total = ref(0)

  const fetchSuppliers = async (page = 1, size = 10, search = ''): Promise<void> => {
    loading.value = true
    try {
      const params = { page, size, search }
      const response: PaginatedResponse<Supplier> = await api.get('/suppliers', { params })
      
      suppliers.value = response.items
      total.value = response.total
    } catch (error) {
      console.error('Failed to fetch suppliers:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createSupplier = async (supplierData: SupplierForm): Promise<Supplier> => {
    try {
      const response: Supplier = await api.post('/suppliers', supplierData)
      suppliers.value.unshift(response)
      return response
    } catch (error) {
      console.error('Failed to create supplier:', error)
      throw error
    }
  }

  const updateSupplier = async (id: number, supplierData: SupplierForm): Promise<Supplier> => {
    try {
      const response: Supplier = await api.put(`/suppliers/${id}`, supplierData)
      const index = suppliers.value.findIndex(s => s.id === id)
      if (index !== -1) {
        suppliers.value[index] = response
      }
      return response
    } catch (error) {
      console.error('Failed to update supplier:', error)
      throw error
    }
  }

  const deleteSupplier = async (id: number): Promise<void> => {
    try {
      await api.delete(`/suppliers/${id}`)
      suppliers.value = suppliers.value.filter(s => s.id !== id)
    } catch (error) {
      console.error('Failed to delete supplier:', error)
      throw error
    }
  }

  return {
    suppliers,
    loading,
    total,
    fetchSuppliers,
    createSupplier,
    updateSupplier,
    deleteSupplier
  }
})