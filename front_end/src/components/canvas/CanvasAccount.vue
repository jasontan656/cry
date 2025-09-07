<template>
  <div class="panel">
    <h4>Account</h4>
    <el-form label-width="160px" class="narrow">
      <!-- Email Field -->
      <el-form-item label="Email">
        <el-input placeholder="you@example.com" v-model="account.email"></el-input>
      </el-form-item>

      <!-- Password Field -->
      <el-form-item label="Password">
        <el-input type="password" placeholder="••••••••" v-model="account.password"></el-input>
      </el-form-item>

      <!-- Two-Factor Authentication -->
      <el-form-item label="Two‑Factor Auth">
        <el-switch v-model="account.twoFactorAuth"></el-switch>
      </el-form-item>

      <!-- Notification Settings -->
      <el-form-item label="Notifications">
        <el-checkbox-group v-model="account.notifications">
          <el-checkbox label="New matches"></el-checkbox>
          <el-checkbox label="Interview updates"></el-checkbox>
          <el-checkbox label="Weekly digest"></el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <!-- Save Button -->
      <el-button type="primary" @click="saveChanges">Save Changes</el-button>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'CanvasAccount',
  data() {
    return {
      account: {
        email: '',
        password: '',
        twoFactorAuth: false,
        notifications: []
      }
    };
  },
  methods: {
    saveChanges() {
      console.log("Account settings saved:", this.account);
      // You can replace this with your save logic, such as an API call.
    }
  }
};
</script>

