<template>
  <div class="panel">
    <h4>Tasks</h4>
    <el-table :data="rows" size="small" stripe>
      <el-table-column prop="who" label="Owner" width="160"></el-table-column>
      <el-table-column prop="task" label="Task"></el-table-column>
      <el-table-column prop="due" label="Due" width="140"></el-table-column>
      <el-table-column label="Status" width="140">
        <template slot-scope="s">
          <el-tag :type="s.row.status === 'Open' ? 'warning' : 'success'">
            {{ s.row.status }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'CanvasTasks',
  data() {
    return {
      rows: [
        { who: 'Applicant', task: 'Complete coding test', due: '2025-08-25', status: 'Open' },
        { who: 'Employer',  task: 'Schedule panel interview', due: '2025-08-23', status: 'Open' },
        { who: 'Applicant', task: 'Upload government IDs', due: '2025-08-22', status: 'Done' },
      ]
    };
  }
};
</script>