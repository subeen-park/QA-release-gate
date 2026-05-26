<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">테스트 케이스</div>
        <div class="page-sub">스모크 · 회귀 · 통합 테스트 관리 및 커버리지 추적</div>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <select v-model="selectedRelease" class="filter-sel">
          <option value="">릴리즈 선택...</option>
          <option v-for="r in releases" :key="r.id" :value="r.id">{{ r.version }}</option>
        </select>
        <select v-model="filterCat" class="filter-sel">
          <option value="">전체 유형</option>
          <option value="smoke">Smoke</option>
          <option value="regression">Regression</option>
          <option value="integration">Integration</option>
        </select>
        <button class="btn btn-primary" :disabled="!selectedRelease" @click="openForm()">+ TC 추가</button>
      </div>
    </div>

    <!-- 커버리지 메트릭 -->
    <div v-if="selectedRelease" class="metrics-grid">
      <div class="metric-card">
        <div class="metric-label">전체 TC</div>
        <div class="metric-val">{{ tcs.length }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Pass</div>
        <div class="metric-val" style="color:var(--green)">{{ byStatus('pass') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Fail</div>
        <div class="metric-val" style="color:var(--red)">{{ byStatus('fail') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Blocked</div>
        <div class="metric-val" style="color:var(--purple)">{{ byStatus('blocked') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">미실행</div>
        <div class="metric-val" style="color:var(--muted)">{{ byStatus('untested') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">통과율</div>
        <div class="metric-val" :style="{color: passRate >= 90 ? 'var(--green)' : 'var(--red)'}">{{ passRate }}%</div>
        <div class="metric-sub">게이트 기준 90%</div>
      </div>
    </div>

    <!-- 커버리지 바 -->
    <div v-if="selectedRelease && tcs.length > 0" class="coverage-bar-wrap">
      <div class="cov-bar">
        <div class="cov-seg cov-pass"  :style="{width: pct('pass')+'%'}"></div>
        <div class="cov-seg cov-fail"  :style="{width: pct('fail')+'%'}"></div>
        <div class="cov-seg cov-block" :style="{width: pct('blocked')+'%'}"></div>
        <div class="cov-seg cov-unt"   :style="{width: pct('untested')+'%'}"></div>
      </div>
      <div class="cov-legend">
        <span class="leg-item"><span class="leg-dot leg-pass"></span>Pass</span>
        <span class="leg-item"><span class="leg-dot leg-fail"></span>Fail</span>
        <span class="leg-item"><span class="leg-dot leg-block"></span>Blocked</span>
        <span class="leg-item"><span class="leg-dot leg-unt"></span>미실행</span>
      </div>
    </div>

    <div v-if="!selectedRelease" class="empty">릴리즈를 선택하면 TC 목록이 표시돼요</div>
    <div v-else class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th style="width:90px">유형</th>
            <th style="width:70px">우선순위</th>
            <th>제목</th>
            <th style="width:90px">담당자</th>
            <th style="width:100px">상태</th>
            <th style="width:40px"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filtered.length === 0">
            <td colspan="6" class="empty">등록된 TC가 없어요</td>
          </tr>
          <tr v-for="t in filtered" :key="t.id">
            <td><span class="chip" :class="'chip-'+t.category">{{ t.category }}</span></td>
            <td><span class="prio-chip" :class="'prio-'+t.priority">{{ t.priority }}</span></td>
            <td style="font-size:13px;font-weight:500">{{ t.title }}</td>
            <td style="font-size:12px;color:var(--muted)">{{ t.assignee || '-' }}</td>
            <td>
              <select class="status-sel" :value="t.status" @change="quickStatus(t, $event.target.value)">
                <option value="untested">미실행</option>
                <option value="pass">Pass</option>
                <option value="fail">Fail</option>
                <option value="blocked">Blocked</option>
              </select>
            </td>
            <td><button class="icon-btn" @click="openForm(t)">⋯</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 모달 -->
    <div v-if="showForm" class="overlay" @click.self="showForm=false">
      <div class="modal">
        <div class="modal-title">{{ editing ? 'TC 수정' : 'TC 추가' }}</div>
        <div class="field">
          <label>제목 *</label>
          <input v-model="form.title" placeholder="테스트 케이스 제목" />
        </div>
        <div class="field-row">
          <div class="field">
            <label>유형</label>
            <select v-model="form.category">
              <option value="smoke">Smoke</option>
              <option value="regression">Regression</option>
              <option value="integration">Integration</option>
            </select>
          </div>
          <div class="field">
            <label>우선순위</label>
            <select v-model="form.priority">
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
        <div class="field-row">
          <div class="field">
            <label>담당자</label>
            <input v-model="form.assignee" placeholder="담당자" />
          </div>
          <div class="field">
            <label>상태</label>
            <select v-model="form.status">
              <option value="untested">미실행</option>
              <option value="pass">Pass</option>
              <option value="fail">Fail</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
        </div>
        <div class="field">
          <label>테스트 절차</label>
          <textarea v-model="form.steps" placeholder="절차를 입력하세요" rows="3"></textarea>
        </div>
        <div class="field">
          <label>예상 결과</label>
          <textarea v-model="form.expected" placeholder="예상 결과를 입력하세요" rows="2"></textarea>
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
  name: 'TestCases',
  props: {
    releases: { type: Array, default: () => [] }
  },
  emits: ['toast'],
  data() {
    return {
      tcs: [],
      selectedRelease: '',
      filterCat: '',
      showForm: false,
      editing: null,
      form: {
        title: '',
        category: 'smoke',
        priority: 'medium',
        assignee: '',
        status: 'untested',
        steps: '',
        expected: ''
      }
    }
  },
  computed: {
    filtered() {
      if (!this.filterCat) return this.tcs
      return this.tcs.filter(function(t) { return t.category === this.filterCat }.bind(this))
    },
    passRate() {
      if (this.tcs.length === 0) return 0
      return Math.round(this.byStatus('pass') / this.tcs.length * 100)
    }
  },
  watch: {
    selectedRelease: function(val) {
      if (val) {
        this.load()
      } else {
        this.tcs = []
      }
    }
  },
  methods: {
    async load() {
      try {
        this.tcs = await api.getTestCases(this.selectedRelease)
      } catch(e) {
        this.tcs = []
      }
    },
    byStatus(s) {
      return this.tcs.filter(function(t) { return t.status === s }).length
    },
    pct(s) {
      if (this.tcs.length === 0) return 0
      return Math.round(this.byStatus(s) / this.tcs.length * 100)
    },
    openForm(t) {
      this.editing = t || null
      if (t) {
        this.form = Object.assign({}, t)
      } else {
        this.form = { title: '', category: 'smoke', priority: 'medium', assignee: '', status: 'untested', steps: '', expected: '' }
      }
      this.showForm = true
    },
    async quickStatus(t, status) {
      try {
        await api.updateTestCase(t.id, Object.assign({}, t, { status: status }))
        await this.load()
      } catch(e) {
        this.$emit('toast', { msg: '상태 변경 실패', type: 'err' })
      }
    },
    async save() {
      if (!this.form.title.trim()) {
        this.$emit('toast', { msg: '제목을 입력하세요', type: 'err' })
        return
      }
      try {
        if (this.editing) {
          await api.updateTestCase(this.editing.id, this.form)
        } else {
          await api.createTestCase(this.selectedRelease, this.form)
        }
        this.showForm = false
        await this.load()
        this.$emit('toast', { msg: this.editing ? '수정되었습니다' : 'TC가 추가되었습니다', type: 'ok' })
      } catch(e) {
        this.$emit('toast', { msg: e.message, type: 'err' })
      }
    },
    async del() {
      if (!confirm('삭제하시겠습니까?')) return
      try {
        await api.deleteTestCase(this.editing.id)
        this.showForm = false
        await this.load()
        this.$emit('toast', { msg: '삭제되었습니다', type: 'info' })
      } catch(e) {
        this.$emit('toast', { msg: e.message, type: 'err' })
      }
    }
  }
}
</script>

<style scoped>
.filter-sel, .status-sel {
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: 7px;
  padding: 5px 8px;
  color: var(--text);
  font-size: 12px;
  outline: none;
  cursor: pointer;
}
.prio-chip { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.prio-high   { background: var(--red-dim);    color: var(--red); }
.prio-medium { background: var(--yellow-dim); color: var(--yellow); }
.prio-low    { background: var(--bg4);        color: var(--muted); }
.coverage-bar-wrap { margin-bottom: 16px; }
.cov-bar { height: 10px; background: var(--bg4); border-radius: 5px; overflow: hidden; display: flex; margin-bottom: 8px; }
.cov-seg { height: 100%; transition: width .4s; }
.cov-pass  { background: var(--green); }
.cov-fail  { background: var(--red); }
.cov-block { background: var(--purple); }
.cov-unt   { background: var(--bg4); }
.cov-legend { display: flex; gap: 14px; font-size: 11px; color: var(--muted); }
.leg-item { display: flex; align-items: center; gap: 4px; }
.leg-dot { width: 8px; height: 8px; border-radius: 50%; }
.leg-pass  { background: var(--green); }
.leg-fail  { background: var(--red); }
.leg-block { background: var(--purple); }
.leg-unt   { background: var(--bg4); }
</style>