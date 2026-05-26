<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">결함 트래커</div>
        <div class="page-sub">결함 등록 · 심각도 분류 · 탈출 결함 추적</div>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <select v-model="filterRelease" class="filter-sel">
          <option value="">전체 릴리즈</option>
          <option v-for="r in releases" :key="r.id" :value="r.id">{{ r.version }}</option>
        </select>
        <select v-model="filterSeverity" class="filter-sel">
          <option value="">전체 심각도</option>
          <option value="critical">Critical</option>
          <option value="major">Major</option>
          <option value="minor">Minor</option>
        </select>
        <select v-model="filterStatus" class="filter-sel">
          <option value="">전체 상태</option>
          <option value="open">Open</option>
          <option value="in-progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
        <button class="btn btn-primary" @click="openForm()">+ 결함 등록</button>
      </div>
    </div>

    <!-- 메트릭 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-label">전체 결함</div>
        <div class="metric-val">{{ defects.length }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Critical</div>
        <div class="metric-val" style="color:var(--red)">{{ bySev('critical') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Major</div>
        <div class="metric-val" style="color:var(--yellow)">{{ bySev('major') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Open</div>
        <div class="metric-val" style="color:var(--primary)">{{ byStatus('open') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">탈출 결함</div>
        <div class="metric-val" style="color:var(--purple)">{{ escaped }}</div>
        <div class="metric-sub">배포 후 발견</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">재발 결함</div>
        <div class="metric-val" style="color:var(--yellow)">{{ recurred }}</div>
        <div class="metric-sub">동일 이슈 재발</div>
      </div>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th style="width:80px">심각도</th>
            <th>제목</th>
            <th style="width:100px">릴리즈</th>
            <th style="width:90px">담당자</th>
            <th style="width:90px">상태</th>
            <th style="width:60px">Jira</th>
            <th style="width:80px">플래그</th>
            <th style="width:80px">등록일</th>
            <th style="width:50px"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!filtered.length"><td colspan="9" class="empty">결함이 없습니다 ✓</td></tr>
          <tr v-for="d in filtered" :key="d.id">
            <td><span class="chip" :class="'chip-'+d.severity">{{ sevLabel(d.severity) }}</span></td>
            <td style="font-size:13px;font-weight:500;max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ d.title }}</td>
            <td class="mono" style="font-size:11px;color:var(--muted)">{{ releaseVersion(d.release_id) }}</td>
            <td style="font-size:12px;color:var(--muted)">{{ d.assignee || '-' }}</td>
            <td><span class="chip" :class="'chip-'+d.status.replace(' ','-')">{{ statusLabel(d.status) }}</span></td>
            <td><a v-if="d.jira" :href="'#'" class="jira-link mono">{{ d.jira }}</a><span v-else class="muted-text">-</span></td>
            <td>
              <span v-if="d.is_escaped" class="flag-chip fc-esc" title="탈출 결함">탈출</span>
              <span v-if="d.is_recurred" class="flag-chip fc-rec" title="재발">재발</span>
            </td>
            <td class="mono" style="font-size:11px;color:var(--muted)">{{ d.created_at?.slice(0,10) }}</td>
            <td><button class="icon-btn" @click="openForm(d)">⋯</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 모달 -->
    <div v-if="showForm" class="overlay" @click.self="showForm=false">
      <div class="modal">
        <div class="modal-title">{{ editing ? '결함 수정' : '결함 등록' }}</div>
        <div class="field"><label>제목 *</label><input v-model="form.title" placeholder="결함 제목" /></div>
        <div class="field-row">
          <div class="field"><label>심각도</label>
            <select v-model="form.severity">
              <option value="critical">Critical — 서비스 불가</option>
              <option value="major">Major — 주요 기능 장애</option>
              <option value="minor">Minor — 경미한 오류</option>
            </select>
          </div>
          <div class="field"><label>상태</label>
            <select v-model="form.status">
              <option value="open">Open</option>
              <option value="in-progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        </div>
        <div class="field-row">
          <div class="field"><label>릴리즈</label>
            <select v-model="form.release_id">
              <option value="">없음</option>
              <option v-for="r in releases" :key="r.id" :value="r.id">{{ r.version }}</option>
            </select>
          </div>
          <div class="field"><label>담당자</label><input v-model="form.assignee" placeholder="담당자" /></div>
        </div>
        <div class="field"><label>Jira 번호</label><input v-model="form.jira" placeholder="DEVICE-123" /></div>
        <div class="field"><label>재현 절차</label><textarea v-model="form.steps" placeholder="1. 설정 진입 / 2. ..."></textarea></div>
        <div class="field"><label>설명</label><textarea v-model="form.description" placeholder="추가 설명"></textarea></div>
        <div style="display:flex;gap:16px;margin-top:4px">
          <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer">
            <input type="checkbox" v-model="form.is_escaped" /> 탈출 결함 (배포 후 발견)
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer">
            <input type="checkbox" v-model="form.is_recurred" /> 재발 결함
          </label>
        </div>
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
  name: 'DefectTracker',
  props: { releases: Array },
  emits: ['toast'],
  data() {
    return {
      defects: [], showForm: false, editing: null,
      filterRelease: '', filterSeverity: '', filterStatus: '',
      form: { title:'', severity:'minor', status:'open', release_id:'', assignee:'', jira:'', steps:'', description:'', is_escaped:false, is_recurred:false }
    }
  },
  computed: {
    filtered() {
      return this.defects.filter(d => {
        if (this.filterRelease   && d.release_id !== this.filterRelease)     return false
        if (this.filterSeverity  && d.severity   !== this.filterSeverity)    return false
        if (this.filterStatus    && d.status      !== this.filterStatus)      return false
        return true
      })
    },
    escaped()  { return this.defects.filter(d=>d.is_escaped).length },
    recurred() { return this.defects.filter(d=>d.is_recurred).length },
  },
  async mounted() { await this.load() },
  methods: {
    async load() { this.defects = await api.getDefects() },
    bySev(s)    { return this.defects.filter(d=>d.severity===s).length },
    byStatus(s) { return this.defects.filter(d=>d.status===s).length },
    sevLabel(s) { return { critical:'Critical', major:'Major', minor:'Minor' }[s] || s },
    statusLabel(s) { return { open:'Open','in-progress':'진행중', resolved:'해결됨', closed:'종료' }[s] || s },
    releaseVersion(id) { return this.releases?.find(r=>r.id===id)?.version || '-' },
    openForm(d) {
      this.editing = d || null
      this.form = d ? { ...d } : { title:'', severity:'minor', status:'open', release_id:'', assignee:'', jira:'', steps:'', description:'', is_escaped:false, is_recurred:false }
      this.showForm = true
    },
    async save() {
      if (!this.form.title.trim()) { this.$emit('toast',{msg:'제목을 입력하세요',type:'err'}); return }
      try {
        if (this.editing) await api.updateDefect(this.editing.id, this.form)
        else              await api.createDefect(this.form)
        this.showForm = false; await this.load()
        this.$emit('toast',{msg:this.editing?'수정되었습니다':'결함이 등록되었습니다',type:'ok'})
      } catch(e) { this.$emit('toast',{msg:e.message,type:'err'}) }
    },
    async del() {
      if (!confirm('삭제하시겠습니까?')) return
      await api.deleteDefect(this.editing.id); this.showForm=false; await this.load()
      this.$emit('toast',{msg:'삭제되었습니다',type:'info'})
    },
  }
}
</script>

<style scoped>
.filter-sel{background:var(--bg2);border:1px solid var(--border2);border-radius:7px;padding:6px 10px;color:var(--text);font-size:12px;outline:none;cursor:pointer}
.jira-link{color:var(--primary);text-decoration:none;font-size:11px}.jira-link:hover{text-decoration:underline}
.muted-text{color:var(--muted);font-size:12px}
.flag-chip{display:inline-block;padding:1px 5px;border-radius:3px;font-size:10px;font-weight:700;margin-right:2px}
.fc-esc{background:var(--purple-dim);color:var(--purple)}
.fc-rec{background:var(--yellow-dim);color:var(--yellow)}
</style>