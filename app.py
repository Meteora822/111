from flask import Flask, render_template, request, jsonify
from datetime import datetime
from models import Record, get_engine, get_session
from sqlalchemy import func

app = Flask(__name__)

# 从配置文件加载数据库连接
try:
    from config import Config
    app.config.from_object(Config)
    engine = get_engine(Config.SQLALCHEMY_DATABASE_URI)
    print(f"✓ 已连接到 MySQL 数据库: {Config.MYSQL_DATABASE}")
except ImportError:
    # 如果没有配置文件，使用 SQLite
    engine = get_engine('sqlite:///records.db')
    print("✓ 使用 SQLite 数据库")
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")
    print("将使用 SQLite 作为备用数据库")
    engine = get_engine('sqlite:///records.db')

def record_to_dict(r):
    return {
        'id': r.id,
        'type': r.type,
        'amount': r.amount,
        'category': r.category,
        'date': r.date.strftime('%Y-%m-%d'),
        'note': r.note or ''
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/records', methods=['GET'])
def list_records():
    session = get_session(engine)
    start = request.args.get('start')
    end = request.args.get('end')
    category = request.args.get('category')
    q = session.query(Record)
    if start:
        try:
            s = datetime.strptime(start, '%Y-%m-%d').date()
            q = q.filter(Record.date >= s)
        except:
            pass
    if end:
        try:
            e = datetime.strptime(end, '%Y-%m-%d').date()
            q = q.filter(Record.date <= e)
        except:
            pass
    if category:
        q = q.filter(Record.category == category)
    rows = q.order_by(Record.date.desc()).all()
    data = [record_to_dict(r) for r in rows]
    session.close()
    return jsonify(data)

@app.route('/api/record', methods=['POST'])
def add_record():
    payload = request.json or {}
    try:
        t = payload.get('type')
        amount = float(payload.get('amount'))
        category = payload.get('category') or '未分类'
        date_s = payload.get('date')
        d = datetime.strptime(date_s, '%Y-%m-%d').date() if date_s else datetime.today().date()
    except Exception as e:
        return jsonify({'error': '参数错误', 'detail': str(e)}), 400
    note = payload.get('note')
    session = get_session(engine)
    rec = Record(type=t, amount=amount, category=category, date=d, note=note)
    session.add(rec)
    session.commit()
    data = record_to_dict(rec)
    session.close()
    return jsonify(data), 201

@app.route('/api/record/<int:rid>', methods=['PUT'])
def update_record(rid):
    payload = request.json or {}
    session = get_session(engine)
    rec = session.get(Record, rid)
    if not rec:
        session.close()
        return jsonify({'error': '记录未找到'}), 404
    if 'type' in payload:
        rec.type = payload['type']
    if 'amount' in payload:
        rec.amount = float(payload['amount'])
    if 'category' in payload:
        rec.category = payload['category']
    if 'date' in payload:
        rec.date = datetime.strptime(payload['date'], '%Y-%m-%d').date()
    if 'note' in payload:
        rec.note = payload['note']
    session.commit()
    data = record_to_dict(rec)
    session.close()
    return jsonify(data)

@app.route('/api/record/<int:rid>', methods=['DELETE'])
def delete_record(rid):
    session = get_session(engine)
    rec = session.get(Record, rid)
    if not rec:
        session.close()
        return jsonify({'error': '记录未找到'}), 404
    session.delete(rec)
    session.commit()
    session.close()
    return jsonify({'result': 'deleted'})

@app.route('/api/stats', methods=['GET'])
def stats():
    # 返回按分类的支出/收入汇总，以及月度结余（简单示例）
    session = get_session(engine)
    start = request.args.get('start')
    end = request.args.get('end')
    
    # 构建基础查询
    q = session.query(Record)
    if start:
        try:
            s = datetime.strptime(start, '%Y-%m-%d').date()
            q = q.filter(Record.date >= s)
        except:
            pass
    if end:
        try:
            e = datetime.strptime(end, '%Y-%m-%d').date()
            q = q.filter(Record.date <= e)
        except:
            pass
    
    # 按分类求和（包含类型）
    cat_rows = session.query(
        Record.category, 
        Record.type,
        func.sum(Record.amount).label('total')
    )
    if start:
        try:
            s = datetime.strptime(start, '%Y-%m-%d').date()
            cat_rows = cat_rows.filter(Record.date >= s)
        except: pass
    if end:
        try:
            e = datetime.strptime(end, '%Y-%m-%d').date()
            cat_rows = cat_rows.filter(Record.date <= e)
        except: pass
    
    cat_rows = cat_rows.group_by(Record.category, Record.type).all()
    categories = [{'category': r[0], 'type': r[1], 'total': r[2]} for r in cat_rows]
    
    # 按日期统计
    daily_rows = session.query(
        Record.date,
        Record.type,
        func.sum(Record.amount).label('total')
    )
    if start:
        try:
            s = datetime.strptime(start, '%Y-%m-%d').date()
            daily_rows = daily_rows.filter(Record.date >= s)
        except: pass
    if end:
        try:
            e = datetime.strptime(end, '%Y-%m-%d').date()
            daily_rows = daily_rows.filter(Record.date <= e)
        except: pass
    
    daily_rows = daily_rows.group_by(Record.date, Record.type).all()
    daily_stats = {}
    for row in daily_rows:
        date_str = row[0].strftime('%Y-%m-%d')
        if date_str not in daily_stats:
            daily_stats[date_str] = {'income': 0, 'expense': 0}
        if row[1] == 'income':
            daily_stats[date_str]['income'] = row[2]
        else:
            daily_stats[date_str]['expense'] = row[2]
    
    # 月度结余（当前月份为示例）
    today = datetime.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))
    start_m = datetime(year, month, 1).date()
    if month == 12:
        next_first = datetime(year+1, 1, 1).date()
    else:
        next_first = datetime(year, month+1, 1).date()
    
    month_rows = session.query(Record).filter(Record.date >= start_m, Record.date < next_first).all()
    income = sum(r.amount for r in month_rows if r.type == 'income')
    expense = sum(r.amount for r in month_rows if r.type == 'expense')
    balance = income - expense
    
    session.close()
    
    return jsonify({
        'by_category': categories,
        'daily_stats': daily_stats,
        'month_summary': {
            'year': year, 
            'month': month, 
            'income': income, 
            'expense': expense, 
            'balance': balance
        }
    })

@app.route('/api/year-stats', methods=['GET'])
def year_stats():
    """年度统计"""
    session = get_session(engine)
    today = datetime.today()
    year = int(request.args.get('year', today.year))
    
    # 该年度的所有记录
    start_year = datetime(year, 1, 1).date()
    end_year = datetime(year, 12, 31).date()
    
    year_rows = session.query(Record).filter(
        Record.date >= start_year, 
        Record.date <= end_year
    ).all()
    
    income = sum(r.amount for r in year_rows if r.type == 'income')
    expense = sum(r.amount for r in year_rows if r.type == 'expense')
    balance = income - expense
    
    # 按月统计
    monthly_stats = {}
    for m in range(1, 13):
        if m == 12:
            next_first = datetime(year+1, 1, 1).date()
        else:
            next_first = datetime(year, m+1, 1).date()
        start_m = datetime(year, m, 1).date()
        
        month_rows = [r for r in year_rows if start_m <= r.date < next_first]
        m_income = sum(r.amount for r in month_rows if r.type == 'income')
        m_expense = sum(r.amount for r in month_rows if r.type == 'expense')
        monthly_stats[m] = {
            'income': m_income,
            'expense': m_expense,
            'balance': m_income - m_expense
        }
    
    session.close()
    
    return jsonify({
        'year': year,
        'income': income,
        'expense': expense,
        'balance': balance,
        'monthly_stats': monthly_stats
    })

if __name__ == '__main__':
    # 开发环境运行
    app.run(host='0.0.0.0', port=5000, debug=True)
    # 生产环境请使用 WSGI 服务器，如 gunicorn 或 waitress
