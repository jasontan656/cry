<template>
  <div class="panel">
    <h4>Job & Candidate Settings</h4>
    <div class="grid">
      <!-- Job Seekers Section -->
      <section class="form-section">
        <h3>For Job Seekers</h3>
        <el-form label-width="120px">
          <el-form-item label="Target Role">
            <el-input placeholder="e.g., Frontend Developer" />
          </el-form-item>
          <el-form-item label="Location">
            <el-input placeholder="e.g., Makati / Remote" />
          </el-form-item>
          <el-form-item label="Salary Range">
            <el-input placeholder="₱45k–₱70k" />
          </el-form-item>
          <el-form-item label="Alerts">
            <el-switch active-text="Email Alerts" />
          </el-form-item>
        </el-form>
      </section>

      <!-- Employers Section -->
      <section class="form-section">
        <h3>For Employers</h3>
        <el-form label-width="120px">
          <el-form-item label="Role">
            <el-input placeholder="e.g., Senior QA Engineer" />
          </el-form-item>
          <el-form-item label="Experience">
            <el-input placeholder="3–5 years" />
          </el-form-item>
          <el-form-item label="Budget">
            <el-input placeholder="₱60k–₱90k" />
          </el-form-item>
          <el-form-item label="Auto-screen">
            <el-switch active-text="Enable" />
          </el-form-item>
        </el-form>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CanvasSettings'
};
</script>

<style scoped>
.panel {
  overflow-y: scroll;
  
}

.grid {
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
}

.form-section {
  flex: 1 1 400px;
  min-width: 300px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.el-form-item {
  margin-bottom: 16px;
}

.el-form-item label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.el-input,
.el-switch {
  width: 100%;
}
</style>
