<template>
  <div class="canvas-profile-panel">
    <h4>Profile</h4>
    <div class="canvas-profile-grid">
      <!-- Applicant Profile -->
      <section class="canvas-profile-section">
        <h3>Applicant Profile</h3>
        <el-form label-width="120px">
          <el-form-item label="Name">
            <el-input placeholder="Juan Dela Cruz" v-model="applicant.name"></el-input>
          </el-form-item>
          <el-form-item label="Headline">
            <el-input placeholder="Full‑stack Developer" v-model="applicant.headline"></el-input>
          </el-form-item>
          <el-form-item label="Skills">
            <el-select multiple placeholder="Add skills" v-model="applicant.skills">
              <el-option value="Vue.js" label="Vue.js"></el-option>
              <el-option value="Laravel" label="Laravel"></el-option>
              <el-option value="SQL" label="SQL"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-upload action="#" drag>
              <i class="el-icon-upload"></i>
              <div class="el-upload__text">Drop CV here</div>
            </el-upload>
          </el-form-item>
        </el-form>
      </section>

      <!-- Employer Profile -->
      <section class="canvas-profile-section">
        <h3>Employer Profile</h3>
        <el-form label-width="120px">
          <el-form-item label="Company">
            <el-input placeholder="Acme Corp" v-model="employer.company"></el-input>
          </el-form-item>
          <el-form-item label="Industry">
            <el-input placeholder="Fintech" v-model="employer.industry"></el-input>
          </el-form-item>
          <el-form-item label="About">
            <el-input
              type="textarea"
              rows="4"
              placeholder="Short description"
              v-model="employer.about"
            ></el-input>
          </el-form-item>
        </el-form>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CanvasProfile',
  data() {
    return {
      applicant: {
        name: '',
        headline: '',
        skills: []
      },
      employer: {
        company: '',
        industry: '',
        about: ''
      }
    };
  }
};
</script>

<style scoped>
.canvas-profile-panel {
  padding: 20px;
}

.canvas-profile-grid {
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
  justify-content: space-between;
}

.canvas-profile-section {
  flex: 1 1 400px;
  min-width: 300px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h3 {
  margin-bottom: 16px;
  font-size: 1.2em;
  font-weight: 600;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-upload__text {
  font-size: 14px;
  color: #888;
}

.el-input,
.el-select {
  width: 100%;
}

.el-input[placeholder],
.el-select[placeholder] {
  color: #999;
}

@media (max-width: 768px) {
  .canvas-profile-grid {
    gap: 20px;
    justify-content: center;
  }

  .canvas-profile-section {
    flex: 1 1 100%;
    padding: 10px;
  }
}
</style>
