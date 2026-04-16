import json
from collections import defaultdict

with open('/home/lighthouse/trading-data/binance_trades.jsonl') as f:
    fills = [json.loads(l) for l in f if l.strip()]

closes = [x for x in fills if x['pnl'] != 0]
opens  = [x for x in fills if x['pnl'] == 0]

total_pnl = sum(x['pnl'] for x in closes)
wins_n    = sum(1 for x in closes if x['pnl'] > 0)
losses_n  = sum(1 for x in closes if x['pnl'] < 0)
win_rate  = wins_n / len(closes) * 100 if closes else 0
avg_win   = sum(x['pnl'] for x in closes if x['pnl'] > 0) / wins_n if wins_n else 0
avg_loss  = sum(x['pnl'] for x in closes if x['pnl'] < 0) / losses_n if losses_n else 0

trade_log = sorted(closes, key=lambda x: x['time'])

sym_pnl = defaultdict(lambda: {'wins': 0, 'losses': 0, 'pnl': 0})
for c in closes:
    d = sym_pnl[c['symbol']]
    d['pnl'] += c['pnl']
    if c['pnl'] > 0:
        d['wins'] += 1
    else:
        d['losses'] += 1

symbol_pnl = sorted(sym_pnl.items(), key=lambda x: x[1]['pnl'], reverse=True)

daily = defaultdict(float)
for c in closes:
    daily[c['time'][:10]] += c['pnl']
daily_pnl = dict(sorted(daily.items()))

last_open = {}
for f2 in opens:
    last_open[f2['symbol']] = f2
active_positions = sorted(last_open.values(), key=lambda x: x['time'], reverse=True)

trade_json = json.dumps(trade_log, ensure_ascii=False)
sym_json   = json.dumps([{'symbol': s, **d} for s, d in symbol_pnl], ensure_ascii=False)
act_json   = json.dumps([{
    'symbol': p['symbol'],
    'side': p['side'],
    'price': p['price'],
    'qty': p['qty'],
    'time': p['time']
} for p in active_positions], ensure_ascii=False)
dlabels    = json.dumps(sorted(daily_pnl.keys()))
dvalues    = json.dumps([round(v, 2) for v in [daily_pnl[k] for k in sorted(daily_pnl.keys())]])

pnl_cl = 'green' if total_pnl >= 0 else 'red'
wr_cl  = 'green' if win_rate >= 50 else 'yellow'
d_cl   = 'green' if list(daily_pnl.values())[-1] >= 0 else 'red'

# Build table rows
rows_t = []
for t in trade_log:
    tc = 'long' if t['side'] == 'BUY' else 'short'
    dl = 'LONG' if t['side'] == 'BUY' else 'SHORT'
    pc = 'pnl-pos' if t['pnl'] >= 0 else 'pnl-neg'
    sign = '+' if t['pnl'] >= 0 else ''
    rows_t.append(
        f"<tr><td>{t['time'][5:]}</td><td>{t['symbol']}</td>"
        f"<td><span class='tag tag-{tc}'>{dl}</span></td>"
        f"<td>{t['price']:.4f}</td><td>{t['qty']:.2f}</td>"
        f"<td class='{pc}'>{sign}${t['pnl']:.2f}</td></tr>"
    )
rows_t_str = ''.join(rows_t)

rows_s = []
for s, d in symbol_pnl:
    total = d['wins'] + d['losses']
    wr = f"{(d['wins'] / total * 100):.0f}%" if total > 0 else '—'
    avg = f"{(d['pnl'] / total):.2f}" if total > 0 else '—'
    pc = 'pnl-pos' if d['pnl'] >= 0 else 'pnl-neg'
    sign = '+' if d['pnl'] >= 0 else ''
    rows_s.append(
        f"<tr><td>{s}</td><td class='{pc}'>{sign}${d['pnl']:.2f}</td>"
        f"<td class='pnl-pos'>{d['wins']}</td><td class='pnl-neg'>{d['losses']}</td>"
        f"<td>{wr}</td><td class='{pc}'>{sign}${avg}</td></tr>"
    )
rows_s_str = ''.join(rows_s)

rows_a = []
for p in active_positions:
    tc = 'long' if p['side'] == 'BUY' else 'short'
    dl = 'LONG' if p['side'] == 'BUY' else 'SHORT'
    rows_a.append(
        f"<tr><td>{p['symbol']}</td><td><span class='tag tag-{tc}'>{dl}</span></td>"
        f"<td>{p['price']:.4f}</td><td>{p['qty']:.2f}</td><td>{p['time']}</td></tr>"
    )
rows_a_str = ''.join(rows_a)

# Load base HTML and replace
with open('/home/lighthouse/trading-data/docs/index.html') as f:
    html = f.read()

html = html.replace('const tradeLog = []; // REPLACED', f'const tradeLog = {trade_json};')
html = html.replace('const symbolPnl = []; // REPLACED', f'const symbolPnl = {sym_json};')
html = html.replace('const activePositions = []; // REPLACED', f'const activePositions = {act_json};')
html = html.replace(
    "labels: DAILY_LABELS_REPLACED, datasets: [{ data: DAILY_VALUES_REPLACED",
    f"labels: {dlabels}, datasets: [{{ data: {dvalues}"
)
html = html.replace('<td id="kpi-pnl">—</div>', f'<td id="kpi-pnl">${"$" + f"{total_pnl:.2f}"}</td>')
html = html.replace('<td id="kpi-winrate">—</td>', f'<td id="kpi-winrate">{win_rate:.1f}%</td>')
html = html.replace('<td id="kpi-trades">—</td>', f'<td id="kpi-trades">{len(closes)}</td>')
html = html.replace('<td id="kpi-positions">—</td>', f'<td id="kpi-positions">{len(active_positions)}</td>')
html = html.replace('id="kpi-pnl"><td class="value red">', f'id="kpi-pnl"><td class="value {pnl_cl}">')
html = html.replace('id="kpi-winrate"><td class="value yellow">', f'id="kpi-winrate"><td class="value {wr_cl}">')
html = html.replace('id="kpi-daily"><td class="value red">—</td>', f'id="kpi-daily"><td class="value {d_cl}">${list(daily_pnl.values())[-1]:+.2f}</td>')
html = html.replace('<tbody id="trade-table"></tbody>', f'<tbody id="trade-table">{rows_t_str}</tbody>')
html = html.replace('<tbody id="symbol-table"></tbody>', f'<tbody id="symbol-table">{rows_s_str}</tbody>')
html = html.replace('<tbody id="active-table"></tbody>', f'<tbody id="active-table">{rows_a_str}</tbody>')

with open('/home/lighthouse/trading-data/docs/index.html', 'w') as f:
    f.write(html)

print(f"Done! {len(trade_log)} closes, {len(symbol_pnl)} symbols, {len(active_positions)} active")
