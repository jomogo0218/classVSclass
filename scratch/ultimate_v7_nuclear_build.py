
import json
import itertools

def ultimate_v7_nuclear_build():
    print("Executing Ultimate V7 Nuclear Build (Self-Contained Implementation)...")
    
    # 1. 準備全量數據 (91場)
    groups = {
        "高二女排 循環賽": ["高二仁 蘇愛甯", "高二孝 顏怡勲", "高二忠 何品蓉", "高二信 蔡沂潔", "高二義 詹沂澄", "高二愛 方奕婷"],
        "高二男排 循環賽": ["高二仁 馮宥鑫", "高二孝 鄧文淮", "高二忠", "高二信 方晙昊", "高二愛 胡廷安"],
        "高三女籃 循環賽": ["高三仁", "高三孝", "高三忠", "高三信 歐品妤", "高三愛 蔣瑋珈"],
        "高三男籃 循環賽": ["高三仁 張允誠", "高三孝", "高三忠", "高三信", "高三愛 汪錦瑞"],
        "國二女排 循環賽": ["國二1 徐嘉儀", "國二2 方倚喬", "國二3", "國二4 陳一汝", "國二5"],
        "國二男排 循環賽": ["國二1 莊明燊", "國二2 安立生", "國二3 陳冠文", "國二4 沈鈺哲", "國二5 方騰毅"],
        "國三女籃 循環賽": ["國三1", "國三2", "國三3", "國三4 楊于萱", "國三5 龔品諭"],
        "國三男籃 循環賽": ["國三1", "國三2 張嵩豪", "國三3 林暄恒", "國三4 張育瑞", "國三5 劉得名"]
    }

    results = [
        ("高二女排 循環賽", "高二仁 蘇愛甯", "高二孝 顏怡勲", "25:21", "高二仁 蘇愛甯"),
        ("高二女排 循環賽", "高二孝 顏怡勲", "高二忠 何品蓉", "25:16", "高二孝 顏怡勲"),
        ("高二女排 循環賽", "高二信 蔡沂潔", "高二愛 方奕婷", "15:25", "高二愛 方奕婷"),
        ("高二女排 循環賽", "高二仁 蘇愛甯", "高二愛 方奕婷", "21:25", "高二愛 方奕婷"),
        ("高二男排 循環賽", "高二仁 馮宥鑫", "高二愛 胡廷安", "19:25", "高二愛 胡廷安"),
        ("高二男排 循環賽", "高二信 方晙昊", "高二愛 胡廷安", "25:21", "高二愛 胡廷安"),
        ("國二女排 循環賽", "國二4 陳一汝", "國二2 方倚喬", "5:25", "國二2 方倚喬"),
        ("國二女排 循環賽", "國二4 陳一汝", "國二1 徐嘉儀", "25:23", "國二4 陳一汝"),
        ("國二男排 循環賽", "國二5 方騰毅", "國二2 安立生", "18:25", "國二2 安立生"),
        ("國二男排 循環賽", "國二5 方騰毅", "國二3 陳冠文", "21:25", "國二3 陳冠文"),
        ("國二男排 循環賽", "國二2 安立生", "國二1 莊明燊", "25:18", "國二2 安立生"),
        ("國二男排 循環賽", "國二2 安立生", "國二3 陳冠文", "25:15", "國二2 安立生"),
        ("國二男排 循環賽", "國二2 安立生", "國二4 沈鈺哲", "25:19", "國二2 安立生"),
        ("國二1 莊明燊", "國二4 沈鈺哲", "21:25", "國二4 沈鈺哲"),
        ("國二3 陳冠文", "國二4 沈鈺哲", "25:21", "國二3 陳冠文"),
        ("國三男籃 循環賽", "國三4 張育瑞", "國三3 林暄恒", "25:42", "國三4 張育瑞"),
        ("國三男籃 循環賽", "國三3 林暄恒", "國三2 張嵩豪", "18:45", "國三2 張嵩豪"),
        ("國三5 劉得名", "國三3 林暄恒", "42:42", "國三5 劉得名")
    ]

    final_matches = []
    for cat, teams in groups.items():
        pairs = list(itertools.combinations(teams, 2))
        for idx, (tA, tB) in enumerate(pairs):
            match = {"id": f"{cat}_{idx}", "category": cat, "teamA": tA, "teamB": tB, "status": "⏳ 待打", "score": "0:0", "winner": None}
            for r_cat, r_a, r_b, r_s, r_w in results:
                if r_cat == cat and ((r_a in tA and r_b in tB) or (r_a in tB and r_b in tA)):
                    match.update({"status": "✅ 已結束", "score": r_s, "winner": r_w, "scoreA": int(r_s.split(':')[0]), "scoreB": int(r_s.split(':')[1])})
                    break
            final_matches.append(match)

    badminton = [
        ("高中羽球團體 第 1 輪", "高三孝 李宇恩", "高二信 蘇宥嘉", "5:2", "高三孝 李宇恩"),
        ("高中羽球團體 第 1 輪", "高二愛 蔡矅宇", "高一忠 郭育綸", "5:0", "高二愛 蔡矅宇"),
        ("高中羽球團體 第 1 輪", "高一愛", "高二忠 陳冠志", "5:1", "高一愛"),
        ("高中羽球團體 第 2 輪", "高二愛 蔡矅宇", "高三信 王威喆", "4:1", "高二愛 蔡矅宇"),
        ("國中羽球團體 第 1 輪", "國二1 蘇品乂", "國二5", "2:3", "國二5"),
        ("國中羽球團體 第 1 輪", "輪空", "國三4 蕭逸傑", "0:21", "國三4 蕭逸傑")
    ]
    for idx, (cat, a, b, s, w) in enumerate(badminton):
        final_matches.append({"id": f"badm_{idx}", "category": cat, "teamA": a, "teamB": b, "status": "✅ 已結束", "score": s, "winner": w, "scoreA": int(s.split(':')[0]), "scoreB": int(s.split(':')[1])})

    # 2. 獲取 HTML / CSS / Schedules
    import os
    html_raw = open('d:/classVSclass/index.html', 'r', encoding='utf-8').read()
    css_raw = open('d:/classVSclass/app.css', 'r', encoding='utf-8').read()
    with open('d:/classVSclass/schedules.json', 'r', encoding='utf-8') as f:
        schedules_json = f.read()

    # 3. 終極純淨版 CSS
    css_final = css_raw.replace('#1a73e8', '#f5750a').replace('#2563eb', '#f5750a')
    css_final += """
:root { --blue: #f5750a !important; --orange: #f5750a !important; --blue-light: #fff7ed !important; }
.rr-dashboard { display: grid; grid-template-columns: 380px 1fr; gap: 24px; padding: 20px; animation: fadeIn 0.3s; }
.rr-header-stats { grid-column: 1 / -1; background: #1e293b; color: white; padding: 24px 32px; border-radius: 20px; display: flex; justify-content: space-between; align-items: center; border-left: 8px solid #f5750a; }
.rr-leaderboard { background: white; border-radius: 20px; padding: 24px; border: 1px solid #e2e8f0; }
.rr-rank-card { display: flex; align-items: center; padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #f1f5f9; transition: 0.2s; }
.rr-rank-card:hover { transform: translateX(5px); background: #fff7ed; }
.rr-matrix-container { background: white; border-radius: 20px; padding: 20px; border: 1px solid #e2e8f0; overflow-x: auto; }
.rr-matrix-table { border-collapse: separate; border-spacing: 8px; width: 100%; }
.rr-matrix-cell { width: 80px; height: 40px; background: #f8fafc; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px; color: #94a3b8; }
.rr-matrix-cell.win { background: #10b981; color: white; }
.category-tab { padding: 14px 20px; cursor: pointer; display: flex; align-items: center; gap: 10px; font-weight: 700; border-bottom: 1px solid #eee; transition: 0.2s; }
.category-tab.active { background: #fff7ed; color: #f5750a; border-right: 5px solid #f5750a; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
"""

    # 4. 終極純淨版 JS
    final_js = """
// 數據區
window.EMBEDDED_MATCHES = """ + json.dumps(final_matches, ensure_ascii=False) + """;
window.EMBEDDED_SCHEDULES = """ + schedules_json + """;

// 狀態區
let currentOverviewCategory = null;

// 初始化
function initApp() {
    console.log('App Initialized (Nuclear V7)');
    renderTournamentOverview();
}

function renderTournamentOverview() {
    const sidebar = document.getElementById('categorySidebar');
    const container = document.getElementById('tournamentContainer');
    if (!sidebar || !container) return;

    sidebar.innerHTML = '';
    const grouped = {};
    window.EMBEDDED_MATCHES.forEach(m => {
        let cat = m.category;
        if (cat.includes('羽球')) cat = cat.split(' ')[0];
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(m);
    });

    const order = ["高二女排", "高二男排", "高三女籃", "高三男籃", "高中羽球團體", "國二女排", "國二男排", "國三女籃", "國三男籃", "國中羽球團體"];
    const cats = Object.keys(grouped).sort((a,b) => {
        let ia = order.findIndex(o => a.startsWith(o));
        let ib = order.findIndex(o => b.startsWith(o));
        return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    });

    cats.forEach(c => {
        const d = document.createElement('div');
        d.className = `category-tab ${currentOverviewCategory === c ? 'active' : ''}`;
        let icon = c.includes('籃')?'🏀':(c.includes('排')?'🏐':'🏸');
        d.innerHTML = `<span>${icon}</span> <span>${c}</span>`;
        d.onclick = () => { currentOverviewCategory = c; renderTournamentOverview(); };
        sidebar.appendChild(d);
    });

    if (!currentOverviewCategory && cats.length > 0) currentOverviewCategory = cats[0];
    
    if (currentOverviewCategory) {
        // 清空容器並直接填入
        container.innerHTML = '';
        const ms = grouped[currentOverviewCategory] || [];
        if (currentOverviewCategory.includes('羽球')) renderBracketTree(ms, container);
        else renderRoundRobinDashboard(ms, container);
    }
}

function renderRoundRobinDashboard(ms, c) {
    const teams = Array.from(new Set(ms.flatMap(m => [m.teamA, m.teamB]))).sort();
    const stats = {}; teams.forEach(t => stats[t] = { pts: 0, w: 0, l: 0, net: 0, pf: 0, pa: 0 });
    const matrix = {};
    ms.forEach(m => {
        if(!matrix[m.teamA]) matrix[m.teamA] = {};
        if(m.status === "✅ 已結束") {
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
                <div><div style="font-size:24px; font-weight:900;">DASHBOARD</div><div>${currentOverviewCategory}</div></div>
                <div style="text-align:right;"><div>完成進度</div><div style="font-size:24px; font-weight:900; color:#10b981;">${percent}%</div></div>
            </div>
            <div class="rr-leaderboard">
                <div style="font-weight:800; margin-bottom:15px; color:#1e293b;">🏆 積分排行榜</div>
                ${Object.entries(stats).sort((a,b)=>b[1].pts-a[1].pts || b[1].net-a[1].net).map(([t,s], i) => `
                    <div class="rr-rank-card">
                        <div style="width:30px; font-weight:900; color:#94a3b8;">#${i+1}</div>
                        <div style="flex:1; font-weight:700;">${t}</div>
                        <div style="text-align:center;"><div style="color:#f5750a; font-weight:900;">${s.pts}</div><div style="font-size:9px;">PTS</div></div>
                        <div style="width:50px; text-align:right; font-weight:800; color:${s.net>=0?'#10b981':'#ef4444'}">${s.net>0?'+':''}${s.net}</div>
                    </div>
                `).join('')}
            </div>
            <div class="rr-matrix-container">
                <table class="rr-matrix-table">
                    <tr><th></th>${teams.map(t=>`<th class="rr-matrix-header">${t}</th>`).join('')}</tr>
                    ${teams.map(rt => `<tr><td class="rr-matrix-row-label">${rt}</td>${teams.map(ct => {
                        if(rt===ct) return `<td class="rr-matrix-cell void">/</td>`;
                        const s = matrix[rt][ct];
                        const m = ms.find(x=>((x.teamA===rt && x.teamB===ct)||(x.teamA===ct && x.teamB===rt)));
                        const isWin = m && m.winner === rt;
                        return `<td class="rr-matrix-cell ${isWin?'win':''}">${s||'待打'}</td>`;
                    }).join('')}</tr>`).join('')}
                </table>
            </div>
        </div>
    `;
}

function renderBracketTree(ms, c) {
    c.innerHTML = `<h3 style="color:#f5750a; padding:20px; font-weight:900;">${currentOverviewCategory} 晉級圖</h3>`;
    const tree = document.createElement('div'); tree.className = 'bracket-tree';
    const rounds = {'R1':[], 'R2':[], 'SF':[], 'Final':[]};
    ms.forEach(m => {
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
}

// 模擬課表功能 (確保其他分頁不壞掉)
function renderSchedule() {
    const container = document.getElementById('mainContent'); if(!container) return;
    container.innerHTML = '<div style="padding:40px; text-align:center;"><h3>本機模式已鎖定對戰表功能</h3><p>請點擊上方對戰表分頁查看完整賽事進度</p></div>';
}

// 攔截分頁點擊
document.addEventListener('click', (e) => {
    if(e.target.closest('[data-tab="tournament"]')) {
        setTimeout(initApp, 100);
    }
});

// 啟動
window.onload = initApp;
"""

    # 5. 生成最終純淨 HTML
    import re
    # 移除所有可能的外部干擾
    clean_html = re.sub(r'<script\b[^>]*>.*?</script>', '', html_raw, flags=re.S)
    clean_html = re.sub(r'<link\b[^>]*>', '', clean_html, flags=re.S)
    
    # 重建基本的 HTML 結構，注入 CSS 與 JS
    final_output = clean_html.replace('</head>', f'<style>{css_final}</style></head>')
    final_output = final_output.replace('</body>', f'<script>{final_js}</script></body>')
    
    with open('d:/classVSclass/index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_output)
    
    print("ULTIMATE V7 NUCLEAR BUILD COMPLETE! 100% Self-Contained.")

if __name__ == "__main__":
    ultimate_v7_nuclear_build()
