<template>
  <div class="search-filter">
    <div class="search-bar">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        class="search-input"
        @input="onSearch"
      />
      <button class="search-btn" @click="onSearch">🔍</button>
    </div>

    <div v-if="showFilters" class="filters">
      <select
        v-model="selectedFilter"
        @change="onFilterChange"
        class="filter-select"
      >
        <option value="">All Categories</option>
        <option
          v-for="filter in filters"
          :key="filter.value"
          :value="filter.value"
        >
          {{ filter.label }}
        </option>
      </select>

      <select
        v-if="showDateFilter"
        v-model="dateRange"
        @change="onDateChange"
        class="filter-select"
      >
        <option value="">All Time</option>
        <option value="today">Today</option>
        <option value="week">This Week</option>
        <option value="month">This Month</option>
        <option value="year">This Year</option>
      </select>
    </div>
  </div>
</template>

<script>
export default {
  name: "SearchFilter",
  props: {
    placeholder: {
      type: String,
      default: "Search...",
    },
    filters: {
      type: Array,
      default: () => [],
    },
    showFilters: {
      type: Boolean,
      default: true,
    },
    showDateFilter: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      searchQuery: "",
      selectedFilter: "",
      dateRange: "",
    };
  },
  methods: {
    onSearch() {
      this.$emit("search", {
        query: this.searchQuery,
        filter: this.selectedFilter,
        dateRange: this.dateRange,
      });
    },

    onFilterChange() {
      this.onSearch();
    },

    onDateChange() {
      this.onSearch();
    },

    clearFilters() {
      this.searchQuery = "";
      this.selectedFilter = "";
      this.dateRange = "";
      this.onSearch();
    },
  },
};
</script>

<style scoped>
.search-filter {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-btn {
  padding: 0.75rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.search-btn:hover {
  background: #2563eb;
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
  }

  .filter-select {
    width: 100%;
  }
}
</style>
