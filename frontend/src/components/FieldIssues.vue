<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">필드 이슈</div>
        <div class="page-sub">CS 유입 이슈 분석 · 재발 패턴 추적 · TC 전환 관리</div>
      </div>
      <button class="btn btn-primary" @click="openForm()">+ 필드 이슈 등록</button>
    </div>

    <div class="metrics-grid">
      <div class="metric-card"><div class="metric-label">전체</div><div class="metric-val">{{ issues.length }}</div></div>
      <div class="metric-card"><div class="metric-label">Open</div><div class="metric-val" style="color:var(--red)">{{ byStatus('open') }}</div></div>
      <div class="metric-card"><div class="metric-label">재발 이슈</div><div class="metric-val" style="color:var(--yellow)">{{ recurred }}</div><div class="metric-sub">동일 패턴 재발</div></div>
      <div class="metric-card"><div class="metric-label">TC 전환됨</div><div class="metric-val" style="color:var(--green)">{{ tcLinked }}</div><div class="metric-sub">테스트케이스로 등록</div></div>
      <div class="metric-card"><div class="metric-label">TC 미전환</div><div class="metric-val" style="color:var(--muted)">{{ issues.length - tcLinked }}</div><div class="metric-sub">추가 전환 필요</div></div>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th style="width:60px">출처</th>
            <th style="width:80px">심각도</th>
            <th>제목</th>
            <th>패턴 / 원인</th>
            <th style="width:90px">담당자</th>
            <th style="width:90px">상태</th>
            <th style="width:100px">플래그</th>
            <th style="width:50px"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!issues.length"><td colspan="8" class="empty">필드 이슈가 없어요 ✓</td></tr>
          <tr v-for="i in issues" :key="i.id" :class="{'row-recurred': i.is_recurred}">
            <td><span class="source-chip">{{ i.source }}</span></td>
            <td><span class="chip" :class="'chip-'+i.severity">{{ sevLabel(i.severity) }}</span></td>
            <td style="font-size:13px;font-weight:500;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ i.title }}</td>
            <td style="font-size:12px;color:var(--muted);max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ i.pattern || '-' }}</td>
            <td style="font-size:12px;color:var(--muted)">{{ i.assignee || '-' }}</td>
            <td><span class="chip" :class="'chip-'+i.status.replace(' ','-')">{{ statusLabel(i.status) }}</span></td>
            <td>
              <span v-if="i.is_recurred" class="flag-chip fc-rec">재발</span>
              <span v-if="i.tc_linked"   class="flag-chip fc-tc">TC✓</span>
              <span v-else               class="flag-chip fc-notc">TC미전환</span>
            </td>
            <td><button class="icon-btn" @click="openForm(i)">⋯</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="overlay" @click.self="showForm=false">
      <div class="modal">
        <div class="modal-title">{{ editing ? '필드 이슈 수정' : '필드 이슈 등록' }}</div>
        <div class="field"><label>제목 *</label><input v-model="form.title" placeholder="이슈 제목" /></div>
        <div class="field-row">
          <div class="field"><label>출처</label>
            <select v-model="form.source">
              <option value="CS">CS (고객 문의)</option>
              <option value="현장">현장 리포트</option>
              <option value="모니터링">모니터링 알럿</option>
              <option value="내부">내부 발견</option>
            </select>
          </div>
          <div class="field"><label>심각도</label>
            <select v-model="form.severity">
              <option value="critical">Critical</option>
              <option value="major">Major</option>
              <option value="minor">Minor</option>
            </select>
          </div>
        </div>
        <div class="field-row">
          <div class="field"><label>상태</label>
            <select v-model="form.status">
              <option value="open">Open</option>
              <option value="in-progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div class="field"><label>담당자</label><input v-model="form.assignee" placeholder="담당자" /></div>
        </div>
        <div class="field"><label>패턴 / 원인 분석</label><textarea v-model="form.pattern" placeholder="특정 단말기 모델에서만 발생"></textarea></div>
        <div style="display:flex;gap:16px;margin-top:4px;flex-wrap:wrap">
          <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer">
            <input type="checkbox" v-model="form.is_recurred" /> 재발 이슈
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer">
            <input type="checkbox" v-model="form.tc_linked" /> TC 전환 완료
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
  name: 'FieldIssues',
  emits: ['toast'],
  data() {
    return {
      issues: [], showForm: false, editing: null,
      form: { title:'', source:'CS', severity:'minor', status:'open', pattern:'', assignee:'', is_recurred:false, tc_linked:false }
    }
  },
  computed: {
    recurred() { return this.issues.filter(i=>i.is_recurred).length },
    tcLinked() { return this.issues.filter(i=>i.tc_linked).length },
  },
  async mounted() { this.issues = await api.getFieldIssues() },
  methods: {
    byStatus(s) { return this.issues.filter(i=>i.status===s).length },
    sevLabel(s) { return { critical:'Critical', major:'Major', minor:'Minor' }[s] || s },
    statusLabel(s) { return { open:'Open','in-progress':'진행중', resolved:'해결됨', closed:'종료' }[s] || s },
    openForm(i) {
      this.editing = i || null
      this.form = i ? {...i} : { title:'', source:'CS', severity:'minor', status:'open', pattern:'', assignee:'', is_recurred:false, tc_linked:false }
      this.showForm = true
    },
    async save() {
      if (!this.form.title.trim()) { this.$emit('toast',{msg:'제목을 입력하세요',type:'err'}); return }
      try {
        if (this.editing) await api.updateFieldIssue(this.editing.id, this.form)
        else              await api.createFieldIssue(this.form)
        this.showForm=false; this.issues = await api.getFieldIssues()
        this.$emit('toast',{msg:this.editing?'수정되었습니다':'이슈가 등록되었습니다',type:'ok'})
      } catch(e) { this.$emit('toast',{msg:e.message,type:'err'}) }
    },
    async del() {
      if (!confirm('삭제하시겠습니까?')) return
      await api.deleteFieldIssue(this.editing.id); this.showForm=false
      this.issues = await api.getFieldIssues()
      this.$emit('toast',{msg:'삭제되었습니다',type:'info'})
    },
  }
}
</script>

<style scoped>
.source-chip{display:inline-block;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700;background:var(--bg4);color:var(--muted)}
.flag-chip{display:inline-block;padding:1px 5px;border-radius:3px;font-size:10px;font-weight:700;margin-right:2px}
.fc-rec{background:var(--yellow-dim);color:var(--yellow)}
.fc-tc{background:var(--green-dim);color:var(--green)}
.fc-notc{background:var(--bg4);color:var(--muted)}
.row-recurred td{background:rgba(217,119,6,.03)}
</style>