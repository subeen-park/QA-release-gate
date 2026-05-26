const BASE = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

async function http(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const e = await res.json().catch(() => ({}))
    throw new Error(e.error || res.statusText)
  }
  return res.json()
}

export const api = {
  getReleases:      ()       => http('GET',    '/releases'),
  createRelease:    (d)      => http('POST',   '/releases', d),
  updateRelease:    (id, d)  => http('PUT',    `/releases/${id}`, d),
  deleteRelease:    (id)     => http('DELETE', `/releases/${id}`),
  getTestCases:     (rid)    => http('GET',    `/releases/${rid}/testcases`),
  createTestCase:   (rid, d) => http('POST',   `/releases/${rid}/testcases`, d),
  updateTestCase:   (tid, d) => http('PUT',    `/testcases/${tid}`, d),
  deleteTestCase:   (tid)    => http('DELETE', `/testcases/${tid}`),
  getDefects:       (rid)    => http('GET',    `/defects${rid ? '?release_id=' + rid : ''}`),
  createDefect:     (d)      => http('POST',   '/defects', d),
  updateDefect:     (id, d)  => http('PUT',    `/defects/${id}`, d),
  deleteDefect:     (id)     => http('DELETE', `/defects/${id}`),
  getFieldIssues:   ()       => http('GET',    '/field-issues'),
  createFieldIssue: (d)      => http('POST',   '/field-issues', d),
  updateFieldIssue: (id, d)  => http('PUT',    `/field-issues/${id}`, d),
  deleteFieldIssue: (id)     => http('DELETE', `/field-issues/${id}`),
  getMetrics:       ()       => http('GET',    '/metrics'),
}