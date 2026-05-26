from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os, uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_conn():
    url = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def uid():
    return str(uuid.uuid4())[:8]

# ── DB 초기화 ──────────────────────────────────────────────
def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS releases (
                    id          TEXT PRIMARY KEY,
                    version     TEXT NOT NULL,
                    platform    TEXT DEFAULT 'Android',
                    status      TEXT DEFAULT 'testing',
                    gate_status TEXT DEFAULT 'pending',
                    description TEXT DEFAULT '',
                    created_at  TEXT DEFAULT '',
                    updated_at  TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS test_cases (
                    id          TEXT PRIMARY KEY,
                    release_id  TEXT REFERENCES releases(id) ON DELETE CASCADE,
                    category    TEXT DEFAULT 'smoke',
                    title       TEXT NOT NULL,
                    steps       TEXT DEFAULT '',
                    expected    TEXT DEFAULT '',
                    status      TEXT DEFAULT 'untested',
                    assignee    TEXT DEFAULT '',
                    priority    TEXT DEFAULT 'medium',
                    created_at  TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS defects (
                    id          TEXT PRIMARY KEY,
                    release_id  TEXT REFERENCES releases(id) ON DELETE SET NULL,
                    title       TEXT NOT NULL,
                    severity    TEXT DEFAULT 'minor',
                    status      TEXT DEFAULT 'open',
                    assignee    TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    steps       TEXT DEFAULT '',
                    is_escaped  BOOLEAN DEFAULT FALSE,
                    is_recurred BOOLEAN DEFAULT FALSE,
                    jira        TEXT DEFAULT '',
                    created_at  TEXT DEFAULT '',
                    resolved_at TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS field_issues (
                    id          TEXT PRIMARY KEY,
                    title       TEXT NOT NULL,
                    source      TEXT DEFAULT 'CS',
                    severity    TEXT DEFAULT 'minor',
                    status      TEXT DEFAULT 'open',
                    pattern     TEXT DEFAULT '',
                    assignee    TEXT DEFAULT '',
                    is_recurred BOOLEAN DEFAULT FALSE,
                    tc_linked   BOOLEAN DEFAULT FALSE,
                    tc_id       TEXT DEFAULT '',
                    created_at  TEXT DEFAULT ''
                );
            """)
        conn.commit()

# ── Health ─────────────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify({'ok': True})

# ── Releases ───────────────────────────────────────────────
@app.route('/api/releases', methods=['GET'])
def get_releases():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.*,
                  (SELECT COUNT(*) FROM test_cases t WHERE t.release_id=r.id) as total_tc,
                  (SELECT COUNT(*) FROM test_cases t WHERE t.release_id=r.id AND t.status='pass') as pass_tc,
                  (SELECT COUNT(*) FROM test_cases t WHERE t.release_id=r.id AND t.status='fail') as fail_tc,
                  (SELECT COUNT(*) FROM defects d WHERE d.release_id=r.id AND d.status!='closed') as open_defects,
                  (SELECT COUNT(*) FROM defects d WHERE d.release_id=r.id AND d.severity='critical' AND d.status!='closed') as critical_defects
                FROM releases r ORDER BY r.created_at DESC
            """)
            return jsonify([dict(r) for r in cur.fetchall()])

@app.route('/api/releases', methods=['POST'])
def create_release():
    d = request.json
    rid = uid()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO releases (id,version,platform,status,gate_status,description,created_at,updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (rid, d['version'], d.get('platform','Android'), d.get('status','testing'),
                 'pending', d.get('description',''), now(), now())
            )
        conn.commit()
    return jsonify({'id': rid})

@app.route('/api/releases/<rid>', methods=['PUT'])
def update_release(rid):
    d = request.json
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE releases SET version=%s,platform=%s,status=%s,gate_status=%s,description=%s,updated_at=%s WHERE id=%s",
                (d['version'], d.get('platform','Android'), d.get('status','testing'),
                 d.get('gate_status','pending'), d.get('description',''), now(), rid)
            )
        conn.commit()
    return jsonify({'ok': True})

@app.route('/api/releases/<rid>', methods=['DELETE'])
def delete_release(rid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM releases WHERE id=%s", (rid,))
        conn.commit()
    return jsonify({'ok': True})

# ── Test Cases ─────────────────────────────────────────────
@app.route('/api/releases/<rid>/testcases', methods=['GET'])
def get_testcases(rid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM test_cases WHERE release_id=%s ORDER BY category, priority DESC, created_at", (rid,))
            return jsonify([dict(r) for r in cur.fetchall()])

@app.route('/api/releases/<rid>/testcases', methods=['POST'])
def create_testcase(rid):
    d = request.json
    tid = uid()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO test_cases (id,release_id,category,title,steps,expected,status,assignee,priority,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (tid, rid, d.get('category','smoke'), d['title'], d.get('steps',''),
                 d.get('expected',''), d.get('status','untested'), d.get('assignee',''),
                 d.get('priority','medium'), now())
            )
        conn.commit()
    return jsonify({'id': tid})

@app.route('/api/testcases/<tid>', methods=['PUT'])
def update_testcase(tid):
    d = request.json
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE test_cases SET category=%s,title=%s,steps=%s,expected=%s,status=%s,assignee=%s,priority=%s WHERE id=%s",
                (d.get('category','smoke'), d['title'], d.get('steps',''), d.get('expected',''),
                 d.get('status','untested'), d.get('assignee',''), d.get('priority','medium'), tid)
            )
        conn.commit()
    return jsonify({'ok': True})

@app.route('/api/testcases/<tid>', methods=['DELETE'])
def delete_testcase(tid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM test_cases WHERE id=%s", (tid,))
        conn.commit()
    return jsonify({'ok': True})

# ── Defects ────────────────────────────────────────────────
@app.route('/api/defects', methods=['GET'])
def get_defects():
    release_id = request.args.get('release_id')
    with get_conn() as conn:
        with conn.cursor() as cur:
            if release_id:
                cur.execute("SELECT * FROM defects WHERE release_id=%s ORDER BY created_at DESC", (release_id,))
            else:
                cur.execute("SELECT * FROM defects ORDER BY created_at DESC")
            return jsonify([dict(r) for r in cur.fetchall()])

@app.route('/api/defects', methods=['POST'])
def create_defect():
    d = request.json
    did = uid()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO defects (id,release_id,title,severity,status,assignee,description,steps,is_escaped,is_recurred,jira,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (did, d.get('release_id'), d['title'], d.get('severity','minor'),
                 d.get('status','open'), d.get('assignee',''), d.get('description',''),
                 d.get('steps',''), d.get('is_escaped',False), d.get('is_recurred',False),
                 d.get('jira',''), now())
            )
        conn.commit()
    return jsonify({'id': did})

@app.route('/api/defects/<did>', methods=['PUT'])
def update_defect(did):
    d = request.json
    resolved = now() if d.get('status') == 'closed' else ''
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE defects SET release_id=%s,title=%s,severity=%s,status=%s,assignee=%s,description=%s,steps=%s,is_escaped=%s,is_recurred=%s,jira=%s,resolved_at=%s WHERE id=%s",
                (d.get('release_id'), d['title'], d.get('severity','minor'), d.get('status','open'),
                 d.get('assignee',''), d.get('description',''), d.get('steps',''),
                 d.get('is_escaped',False), d.get('is_recurred',False), d.get('jira',''), resolved, did)
            )
        conn.commit()
    return jsonify({'ok': True})

@app.route('/api/defects/<did>', methods=['DELETE'])
def delete_defect(did):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM defects WHERE id=%s", (did,))
        conn.commit()
    return jsonify({'ok': True})

# ── Field Issues ───────────────────────────────────────────
@app.route('/api/field-issues', methods=['GET'])
def get_field_issues():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM field_issues ORDER BY created_at DESC")
            return jsonify([dict(r) for r in cur.fetchall()])

@app.route('/api/field-issues', methods=['POST'])
def create_field_issue():
    d = request.json
    fid = uid()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO field_issues (id,title,source,severity,status,pattern,assignee,is_recurred,tc_linked,tc_id,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (fid, d['title'], d.get('source','CS'), d.get('severity','minor'),
                 d.get('status','open'), d.get('pattern',''), d.get('assignee',''),
                 d.get('is_recurred',False), d.get('tc_linked',False), d.get('tc_id',''), now())
            )
        conn.commit()
    return jsonify({'id': fid})

@app.route('/api/field-issues/<fid>', methods=['PUT'])
def update_field_issue(fid):
    d = request.json
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE field_issues SET title=%s,source=%s,severity=%s,status=%s,pattern=%s,assignee=%s,is_recurred=%s,tc_linked=%s,tc_id=%s WHERE id=%s",
                (d['title'], d.get('source','CS'), d.get('severity','minor'), d.get('status','open'),
                 d.get('pattern',''), d.get('assignee',''), d.get('is_recurred',False),
                 d.get('tc_linked',False), d.get('tc_id',''), fid)
            )
        conn.commit()
    return jsonify({'ok': True})

@app.route('/api/field-issues/<fid>', methods=['DELETE'])
def delete_field_issue(fid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM field_issues WHERE id=%s", (fid,))
        conn.commit()
    return jsonify({'ok': True})

# ── 품질 지표 ──────────────────────────────────────────────
@app.route('/api/metrics')
def get_metrics():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.version, r.platform, r.created_at,
                  COUNT(DISTINCT t.id) as total_tc,
                  COUNT(DISTINCT CASE WHEN t.status='pass' THEN t.id END) as pass_tc,
                  COUNT(DISTINCT CASE WHEN t.status='fail' THEN t.id END) as fail_tc,
                  COUNT(DISTINCT d.id) as total_defects,
                  COUNT(DISTINCT CASE WHEN d.severity='critical' THEN d.id END) as critical,
                  COUNT(DISTINCT CASE WHEN d.severity='major' THEN d.id END) as major,
                  COUNT(DISTINCT CASE WHEN d.is_escaped=TRUE THEN d.id END) as escaped
                FROM releases r
                LEFT JOIN test_cases t ON t.release_id=r.id
                LEFT JOIN defects d ON d.release_id=r.id
                GROUP BY r.id, r.version, r.platform, r.created_at
                ORDER BY r.created_at DESC LIMIT 10
            """)
            rows = [dict(r) for r in cur.fetchall()]
            for row in rows:
                total = row['total_tc'] or 0
                passed = row['pass_tc'] or 0
                row['pass_rate'] = round(passed / total * 100) if total > 0 else 0
                row['defect_density'] = round(row['total_defects'] / total, 2) if total > 0 else 0
            return jsonify(rows)

try:
    init_db()
    print("DB 초기화 완료")
except Exception as e:
    print(f"DB 초기화 실패: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)