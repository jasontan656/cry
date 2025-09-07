<template>
  <div class="panel">
    <h4>Records</h4>
    <el-tabs value="apps">
      <el-tab-pane label="My Applications" name="apps">
        <el-table :data="apps" size="small" stripe>
          <el-table-column prop="company" label="Company"></el-table-column>
          <el-table-column prop="role" label="Role"></el-table-column>
          <el-table-column prop="stage" label="Stage"></el-table-column>
          <el-table-column prop="updated" label="Updated"></el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="My Job Posts" name="posts">
        <el-table :data="posts" size="small" stripe>
          <el-table-column prop="title" label="Title"></el-table-column>
          <el-table-column prop="apps" label="Applicants" width="120"></el-table-column>
          <el-table-column prop="status" label="Status" width="140"></el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
export default {
  name: 'CanvasRecords',
  data() {
    return {
      apps: [
        { company: 'Acme Corp', role: 'Frontend Dev', stage: 'Interview', updated: '2025-08-20' },
        { company: 'Globex', role: 'Data Analyst', stage: 'Screening', updated: '2025-08-18' }
      ],
      posts: [
        { title: 'QA Engineer', apps: 24, status: 'Open' },
        { title: 'Sales Lead', apps: 12, status: 'Closed' }
      ]
    };
  }
};
</script>
