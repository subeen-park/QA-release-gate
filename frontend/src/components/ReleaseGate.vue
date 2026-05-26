<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">릴리즈 게이트</div>
        <div class="page-sub">무선(OTA) 배포 전 QA 통과 기준을 점검하고 Go / No-Go를 판정합니다</div>
      </div>
      <button class="btn btn-primary" @click="openForm()">+ 릴리즈 등록</button>
    </div>

    <div v-if="loading" class="empty">로딩 중...</div>
    <div v-else-if="releases.length === 0" class="empty">등록된 릴리즈가 없어요. 첫 릴리즈를 등록해보세요!</div>
    <div v-else class="release-grid">
      <div v-for="r in releases" :key="r.id" class="release-card" :class="cardClass(r)">
        <div class="rc-header">
          <div class="rc-version">
            <span class="mono">{{ r.version }}</span>
            <span class="platform-chip">{{ r.platform }}</span>
          </div>
          <div class="rc-gate" :class="gateClass2(r)">{{ gateLabel(r) }}</div>
        </div>

        <div class="rc-desc" v-if="r.description">{{ r.description }}</div>

        <div class="gate-criteria">
          <div class="criteria-row" :class="critClass(r.critical_defects > 0)">
            <span class="crit-icon">{{ r.critical_defects > 0 ? '✕' : '✓' }}</span>
            <span>Critical 결함</span>
            <span class="crit-val mono">{{ r.critical_defects }}건</span>
          </div>
          <div class="criteria-row" :class="critClass(passRate(r) < 90)">
            <span class="crit-icon">{{ passRate(r) < 90 ? '✕' : '✓' }}</span>
            <span>TC 통과율</span>
            <span class="crit-val mono">{{ passRate(r) }}%</span>
          </div>
          <div class="criteria-row" :class="warnClass(r.open_defects > 5)">
            <span class="crit-icon">{{ r.open_defects > 5 ? '⚠' : '✓' }}</span>
            <span>미해결 결함</span>
            <span class="crit-val mono">{{ r.open_defects }}건</span>
          </div>
        </div>

        <div class="tc-progress">
          <div class="tcp-label">
            <span>TC 진행</span>
            <span class="mono">{{ r.pass_tc }}/{{ r.total_tc }}</span>
          </div>
          <div class="tcp-bar">
            <div class="tcp-fill tcp-pass" :style="barStyle(r.pass_tc, r.total_tc)"></div>
            <div class="tcp-fill tcp-fail" :style="barStyle(r.fail_tc, r.total_tc)"></div>
          </div>
        </div>

        <div class="rc-footer">
          <span class="rc-date mono">{{ shortDate(r.created_at) }}</span>
          <div class="rc-actions">
            <button class="btn btn-ghost btn-sm" @click="updateGate(r, 'go')">Go ✓</button>
            <button class="btn btn-danger btn-sm" @click="updateGate(r, 'no-go')">No-Go ✕</button>
            <button class="btn btn-ghost btn-sm" @click="openForm(r)">수정</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showForm" class="overlay" @click.self="showForm=false">
      <div class="modal">
        <div class="modal-title">{{ editing ? '릴리즈 수정' : '릴리즈 등록' }}</div>
        <div class="field"><label>버전 *</label><input v-model="form.version" placeholder="예: v2.4.1" /></div>
        <div class="field-row">
          <div class="field"><label>플랫폼</label>
            <select v-model="form.platform">
              <option>Android</option><option>iOS</option><option>Web</option><option>All</option>
            </select>
          </div>
          <div class="field"><label>상태</label>
            <select v-model="form.status">
              <option value="testing">Testing</option>
              <option value="rc">RC</option>
              <option value="released">Released</option>
              <option value="hotfix">Hotfix</option>
            </select>
          </div>
        </div>
        <div class="field"><label>설명</label><textarea v-model="form.description" placeholder="주요 변경사항" rows="3"></textarea></div>
        <div class="modal-actions">
          <button v-if="editing" class="btn btn-danger" @click="del">삭제</button>
          <div style="flex:1"></div>
          <button class="btn btn-ghost" @click="showForm=false">취소</button>
          <button class="btn btn-primary" @click="save">저장</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../api/index.js'

export default {
  name: 'ReleaseGate',
  props: {
    releases: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  emits: ['reload', 'toast'],
  data() {
    return {
      showForm: false,
      editing: null,
      form: { version: '', platform: 'Android', status: 'testing', description: '' }
    }
  },
  methods: {
    passRate(r) {
      if (!r.total_tc) return 0
      return Math.round((r.pass_tc / r.total_tc) * 100)
    },
    gateKey(r) {
      if (r.gate_status === 'go') return 'go'
      if (r.gate_status === 'no-go') return 'nogo'
      if (r.critical_defects > 0) return 'nogo'
      if (this.passRate(r) >= 90 && r.open_defects <= 5) return 'ready'
      return 'pending'
    },
    cardClass(r) { return 'rc-' + this.gateKey(r) },
    gateClass2(r) { return 'gate-' + this.gateKey(r) },
    gateLabel(r) {
      const map = { go: '✓ Go', nogo: '✕ No-Go', ready: '◉ 준비됨', pending: '○ 검증중' }
      return map[this.gateKey(r)] || '○ 검증중'
    },
    critClass(isFail) { return isFail ? 'crit-fail' : 'crit-pass' },
    warnClass(isWarn) { return isWarn ? 'crit-warn' : 'crit-pass' },
    barStyle(a, b) {
      const w = b ? Math.round(a / b * 100) : 0
      return { width: w + '%' }
    },
    shortDate(d) { return d ? String(d).slice(0, 10) : '' },
    openForm(r) {
      this.editing = r || null
      if (r) {
        this.form = { version: r.version, platform: r.platform, status: r.status, description: r.description }
      } else {
        this.form = { version: '', platform: 'Android', status: 'testing', description: '' }
      }
      this.showForm = true
    },
    async save() {
      if (!this.form.version.trim()) {
        this.$emit('toast', { msg: '버전을 입력하세요', type: 'err' })
        return
      }
      try {
        if (this.editing) {
          await api.updateRelease(this.editing.id, Object.assign({}, this.editing, this.form))
        } else {
          await api.createRelease(this.form)
        }
        this.showForm = false
        this.$emit('reload')
        this.$emit('toast', { msg: this.editing ? '수정되었습니다' : '릴리즈가 등록되었습니다', type: 'ok' })
      } catch(e) {
        this.$emit('toast', { msg: e.message, type: 'err' })
      }
    },
    async del() {
      if (!confirm('이 릴리즈를 삭제하시겠습니까?')) return
      await api.deleteRelease(this.editing.id)
      this.showForm = false
      this.$emit('reload')
      this.$emit('toast', { msg: '삭제되었습니다', type: 'info' })
    },
    async updateGate(r, status) {
      await api.updateRelease(r.id, Object.assign({}, r, { gate_status: status }))
      this.$emit('reload')
      this.$emit('toast', { msg: status === 'go' ? 'Go 판정되었습니다' : 'No-Go 판정되었습니다', type: status === 'go' ? 'ok' : 'err' })
    }
  }
}
</script>

<style scoped>
.release-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.release-card { background: var(--bg2); border: 1.5px solid var(--border); border-radius: 12px; padding: 18px; display: flex; flex-direction: column; gap: 14px; }
.rc-go { border-color: rgba(22,163,74,.3); }
.rc-nogo { border-color: rgba(220,38,38,.3); }
.rc-ready { border-color: rgba(37,99,235,.2); }
.rc-header { display: flex; align-items: center; justify-content: space-between; }
.rc-version { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; }
.platform-chip { font-size: 10px; background: var(--bg4); color: var(--muted); padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.rc-gate { font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 6px; }
.gate-go { background: var(--green-dim); color: var(--green); }
.gate-nogo { background: var(--red-dim); color: var(--red); }
.gate-ready { background: var(--primary-dim); color: var(--primary); }
.gate-pending { background: var(--bg4); color: var(--muted); }
.rc-desc { font-size: 12px; color: var(--muted); line-height: 1.6; }
.gate-criteria { display: flex; flex-direction: column; gap: 6px; background: var(--bg3); border-radius: 8px; padding: 10px 12px; }
.criteria-row { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.crit-icon { width: 16px; font-weight: 700; flex-shrink: 0; }
.crit-val { margin-left: auto; font-size: 12px; }
.crit-pass .crit-icon { color: var(--green); }
.crit-fail { color: var(--red); }
.crit-fail .crit-icon { color: var(--red); }
.crit-warn { color: var(--yellow); }
.crit-warn .crit-icon { color: var(--yellow); }
.tc-progress { display: flex; flex-direction: column; gap: 5px; }
.tcp-label { display: flex; justify-content: space-between; font-size: 11px; color: var(--muted); }
.tcp-bar { height: 6px; background: var(--bg4); border-radius: 3px; overflow: hidden; display: flex; }
.tcp-fill { height: 100%; transition: width .3s; }
.tcp-pass { background: var(--green); }
.tcp-fail { background: var(--red); }
.rc-footer { display: flex; align-items: center; justify-content: space-between; padding-top: 4px; border-top: 1px solid var(--border); }
.rc-date { font-size: 11px; color: var(--muted); }
.rc-actions { display: flex; gap: 6px; }
</style>