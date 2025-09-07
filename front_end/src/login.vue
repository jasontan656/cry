<template>
  <div>
    <div class="content" id="login_area">
    <div class="container">
      <div class="row section_padding_top">
        <div class="col-md-6 section_padding_top">
          <!-- <img src="images/undraw_remotely_2j6y.svg" alt="Image" class="img-fluid"> -->
          <img src="../assets/img/login.svg" alt="login image" class="img-fluid">
        </div>
        <div class="col-md-6 contents section_padding_top" >
          <div class="row justify-content-center">
            <div class="col-md-8">
              <div class="mb-4">
              <h3>Sign In</h3>
              <p class="mb-4">Lorem ipsum dolor sit amet elit. Sapiente sit aut eos consectetur adipisicing.</p>
            </div>
            <el-form class="login-form" auto-complete="off" :model="model" :rules="rules" ref="login-form" label-position="top">
            <!-- <form action="#" method="post"> -->
              <div class="form-group first">
                <!-- <label for="username">Username</label> -->
                <el-form-item label="Username" prop="email" >
                  <input type="text" class="form-control" id="username" v-model="model.email" :placeholder="$t('Common.please_enter_username')" @keyup.enter.native="submit('login-form')" />
                  <el-input type="text" class="form-control" id="username" v-model="model.email" :placeholder="$t('Common.please_enter_username')" @keyup.enter.native="submit('login-form')" v-show="isVisible"/>
                </el-form-item>
              </div>
              <div class="form-group last mb-4">
                <el-form-item label="Password" prop="password" >
                  <input type="password" class="form-control" id="password" v-model="model.password" :placeholder="$t('Common.please_enter_pass')" @keyup.enter.native="submit('login-form')"/>
                  <el-input type="password" class="form-control" id="password" v-model="model.password" :placeholder="$t('Common.please_enter_pass')" @keyup.enter.native="submit('login-form')" v-show="isVisible"/>
                </el-form-item>
                
              </div>
              
              <div class="d-flex mb-2 align-items-center">
                <label class="control control--checkbox mb-0">
                  <input type="checkbox" checked="checked"/><span class="caption mx-2">Remember me</span>
                  <div class="control__indicator"></div>
                </label><
                <span class="ml-auto"><a href="#" class="forgot-pass mx-2">Forgot Password</a></span> 
              </div>
              <el-button class="btn btn-block btn-danger" @click="submit('login-form')">{{ loading ? $t('Reports.loading')+'...' : $t('Common.login') }}</el-button>

              <el-alert v-if="error" :title="error.title" type="warning" :description="error.message" show-icon/>

              <span class="d-block text-left my-2 text-muted">&mdash; or login with &mdash;</span>
              
              <div>
                <!-- <img :src="require('@/assets/img/icon/facebook.png')" class="image-icon"> -->

                <el-button id="facebookloginbtn" class="btn btn-block fb-button ">
                  <img :src="require('@/assets/img/icon/fb-icon.png')" class="icon">
                  Continue with Facebook
                </el-button>
                <div id="g_id_onload"
                  data-client_id="279762919265-i1c0jaofqjmk8ik1qfaf7gjchjah0euv.apps.googleusercontent.com"
                  data-context="signin"
                  data-ux_mode="popup"
                  data-callback="handleCredentialResponse"
                  data-auto_prompt="false">
                </div>
                <div class="g_id_signin" data-type="standard"></div>
                <!-- <img :src="require('@/assets/img/icon/google.png')" class="image-icon" id="googleloginbtn"> -->
              </div>
            </el-form>
            </div>
          </div>
          
        </div>
        
      </div>
    </div>
  </div>
  <!-- <section class="login">
    <header class="login-header">
      <h1 class="brand"><router-link to="/" tabindex="-1">TEST</router-link></h1>
      <el-alert v-if="error" :title="error.title" type="warning" :description="error.message" show-icon/>
    </header>
    <el-form class="login-form" auto-complete="off" :model="model" :rules="rules" ref="login-form" label-position="top">
      <h2 class="heading">{{ $t('Common.sign_in') }}</h2>
      <el-form-item :label="$t('Common.login')" prop="email">
        <el-input type="text" v-model="model.email" :placeholder="$t('Common.please_enter_username')" @keyup.enter.native="submit('login-form')"/>
      </el-form-item>
      <el-form-item :label="$t('Common.password')" prop="password">
        <el-input type="password" v-model="model.password" :placeholder="$t('Common.please_enter_pass')" @keyup.enter.native="submit('login-form')"/>
      </el-form-item>
      <el-button type="primary" :loading="loading" @click="submit('login-form')">{{ loading ? $t('Reports.loading')+'...' : $t('Common.login') }}</el-button>
    </el-form>


    <div>TEST FB
      <p v-if="isFBLoaded">Facebook SDK Loaded</p>
      <button v-if="isFBLoaded" @click="checkLoginStatus">Check Login Status</button>
      <p v-if="loginStatus">Status: {{ loginStatus }}</p>
    </div>

    <div>TEST GOOGLE
      <div id="g_id_onload"
      data-client_id="279762919265-i1c0jaofqjmk8ik1qfaf7gjchjah0euv.apps.googleusercontent.com"
      data-context="signin"
      data-ux_mode="popup"
      data-callback="handleCredentialResponse"
      data-auto_prompt="false">
    </div>
    <div class="g_id_signin" data-type="standard"></div>
    </div>
    <footer class="login-footer">
      © 2020
    </footer>
  </section> -->
</div>
</template>
<script>

import { mapGetters, mapActions } from 'vuex'
// import Header from '../components/header'
// import Sidebar from '../components/sidebar'
// import Heading from '../components/heading'
// import Modal from '../components/modal'
// import Lightbox from '../components/lightbox'
// import Lightbox2 from '../components/lightbox2'
// import Lightbox3 from '../components/lightbox3'
// import MenuList from '../components/menu'
export default {
  name: 'login',
  title: 'Login',
  // components: {
  //   'app-header': Header,
  //   'app-sidebar': Sidebar,
  //   'app-heading': Heading,
  //   'app-modal': Modal,
  //   'app-lightbox': Lightbox,
  //   'app-lightbox2': Lightbox2,
  //   'app-lightbox3': Lightbox3,
  //   'MenuList': MenuList,
  // },
  data () {
    // form model
    // TODO: remove default values

    const model = {
      email: '',
      password: '',
      source: 'web'
    }

    // form validate rules
    const rules = {
      email: [
        { required: true, message: this.replaceName(this.$t('Service.is_required'), this.$t('Common.username')) }
        // { min: 2, max: 16, message: 'Username must be between 2 and 16 characters' }
      ],
      password: [
        { required: true, message: this.replaceName(this.$t('Service.is_required'), this.$t('Common.password')) }
        // { min: 4, max: 16, message: 'Password must be between 4 and 16 characters' }
      ]
    }

    return { model: model, rules: rules, error: null, loading: false, 
             isFBLoaded: false,
             loginStatus: "",
             isVisible: false
     }
  },

  computed: mapGetters({
    session: 'session'
  }),

  created(){
    window.handleCredentialResponse = this.handleCredentialResponse;

    window.onload = function () {
    const client = google.accounts.oauth2.initTokenClient({
      client_id: '279762919265-i1c0jaofqjmk8ik1qfaf7gjchjah0euv.apps.googleusercontent.com',
      scope: 'email profile openid',
      callback: handleCredentialResponse,
      // callback: (tokenResponse) => {
      //   console.log(tokenResponse); // handle login result
      //   // this.handleCredentialResponse(tokenResponse);
      // },
    });

    // document.getElementById("googleloginbtn").onclick = () => {
    //   client.requestAccessToken();
    // };
  };
  },

  mounted() {
    this.loadGoogleScript();
    this.loadFacebookSDK();

  },

  methods: {

    loadGoogleScript() {
      const script = document.createElement("script");
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    },

    handleCredentialResponse(response) {
      console.log("Google JWT Token:", response.credential);
      alert();
      // Send token to Laravel for verification
      this.$store.dispatch('authGoogle', { token: response.credential })
          .then(res => {
            localStorage.setItem("token", res.token);
            window.location.href = "/home";
          });
      // this.$axios
      //   .post("http://localhost:8000/api/auth/google", { token: response.credential })
      //   .then((res) => {
      //     localStorage.setItem("token", res.data.token);
      //     window.location.href = "/dashboard";
      //   })
      //   .catch((error) => {
      //     console.error("Login failed:", error);
      //   });
    },

    loadFacebookSDK() {
      if (document.getElementById("facebook-jssdk")) {
        this.initializeFB();
        return;
      }

      window.fbAsyncInit = () => {
        FB.init({
          appId: "1364332831428891",
          cookie: true,
          xfbml: true,
          version: "v22.0",
        });

        FB.AppEvents.logPageView();
        this.isFBLoaded = true;
      };

      let js = document.createElement("script");
      js.id = "facebook-jssdk";
      js.src = "https://connect.facebook.net/en_US/sdk.js";
      js.onload = this.initializeFB;
      let fjs = document.getElementsByTagName("script")[0];
      fjs.parentNode.insertBefore(js, fjs);
    },

    initializeFB() {
      if (typeof FB !== "undefined") {
        this.isFBLoaded = true;
      }
    },

    checkLoginStatus() {
      if (!this.isFBLoaded) {
        console.warn("Facebook SDK not loaded yet");
        return;
      }

      FB.getLoginStatus((response) => {
        this.statusChangeCallback(response);
      });
    },

    statusChangeCallback(response) {
      if (response.status === "connected") {
        this.loginStatus = "Logged in";
      } else if (response.status === "not_authorized") {
        this.loginStatus = "Logged into Facebook but not authorized.";
      } else {
        this.loginStatus = "Not logged into Facebook.";
      }
    },

    isDesktopMode() {
        return window.innerWidth + " = " + screen.availWidth;
    },

    submit (ref) {
      // form validate
      this.$refs[ref].validate(valid => {
        if (!valid) return false

        // validated
        this.error = null
        this.loading = true

        // create token from remote
        this.$store.dispatch('createToken', this.model)
          .then(ret => {
            if(ret.status == 'Success'){
              // console.log('test',ret.data.token);
              const data = {
                token: ret.data.token
              }
              this.$store.dispatch('fetchUser').then(() => {

              });
              // console.log(data);
              this.$tabEvent.emit('setToken', ret.data.token);
              if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){
                this.$router.replace({ path: this.$route.query.redirect || '/client-search' })
              }else{
                this.$router.replace({ path: this.$route.query.redirect || '/' })
                this.loading = false;
              }
            }
            else{
              switch (ret.code) {
                case 401:
                  this.error = { title: this.$t('Common.please_try_again'), message: this.$t('Common.incorrect_user_pass') }
                  break
                case 500:
                  this.error = { title: this.$t('Common.please_try_again'), message: this.$t('Common.internal_server_error') }
                  break
              }
              this.loading = false
            }
          })
          .catch(err => {
            console.log('error login',err)
            this.error = { title: this.$t('Common.error_occured'), message: this.$t('Common.please_try_again') }
            switch (err.response && err.response.status) {
              case 401:
                this.error.message = this.$t('Common.incorrect_user_pass')
                break
              case 500:
                this.error.message = this.$t('Common.internal_server_error')
                break
            }
            this.loading = false
          })
      })
    },

    replaceName (message, data) {
      return message.replace(':name', data)
    }
  }
}
</script>

<style lang="scss">
  @import '../assets/styles/variables';
  /*@import '../assets/styles/alternative';*/

  .fb-button {
  display: flex;
  color: #3c4043;
  text-align: center;
  align-items: center;
  gap: 8px;
  border: 1px solid #ccc;
  padding: 10px 16px;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  font-family: Roboto, sans-serif;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.fb-button {
  .icon {
    width: 20px;
    height: 20px;
    margin-left: -5px;
    margin-right: 118px;
  }
}
  .el-form-item__error{
    font-size: 11px;
    color:  red;
  }

  .image-icon {
    cursor: pointer;
    transition: transform 0.3s ease;
    width: 60px;
  }

  .image-icon:hover {
    transform: rotate(5deg);
    transform: scale(1.5);
  }

  .login {
    flex: 1;
    width: 95%;
    max-width: 22rem;
    margin: 0 auto;
    font-size: .875rem;

    &-header {
      margin-bottom: 1rem;

      .brand {
        margin: 4.5rem 0 3.5rem;
        text-align: center;
        letter-spacing: .125rem;

        a {
          margin: 0;
          color: $brand-color;
          font: 300 3rem sans-serif;

          &:hover {
            color: $brand-hover-color;
            text-shadow: 0 0 1rem $brand-hover-color;
          }
        }
      }
    }

    &-form {
      margin-bottom: 2.5rem;
      padding: 1.875rem 1.25rem;
      background: #fff;
      color: $login-form-color;

      .heading {
        margin: 0 0 1rem;
        font-weight: 400;
        font-size: 1.5rem;
      }

      .el-button {
        margin-top: .5rem;
        width: 100%;
      }
    }

    &-footer {
      margin-bottom: 1rem;
      padding: .625rem;
      border: .0625rem solid $brand-color;
      font-size: .75rem;
      text-align: center;

      a {
        color: $brand-color;
      }
    }
  }
</style>
