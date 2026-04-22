from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
import pandas as pd
import datetime, decimal, traceback

app = Flask(__name__)
CORS(app)

DB_HOST     = 'localhost'
DB_USER     = 'root'
DB_PASSWORD = '*****'   # ← change this if needed
DB_NAME     = '*****'

# ─── DB ───────────────────────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, use_pure=True)

# ─── TYPE SAFETY ──────────────────────────────────────────────────────────────
def _s(v):
    """Convert any MySQL type to a plain Python JSON-safe scalar."""
    if v is None:                          return 0
    if isinstance(v, bool):                return v
    if isinstance(v, decimal.Decimal):
        f = float(v)
        return int(f) if f == int(f) else round(f, 4)
    if isinstance(v, datetime.datetime):   return v.strftime('%Y-%m-%dT%H:%M:%S')
    if isinstance(v, datetime.date):       return v.strftime('%Y-%m-%d')
    if isinstance(v, (bytes, bytearray)):  return v.decode('utf-8', errors='replace')
    return v

def clean(rows):
    """Apply _s() to every value in every row dict."""
    return [{k: _s(v) for k, v in row.items()} for row in (rows or [])]

def safe_json(obj):
    """Recursively make any object JSON-safe (for nested structures)."""
    if isinstance(obj, list):   return [safe_json(i) for i in obj]
    if isinstance(obj, dict):   return {k: safe_json(v) for k, v in obj.items()}
    return _s(obj)

# ─── ERROR WRAPPER ─────────────────────────────────────────────────────────────
def api(fn):
    """Decorator: catch any exception and return it as JSON so the UI shows the real error."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        try:
            return fn(*a, **kw)
        except Exception:
            tb = traceback.format_exc()
            print(tb)
            return jsonify({'error': tb.strip().splitlines()[-1]}), 500
    return wrapper

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def prev_kpi(cur, where_sql, params):
    """Compute KPI summary for a previous period. Returns plain-Python dict or {}."""
    cur.execute(f"""
        SELECT
            CAST(COUNT(*)                        AS UNSIGNED) AS tot,
            CAST(SUM(tat_status='Pass')          AS UNSIGNED) AS pc,
            CAST(SUM(tat_status='Fail')          AS UNSIGNED) AS fc,
            CAST(COUNT(DISTINCT req_number)      AS UNSIGNED) AS uniq
        FROM tat_data WHERE {where_sql}
    """, params)
    row = cur.fetchone() or {}
    tot  = int(_s(row.get('tot'))  or 0)
    pc   = int(_s(row.get('pc'))   or 0)
    fc   = int(_s(row.get('fc'))   or 0)
    uniq = int(_s(row.get('uniq')) or 0)
    if not tot:
        return {}
    return {
        'tot':  tot,
        'uniq': uniq,
        'pr':   round(pc / tot * 100, 1),
        'fr':   round(fc / tot * 100, 1),
    }

# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/weeks')
@api
def get_weeks():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT week_id,
               DATE_FORMAT(MIN(entry_datetime), '%d %b')     AS period_start,
               DATE_FORMAT(MAX(entry_datetime), '%d %b %Y')  AS period_end,
               CAST(COUNT(*) AS UNSIGNED)                     AS total_tests
        FROM tat_data
        GROUP BY week_id
        ORDER BY week_id DESC
    """)
    rows = clean(cur.fetchall())
    cur.close(); conn.close()
    return jsonify(rows)


@app.route('/api/months')
@api
def get_months():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT DATE_FORMAT(entry_datetime, '%Y-%m')        AS month_id,
               DATE_FORMAT(MIN(entry_datetime), '%b %Y')   AS month_label,
               CAST(COUNT(*) AS UNSIGNED)                  AS total_tests,
               CAST(COUNT(DISTINCT week_id) AS UNSIGNED)   AS num_weeks
        FROM tat_data
        GROUP BY DATE_FORMAT(entry_datetime, '%Y-%m')
        ORDER BY month_id DESC
    """)
    rows = clean(cur.fetchall())
    cur.close(); conn.close()
    return jsonify(rows)


@app.route('/api/week-data')
@api
def get_week_data():
    week_id = request.args.get('week_id', '').strip()
    if not week_id:
        return jsonify({'error': 'week_id required'}), 400

    conn = get_db(); cur = conn.cursor(dictionary=True)

    # Site × Department aggregates (drives all charts)
    cur.execute("""
        SELECT site_name    AS `Site Names`,
               department   AS Department,
               CAST(COUNT(*)                   AS UNSIGNED) AS total,
               CAST(COUNT(DISTINCT req_number) AS UNSIGNED) AS unique_reqs,
               CAST(SUM(tat_status='Pass')     AS UNSIGNED) AS pass_c,
               CAST(SUM(tat_status='Fail')     AS UNSIGNED) AS fail_c,
               ROUND(AVG(tat_minutes), 1)                   AS avg_tat
        FROM tat_data
        WHERE week_id = %s
        GROUP BY site_name, department
    """, (week_id,))
    site_dept = clean(cur.fetchall())

    # Daily data — per site, per department, per day (enables dept-aware daily chart)
    cur.execute("""
        SELECT site_name    AS `Site Names`,
               department   AS Department,
               DATE(entry_datetime)                             AS day_date,
               DATE_FORMAT(MIN(entry_datetime), '%a %b %d')  AS DayLabel,
               CAST(SUM(tat_status='Pass') AS UNSIGNED)         AS pass_c,
               CAST(SUM(tat_status='Fail') AS UNSIGNED)         AS fail_c,
               CAST(COUNT(*)               AS UNSIGNED)         AS total,
               ROUND(AVG(tat_minutes), 1)                       AS avg_tat
        FROM tat_data
        WHERE week_id = %s
        GROUP BY site_name, department, DATE(entry_datetime)
        ORDER BY DATE(entry_datetime)
    """, (week_id,))
    site_day = clean(cur.fetchall())

    # Unique patients per site
    cur.execute("""
        SELECT site_name,
               CAST(COUNT(DISTINCT req_number) AS UNSIGNED) AS unique_reqs
        FROM tat_data
        WHERE week_id = %s
        GROUP BY site_name
    """, (week_id,))
    site_unique = {r['site_name']: int(_s(r['unique_reqs'])) for r in clean(cur.fetchall())}

    # Day ordering list
    cur.execute("""
        SELECT DATE(entry_datetime)                             AS day_date,
               DATE_FORMAT(MIN(entry_datetime), '%a %b %d')  AS day_label
        FROM tat_data
        WHERE week_id = %s
        GROUP BY DATE(entry_datetime)
        ORDER BY DATE(entry_datetime)
    """, (week_id,))
    day_order = [{'date': r['day_date'], 'label': r['day_label']}
                 for r in clean(cur.fetchall()) if r.get('day_date')]

    # Week range label
    cur.execute("""
        SELECT DATE_FORMAT(MIN(entry_datetime), '%a %d %b')      AS wstart,
               DATE_FORMAT(MAX(entry_datetime), '%a %d %b %Y')  AS wend
        FROM tat_data WHERE week_id = %s
    """, (week_id,))
    wr = cur.fetchone() or {}
    week_range = f"{wr.get('wstart','')} \u2013 {wr.get('wend','')}" if wr.get('wstart') else ''

    # Previous week KPIs (for delta arrows)
    cur.execute("SELECT MAX(week_id) AS prev FROM tat_data WHERE week_id < %s", (week_id,))
    pr = cur.fetchone()
    pstats = prev_kpi(cur, 'week_id = %s', (pr['prev'],)) if (pr and pr.get('prev')) else {}

    cur.close(); conn.close()
    return jsonify({
        'site_dept':   site_dept,
        'site_day':    site_day,
        'site_unique': site_unique,
        'day_order':   day_order,
        'week_range':  week_range,
        'prev_stats':  pstats,
    })


@app.route('/api/all-months-data')
@api
def get_all_months_data():
    """All-time aggregate for the Monthly 'All Months' option — no day queries (fast)."""
    conn = get_db(); cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT site_name    AS `Site Names`,
               department   AS Department,
               CAST(COUNT(*)                   AS UNSIGNED) AS total,
               CAST(COUNT(DISTINCT req_number) AS UNSIGNED) AS unique_reqs,
               CAST(SUM(tat_status='Pass')     AS UNSIGNED) AS pass_c,
               CAST(SUM(tat_status='Fail')     AS UNSIGNED) AS fail_c,
               ROUND(AVG(tat_minutes), 1)                   AS avg_tat
        FROM tat_data
        GROUP BY site_name, department
    """)
    site_dept = clean(cur.fetchall())

    cur.execute("""
        SELECT site_name,
               CAST(COUNT(DISTINCT req_number) AS UNSIGNED) AS unique_reqs
        FROM tat_data GROUP BY site_name
    """)
    site_unique = {r['site_name']: int(_s(r['unique_reqs'])) for r in clean(cur.fetchall())}

    cur.close(); conn.close()
    return jsonify({
        'site_dept':        site_dept,
        'site_day':         [],
        'site_unique':      site_unique,
        'day_order':        [],
        'weekly_breakdown': [],
        'month_label':      'All Months',
        'prev_stats':       {},
    })


@app.route('/api/month-data')
@api
def get_month_data():
    month_id = request.args.get('month_id', '').strip()
    if not month_id:
        return jsonify({'error': 'month_id required'}), 400

    conn = get_db(); cur = conn.cursor(dictionary=True)

    # Site × Department aggregates
    cur.execute("""
        SELECT site_name    AS `Site Names`,
               department   AS Department,
               CAST(COUNT(*)                   AS UNSIGNED) AS total,
               CAST(COUNT(DISTINCT req_number) AS UNSIGNED) AS unique_reqs,
               CAST(SUM(tat_status='Pass')     AS UNSIGNED) AS pass_c,
               CAST(SUM(tat_status='Fail')     AS UNSIGNED) AS fail_c,
               ROUND(AVG(tat_minutes), 1)                   AS avg_tat
        FROM tat_data
        WHERE DATE_FORMAT(entry_datetime, '%Y-%m') = %s
        GROUP BY site_name, department
    """, (month_id,))
    site_dept = clean(cur.fetchall())

    # Daily data per site/dept
    cur.execute("""
        SELECT site_name    AS `Site Names`,
               department   AS Department,
               DATE(entry_datetime)                             AS day_date,
               DATE_FORMAT(MIN(entry_datetime), '%a %d %b')  AS DayLabel,
               CAST(SUM(tat_status='Pass') AS UNSIGNED)         AS pass_c,
               CAST(SUM(tat_status='Fail') AS UNSIGNED)         AS fail_c,
               CAST(COUNT(*)               AS UNSIGNED)         AS total,
               ROUND(AVG(tat_minutes), 1)                       AS avg_tat
        FROM tat_data
        WHERE DATE_FORMAT(entry_datetime, '%Y-%m') = %s
        GROUP BY site_name, department, DATE(entry_datetime)
        ORDER BY DATE(entry_datetime)
    """, (month_id,))
    site_day = clean(cur.fetchall())

    # Unique patients
    cur.execute("""
        SELECT site_name,
               CAST(COUNT(DISTINCT req_number) AS UNSIGNED) AS unique_reqs
        FROM tat_data
        WHERE DATE_FORMAT(entry_datetime, '%Y-%m') = %s
        GROUP BY site_name
    """, (month_id,))
    site_unique = {r['site_name']: int(_s(r['unique_reqs'])) for r in clean(cur.fetchall())}

    # Day ordering
    cur.execute("""
        SELECT DATE(entry_datetime)                             AS day_date,
               DATE_FORMAT(MIN(entry_datetime), '%a %d %b')  AS day_label
        FROM tat_data
        WHERE DATE_FORMAT(entry_datetime, '%Y-%m') = %s
        GROUP BY DATE(entry_datetime)
        ORDER BY DATE(entry_datetime)
    """, (month_id,))
    day_order = [{'date': r['day_date'], 'label': r['day_label']}
                 for r in clean(cur.fetchall()) if r.get('day_date')]

    # Weekly breakdown cards
    cur.execute("""
        SELECT week_id,
               DATE_FORMAT(MIN(entry_datetime), '%d %b')  AS week_label,
               CAST(COUNT(*)               AS UNSIGNED)      AS total,
               CAST(SUM(tat_status='Pass') AS UNSIGNED)      AS pass_c
        FROM tat_data
        WHERE DATE_FORMAT(entry_datetime, '%Y-%m') = %s
        GROUP BY week_id
        ORDER BY week_id
    """, (month_id,))
    wb = []
    for r in clean(cur.fetchall()):
        tot = int(_s(r.get('total')) or 0)
        pc  = int(_s(r.get('pass_c')) or 0)
        wb.append({
            'week_id':    str(r.get('week_id', '')),
            'total':      tot,
            'week_label': r.get('week_label', ''),
            'pass_rate':  round(pc / tot * 100, 1) if tot else 0,
        })

    # Month label
    cur.execute("""
        SELECT DATE_FORMAT(MIN(entry_datetime), '%M %Y') AS month_label
        FROM tat_data
        WHERE DATE_FORMAT(entry_datetime, '%Y-%m') = %s
    """, (month_id,))
    ml = cur.fetchone()
    month_label = (ml.get('month_label') or month_id) if ml else month_id

    # Previous month KPIs
    try:
        y, m = int(month_id[:4]), int(month_id[5:7])
        prev_mid = f"{y-1}-12" if m == 1 else f"{y}-{m-1:02d}"
        pstats = prev_kpi(cur, "DATE_FORMAT(entry_datetime,'%Y-%m') = %s", (prev_mid,))
    except Exception:
        pstats = {}

    cur.close(); conn.close()
    return jsonify({
        'site_dept':        site_dept,
        'site_day':         site_day,
        'site_unique':      site_unique,
        'day_order':        day_order,
        'weekly_breakdown': wb,
        'month_label':      month_label,
        'prev_stats':       pstats,
    })


@app.route('/api/weekly-trend')
@api
def get_weekly_trend():
    site = request.args.get('site', '').strip()
    dept = request.args.get('dept', '').strip()
    conn = get_db(); cur = conn.cursor(dictionary=True)

    conds = []; params = []
    if site: conds.append('site_name = %s'); params.append(site)
    if dept: conds.append('department = %s'); params.append(dept)
    where = ' AND '.join(conds) if conds else '1=1'

    if params:
        cur.execute(f"""
            SELECT week_id,
                   DATE_FORMAT(MIN(entry_datetime), '%d %b') AS week_label,
                   CAST(COUNT(*)               AS UNSIGNED)    AS total_tests,
                   CAST(SUM(tat_status='Pass') AS UNSIGNED)    AS pass_c
            FROM tat_data
            WHERE {where}
            GROUP BY week_id
            ORDER BY week_id
        """, params)
    else:
        cur.execute("""
            SELECT week_id,
                   DATE_FORMAT(MIN(entry_datetime), '%d %b') AS week_label,
                   CAST(COUNT(*)               AS UNSIGNED)   AS total_tests,
                   CAST(SUM(tat_status='Pass') AS UNSIGNED)   AS pass_c
            FROM tat_data
            GROUP BY week_id
            ORDER BY week_id
        """)

    overall = []
    for r in clean(cur.fetchall()):
        tot = int(_s(r.get('total_tests')) or 0)
        pc  = int(_s(r.get('pass_c')) or 0)
        overall.append({
            'week_id':     r['week_id'],
            'total_tests': tot,
            'week_label':  r.get('week_label') or r['week_id'],
            'pass_rate':   round(pc / tot * 100, 1) if tot else 0,
        })
    cur.close(); conn.close()
    return jsonify({'overall': overall, 'by_site': {}})


@app.route('/api/monthly-trend')
@api
def get_monthly_trend():
    site = request.args.get('site', '').strip()
    dept = request.args.get('dept', '').strip()
    conn = get_db(); cur = conn.cursor(dictionary=True)
    conds = []; params = []
    if site: conds.append('site_name = %s'); params.append(site)
    if dept: conds.append('department = %s'); params.append(dept)
    where = ('WHERE ' + ' AND '.join(conds)) if conds else ''
    sql = f"""
        SELECT DATE_FORMAT(entry_datetime, '%Y-%m')       AS month_id,
               DATE_FORMAT(MIN(entry_datetime), '%b %Y')  AS month_label,
               CAST(COUNT(*)               AS UNSIGNED)   AS total_tests,
               CAST(SUM(tat_status='Pass') AS UNSIGNED)   AS pass_c
        FROM tat_data {where}
        GROUP BY DATE_FORMAT(entry_datetime, '%Y-%m')
        ORDER BY month_id
    """
    cur.execute(sql, params) if params else cur.execute(sql)
    overall = []
    for r in clean(cur.fetchall()):
        tot = int(_s(r.get('total_tests')) or 0)
        pc  = int(_s(r.get('pass_c')) or 0)
        overall.append({
            'month_id':    r['month_id'],
            'total_tests': tot,
            'month_label': r.get('month_label') or r['month_id'],
            'pass_rate':   round(pc / tot * 100, 1) if tot else 0,
        })
    cur.close(); conn.close()
    return jsonify({'overall': overall, 'by_site': {}})


@app.route('/api/failed-reqs')
@api
def get_failed_reqs():
    week_id = request.args.get('period_id', '').strip()
    site    = request.args.get('site', '').strip()
    dept    = request.args.get('dept', '').strip()
    limit   = min(int(request.args.get('limit', 100)), 500)
    if not week_id:
        return jsonify([])

    conn = get_db(); cur = conn.cursor(dictionary=True)
    where  = "tat_status = 'Fail' AND week_id = %s"; params = [week_id]
    if site: where += ' AND site_name = %s';   params.append(site)
    if dept: where += ' AND department = %s';  params.append(dept)

    cur.execute(f"""
        SELECT req_number, site_name,
               MIN(test_name)                                              AS test_name,
               ROUND(MAX(tat_minutes), 0)                                  AS tat_minutes,
               ROUND(MIN(target_tat_minutes), 0)                           AS target_minutes,
               ROUND(MAX(tat_minutes / NULLIF(target_tat_minutes, 0)), 2)  AS tat_ratio,
               ROUND(MAX(tat_minutes) - MIN(target_tat_minutes), 0)        AS excess_minutes
        FROM tat_data
        WHERE {where}
        GROUP BY req_number, site_name
        ORDER BY tat_ratio DESC
        LIMIT %s
    """, params + [limit])

    def fmt(m):
        if not m: return '—'
        m = int(float(_s(m))); return f"{m//60}:{m%60:02d}"

    rows = clean(cur.fetchall())
    for r in rows:
        r['tat_fmt']    = fmt(r.get('tat_minutes'))
        r['target_fmt'] = fmt(r.get('target_minutes'))
        r['excess_fmt'] = fmt(r.get('excess_minutes'))

    cur.close(); conn.close()
    return jsonify(rows)


@app.route('/api/weekly-breakdown')
@api
def get_weekly_breakdown():
    """Weekly cards inside a specific month — respects site & dept filter."""
    month_id = request.args.get('month_id', '').strip()
    site     = request.args.get('site', '').strip()
    dept     = request.args.get('dept', '').strip()
    if not month_id:
        return jsonify([])
    conn = get_db(); cur = conn.cursor(dictionary=True)
    conds = ["DATE_FORMAT(entry_datetime, '%Y-%m') = %s"]; params = [month_id]
    if site: conds.append('site_name = %s'); params.append(site)
    if dept: conds.append('department = %s'); params.append(dept)
    where = ' AND '.join(conds)
    cur.execute(f"""
        SELECT week_id,
               DATE_FORMAT(MIN(entry_datetime), '%d %b') AS week_label,
               CAST(COUNT(*)               AS UNSIGNED)  AS total,
               CAST(SUM(tat_status='Pass') AS UNSIGNED)  AS pass_c
        FROM tat_data
        WHERE {where}
        GROUP BY week_id
        ORDER BY week_id
    """, params)
    wb = []
    for r in clean(cur.fetchall()):
        tot = int(_s(r.get('total')) or 0)
        pc  = int(_s(r.get('pass_c')) or 0)
        wb.append({
            'week_id':    str(r.get('week_id', '')),
            'total':      tot,
            'week_label': r.get('week_label', ''),
            'pass_rate':  round(pc / tot * 100, 1) if tot else 0,
        })
    cur.close(); conn.close()
    return jsonify(wb)


@app.route('/api/shift-data')
@api
def get_shift_data():
    """Pass/fail breakdown by shift for the selected week.

    24-hour labs (V.I, Itire Logged, Itire Run, Micro, Histo/cyto, Cedacrest):
        Morning    08:00 – 13:59
        Handover   14:00 – 15:59  (morning + afternoon overlap)
        Afternoon  16:00 – 19:59
        Night      20:00 – 07:59

    12-hour labs (all others):
        Morning    08:00 – 13:59
        Handover   14:00 – 15:59
        Afternoon  16:00 – 19:59
        Outside Hrs 20:00 – 07:59  (flags unexpected samples outside operating hours)
    """
    week_id = request.args.get('week_id', '').strip()
    site    = request.args.get('site', '').strip()
    dept    = request.args.get('dept', '').strip()
    if not week_id:
        return jsonify([])

    LABS_24HR = ('V.I', 'Itire Logged', 'Itire Run', 'Micro', 'Histo/cyto', 'Cedacrest')

    conn = get_db(); cur = conn.cursor(dictionary=True)
    conds = ['week_id = %s']; params = [week_id]
    if site: conds.append('site_name = %s'); params.append(site)
    if dept: conds.append('department = %s'); params.append(dept)
    where = ' AND '.join(conds)

    # Build the IN list for 24hr labs as a safe literal (site names have no SQL-injection risk here,
    # but we parameterise anyway)
    placeholders = ','.join(['%s'] * len(LABS_24HR))

    cur.execute(f"""
        SELECT
            CASE
                WHEN HOUR(entry_datetime) >= 8  AND HOUR(entry_datetime) < 14 THEN 'Morning (8am-2pm)'
                WHEN HOUR(entry_datetime) >= 14 AND HOUR(entry_datetime) < 16 THEN 'Handover (2pm-4pm)'
                WHEN HOUR(entry_datetime) >= 16 AND HOUR(entry_datetime) < 20 THEN 'Afternoon (4pm-8pm)'
                WHEN site_name IN ({placeholders})                             THEN 'Night (8pm-8am)'
                ELSE 'Outside Hours'
            END                                          AS shift_name,
            CAST(COUNT(*)               AS UNSIGNED)     AS total,
            CAST(SUM(tat_status='Pass') AS UNSIGNED)     AS pass_c,
            CAST(SUM(tat_status='Fail') AS UNSIGNED)     AS fail_c
        FROM tat_data
        WHERE {where}
        GROUP BY shift_name
        ORDER BY FIELD(shift_name,
            'Morning (8am-2pm)',
            'Handover (2pm-4pm)',
            'Afternoon (4pm-8pm)',
            'Night (8pm-8am)',
            'Outside Hours')
    """, list(LABS_24HR) + params)

    rows = clean(cur.fetchall())
    for r in rows:
        tot = int(_s(r.get('total')) or 0)
        pc  = int(_s(r.get('pass_c')) or 0)
        r['pass_rate'] = round(pc / tot * 100, 1) if tot else 0

    cur.close(); conn.close()
    return jsonify(rows)


@app.route('/api/upload', methods=['POST'])
@api
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    f = request.files['file']
    if not f.filename.lower().endswith('.xlsx'):
        return jsonify({'error': 'Only .xlsx files accepted'}), 400

    df = pd.read_excel(f, sheet_name='Analyzed_Data')
    df.columns = df.columns.str.strip()
    df['entry_dt']   = pd.to_datetime(df['EntDate & EntTime'],         errors='coerce')
    df['verify_dt']  = pd.to_datetime(df['TestVerDate & TestVerTime'], errors='coerce')
    df['tat_min']    = pd.to_timedelta(df['TAT (h:mm)'],        errors='coerce').dt.total_seconds() / 60
    df['target_min'] = pd.to_timedelta(df['Target TAT (h:mm)'], errors='coerce').dt.total_seconds() / 60

    min_date = df['entry_dt'].dropna().min()
    week_id  = min_date.strftime('%Y-%m-%d')

    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM tat_data WHERE week_id = %s", (week_id,))
    sql = """INSERT INTO tat_data
                 (week_id, req_number, site_name, department, test_name,
                  entry_datetime, verify_datetime, tat_status,
                  tat_minutes, target_tat_minutes)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rows = []
    for _, row in df.iterrows():
        rows.append((
            week_id,
            str(row.get('Req Number', '')),
            str(row.get('Site Names', '')),
            str(row.get('Department', '')),
            str(row.get('Test Name', '')),
            row['entry_dt']   if pd.notna(row['entry_dt'])   else None,
            row['verify_dt']  if pd.notna(row['verify_dt'])  else None,
            str(row.get('TAT Status', '')),
            float(row['tat_min'])    if pd.notna(row['tat_min'])    else None,
            float(row['target_min']) if pd.notna(row['target_min']) else None,
        ))
    cur.executemany(sql, rows)
    conn.commit(); cur.close(); conn.close()
    return jsonify({
        'success':       True,
        'week_id':       week_id,
        'rows_inserted': len(rows),
        'week_label':    min_date.strftime('%d %b %Y'),
    })


@app.route('/logo.jpg')
def logo():
    return send_from_directory('.', 'logo.jpg')

@app.route('/')
def index():
    from flask import make_response
    resp = make_response(send_from_directory('.', 'TAT_Dashboard_v4.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma']  = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


if __name__ == '__main__':
    print("\n" + "="*52)
    print("  TAT Dashboard — Cerba Lancet Nigeria")
    print("  Server is RUNNING!\n")
    print("  Open your browser: http://localhost:5000\n")
    print("  Keep this window open. CTRL+C to stop.")
    print("="*52 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
