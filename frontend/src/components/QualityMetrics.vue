<template>
  <div>
    <!-- 상단 요약 배너 -->
    <div class="summary-banner">
      <div class="sb-left">
        <div class="sb-version">
          <span class="sb-rocket">▲</span>
          <div>
            <div class="sb-label">최신 릴리즈</div>
            <div class="sb-value mono">{{ latestVersion }}</div>
          </div>
        </div>
      </div>
      <div class="sb-divider"></div>
      <div class="sb-stat">
        <div class="sb-stat-label">평균 통과율</div>
        <div class="sb-stat-row">
          <span class="sb-stat-val" :style="{color: avgPassRate>=90?'var(--green)':'var(--red)'}">{{ avgPassRate }}%</span>
          <span class="sb-delta" :class="passRateDelta>=0?'up':'down'">{{ passRateDelta>=0?'▲':'▼' }}{{ Math.abs(passRateDelta) }}%</span>
        </div>
      </div>
      <div class="sb-stat">
        <div class="sb-stat-label">결함 밀도</div>
        <div class="sb-stat-row">
          <span class="sb-stat-val" style="color:var(--yellow)">{{ avgDensity }}</span>
          <span class="sb-stat-unit">/ TC</span>
        </div>
      </div>
      <div class="sb-stat">
        <div class="sb-stat-label">탈출 결함</div>
        <div class="sb-stat-row">
          <span class="sb-stat-val" style="color:var(--purple)">{{ totalEscaped }}</span>
        </div>
      </div>
      <div class="sb-stat">
        <div class="sb-stat-label">Critical 누적</div>
        <div class="sb-stat-row">
          <span class="sb-stat-val" style="color:var(--red)">{{ totalCritical }}</span>
        </div>
      </div>
    </div>

    <div v-if="metrics.length === 0" class="empty">릴리즈와 TC/결함을 등록하면 지표가 표시돼요</div>

    <template v-else>
      <!-- 차트 영역 -->
      <div class="chart-row">
        <!-- 통과율 추이 (꺾은선) -->
        <div class="chart-card">
          <div class="chart-head">
            <div class="chart-title">릴리즈별 TC 통과율 추이</div>
            <div class="chart-legend">
              <span class="lg"><span class="lg-line lg-pass"></span>통과율</span>
              <span class="lg"><span class="lg-dash"></span>게이트 기준 90%</span>
            </div>
          </div>
          <svg class="line-chart" viewBox="0 0 520 180" preserveAspectRatio="none">
            <!-- 그리드 -->
            <line v-for="y in [0,25,50,75,100]" :key="'g'+y"
              :x1="40" :y1="gridY(y)" :x2="510" :y2="gridY(y)" class="grid-line" />
            <text v-for="y in [0,50,100]" :key="'t'+y"
              :x="32" :y="gridY(y)+4" class="axis-text" text-anchor="end">{{ y }}</text>
            <!-- 90% 기준선 -->
            <line :x1="40" :y1="gridY(90)" :x2="510" :y2="gridY(90)" class="threshold-line" />
            <!-- 통과율 폴리라인 -->
            <polyline :points="passLinePoints" class="pass-line" />
            <circle v-for="(m,i) in chartData" :key="'c'+i"
              :cx="chartX(i)" :cy="gridY(m.pass_rate)" r="3.5" class="pass-dot" />
            <!-- x축 라벨 -->
            <text v-for="(m,i) in chartData" :key="'x'+i"
              :x="chartX(i)" :y="172" class="axis-text" text-anchor="middle">{{ shortVer(m.version) }}</text>
          </svg>
        </div>

        <!-- 결함 분포 (막대) -->
        <div class="chart-card">
          <div class="chart-head">
            <div class="chart-title">릴리즈별 결함 분포</div>
            <div class="chart-legend">
              <span class="lg"><span class="lg-box" style="background:var(--red)"></span>Critical</span>
              <span class="lg"><span class="lg-box" style="background:var(--yellow)"></span>Major</span>
            </div>
          </div>
          <svg class="bar-chart" viewBox="0 0 520 180" preserveAspectRatio="none">
            <line v-for="y in [0,25,50,75,100]" :key="'bg'+y"
              :x1="40" :y1="gridY(y)" :x2="510" :y2="gridY(y)" class="grid-line" />
            <text v-for="y in [0,maxDefect]" :key="'bt'+y"
              :x="32" :y="gridYD(y)+4" class="axis-text" text-anchor="end">{{ y }}</text>
            <g v-for="(m,i) in chartData" :key="'bar'+i">
              <rect :x="barX(i)" :y="gridYD(m.critical)" :width="barW" :height="barH(m.critical)" class="bar-crit" />
              <rect :x="barX(i)" :y="gridYD(m.critical+m.major)" :width="barW" :height="barH(m.major)" class="bar-major" />
            </g>
            <text v-for="(m,i) in chartData" :key="'bx'+i"
              :x="barX(i)+barW/2" :y="172" class="axis-text" text-anchor="middle">{{ shortVer(m.version) }}</text>
          </svg>
        </div>
      </div>

      <!-- 상세 테이블 -->
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>릴리즈</th>
              <th style="width:70px">플랫폼</th>
              <th style="width:80px">전체 TC</th>
              <th style="width:120px">통과율</th>
              <th style="width:70px">결함</th>
              <th style="width:80px">밀도</th>
              <th style="width:70px">Critical</th>
              <th style="width:70px">탈출</th>
              <th style="width:90px">등록일</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in metrics" :key="m.version">
              <td class="mono" style="font-weight:600">{{ m.version }}</td>
              <td style="font-size:12px;color:var(--muted)">{{ m.platform }}</td>
              <td class="mono" style="text-align:center">{{ m.total_tc }}</td>
              <td>
                <div class="rate-cell">
                  <div class="rate-bar"><div class="rate-fill" :class="m.pass_rate>=90?'rf-good':'rf-bad'" :style="{width:m.pass_rate+'%'}"></div></div>
                  <span class="rate-num mono" :style="{color: m.pass_rate>=90?'var(--green)':'var(--red)'}">{{ m.pass_rate }}%</span>
                </div>
              </td>
              <td class="mono" style="text-align:center">{{ m.total_defects }}</td>
              <td class="mono" style="text-align:center;color:var(--muted)">{{ m.defect_density }}</td>
              <td style="text-align:center">
                <span v-if="m.critical>0" class="chip chip-critical">{{ m.critical }}</span>
                <span v-else class="mono" style="color:var(--green)">0</span>
              </td>
              <td style="text-align:center">
                <span v-if="m.escaped>0" class="chip" style="background:var(--purple-dim);color:var(--purple)">{{ m.escaped }}</span>
                <span v-else class="mono" style="color:var(--green)">0</span>
              </td>
              <td class="mono" style="font-size:11px;color:var(--muted)">{{ shortDate(m.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script>
import { api } from '../api/index.js'

export default {
  name: 'QualityMetrics',
  data() {
    return { metrics: [] }
  },
  computed: {
    chartData() {
      // 오래된 → 최신 순으로 (차트는 왼→오 시간순)
      return [...this.metrics].reverse().slice(-8)
    },
    latestVersion() { return this.metrics.length ? this.metrics[0].version : '-' },
    avgPassRate() {
      if (!this.metrics.length) return 0
      return Math.round(this.metrics.reduce((s,m)=>s+m.pass_rate,0)/this.metrics.length)
    },
    passRateDelta() {
      if (this.metrics.length < 2) return 0
      return this.metrics[0].pass_rate - this.metrics[1].pass_rate
    },
    avgDensity() {
      if (!this.metrics.length) return 0
      return (this.metrics.reduce((s,m)=>s+m.defect_density,0)/this.metrics.length).toFixed(2)
    },
    totalEscaped()  { return this.metrics.reduce((s,m)=>s+m.escaped,0) },
    totalCritical() { return this.metrics.reduce((s,m)=>s+m.critical,0) },
    maxDefect() {
      const max = Math.max(...this.chartData.map(m=>m.critical+m.major), 1)
      return Math.ceil(max)
    },
    passLinePoints() {
      return this.chartData.map((m,i)=>`${this.chartX(i)},${this.gridY(m.pass_rate)}`).join(' ')
    },
    barW() {
      const n = this.chartData.length || 1
      return Math.min(36, (470/n) * 0.5)
    },
  },
  async mounted() {
    try { this.metrics = await api.getMetrics() } catch(e) { this.metrics = [] }
  },
  methods: {
    gridY(pct) { return 150 - (pct/100)*130 },          // 통과율(0~100) → y
    gridYD(v)  { return 150 - (v/this.maxDefect)*130 },  // 결함수 → y
    chartX(i) {
      const n = this.chartData.length
      if (n === 1) return 275
      return 50 + (i/(n-1))*450
    },
    barX(i) {
      const n = this.chartData.length || 1
      const slot = 470/n
      return 45 + i*slot + (slot - this.barW)/2
    },
    barH(v) { return (v/this.maxDefect)*130 },
    shortVer(v) { return String(v).replace(/^v/,'').slice(0,6) },
    shortDate(d){ return d ? String(d).slice(0,10) : '' },
  }
}
</script>

<style scoped>
/* 요약 배너 */
.summary-banner {
  display: flex; align-items: center; gap: 0;
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px 20px; margin-bottom: 20px;
  flex-wrap: wrap;
}
.sb-left { padding-right: 24px; }
.sb-version { display: flex; align-items: center; gap: 12px; }
.sb-rocket { font-size: 18px; color: var(--primary); }
.sb-label { font-size: 11px; color: var(--muted); margin-bottom: 2px; }
.sb-value { font-size: 16px; font-weight: 700; }
.sb-divider { width: 1px; height: 40px; background: var(--border2); margin-right: 24px; }
.sb-stat { padding: 0 24px; border-left: 1px solid var(--border); }
.sb-stat:first-of-type { border-left: none; }
.sb-stat-label { font-size: 11px; color: var(--muted); margin-bottom: 4px; }
.sb-stat-row { display: flex; align-items: baseline; gap: 6px; }
.sb-stat-val { font-size: 22px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.sb-stat-unit { font-size: 11px; color: var(--muted); }
.sb-delta { font-size: 11px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.sb-delta.up { color: var(--green); }
.sb-delta.down { color: var(--red); }

/* 차트 */
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px; }
.chart-card { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 18px; }
.chart-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.chart-title { font-size: 13px; font-weight: 600; }
.chart-legend { display: flex; gap: 12px; }
.lg { display: flex; align-items: center; gap: 4px; font-size: 11px; color: var(--muted); }
.lg-line { width: 14px; height: 2px; border-radius: 1px; }
.lg-pass { background: var(--primary); }
.lg-dash { width: 14px; height: 0; border-top: 1.5px dashed var(--yellow); }
.lg-box { width: 10px; height: 10px; border-radius: 2px; }

.line-chart, .bar-chart { width: 100%; height: 180px; }
.grid-line { stroke: var(--border); stroke-width: 1; }
.threshold-line { stroke: var(--yellow); stroke-width: 1.5; stroke-dasharray: 4 3; opacity: .7; }
.axis-text { fill: var(--muted); font-size: 9px; font-family: 'JetBrains Mono', monospace; }
.pass-line { fill: none; stroke: var(--primary); stroke-width: 2; }
.pass-dot { fill: var(--bg2); stroke: var(--primary); stroke-width: 2; }
.bar-crit { fill: var(--red); }
.bar-major { fill: var(--yellow); }

/* 통과율 셀 */
.rate-cell { display: flex; align-items: center; gap: 8px; }
.rate-bar { flex: 1; height: 5px; background: var(--bg4); border-radius: 3px; overflow: hidden; }
.rate-fill { height: 100%; }
.rf-good { background: var(--green); }
.rf-bad { background: var(--red); }
.rate-num { font-size: 12px; min-width: 38px; text-align: right; }

@media (max-width: 900px) {
  .chart-row { grid-template-columns: 1fr; }
}
</style>