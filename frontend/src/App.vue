<template>
  <div class="app">
    <!-- 좌측 사이드바 -->
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">QA</div>
        <div class="brand-text">
          <div class="brand-name">Release Gate</div>
          <div class="brand-sub">Device QA Console</div>
        </div>
      </div>

      <nav class="nav">
        <div class="nav-section">QUALITY</div>
        <div v-for="t in TABS" :key="t.key"
          class="nav-item" :class="{active: view===t.key}"
          @click="view=t.key">
          <span class="nav-icon" v-html="t.icon"></span>
          <span class="nav-label">{{ t.label }}</span>
          <span v-if="t.key==='gate' && releases.length" class="nav-count">{{ releases.length }}</span>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="status-dot" :class="connected ? 'dot-on' : 'dot-off'"></div>
        <span>{{ connected ? '백엔드 연결됨' : '백엔드 미연결' }}</span>
      </div>
    </aside>

    <!-- 메인 -->
    <div class="content">
      <header class="topbar">
        <div class="topbar-title">{{ currentTab.label }}</div>
        <div class="topbar-right">
          <span class="sync">{{ syncTime }}</span>
          <button class="refresh-btn" @click="refresh">↻ 새로고침</button>
        </div>
      </header>

      <main class="main">
        <release-gate    v-if="view==='gate'"    :releases="releases" :loading="loading" @reload="refresh" @toast="showToast" />
        <test-cases      v-if="view==='tc'"      :releases="releases" @toast="showToast" />
        <defect-tracker  v-if="view==='defect'"  :releases="releases" @toast="showToast" />
        <field-issues    v-if="view==='field'"   @toast="showToast" />
        <quality-metrics v-if="view==='metrics'" />
      </main>
    </div>

    <div class="toast-wrap">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="'toast-'+t.type">
        <span class="toast-icon">{{ t.type==='ok'?'✓':t.type==='err'?'✕':'ℹ' }}</span>{{ t.msg }}
      </div>
    </div>
  </div>
</template>

<script>
import { api } from './api/index.js'
import ReleaseGate    from './components/ReleaseGate.vue'
import TestCases      from './components/TestCases.vue'
import DefectTracker  from './components/DefectTracker.vue'
import FieldIssues    from './components/FieldIssues.vue'
import QualityMetrics from './components/QualityMetrics.vue'

export default {
  name: 'App',
  components: { ReleaseGate, TestCases, DefectTracker, FieldIssues, QualityMetrics },
  data() {
    return {
      view: 'gate',
      releases: [],
      loading: false,
      connected: false,
      toasts: [],
      syncTime: '',
      TABS: [
        { key: 'gate',    label: '릴리즈 게이트', icon: '<svg viewBox=\'0 0 20 20\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'1.6\'><path d=\'M10 2.5 17 6v8l-7 3.5L3 14V6z\'/><path d=\'m3 6 7 3.5L17 6M10 9.5v8\'/></svg>' },
        { key: 'tc',      label: '테스트 케이스', icon: '<svg viewBox=\'0 0 20 20\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'1.6\'><path d=\'M4 3h12v14H4z\'/><path d=\'m7 8 2 2 4-4\'/><path d=\'M7 13h6\'/></svg>' },
        { key: 'defect',  label: '결함 트래커',   icon: '<svg viewBox=\'0 0 20 20\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'1.6\'><circle cx=\'10\' cy=\'11\' r=\'5\'/><path d=\'M10 6V3M6.5 7 4.5 5M13.5 7l2-2M3 11H1M19 11h-2M10 16v2\'/></svg>' },
        { key: 'field',   label: '필드 이슈',     icon: '<svg viewBox=\'0 0 20 20\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'1.6\'><path d=\'M10 2a6 6 0 0 0-6 6c0 4 6 10 6 10s6-6 6-10a6 6 0 0 0-6-6z\'/><circle cx=\'10\' cy=\'8\' r=\'2\'/></svg>' },
        { key: 'metrics', label: '품질 지표',     icon: '<svg viewBox=\'0 0 20 20\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'1.6\'><path d=\'M3 17V3M3 17h14\'/><path d=\'m6 13 3-4 3 2 4-6\'/></svg>' },
      ]
    }
  },
  computed: {
    currentTab() { return this.TABS.find(t => t.key === this.view) || this.TABS[0] }
  },
  mounted() { this.refresh() },
  methods: {
    async refresh() {
      this.loading = true
      try {
        this.releases = await api.getReleases()
        this.connected = true
        this.syncTime = new Date().toLocaleTimeString('ko', { hour: '2-digit', minute: '2-digit' }) + ' 동기화'
      } catch(e) {
        this.connected = false
        this.syncTime = '오프라인'
        this.releases = []
      } finally {
        this.loading = false
      }
    },
    showToast({ msg, type = 'info' }) {
      const id = Date.now()
      this.toasts.push({ id, msg, type })
      setTimeout(() => { this.toasts = this.toasts.filter(t => t.id !== id) }, 4000)
    },
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #fafbfc;
  --bg2: #ffffff;
  --bg3: #f5f6f8;
  --bg4: #eceef1;
  --primary: #0d9488;
  --primary-dim: #e6f7f4;
  --primary-hover: #0f766e;
  --accent: #0891b2;
  --green: #16a34a;
  --green-dim: #e9f7ef;
  --red: #dc2626;
  --red-dim: #fdeaea;
  --yellow: #d97706;
  --yellow-dim: #fdf4e3;
  --purple: #7c3aed;
  --purple-dim: #f1ecfd;
  --text: #1f2328;
  --muted: #656d76;
  --faint: #afb8c1;
  --border: #e1e4e8;
  --border2: #d0d7de;
  --radius: 10px;
  --sidebar-w: 256px;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
}

.app { display: flex; min-height: 100vh; }

/* 사이드바 */
.sidebar {
  width: var(--sidebar-w);
  background: var(--bg2);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
}
.brand {
  display: flex; align-items: center; gap: 11px;
  padding: 20px 20px;
  border-bottom: 1px solid var(--border);
}
.brand-mark {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #ffffff;
  font-size: 13px; font-weight: 700;
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 9px;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: .02em;
}
.brand-name { font-size: 15px; font-weight: 700; color: var(--text); line-height: 1.25; }
.brand-sub { font-size: 12px; color: var(--muted); margin-top: 2px; }

.nav { flex: 1; padding: 18px 14px; }
.nav-section { font-size: 11px; font-weight: 700; color: var(--faint); letter-spacing: .1em; padding: 0 12px; margin-bottom: 12px; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 14px; border-radius: 8px;
  font-size: 14px; color: var(--muted);
  cursor: pointer; transition: all .15s;
  margin-bottom: 3px;
}
.nav-item:hover { background: var(--bg3); color: var(--text); }
.nav-item.active { background: var(--primary-dim); color: var(--primary); font-weight: 600; }
.nav-icon { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.nav-icon svg { width: 19px; height: 19px; }
.nav-label { flex: 1; }
.nav-count { background: var(--bg4); color: var(--muted); font-size: 11px; font-weight: 600; padding: 1px 7px; border-radius: 9px; font-family: 'JetBrains Mono', monospace; }
.nav-item.active .nav-count { background: var(--primary); color: #ffffff; }

.sidebar-footer {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 20px;
  border-top: 1px solid var(--border);
  font-size: 11px; color: var(--muted);
}
.status-dot { width: 7px; height: 7px; border-radius: 50%; }
.dot-on { background: var(--green); box-shadow: 0 0 6px var(--green); }
.dot-off { background: var(--faint); }

/* 콘텐츠 */
.content { flex: 1; margin-left: var(--sidebar-w); display: flex; flex-direction: column; min-height: 100vh; }
.topbar {
  height: 64px;
  border-bottom: 1px solid var(--border);
  background: var(--bg2);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 32px;
  position: sticky; top: 0; z-index: 50;
}
.topbar-title { font-size: 18px; font-weight: 700; }
.topbar-right { display: flex; align-items: center; gap: 14px; }
.sync { font-size: 11px; color: var(--muted); font-family: 'JetBrains Mono', monospace; }
.refresh-btn { background: var(--bg3); border: 1px solid var(--border2); color: var(--muted); padding: 6px 12px; border-radius: 7px; font-size: 12px; cursor: pointer; font-family: inherit; }
.refresh-btn:hover { background: var(--bg4); color: var(--text); }

.main { flex: 1; padding: 32px; }

/* 공통 */
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; gap: 12px; flex-wrap: wrap; }
.page-title { font-size: 19px; font-weight: 700; }
.page-sub { font-size: 13px; color: var(--muted); margin-top: 4px; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 9px 17px; border-radius: 8px; font-size: 14px; font-family: inherit; cursor: pointer; border: none; font-weight: 500; transition: all .15s; }
.btn-primary { background: var(--primary); color: #ffffff; font-weight: 600; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-primary:disabled { opacity: .4; cursor: not-allowed; }
.btn-ghost { background: var(--bg3); color: var(--muted); border: 1px solid var(--border2); }
.btn-ghost:hover { background: var(--bg4); color: var(--text); }
.btn-danger { background: var(--red-dim); color: var(--red); border: 1px solid rgba(248,113,113,.25); }
.btn-danger:hover { background: rgba(248,113,113,.2); }
.btn-sm { padding: 5px 11px; font-size: 12px; }

.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(165px, 1fr)); gap: 14px; margin-bottom: 28px; }
.metric-card { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
.metric-label { font-size: 12px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 8px; }
.metric-val { font-size: 30px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.metric-sub { font-size: 12px; color: var(--muted); margin-top: 4px; }

.table-wrap { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: var(--bg3); padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 700; color: var(--muted); border-bottom: 1px solid var(--border); white-space: nowrap; text-transform: uppercase; letter-spacing: .04em; }
.data-table td { padding: 13px 16px; border-bottom: 1px solid var(--border); font-size: 14px; vertical-align: middle; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: var(--bg3); }

.chip { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }
.chip-critical { background: var(--red-dim); color: var(--red); }
.chip-major    { background: var(--yellow-dim); color: var(--yellow); }
.chip-minor    { background: var(--green-dim); color: var(--green); }
.chip-open       { background: var(--red-dim);     color: var(--red); }
.chip-in-progress{ background: var(--yellow-dim);  color: var(--yellow); }
.chip-resolved   { background: var(--primary-dim); color: var(--primary); }
.chip-closed     { background: var(--bg4);         color: var(--muted); }
.chip-pass       { background: var(--green-dim);   color: var(--green); }
.chip-fail       { background: var(--red-dim);     color: var(--red); }
.chip-blocked    { background: var(--purple-dim);  color: var(--purple); }
.chip-untested   { background: var(--bg4);         color: var(--muted); }
.chip-smoke      { background: var(--primary-dim); color: var(--primary); }
.chip-regression { background: var(--purple-dim);  color: var(--purple); }
.chip-integration{ background: var(--yellow-dim);  color: var(--yellow); }

.mono { font-family: 'JetBrains Mono', monospace; }
.empty { text-align: center; padding: 48px; color: var(--muted); font-size: 13px; }

/* 모달 */
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 300; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(2px); }
.modal { background: var(--bg2); border: 1px solid var(--border2); border-radius: 12px; padding: 24px; width: 520px; max-width: 90vw; max-height: 85vh; overflow-y: auto; }
.modal-title { font-size: 15px; font-weight: 700; margin-bottom: 18px; }
.field { margin-bottom: 12px; }
.field label { display: block; font-size: 11px; color: var(--muted); font-weight: 600; margin-bottom: 5px; text-transform: uppercase; letter-spacing: .04em; }
.field input, .field select, .field textarea { width: 100%; background: var(--bg3); border: 1px solid var(--border2); border-radius: 7px; padding: 8px 10px; color: var(--text); font-size: 13px; font-family: inherit; outline: none; transition: border-color .15s; }
.field input:focus, .field select:focus, .field textarea:focus { border-color: var(--primary); }
.field textarea { resize: vertical; min-height: 72px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border); }

/* 토스트 */
.toast-wrap { position: fixed; bottom: 24px; right: 24px; z-index: 400; display: flex; flex-direction: column; gap: 8px; }
.toast { background: var(--bg2); border: 1px solid var(--border2); border-radius: 9px; padding: 11px 16px; font-size: 13px; display: flex; align-items: center; gap: 8px; min-width: 220px; box-shadow: 0 4px 16px rgba(0,0,0,.1); animation: slideIn .2s; }
.toast-ok   { border-left: 3px solid var(--green); }
.toast-err  { border-left: 3px solid var(--red); }
.toast-info { border-left: 3px solid var(--primary); }
.toast-ok   .toast-icon { color: var(--green); }
.toast-err  .toast-icon { color: var(--red); }
.toast-info .toast-icon { color: var(--primary); }
.toast-icon { font-size: 14px; font-weight: 700; }

@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
</style>