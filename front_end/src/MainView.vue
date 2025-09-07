<template>
  <div>
    <div class="app">
    <div class="d-none d-md-block">
        <div class=" h100">
              <div id="app" class="shell">
                  <header class="topbar fixed-top" v-if="!isDocked">
                    <div class="container-fluid d-flex align-items-center px-3 py-2">
                      <div class="brand me-3">Career Bot<div class="subtitle">Powered by 4ways Group</div></div>
                      

                      <!-- push this to the right -->
                      <nav class="trm ms-auto bg-white d-flex align-items-center px-2 py-1" aria-label="Utility menu">
                        <template v-for="item in items">
                          <el-tooltip :key="item.key" :content="item.label" placement="bottom" effect="dark" :open-delay="80">
                            <button
                              class="icon-btn btn btn-link p-2"
                              type="button"
                              :aria-label="item.label"
                              :title="item.label"
                              @click="onMenuClick(item.key)"
                            >
                              <i :class="item.icon" aria-hidden="true"></i>
                            </button>
                          </el-tooltip>
                        </template>
                      </nav>
                    </div>
                  </header>

    <main class="stage">
      <!-- Chat card that moves from center to left -->
      <section :class="['chat-wrap', { docked: isDocked }]">
        <div class="chat-card">
          <h4 class="welcome-title" v-if="!isDocked">Welcome to the Career Planning Bot. What would you like to do?</h4>
          <el-card shadow="never" class="main-card">

            <div class="choice-row" v-if="!isDocked">
              <span class="choice" @click="start('job')">Find a job.</span><br>
              <span class="choice" @click="start('hire')">I want to hire.</span>
              <div style="display:flex; align-items:center; justify-content: space-between; margin-top:10px;">
                <div class="icons">
                  <i class="el-icon-paperclip"></i>
                  <i class="el-icon-microphone"></i>
                </div>
                <!-- <el-button type="primary" size="mini" @click="send">Send</el-button> -->
              </div>
            </div>

            <div class="input-area" v-else>
              <header class="topbar fixed-top" style="padding: 6px">
  <div class="container-fluid d-flex align-items-center justify-content-between ">
    <!-- LEFT: brand -->
    <div class="brand me-3">
      Career Bot
      <div class="subtitle">Powered by 4ways Group</div>
    </div>

    <!-- RIGHT: user icon + popover -->
    <div class="d-flex align-items-center">
      <!-- click-out overlay -->
      <div v-if="menuOpen" class="popover-overlay" @click="menuOpen = false"></div>

      <el-popover
        placement="bottom-end"
        width="220"
        trigger="click"
        v-model="menuOpen"
        popper-class="user-menu-popper"
        append-to-body
      >
        <ul class="user-menu">
          <li
            v-for="it in items"
            :key="it.key"
             @click="onMenuClick(it.key)"
          >
            <i :class="it.icon + ' me-2'"></i>
            {{ it.label }}
          </li>
        </ul>

        <template slot="reference">
          <button class="icon-btn btn btn-link p-2" type="button" @click.stop>
            <i class="bi bi-person-circle" aria-hidden="true"></i>
          </button>
        </template>
      </el-popover>
    </div>
  </div>
</header>

              <div class="chat-panel">
              <div class="chat-list">
                <div
                  v-for="m in messages"
                  :key="m.id"
                  class="msg-row d-flex align-items-end mb-3"
                  :class="m.from"
                >
                  <!-- left avatar -->
                  <el-avatar
                    v-if="m.from==='bot'"
                    class="me-2"
                    :size="28"
                    icon="el-icon-user"
                  />

                  <!-- bubble -->
                  <div class="bubble" :class="m.from">
                    {{ m.text }}
                  </div>

                  <!-- right avatar -->
                  <el-avatar
                    v-if="m.from==='user'"
                    class="ms-2"
                    :size="28"
                    icon="el-icon-user"
                  />
                </div>
              </div>
              <div class="chat-wrapper2" 
    @paste="handlePaste" 
    @dragover.prevent="dragOver = true"
    @dragleave="dragOver = false"
    @drop.prevent="handleDrop"
    :class="{ 'dragging': dragOver }">
    <div 
      class="chat-input-bar2"
    >
      <el-upload
        ref="upload"
        class="upload-trigger hidden-uploader"
        drag
        action=""
        multiple
        :auto-upload="false"
        :http-request="uploadFiles"
        :file-list="uiFileList"
        change="uploadFiles"
      >
        <i class="el-icon-plus" title="Attach file"></i>
      </el-upload>
      <div class="chat-box2">
      <div class="file-preview-wrapper2" v-if="uiFileList.length">
        <div class="file-preview2" v-for="(file, index) in uiFileList" :key="index">
          <i class="el-icon-document file-icon"></i>
          <div class="file-info">
            <div class="file-name" :title="file.name">{{ truncate(file.name) }}</div>
            <!-- <div class="file-type">Document</div> -->
          </div>
          <i class="el-icon-close close-btn" @click="removeFile(file)"></i>
        </div>
      </div>

      <input
        v-model="newMessage"
        @keyup.enter.exact="sendMessage"
        placeholder="Ask anything"
        class="chat-text-input"
      />

      <div class="action-buttons">
        <input
          type="file"
          ref="fileInput"
          @change="onFileSelected"
          style="display: none"
        />
        <button type="text" class="pill-button plus-button" @click="triggerFilePicker"><i class="el-icon-paperclip"></i></button>
      </div>

      <!-- <button class="mic-button" @click="sendMessage"><i class="el-icon-s-promotion"></i></button> -->
    </div>
    </div>

  </div>
              <!-- <div class="textarea-box">
              <div class="d-flex gap-2 mt-2 chat-composer">
                <el-input
                  type="textarea"
                  :autosize="{ minRows: 2, maxRows: 6 }"
                  placeholder="Type your message…"
                  v-model="newMessage"
                  @keyup.enter.native="send"
                ></el-input>
                </div>
              <div class="composer-actions">
                  <div class="icons">
                    <i class="el-icon-paperclip"></i>
                    <i class="el-icon-microphone"></i>
                  </div>
                </div>

                
              </div> -->

            </div>
            </div>
          </el-card>
        </div>
      </section>

      <!-- Right-side canvas that becomes visible once docked -->
      <section class="canvas" :class="{ active: isDocked }">
        <div v-if="canvasmode === 'single'" class="canvas-inner">
          <slot name="single">
            <div class="placeholder">
              <div>
                <div class="ph-title">Canvas</div>
                <div class="ph-text">
                  
                </div>
              </div>
            </div>
          </slot>
        </div>

        <div v-else-if="canvasmode === 'menu'" class="canvas-inner">
          <slot name="single">
            <div class="placeholder">
              <keep-alive>
                <component :is="resolvedCanvas"></component>
              </keep-alive>
            </div>
          </slot>
        </div>

        <div v-else-if="canvasmode === 'multiple'" class=" canvas-inner">
          <el-tabs v-model="activeId" type="card" editable @edit="onEdit">
            <el-tab-pane v-for="p in panes" :key="p.id" :name="p.id" :label="p.title" closable style="height: calc(86vh - 60px)">
              <!-- <div class="canvas-inner"> -->
                <div class="placeholder">
                  <div v-if="p.id === 'applicant1'">
                    <h3>Juan Dela Cruz - Full-stack Developer</h3>
                    <p><strong>Email:</strong> juan.dela.cruz@example.com</p>
                    <p><strong>Phone:</strong> +639xxxxxxxxx</p>
                    <p><strong>Location:</strong> Makati, Philippines</p>
                    <h4>Summary:</h4>
                    <p>Passionate and experienced Full-stack Developer with 5+ years of experience in developing web applications. Proficient in Vue.js, Laravel, Node.js, and SQL. Aiming to leverage my technical skills to contribute to innovative projects.</p>
                    <h4>Skills:</h4>
                    <ul>
                      <li>Vue.js, React, Angular</li>
                      <li>Laravel, Node.js</li>
                      <li>SQL, MongoDB, PostgreSQL</li>
                      <li>HTML5, CSS3, JavaScript, TypeScript</li>
                      <li>Git, Docker, CI/CD</li>
                    </ul>
                    <h4>Experience:</h4>
                    <ul>
                      <li><strong>Full-stack Developer</strong> | ABC Technologies | Jan 2020 - Present
                        <p>Led the development of a full-featured web app using Vue.js and Laravel. Collaborated with the design and product teams to optimize user experience and drive performance.</p>
                      </li>
                      <li><strong>Junior Developer</strong> | XYZ Solutions | Jun 2017 - Dec 2019
                        <p>Contributed to the development of scalable backend services using Node.js and SQL. Assisted in designing the front-end interface with React.js.</p>
                      </li>
                    </ul>
                    <h4>Education:</h4>
                    <ul>
                      <li><strong>Bachelor of Science in Computer Science</strong> | University of Manila | 2013 - 2017</li>
                    </ul>
                    <h4>Certifications:</h4>
                    <ul>
                      <li>Certified Vue.js Developer</li>
                      <li>Laravel Certified Developer</li>
                    </ul>
                  </div>

                  <div v-else-if="p.id === 'applicant2'">
                    <h3>Maria Santos - Project Manager</h3>
                    <p><strong>Email:</strong> maria.santos@example.com</p>
                    <p><strong>Phone:</strong> +639yyyyyyyy</p>
                    <p><strong>Location:</strong> Taguig, Philippines</p>
                    <h4>Summary:</h4>
                    <p>Highly organized Project Manager with 8+ years of experience in leading diverse teams to successfully complete projects on time and within budget. Expertise in Agile methodologies, resource allocation, and stakeholder communication.</p>
                    <h4>Skills:</h4>
                    <ul>
                      <li>Agile Project Management (Scrum, Kanban)</li>
                      <li>Stakeholder Management</li>
                      <li>Team Leadership</li>
                      <li>Risk Management</li>
                      <li>Jira, Trello, Asana</li>
                    </ul>
                    <h4>Experience:</h4>
                    <ul>
                      <li><strong>Project Manager</strong> | GlobalTech Innovations | Mar 2018 - Present
                        <p>Managed cross-functional teams to deliver IT projects for clients in finance, healthcare, and education sectors. Ensured projects were completed on time and within budget while maintaining high-quality standards.</p>
                      </li>
                      <li><strong>Assistant Project Manager</strong> | TechX Solutions | Apr 2015 - Feb 2018
                        <p>Assisted in managing project schedules, budgets, and client communications. Worked with senior PMs to implement Agile methodologies across teams.</p>
                      </li>
                    </ul>
                    <h4>Education:</h4>
                    <ul>
                      <li><strong>Master of Business Administration (MBA)</strong> | Ateneo de Manila University | 2017 - 2019</li>
                      <li><strong>Bachelor of Science in Information Technology</strong> | University of Makati | 2010 - 2014</li>
                    </ul>
                    <h4>Certifications:</h4>
                    <ul>
                      <li>Project Management Professional (PMP)</li>
                      <li>Certified Scrum Master (CSM)</li>
                    </ul>
                  </div>
                </div>

              <!-- </div> -->
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- <div class="canvas-inner">
          <div class="placeholder">
            <div>
              <div style="font-weight:600; margin-bottom:6px; text-align:center;">Canvas</div>
              <div style="max-width:560px; text-align:center;">
                This area is intentionally empty for now. Will use it to display search results, resumes, job matches, hiring funnels, or any auxiliary panels while the chat stays docked on the left.
              </div>
            </div>
          </div>
        </div> -->
      </section>
    </main>
  </div>
        </div>
    </div>

  <!-- Mobile version -->
  <div class="d-md-none">

    <!-- <div class="navbar-area">
        <div class="main-responsive-nav">
            <div class="container">
                <div class="main-responsive-menu mean-container">
                    <nav class="navbar">
                        <div class="container">
                            <div class="logo">
                                <router-link to="/">
                                    <div class="branding">
            <div class="title">Career Bot</div>
            <div class="subtitle">Powered by 4ways Group</div>
          </div>
                                </router-link>
                            </div>
                        </div>
                    </nav>
                </div>
            </div>
        </div>
    </div> -->

    
      <!-- <div class="video-background">
            <video autoplay muted loop playsinline>
              <source :src="require('@/assets/img/background.mp4')" type="video/mp4">
            </video>
      </div> -->


  
  </div>

        <el-dialog title="Login Required" :visible.sync="loginDialogVisible" width="400px">
                    <div style="text-align:center;" >
                        <div class="google-wrapper">
                        <div id="google-signin-btn">
                       <div id="g_id_onload"
                        data-client_id="279762919265-i1c0jaofqjmk8ik1qfaf7gjchjah0euv.apps.googleusercontent.com"
                        data-context="signin"
                        data-ux_mode="popup"
                        data-callback="handleCredentialResponse"
                        data-auto_prompt="false">
                      </div>
                      <div class="g_id_signin" data-type="standard" data-width="100%"
                      data-size="large"
                      data-theme="outline"></div></div>
                    </div>

                      <p style="margin-top:10px;font-size: 14px;">or use your account below:</p>
                      <el-form :model="loginForm" ref="loginForm">
                        <el-form-item >
                          <el-input v-model="loginForm.email" placeholder="Email"></el-input>
                        </el-form-item>
                        <el-form-item >
                          <el-input v-model="loginForm.password" type="password" placeholder="Password"></el-input>
                        </el-form-item>
                        <p style="font-size: 14px;">Don't have an account?
                          <el-button type="text" class="global-btn-underlined" @click="openSignupDialog">Sign up now!</el-button>
                        </p>
                        <el-form-item>
                          <el-button class="global-btn" @click="submitLogin">Login</el-button>
                        </el-form-item>
                      </el-form>
                    </div>
                  </el-dialog>

                  <!-- Signup dialog -->
                    <el-dialog title="Sign Up" :visible.sync="signupDialogVisible" width="400px">
                      <div style="text-align:center;">
                        <!-- your signup form here -->
                        <el-form :model="signupForm" :rules="rules" ref="signupForm">
                          <!-- <el-form-item prop="name">
                            <el-input v-model="signupForm.name" placeholder="Name"></el-input>
                          </el-form-item> -->

                          <el-form-item prop="email2">
                            <el-input v-model="signupForm.email2" placeholder="Email"></el-input>
                          </el-form-item>

                          <el-form-item prop="password2">
                            <el-input v-model="signupForm.password2" type="password" placeholder="Password"></el-input>
                          </el-form-item>

                          <el-form-item prop="otp">
                            <el-input v-model="signupForm.otp" placeholder="Enter OTP"></el-input>
                          </el-form-item>

                          <!-- <el-form-item> -->
                            <el-button type="text" class="global-btn-underlined" @click="sendOtp">Send OTP</el-button>
                            <el-button type="text" class="global-btn-underlined" @click="submitForm">Verify & Sign Up</el-button>
                          <!-- </el-form-item> -->
                        </el-form>
                        <el-button type="text" class="global-btn-underlined" @click="openLoginDialog">Already have an account? Login</el-button>
                      </div>
                    </el-dialog>
    </div>
  </div>
</template>

<script>
// @ is an alias to /src
import { mapGetters } from 'vuex'
import axios from 'axios';
import { marked } from 'marked';

import CanvasPlaceholder from '@/components/canvas/CanvasPlaceholder.vue'
import CanvasSettings    from '@/components/canvas/CanvasSettings.vue'
import CanvasChat        from '@/components/canvas/CanvasChat.vue'
import CanvasTasks       from '@/components/canvas/CanvasTasks.vue'
import CanvasRecords     from '@/components/canvas/CanvasRecords.vue'
import CanvasProfile     from '@/components/canvas/CanvasProfile.vue'
import CanvasPerf        from '@/components/canvas/CanvasPerf.vue'
import CanvasAccount     from '@/components/canvas/CanvasAccount.vue'

export function entryPost(intent, params = {}, extraCtx = {}) {
  const payload = {
    task_type: intent,
    additional_params: params,
    context: { client: 'web', envelope_processed: true, ...extraCtx }
  };

  return axios.post('/api/v1/entry/', payload)
    .then(response => {
      const data = response.data;
      if (!data || !data.success) {
        throw new Error(data && data.message ? data.message : 'Request failed');
      }
      return data;
    })
    .catch(error => {
      console.error('Error in entryPost:', error);
      throw error;
    });
}

// Get request function
export function entryGet(query = {}) {
  // query should include at least: { intent: '...' }
  return axios.get('/api/v1/entry/', { params: query })
    .then(response => {
      const data = response.data;
      if (!data || !data.success) {
        throw new Error(data && data.message ? data.message : 'Request failed');
      }
      return data;
    })
    .catch(error => {
      console.error('Error in entryGet:', error);
      throw error;
    });
}

export default {
  name: 'Home',
  components: {
    marked,
    CanvasSettings, CanvasChat, CanvasTasks, CanvasRecords,
    CanvasProfile, CanvasPerf, CanvasAccount, CanvasPlaceholder
  },
  data() {
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
        ],

        name: [
          { required: true, message: 'Please input your name', trigger: 'blur' }
        ],
        email2: [
          { required: true, message: 'Please input email address', trigger: 'blur' },
          { type: 'email', message: 'Please input correct email address', trigger: 'blur' }
        ],
        otp: [
          { required: true, message: 'Please enter OTP', trigger: 'blur' }
        ],
        password2: [
          { required: true, message: 'Please input password', trigger: 'blur' },
          { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
        ]
      
      }
        return {
          menuOpen: false,
          isDocked: false,
          selectedRole: null, // 'job' | 'hire'
          message: '',
          view: 'chat', // 'landing' | 'chat'
          items: [
              { key: 'settings', label: 'Settings',   icon: 'bi bi-gear' },
              { key: 'chat',     label: 'Messages',   icon: 'bi bi-chat-dots' },
              { key: 'tasks',    label: 'Tasks',      icon: 'bi bi-clipboard-check' },
              { key: 'records',  label: 'Records',    icon: 'bi bi-card-checklist' },
              { key: 'profile',  label: 'Profile',    icon: 'bi bi-person-badge' },
              { key: 'perf',     label: 'Performance',icon: 'bi bi-speedometer2' },
              { key: 'account',  label: 'Account',    icon: 'bi bi-person-circle' },
          ],
          canvasMap: {
            settings: 'CanvasSettings',
            chat: 'CanvasChat',
            tasks: 'CanvasTasks',
            records: 'CanvasRecords',
            profile: 'CanvasProfile',
            perf: 'CanvasPerf',
            account: 'CanvasAccount',
          },
          activeId: "applicant1", // Default to show the first applicant's CV
          panes: [
            { id: "applicant1", title: "Juan Dela Cruz - Full-stack Developer" },
            { id: "applicant2", title: "Maria Santos - Project Manager" }
          ],
          // panes: initial,        // ✅ no props used
          // activeId: initial[0].id,
          activeSection: 'about',
          activeMenu: '',
          canvasmode : '',
          activeIndex: null,
          fileList: [],
          uiFileList: [],
          isTyping: false,
          dragOver: false,
          typingSpeed: 5,
          displayedText: '',
          currentIndex: 0,
          showCard: false,
          inquiryMessage: null,
          expanded: [],
          isChatOpen: false,
          model: model, rules: rules, error: null, loading: false, 
          isFBLoaded: false,
          loginStatus: "",
          videoLoaded: false,
          mainvideoLoaded: false,
          isVisible: false,
          isLoggedIn2: false,
          loginDialogVisible: false,
          signupDialogVisible: false,
          loginForm: {
            email: '',
            password: ''
          },
          signupForm: {
            name: 'user',
            email2: '',
            password2: '',
            otp: ''
          },
          showPopup: false,
          selectedVideo: '',
          videoLoading: true,
          showHint: false,
          isMinimized: false,
          isMobile: window.innerWidth <= 768,
          messages: [
            {
              id: 1,
              from: 'bot',
              text: 'Welcome to the Career Planning Bot. What would you like to do?'
            },
            { id: 2, from: 'user', text: 'Find a job.' }
          ],
          form: {
            selectedFeatures: []
          },
          newMessage: "",
          userId: 1,
        };
      },
    computed: {
      ...mapGetters( ['isLoggedIn', 'user', 'userlogged']),
       resolvedCanvas () {
        return this.canvasMap[this.activeMenu] 
      }
    },

  created(){
    // Placeholder for Google API - will be loaded when needed
    if (typeof window !== 'undefined' && !window.google) {
      window.google = {
        accounts: {
          oauth2: {
            initTokenClient: () => ({
              requestAccessToken: () => {},
              callback: () => {}
            })
          },
          id: {
            initialize: () => {},
            renderButton: () => {}
          }
        }
      };
    }

    // Placeholder for Facebook API - will be loaded when needed
    if (typeof window !== 'undefined' && !window.FB) {
      window.FB = {
        init: () => {},
        AppEvents: {
          logPageView: () => {}
        },
        getLoginStatus: () => {},
        login: () => {},
        logout: () => {}
      };
    }

    this.$eventBus.$on('section-change', (section) => {
      this.activeSection = section
    })
    window.handleCredentialResponse = this.handleCredentialResponse;

    window.onload = () => {
      if (window.google && window.google.accounts) {
        window.google.accounts.oauth2.initTokenClient({
          client_id: 'YOUR_GOOGLE_CLIENT_ID_HERE',
          scope: 'email profile openid',
          callback: this.handleCredentialResponse,
        });
      }
    };
  },

  beforeDestroy() {
    document.removeEventListener('click', this.handleClickOutside);
    this.$eventBus.$off('section-change') // avoid memory leak
  },

  updated() { 
    this.scrollToBottom(); 
  },

  mounted() {
    this.scrollToBottom();
    this.$store.dispatch('trackVisit',{
      url: window.location.href,
      referrer: document.referrer
    })
    .then(() => {
      // console.log('Visit tracked');
    });

    document.addEventListener('click', this.handleClickOutside);
    this.loadGoogleScript().then(() => {
      // optional: you can render immediately if dialog is open
      if (this.loginDialogVisible) {
        setTimeout(() => {
        this.renderGoogleButton();
      }, 300);

    }

    if (this.isLoggedIn && !this.userlogged) {
          this.isLoggedIn2 = true;
          // console.log(this.isLoggedIn2);
          // console.log(this.userlogged);
        }
    });

    // alert(this.isLoggedIn2);
    if (!this.isLoggedIn2) {
      this.openLoginDialog();
      // alert();
      return;
    }
  },

  watch: {
    loginDialogVisible(newVal) {
    if (newVal) {
      // Dialog just became visible → render the button
      this.loadGoogleScript().then(() => {
        setTimeout(() => {
          this.renderGoogleButton();
        }, 300);
      });
    }
  },
  },

  methods: {
    start(role) {
        this.selectedRole = role;
        // trigger dock transition
        this.isDocked = true;
        this.canvasmode = 'single';
        // this.bgMode = "video"; // Removed bgMode reference
        // seed an opening assistant message in a real app
        this.$nextTick(() => {
          // focus textarea when it appears
          const ta = this.$el.querySelector('textarea');
          if (ta) ta.focus();
        });
    },

    onMenuClick(key) {
      this.isDocked = true;
      this.canvasmode = "menu";
      this.activeMenu = key;
      this.bgMode = "video";
      // this.$emit('menu-change', key); // if parent needs to know
    },

    async sendMessage() {
      if (!(this.newMessage).trim()) return
      this.messages.push({
        id: Date.now(),
        from: 'user',
        text: this.newMessage.trim(),
        files : this.uiFileList 
      })
      this.newMessage = ''

      setTimeout(() => {
          this.messages.push({
            id: Date.now() + 1,
            from: 'bot',
            text: 'here are the results' // ai bot reply will now displayed to conversation
          })
          this.setMode('multiple'); // 
        }, 500)
      // POST REQUEST TO BACKEND
      try {
        await entryPost('send_message', {
          conversation: this.messages
        });

        // After sending the message, simulate a delay before adding the bot's response
        setTimeout(() => {
          this.messages.push({
            id: Date.now() + 1,
            from: 'bot',
            text: 'Here are the results' // AI bot reply
          });
          this.setMode('multiple'); // Change mode to 'multiple' after receiving bot response
        }, 500);

      } catch (err) {
        this.$message.error(err.message || 'Sending message failed');
      }

      
    },

    setMode(m) { 
      this.canvasmode = m; 
    },

    addCanvas(title = 'New Canvas') {
      const id = 'cv-' + Date.now();
      this.panes.push({ id, title });
      this.activeId = id;
    },

    removeCanvas(id) {
      const i = this.panes.findIndex(p => p.id === id);
      if (i === -1) return;
      this.panes.splice(i, 1);
      if (this.activeId === id) {
        const next = this.panes[i] || this.panes[i - 1];
        this.activeId = next ? next.id : '';
      }
    },

    onEdit(targetName, action) {
      if (action === 'add') this.addCanvas();
      if (action === 'remove') this.removeCanvas(targetName);
    },

    uploadFiles(param) {
      console.log('File received:', param.file);
      console.log('Raw:', param.file.raw);
      const raw = param.file.raw || param.file;
      this.fileList.push(raw);

      // Optionally maintain UI file list too
      this.uiFileList.push(param.file);
    },


    handleManualUpload({ file }) {
      this.uiFileList.push(file);
    },

    handlePaste(event) {
      // Paste event so user can paste document to be uploaded
      const items = event.clipboardData.items;
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.kind === "file") {
          const file = item.getAsFile();
          this.uploadFileManually(file);
        }
      }
    },

    handleDrop(event) {
      // drag and drop event so user can drag files or documents to be uploaded
      this.dragOver = false;
      const files = event.dataTransfer.files;
      for (let i = 0; i < files.length; i++) {
        this.uploadFileManually(files[i]);
      }
    },

    uploadFileManually(file) {
      // Use el-upload's http-request manually
      this.$refs.upload.handleStart(file);
      this.handleManualUpload({ file });
    },

    removeFile(index) {
      this.uiFileList.splice(index, 1);
    },

    triggerFilePicker() {
      this.$refs.fileInput.click();
    },

    uploadFileManually2(file) {
      const fileObj = {
        name: file.name,
        size: file.size,
        status: "ready",
        raw: file
      };
      this.uiFileList.push(fileObj);
      this.$refs.upload.submit();
    },

    onFileSelected(event) {
      const file = event.target.files[0];
      if (file) {
        this.uploadFileManually2(file);
        event.target.value = "";
      }
    },

    scrollToBottom() {
      const el = this.$refs.list
      if (el) el.scrollTop = el.scrollHeight
    },

    onVideoLoaded() {
      this.videoLoading = false;
      this.mainvideoLoaded = true;
      // alert();
    },

    handleBgChange() {
      // this.$eventBus.$emit('bg-change', this.bgMode); // Removed bgMode reference
    },

    setSection(section) {
      this.activeSection = section
    },

    loadGoogleScript() { // load google script so login using google will work smoothly
      return new Promise((resolve, reject) => {
        if (window.google && window.google.accounts && window.google.accounts.id) {
          resolve();
          return;
        }
        const script = document.createElement("script");
        script.src = "https://accounts.google.com/gsi/client";
        script.async = true;
        script.defer = true;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
    },

  renderGoogleButton() { //adding og google button so user can login/signup using google account
    if (window.google && window.google.accounts && window.google.accounts.id) {
      const container = document.getElementById("google-signin-btn");
      if (container) {
        container.innerHTML = ""; // clear previous
        window.google.accounts.id.initialize({
          client_id: 'YOUR_GOOGLE_CLIENT_ID_HERE',
          callback: this.handleCredentialResponse,
        });
        window.google.accounts.id.renderButton(container, {
          theme: "outline",
          size: "large",
          width: "320px",
          border: "0px"
        });
      }
    } else {
      console.error("Google API not loaded");
    }
  },

  // handleCredentialResponse(response) { // POST REQUEST TO BACKEND
  //   console.log("Google JWT Token:", response.credential);
  //   this.$store.dispatch('handleGoogleLogin', { token: response.credential })
  //     .then(res => {
  //       localStorage.setItem("token", res.token);
  //       window.location.href = "/";
  //     });
  // },

  async handleCredentialResponse(response) {
      try {
        // Log the received Google JWT token (for debugging)
        console.log("Google JWT Token:", response.credential);

        // Send the token to the backend using entryPost
        const res = await entryPost('google_login', {
          token: response.credential
        });

        // If the response contains a token, store it in localStorage and redirect
        if (res.data.token) {
          localStorage.setItem("token", res.data.token);
          window.location.href = "/";
        } else {
          throw new Error("Login failed. Token not received.");
        }
      } catch (err) {
        // Handle any errors (e.g., network errors or server errors)
        this.$message.error(err.message || 'Login failed');
      }
  },

  openLoginDialog() {
    this.signupDialogVisible = false;
    this.loginDialogVisible = true;
  },
  openSignupDialog() {
    this.loginDialogVisible = false;
    this.signupDialogVisible = true;
  },

    


    sendEmailConfirmation(clientForm){
      this.loading = true;

       this.$refs[clientForm].validate((response) => {
        console.log(response);
        if (response) {
          // Form validation successful
        }else{
          this.loading = false;
        }
        });

    },

  async submitLogin() {
    this.$refs.loginForm.validate(async (valid) => {
      if (valid) {
        const form = {
          email: this.loginForm.email,
          password: this.loginForm.password,
        };

        try {
          // Call entryPost to send login request
          const res = await entryPost('auth_login', form);

          // Handle successful login response
          if (res.success) {
            this.$message.success('Login successful!');
            // Save token to localStorage
            localStorage.setItem('token', res.token);
          } else {
            // Handle unsuccessful login (e.g., incorrect credentials)
            this.$message.error('Login failed. Please check your credentials.');
          }
        } catch (err) {
          // Handle any error that occurs during the login request
          this.$message.error(err.message || 'Login request failed');
        }
      }
    });
  },

  async sendOtp() {
    if (!this.signupForm.email2) {
      this.$message.error('Please enter email first');
      return;
    }

    try {
      // Call entryPost to send OTP request
      await entryPost('send_otp', {
        email: this.signupForm.email2,
      });

      // Handle successful OTP sending
      this.$message.success('OTP sent to your email');
    } catch (err) {
      // Handle any error that occurs during the OTP request
      this.$message.error('Failed to send OTP');
    }
  },

  async submitForm() {
      const form = {
        name: this.signupForm.name,
        email2: this.signupForm.email2,
        password2: this.signupForm.password2,
        otp: this.signupForm.otp,
      };

      this.$refs.signupForm.validate(async (valid) => {
        if (valid) {
          try {
            // Call entryPost to verify OTP and complete registration
            const res = await entryPost('verify_otp_register', form);

            // Handle successful signup response
            if (res.success) {
              this.$message.success('Successfully signed up!');
              // Store token to localStorage
              localStorage.setItem('token', res.token);
              // Redirect to home page
              window.location.href = "/";
            } else {
              // Handle case where success is false, if needed
              this.$message.error('Signup failed. Please check the details and try again.');
            }
          } catch (err) {
            // Handle error during the signup request
            if (err.response && err.response.data && err.response.data.message) {
              this.$message.error(err.response.data.message);
            } else {
              this.$message.error('Failed to sign up');
            }
          }
        } else {
          console.log('Error in form validation!');
          return false;
        }
      });
    },

    handleClickOutside() {
      const card = this.$refs.card ? this.$refs.card.$el : null;
      const sidebar = this.$refs.sidebar;

      // If card is open, and click is outside card & sidebar -> close
      if (card && !card.contains(event.target) &&
        sidebar && !sidebar.contains(event.target)
      ) {
        this.activeIndex = null;
      }
    },

    loadFacebookSDK() {
      if (document.getElementById("facebook-jssdk")) {
        this.initializeFB();
        return;
      }

      window.fbAsyncInit = () => {
        if (window.FB) {
          window.FB.init({
            appId: "1364332831428891",
            cookie: true,
            xfbml: true,
            version: "v22.0",
          });

          window.FB.AppEvents.logPageView();
          this.isFBLoaded = true;
        }
      };

      let js = document.createElement("script");
      js.id = "facebook-jssdk";
      js.src = "https://connect.facebook.net/en_US/sdk.js";
      js.onload = this.initializeFB;
      let fjs = document.getElementsByTagName("script")[0];
      fjs.parentNode.insertBefore(js, fjs);
    },

    async checkUserCurrentStage(ref) {
      // form validation
      this.$refs[ref].validate(async (valid) => {
        if (!valid) return false;

        // Reset error and set loading
        this.error = null;
        this.loading = true;

        try {
          // Call entryGet to check the user's current stage
          const ret = await entryGet({ intent: 'check_user_current_stage', model: this.model });

          // Handle successful response
          if (ret.status === 'Success') {
            this.$tabEvent.emit('setToken', ret.data.token);

            // Redirect user based on device type
            if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
              this.$router.replace({ path: this.$route.query.redirect || '/client-search' });
            } else {
              this.$router.replace({ path: this.$route.query.redirect || '/' });
            }
            this.loading = false;
          } else {
            // Handle error codes
            this.handleError(ret.code);
          }
        } catch (err) {
          // Handle any errors from the GET request
          console.log('Error checking user stage:', err);
          this.error = { title: this.$t('Common.error_occured'), message: this.$t('Common.please_try_again') };
          if (err.response && err.response.status) {
            this.handleError(err.response.status);
          }
          this.loading = false;
        }
      });
    },

    handleError(code) {
      switch (code) {
        case 401:
          this.error = { title: this.$t('Common.please_try_again'), message: this.$t('Common.incorrect_user_pass') };
          break;
        case 500:
          this.error = { title: this.$t('Common.please_try_again'), message: this.$t('Common.internal_server_error') };
          break;
        default:
          this.error = { title: this.$t('Common.please_try_again'), message: this.$t('Common.error_occured') };
          break;
      }
    },

    // GET REQUEST TO BACKEND
    async getUserLoggedIn() {
      try {
        // Call entryGet to check the user login status
        const res = await entryGet({ intent: 'get_user_logged_in' });

        // If the response is successful, assign the user data and roles
        if (res && res.user && res.roles) {
          this.authUser = res.user;
          this.roles = res.roles;
        } else {
          // Handle case where there's no user data
          this.$message.error('User data not found');
        }
      } catch (err) {
        // Handle error, for example, if session has expired (401 error)
        if (err.response && err.response.status === 401) {
          this.$message({
            message: 'Login session expired, please try to login again.',
            type: 'warning'
          });
          this.$router.replace({ path: '/login' });
        } else {
          // Generic error handling
          this.$message.error(err.message || 'Failed to fetch user data');
        }
      }
    },

    truncate(name) {
      return name.length > 30 ? name.slice(0, 27) + '...' : name;
    },
    replaceName (message, data) {
          return message.replace(':name', data)
        },

    toggleEntry(index) {
      this.$set(this.expanded, index, !this.expanded[index]);
    },
    truncated(html) {
      const div = document.createElement('div');
      div.innerHTML = html;
      const text = div.innerText;
      return text.length > 120 ? text.slice(0, 120) + '...' : text;
    }
}
}
</script>
<style>
  .main-card .el-card__body{
      padding: 2px !important;
      height: 100%;
      /*padding-bottom: 2px !important;*/
    }
  .chat-list{
    height: 80%;
  }

      .el-textarea__inner{
      border: 0px !important;
      padding : 5px !important;
    }
</style>
<style scoped>

    :root {
      --page-bg: #fff;
      --text: #111;
      --muted: #6b7280; /* gray-500 */
      --border: #e5e7eb; /* gray-200 */
      --card: #ffffff;
      --accent: #111; /* black */
      --radius: 14px;
      --shadow: 0 6px 22px rgba(0,0,0,.08);
    }
    html, body { height: 100%; }
    body { margin: 0; font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; background: var(--page-bg); color: var(--text); }

    /* Layout shell */
    .shell {
      position: relative;
      min-height: 100vh;
      overflow: hidden;
    }

    .topbar {
      height: 72px;
      display: flex;
      align-items: center;
      padding: 0 28px;
      /*border-bottom: 1px solid var(--border);*/
    }
    .brand { font-weight: 700; letter-spacing: .2px; }

    /* Center stage: initial card */
    .stage {
      position: relative;
      height: calc(100vh );
    }

    /* Chatbox wrapper that animates from center to left dock */
    .chat-wrap {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      width: min(680px, calc(100% - 48px));
      transition: transform .55s cubic-bezier(.22,.61,.36,1), left .55s cubic-bezier(.22,.61,.36,1), top .55s cubic-bezier(.22,.61,.36,1), width .55s cubic-bezier(.22,.61,.36,1);
      z-index: 2;
    }

    .chat-wrap.docked {
      left: 24px;
      top: 40px;
      transform: translate(0, 0);
      width: 360px;
      height: 100%;
    }

    .chat-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      bottom: 0;
      height: 100%;
    }

    .textarea-box{
      border-radius: 12px;
      border: 1px solid #333;
      padding : 4px;
    }

    .welcome-title { font-weight: 600; text-align: center; margin: 18px 0px 18px 0px; }
    .prompt { color: var(--muted); text-align: center; margin-bottom: 16px; }

    .input-area { border-top: 1px dashed var(--border); padding-top: 12px; }

    /* Inline "button-like" choices */
    .choice-row { margin: 8px 0 12px; }
    .choice {
      display: inline-block;
      margin: 4px 0;
      text-decoration: underline;
      cursor: pointer;
      color: var(--accent);
      border-radius: 8px;
      padding: 2px 4px;
      transition: background-color .2s ease;
      font-size: 14px;
    }
    .choice:hover { background: #f3f4f6; }

    /* Footer icons row mimic (paperclip/mic/eq) */
    /*.icons { display: flex; align-items: center; margin-left: 0px; gap: 12px; color: var(--muted); }*/
    .icons {
      display: flex;
      justify-content: space-between; /* left & right edges */
      align-items: center;
      width: 100%;
    }
    /* The right-side canvas appears after docking */
    .canvas {
      position: absolute;
      inset: 0 0 0 0; /* full stage */
      opacity: 1;
      pointer-events: none;
      transition: opacity .45s ease .25s; /* fade in slightly after chat moves */
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 24px;
    }
    .canvas.active { opacity: 1; pointer-events: auto; }

    /* Canvas content leaves space for the docked chat */
    .canvas-inner {
      width: 100%;
      height: 100%;
      padding-left: clamp(0px, 360px + 28px, 40vw); /* reserve left rail when docked */
      transition: padding-left .55s cubic-bezier(.22,.61,.36,1);
      box-sizing: border-box;
      border-radius: 20px;
    }

    .canvas-inner >>> .el-tabs{
      background-color:   #FFF;
      padding : 8px;
      border-radius: 20px;
      margin-top: 16px;
    }

    .placeholder {
      opacity: 1;
      border: 2px dashed var(--border);
      border-radius: 16px;
      height: 97%;
      margin-top: 16px;
      display: grid;
      padding : 20px;
      overflow-y: auto;
      /*place-items: center;*/
      font-size: 14px;
      color: var(--muted);
      background: #fff;
    }

    .topbar {
  /*background:#fff;*/
  /*border-bottom:1px solid rgba(0,0,0,.06);*/
  z-index:1050; /* above content */
}
.brand { font-weight:600; }

/* same icon styling you had */
.trm { gap:.25rem; }
.icon-btn { line-height:1; border-radius:999px; color:#212529; transition:transform .15s, background-color .15s, color .15s; }
.icon-btn i { font-size:20px; width:20px; display:inline-block; }
.icon-btn:hover { background:rgba(0,0,0,.06); transform:translateY(-1px); }
.icon-btn:active { transform:translateY(0); }

.main-card {
  padding: 2px 6px 14px;
  border-radius: 20px;
  border-color: #000;
  height: 90%;
}

.main-card >>> .el-card__body{
  padding: 2px !important;
  height: 100%;
  /*padding-bottom: 2px !important;*/
}

.chat-panel {
  display: flex;
  flex-direction: column;
  height: 78vh;           /* or 100% of a parent, or calc(100vh - headerHeight) */
  background: #fff;
  margin-top: 55px;
}

/* Fills remaining space, scrolls; bottom-first when content is short */
.chat-list {
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 12px 8px 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end; /* keeps content at bottom until overflow */
}

/* Composer stays visible at bottom while list scrolls */
.chat-composer {
  position: sticky;  /* sticky inside chat-panel */
  bottom: 0;
  background: #fff;
  padding: 8px 8px 10px;
  /*border-top: 1px solid rgba(0,0,0,.06);*/
}

/* Actions row under the input */
.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}

/* Icons: paperclip left, mic right */
.icons {
  display: flex;
  align-items: center;
  width: 100%;
}
.icons .el-icon-microphone { margin-left: auto; }



    .msg-row.bot  { justify-content: flex-start; }
.msg-row.user { justify-content: flex-end; }



.canvas.active { /* keep your state hook if you need it */ }

/* Placeholder styling (your original content) */

.ph-title { font-weight: 600; margin-bottom: 6px; }
.ph-text  { max-width: 560px; margin: 0 auto; }

.canvas-tabs :deep(.el-tabs__content) { /* make tab content fill height */
  height: calc(100% - 40px); /* minus tabs header */
}
.canvas-tabs :deep(.el-tab-pane) {
  height: 100%;
}

  .chat-box2 {
    color: #111;
  height: 120px;
  background: transparent !important;
  /*padding: 16px;*/
  border-radius: 12px;
  position: relative;
  width: 100%;
  border: 1px solid #333;
  /*max-width: 600px;*/
  display: flex;
  align-items: center;
  background-color: #2a2a2a;
  border-radius: 20px;
  padding: 8px 12px;
  gap: 8px;
  flex-wrap: wrap;
  position: relative;
}



.text-area ::v-deep .el-textarea__inner {
  background: transparent;
  color: white;
  border: none;
  padding-top: 60px; /* allow space for file preview */
  resize: none;
}

.file-preview-wrapper2 {
  position: absolute;
  top: 2px;
  left: 16px;
  right: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  /*margin-bottom: 20px;*/
}

.file-preview2 {
  font-size: 11px;
  display: flex;
  align-items: center;
  background: transparent;
  border: 1px solid #333;
  padding: 8px 12px;
  border-radius: 8px;
  color: #111;
  max-width: 200px;
  flex-shrink: 0;
  position: relative;
}

.file-icon {
  font-size: 11px;
  margin-right: 8px;
  color: #f56c6c;
}

.file-info {
  flex: 1;
  overflow: hidden;
}

.file-name {
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-type {
  font-size: 12px;
  color: #ccc;
}

.close-btn {
  font-size: 14px;
  color: #aaa;
  cursor: pointer;
  margin-left: 8px;
}

.close-btn:hover {
  color: #f56c6c;
}

.toolbar {
  position: absolute;
  bottom: 12px;
  right: 16px;
}

.attach-icon {
  font-size: 20px;
  color: white;
  cursor: pointer;
}

.chat-wrapper2 {
  /*background: #2b2b2b;*/
  /*padding: 6px;*/
  border-radius: 12px;
  position: relative;
  /*border-top: 1px solid #333;*/
  font-family: 'Segoe UI', sans-serif;
  /*margin-top: -10px;*/
}

.chat-input-bar2 {
  display: flex;
  align-items: center;
  /*background-color: #2a2a2a;*/
  border-radius: 20px;
  /*padding: 8px 12px;*/
  gap: 8px;
  flex-wrap: wrap;
  position: relative;
}

.chat-text-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #111;
  font-size: 14px;
  width: 100%;
  /*min-width: 120px;*/
}

.hidden-uploader {
  display: none !important;
}
.upload-trigger {
  color: white;
  font-size: 18px;
  cursor: pointer;
}

.action-buttons {
  position: absolute;
  bottom: 2px;
  left: 16px;
  right: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.file-preview-list {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.file-preview {
  background-color: #333;
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.remove-file {
  cursor: pointer;
  color: #f87171;
}

.pill-button {
  background-color: transparent;
  color: #111;
  border: none;
  border-radius: 20px;
  padding: 6px 0px;
  font-size: 13px;
  cursor: pointer;
}


/* bubbles */
.bubble {
  max-width: 78%;
  padding: 10px 12px;
  border-radius: 16px;
  line-height: 1.35;
  word-break: break-word;
  box-shadow: 0 1px 0 rgba(0,0,0,.04);
  font-size: 14px;
}
.bubble.bot {
  background: #f1f3f5;     /* light gray like screenshot */
  color: #222;
  border-top-left-radius: 6px; /* subtle asymmetry */
}
.bubble.user {
  background: #e7f6ff;     /* pale blue like screenshot */
  color: #0b3b5e;
  border-top-right-radius: 6px;
}



    /* Respect users who prefer reduced motion */
    @media (prefers-reduced-motion: reduce) {
      .icon-btn { transition: none; }
    }

    /* Responsive tweaks */
    @media (max-width: 720px) {
      .chat-wrap.docked { width: calc(100% - 32px); left: 16px; top: 16px; }
      .canvas-inner { padding-left: 0; }
    }
  .wrapper {
    height: 100%;
    width: 100%;
  }
/*.app {
  height: 100vh;
  width: 100%;
}*/
  .sidebar{
    background-color: white;
    color: #000 !important;
    border: 1px solid #EBEEF5;
    width: 160px;
    border-radius: 10px;
    margin-top: 50px;
    height: auto;
  }
    
  .sidebar-item.active {
    font-weight: bold;
    color: #000; /* highlight color when active */
  }

.h100{
  height: 100%;
}

.about-card p {
    /*font-size: 15px !important;*/
}




.extra-card {
  background: rgba(255, 255, 255);
  border-radius: 20px;
  padding: 10px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  /*width: 700px;*/
  max-width: 80%;
  color: #000;
  margin-left: 20px;
  margin-top: -15px;
}

.extra-card p{
  font-size: 16px;
}

.extra-card .el-checkbox__label {

    /*width: 500px !important;*/
    }



.branding {
  font-family: 'Helvetica', 'Arial', sans-serif;
  text-align: left;
}

.title {
  font-weight: bold;
  font-size: 22px; /* Adjust to match the image size */
  color: #FFF;
}

.subtitle {
  font-weight: normal;
  font-size: 14px; /* Slightly smaller than title */
  color: #999999;  /* Approximate gray as in image */
}


ul {
  margin-left: 20px;
}

ul li {
  margin-bottom: 10px;
}

/*.custom-card{
  max-width: 80%;
}*/

.video-card {
  background: rgba(255, 255, 255);
  border-radius: 20px;
  padding: 10px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden; /* for rounded corners to clip children */
  /*width: 700px;*/
  max-width: 80%;
  color: #000;
  margin-left: 20px;
  margin-top: -15px;
}

.video-card >>> .el-card__body {
  padding: 16px;
  border: 1px solid #dcdcdc;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  background: #fff;
  text-align: left;
}

.video-card p{
  font-size: 16px;
}

.video-card .el-checkbox__label {

    /*width: 500px !important;*/
    }
.card-grid {
  display: grid;
  grid-template-columns: 1fr; /* 4 equal columns */
  gap: 20px; /* spacing between cards */
  max-width: 100%;
}
.card-container {
  max-width: 800px;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  gap: 20px; /* spacing between cards */
  /*max-width: 80%;*/
/*  padding: 16px;*/
}


.transparent-dialog {
  background-color: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
  overflow: visible;
}

.transparent-dialog .el-dialog
 {
    background-color: transparent !important;
    }

.transparent-dialog .el-dialog__body {
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}




.popover-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.3); /* semi-transparent grey */
  z-index: 999; /* below the popover (which is usually around 1000+) */
}


@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}



@media (max-width: 768px) {
    .branding {
      text-align: center;
    }

    .title {
       font-size: 26px;
    }
  }
</style>