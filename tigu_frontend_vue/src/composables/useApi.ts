import { ref, Ref } from 'vue';
import api from '@/services/api';
import type { ApiResponse } from '@/types';

export function useApi<T, P = any>(url: string) {
  const data: Ref<T | null> = ref(null);
  const error: Ref<Error | null> = ref(null);
  const loading = ref(false);

  const fetchData = async (params?: P): Promise<void> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get<ApiResponse<T>>(url, { params });
      data.value = response.data.data;
    } catch (err) {
      error.value = err as Error;
      console.error('API Error:', err);
    } finally {
      loading.value = false;
    }
  };

  const postData = async (payload: any): Promise<T | null> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.post<ApiResponse<T>>(url, payload);
      data.value = response.data.data;
      return response.data.data;
    } catch (err) {
      error.value = err as Error;
      console.error('API Error:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const updateData = async (id: string | number, payload: any): Promise<T | null> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.put<ApiResponse<T>>(`${url}/${id}`, payload);
      data.value = response.data.data;
      return response.data.data;
    } catch (err) {
      error.value = err as Error;
      console.error('API Error:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const deleteData = async (id: string | number): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      await api.delete(`${url}/${id}`);
      return true;
    } catch (err) {
      error.value = err as Error;
      console.error('API Error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  return {
    data,
    error,
    loading,
    fetchData,
    postData,
    updateData,
    deleteData
  };
}
