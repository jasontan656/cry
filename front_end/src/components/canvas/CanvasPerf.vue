<template>
  <div class="panel">
    <h4>Performance</h4>
    <el-row :gutter="12" class="mb12">
      <el-col :span="6">
        <el-card shadow="never">
          <div class="kpi">
            <div>Views</div>
            <b>3,214</b>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div class="kpi">
            <div>Applications</div>
            <b>126</b>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div class="kpi">
            <div>Interviews</div>
            <b>42</b>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div class="kpi">
            <div>Hires</div>
            <b>7</b>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <p class="muted">
      Tip: improve screening questions to raise Applications ➜ Interviews conversion.
    </p>
  </div>
</template>

<script>
export default {
  name: 'CanvasPerf'
};
</script>

<style scoped>

.kpi {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mb12 {
  margin-bottom: 12px;
}

.muted {
  color: #888;
  font-style: italic;
}
</style>
