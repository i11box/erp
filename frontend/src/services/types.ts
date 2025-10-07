// Common types for the application

export interface User {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Supplier {
  id: number
  name: string
  contact_person?: string
  phone?: string
  email?: string
  address?: string
  created_at: string
  updated_at: string
}

export interface Customer {
  id: number
  name: string
  contact_person?: string
  phone?: string
  email?: string
  address?: string
  created_at: string
  updated_at: string
}

export interface Product {
  id: number
  name: string
  sku?: string
  description?: string
  unit: string
  cost_price: number
  selling_price: number
  reorder_level: number
  created_at: string
  updated_at: string
}

export interface Inventory {
  id: number
  product_id: number
  quantity: number
  avg_cost: number
  last_updated: string
  product?: Product
}

export interface Purchase {
  id: number
  supplier_id: number
  user_id: number
  purchase_number: string
  purchase_date: string
  total_amount: number
  status: string
  created_at: string
  updated_at: string
  supplier?: Supplier
  user?: User
  items?: PurchaseItem[]
}

export interface PurchaseItem {
  id: number
  purchase_id: number
  product_id: number
  quantity: number
  unit_price: number
  total_price: number
  product?: Product
}

export interface Sale {
  id: number
  customer_id: number
  user_id: number
  sale_number: string
  sale_date: string
  total_amount: number
  status: string
  created_at: string
  updated_at: string
  customer?: Customer
  user?: User
  items?: SaleItem[]
}

export interface SaleItem {
  id: number
  sale_id: number
  product_id: number
  quantity: number
  unit_price: number
  total_price: number
  product?: Product
}

export interface InventoryMovement {
  id: number
  product_id: number
  movement_type: string
  quantity: number
  reference_type?: string
  reference_id?: number
  reason?: string
  user_id?: number
  created_at: string
  product?: Product
  user?: User
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Form types
export interface SupplierForm {
  name: string
  contact_person?: string
  phone?: string
  email?: string
  address?: string
}

export interface CustomerForm {
  name: string
  contact_person?: string
  phone?: string
  email?: string
  address?: string
}

export interface ProductForm {
  name: string
  sku?: string
  description?: string
  unit: string
  cost_price: number
  selling_price: number
  reorder_level: number
}

export interface LoginForm {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}