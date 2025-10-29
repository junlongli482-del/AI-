<template>
  <div class="stats-cards">
    <div class="stats-container">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.total_documents || 0 }}</div>
          <div class="stat-label">总文档数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">👀</div>
        <div class="stat-content">
          <div class="stat-number">{{ formatViewCount(stats.total_views) }}</div>
          <div class="stat-label">总浏览量</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">🆕</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.today_published || 0 }}</div>
          <div class="stat-label">今日发布</div>
        </div>
      </div>

      <div v-if="stats.featured_count" class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.featured_count || 0 }}</div>
          <div class="stat-label">推荐文档</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatViewCount } from '@/api/v2/tech_square'

// Props
defineProps({
  stats: {
    type: Object,
    default: () => ({
      total_documents: 0,
      total_views: 0,
      today_published: 0,
      featured_count: 0
    })
  }
})
</script>

<style scoped>
.stats-cards {
  margin-bottom: 32px;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #e1e4e8;
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f8fa;
  border-radius: 12px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #007AFF;
  margin-bottom: 4px;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #656d76;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .stat-card {
    padding: 16px;
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .stat-icon {
    font-size: 24px;
    width: 40px;
    height: 40px;
  }

  .stat-number {
    font-size: 24px;
  }

  .stat-label {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .stats-container {
    grid-template-columns: 1fr;
  }

  .stat-card {
    flex-direction: row;
    text-align: left;
  }
}
</style>
