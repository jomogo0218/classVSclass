
import json
import os

def final_mega_integration_v2():
    print("Executing Final Mega Integration V2...")
    
    # 1. 準備數據
    with open('d:/classVSclass/matches.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)

    excel_results = [
        {"teamA": "高二仁 蘇愛甯", "teamB": "高二孝 顏怡勲", "score": "25:21", "win": "高二仁 蘇愛甯"},
        {"teamA": "高二孝 顏怡勲", "teamB": "高二忠 何品蓉", "score": "25:16", "win": "高二孝 顏怡勲"},
        {"teamA": "高二信 蔡沂潔", "teamB": "高二愛 方奕婷", "score": "15:25", "win": "高二愛 方奕婷"},
        {"teamA": "高二仁 蘇愛甯", "teamB": "高二愛 方奕婷", "score": "21:25", "win": "高二愛 方奕婷"},
        {"teamA": "高二仁 馮宥鑫", "teamB": "高二愛 胡廷安", "score": "19:25", "win": "高二愛 胡廷安"},
        {"teamA": "高二信 方晙昊", "teamB": "高二愛 胡廷安", "score": "25:21", "win": "高二愛 胡廷安"},
        {"teamA": "國二4 陳一汝", "teamB": "國二2 方倚喬", "score": "5:25", "win": "國二2 方倚喬"},
        {"teamA": "國二4 陳一汝", "teamB": "國二1 徐嘉儀", "score": "25:23", "win": "國二4 陳一汝"},
        {"teamA": "國二5 方騰毅", "teamB": "國二2 安立生", "score": "18:25", "win": "國二2 安立生"},
        {"teamA": "國二5 方騰毅", "teamB": "國二3 陳冠文", "score": "21:25", "win": "國二3 陳冠文"},
        {"teamA": "國二2 安立生", "teamB": "國二1 莊明燊", "score": "25:18", "win": "國二2 安立生"},
        {"teamA": "國二2 安立生", "teamB": "國二3 陳冠文", "score": "25:15", "win": "國二2 安立生"},
        {"teamA": "國二2 安立生", "teamB": "國二4 沈鈺哲", "score": "25:19", "win": "國二2 安立生"},
        {"teamA": "國二1 莊明燊", "teamB": "國二4 沈鈺哲", "score": "21:25", "win": "國二4 沈鈺哲"},
        {"teamA": "國二3 陳冠文", "teamB": "國二4 沈鈺哲", "score": "25:21", "win": "國二3 陳冠文"},
        {"teamA": "國三4 張育瑞", "teamB": "國三3 林暄恒", "score": "25:42", "win": "國三4 張育瑞"},
        {"teamA": "國三3 林暄恒", "teamB": "國三2 張嵩豪", "score": "18:45", "win": "國三2 張嵩豪"},
        {"teamA": "國三5 劉得名", "teamB": "國三3 林暄恒", "score": "42:42", "win": "國三5 劉得名"},
        {"teamA": "高三孝 李宇恩", "teamB": "高二信 蘇宥嘉", "score": "5:2", "win": "高三孝 李宇恩"},
        {"teamA": "高二愛 蔡矅宇", "teamB": "高一忠 郭育綸", "score": "5:0", "win": "高二愛 蔡矅宇"},
        {"teamA": "高一愛", "teamB": "高二忠 陳冠志", "score": "5:1", "win": "高一愛"},
        {"teamA": "高二愛 蔡矅宇", "teamB": "高三信 王威喆", "score": "4:1", "win": "高二愛 蔡矅宇"},
        {"teamA": "國二1 蘇品乂", "teamB": "國二5", "score": "2:3", "win": "國二5"},
        {"teamA": "輪空", "teamB": "高三信 王威喆", "score": "0:21", "win": "高三信 王威喆"},
        {"teamA": "輪空", "teamB": "高三愛 王宏益", "score": "0:21", "win": "高三愛 王宏益"},
        {"teamA": "輪空", "teamB": "國三4 蕭逸傑", "score": "0:21", "win": "國三4 蕭逸傑"}
    ]

    for r in excel_results:
        for m in matches:
            if (m['teamA'] == r['teamA'] and m['teamB'] == r['teamB']) or \
               (m['teamA'] == r['teamB'] and m['teamB'] == r['teamA']):
                m['status'] = "✅ 已結束"
                m['score'] = r['score']
                m['winner'] = r['win']
                parts = r['score'].split(':')
                m['scoreA'] = int(parts[0])
                m['scoreB'] = int(parts[1])

    # 2. 讀取原始碼
    css = open('d:/classVSclass/app.css', 'r', encoding='utf-8').read()
    js = open('d:/classVSclass/app.js', 'r', encoding='utf-8').read()
    html = open('d:/classVSclass/index.html', 'r', encoding='utf-8').read()

    css_final = css.replace('#1a73e8', '#f5750a').replace('#2563eb', '#f5750a').replace('#e8f0fe', '#fff7ed')
    css_final += """
:root { --blue: #f5750a !important; --orange: #f5750a !important; --blue-light: #fff7ed !important; }
.rr-dashboard { display: grid; grid-template-columns: 380px 1fr; gap: 24px; padding: 20px; }
.rr-header-stats { grid-column: 1 / -1; background: #1e293b; color: white; padding: 24px 32px; border-radius: 20px; display: flex; justify-content: space-between; align-items: center; border-left: 8px solid #f5750a; }
.rr-leaderboard { background: white; border-radius: 20px; padding: 24px; border: 1px solid #e2e8f0; }
.rr-rank-card { display: flex; align-items: center; padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #f1f5f9; }
.rr-matrix-container { background: white; border-radius: 20px; padding: 20px; border: 1px solid #e2e8f0; overflow-x: auto; }
.rr-matrix-table { border-collapse: separate; border-spacing: 8px; }
.rr-matrix-cell { width: 80px; height: 40px; background: #f8fafc; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; }
.rr-matrix-cell.win { background: #10b981; color: white; }
.category-tab { padding: 12px 20px; cursor: pointer; display: flex; align-items: center; gap: 10px; font-weight: 600; border-bottom: 1px solid #eee; }
.category-tab.active { background: #fff7ed; color: #f5750a; border-right: 4px solid #f5750a; }
"""

    # 3. 組合 JS 邏輯
    js_inject = """
const EMBEDDED_MATCHES = """ + json.dumps(matches, ensure_ascii=False) + """;
const EMBEDDED_SCHEDULES = [];

const originalFetch = window.fetch;
window.fetch = function(url) {
    if (url.includes('matches.json')) return Promise.resolve({ ok: true, json: () => Promise.resolve(EMBEDDED_MATCHES) });
    if (url.includes('schedules.json')) return Promise.resolve({ ok: true, json: () => Promise.resolve(EMBEDDED_SCHEDULES) });
    return originalFetch(url);
};

""" + js + """

function renderTournamentOverview() {
    const sidebar = document.getElementById('categorySidebar'); if (!sidebar) return;
    sidebar.innerHTML = '';
    const grouped = {};
    matchesData.forEach(m => {
        let cat = m.category;
        if (cat.includes('羽球')) cat = "羽球團體";
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(m);
    });
    const order = ["高二女排", "高二男排", "高三女籃", "高三男籃", "國二女排", "國二男排", "國三女籃", "國三男籃", "羽球團體"];
    const cats = Object.keys(grouped).sort((a,b) => {
        let ia = order.findIndex(o => a.startsWith(o));
        let ib = order.findIndex(o => b.startsWith(o));
        return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    });
    
    cats.forEach(c => {
        const d = document.createElement('div'); d.className = `category-tab ${currentOverviewCategory === c ? 'active' : ''}`;
        let icon = c.includes('籃')?'🏀':(c.includes('排')?'🏐':'🏸');
        d.innerHTML = `<span>${icon}</span> <span>${c}</span>`;
        d.onclick = () => { currentOverviewCategory = c; renderTournamentOverview(); };
        sidebar.appendChild(d);
    });
    if (!currentOverviewCategory && cats.length > 0) currentOverviewCategory = cats[0];
    const container = document.getElementById('tournamentContainer');
    if (container && currentOverviewCategory) {
        container.innerHTML = '';
        if (currentOverviewCategory.includes('羽球')) renderBracketTree(grouped[currentOverviewCategory], container);
        else renderRoundRobinDashboard(grouped[currentOverviewCategory], container);
    }
}

function renderRoundRobinDashboard(ms, c) {
    const teams = Array.from(new Set(ms.flatMap(m => [m.teamA, m.teamB]))).sort();
    const stats = {}; teams.forEach(t => stats[t] = { pts: 0, w: 0, l: 0, net: 0, pf: 0, pa: 0 });
    const matrix = {};
    ms.forEach(m => {
        if(!matrix[m.teamA]) matrix[m.teamA] = {};
        if(m.score) {
            matrix[m.teamA][m.teamB] = m.score;
            matrix[m.teamB][m.teamA] = m.score.split(':').reverse().join(':');
            stats[m.teamA].pf += (m.scoreA||0); stats[m.teamA].pa += (m.scoreB||0);
            stats[m.teamB].pf += (m.scoreB||0); stats[m.teamB].pa += (m.scoreA||0);
            if(m.winner===m.teamA) { stats[m.teamA].w++; stats[m.teamA].pts+=3; stats[m.teamB].l++; }
            else if(m.winner===m.teamB) { stats[m.teamB].w++; stats[m.teamB].pts+=3; stats[m.teamA].l++; }
        }
    });
    teams.forEach(t => stats[t].net = stats[t].pf - stats[t].pa);
    const completed = ms.filter(m => m.status === "✅ 已結束").length;
    const percent = Math.round((completed / ms.length) * 100);

    c.innerHTML = `
        <div class="rr-dashboard">
            <div class="rr-header-stats">
                <div><div style="font-size:24px; font-weight:900;">DASHBOARD</div><div>${currentOverviewCategory} 即時戰況</div></div>
                <div style="text-align:right;"><div>完成度</div><div style="font-size:24px; font-weight:900; color:#10b981;">${percent}%</div></div>
            </div>
            <div class="rr-leaderboard">
                <div style="font-weight:800; margin-bottom:15px;">🏆 即時排名</div>
                ${Object.entries(stats).sort((a,b)=>b[1].pts-a[1].pts || b[1].net-a[1].net).map(([t,s], i) => `
                    <div class="rr-rank-card">
                        <div style="width:30px;font-weight:900;">#${i+1}</div>
                        <div style="flex:1;font-weight:700;">${t}</div>
                        <div style="text-align:center;"><div style="color:#f5750a;font-weight:900;">${s.pts}</div><div style="font-size:9px;">PTS</div></div>
                        <div style="width:50px;text-align:right;font-weight:800;color:${s.net>=0?'#10b981':'#ef4444'}">${s.net>0?'+':''}${s.net}</div>
                    </div>
                `).join('')}
            </div>
            <div class="rr-matrix-container">
                <table class="rr-matrix-table">
                    <tr><th></th>${teams.map(t=>`<th class="rr-matrix-header">${t}</th>`).join('')}</tr>
                    ${teams.map(rt => `<tr><td class="rr-matrix-row-label">${rt}</td>${teams.map(ct => {
                        if(rt===ct) return `<td class="rr-matrix-cell void">/</td>`;
                        const s = matrix[rt][ct];
                        const isWin = ms.find(m=>((m.teamA===rt && m.teamB===ct)||(m.teamA===ct && m.teamB===rt)) && m.winner===rt);
                        return `<td class="rr-matrix-cell ${isWin?'win':''}">${s||'0:0'}</td>`;
                    }).join('')}</tr>`).join('')}
                </table>
            </div>
        </div>
    `;
}

function renderBracketTree(ms, c) {
    const groups = {'高中組': ms.filter(m=>m.category.includes('高中')), '國中組': ms.filter(m=>m.category.includes('國中'))};
    Object.entries(groups).forEach(([name, list]) => {
        const h = document.createElement('h3'); h.style.color='#f5750a'; h.style.padding='20px 0 0 20px'; h.textContent = name + " 晉級圖"; c.appendChild(h);
        const tree = document.createElement('div'); tree.className = 'bracket-tree';
        const rounds = {'R1':[], 'R2':[], 'SF':[], 'Final':[]};
        list.forEach(m => {
            let r='R1'; if(m.category.includes('2')) r='R2'; if(m.category.includes('準')) r='SF'; if(m.category.includes('決賽')) r='Final';
            rounds[r].push(m);
        });
        ['R1','R2','SF','Final'].forEach(rk => {
            if(!rounds[rk].length) return;
            const rd = document.createElement('div'); rd.className = 'bracket-round'; rd.innerHTML = `<div class='round-header'>${rk}</div>`;
            rounds[rk].forEach(m => {
                rd.innerHTML += `<div class='tree-match'><div class='tree-team'>${m.teamA}</div><div class='tree-team'>${m.teamB}</div><div class='tree-footer'>${m.score || '待定'}</div></div>`;
            });
            tree.appendChild(rd);
        });
        c.appendChild(tree);
    });
}

document.addEventListener('DOMContentLoaded', () => { if(typeof initApp === 'function') initApp(); });
"""
    # 4. 組合 HTML
    import re
    clean_html = re.sub(r'<link.*?>', '', html)
    clean_html = re.sub(r'<script src="app.js"></script>', '', clean_html)
    clean_html = re.sub(r'<script src="firebase.*?</script>', '', clean_html)
    
    final_output = clean_html.replace('</head>', f'<style>{css_final}</style></head>')
    final_output = final_output.replace('</body>', f'<script>{js_inject}</script></body>')
    
    with open('d:/classVSclass/index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_output)
    
    print("ULTIMATE MEGA INTEGRATION V2 COMPLETE!")

if __name__ == "__main__":
    final_mega_integration_v2()
