<template>
  <transition name="slide-fade">
    <div v-if="progressStore.isCollecting" class="collection-toast">
      <div class="toast-header">
        <el-icon class="spinning"><Loading /></el-icon>
        <span class="toast-title">Сбор данных</span>
        <el-button 
          size="small" 
          text 
          @click="progressStore.reset()"
          :disabled="progressStore.progress < 100"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
      
      <div class="toast-body">
        <div class="progress-info">
          <span class="progress-text">
            {{ progressStore.completed }} / {{ progressStore.total }}
            <span v-if="progressStore.failed > 0" class="failed-count">
              ({{ progressStore.failed }} ошибок)
            </span>
          </span>
          <span class="progress-percent">{{ progressStore.progress }}%</span>
        </div>
        
        <el-progress 
          :percentage="progressStore.progress" 
          :status="progressStore.failed > 0 ? 'warning' : undefined"
          :show-text="false"
        />
        
        <div v-if="progressStore.currentAccount" class="current-account">
          Обработка: {{ progressStore.currentAccount }}
        </div>

        <div v-if="progressStore.progress === 100" class="completion-summary">
          <el-icon class="success-icon" v-if="progressStore.failed === 0"><CircleCheck /></el-icon>
          <el-icon class="warning-icon" v-else><Warning /></el-icon>
          <span>
            Завершено! 
            {{ progressStore.total - progressStore.failed }} успешно
            <span v-if="progressStore.failed > 0">, {{ progressStore.failed }} ошибок</span>
          </span>
        </div>

        <div v-if="progressStore.errors.length > 0" class="errors-section">
          <el-collapse accordion>
            <el-collapse-item title="Показать ошибки" name="1">
              <div v-for="(err, idx) in progressStore.errors" :key="idx" class="error-item">
                <strong>{{ err.account }}:</strong> {{ err.error }}
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { Loading, Close, CircleCheck, Warning } from '@element-plus/icons-vue'
import { useCollectionProgressStore } from '@/stores/collectionProgress'

const progressStore = useCollectionProgressStore()
</script>

<style scoped>
.collection-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 380px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  overflow: hidden;
}

.toast-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.toast-title {
  flex: 1;
  font-weight: 600;
  font-size: 14px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.toast-body {
  padding: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.failed-count {
  color: #e6a23c;
  font-weight: 500;
}

.progress-percent {
  font-weight: 600;
  color: #409eff;
}

.current-account {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.completion-summary {
  margin-top: 12px;
  padding: 10px;
  background: #f0f9ff;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
}

.success-icon {
  color: #67c23a;
  font-size: 18px;
}

.warning-icon {
  color: #e6a23c;
  font-size: 18px;
}

.errors-section {
  margin-top: 12px;
}

.error-item {
  padding: 6px 0;
  font-size: 12px;
  color: #f56c6c;
  border-bottom: 1px solid #f5f7fa;
}

.error-item:last-child {
  border-bottom: none;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
