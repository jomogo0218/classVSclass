
import os
import json
import re

def upgrade_to_matrix_dashboard():
    print("Upgrading to Round Robin Matrix Dashboard...")
    
    # 1. 讀取組件
    def r(n): return open(n, 'r', encoding='utf-8').read()
    
    html = r('index.html')
    css = r('app.css')
    js = r('app.js')
    matches = r('matches.json')
    schedules = r('schedules.json')

    # --- 2. CSS 強化 (矩陣與排行榜專用) ---
    dashboard_css = """
/* ══ 循環賽數據儀表板 ══ */
.rr-dashboard { display: grid; grid-template-columns: 350px 1fr; gap: 24px; padding: 20px; animation: fadeIn 0.5s ease; }
.rr-header-stats { grid-column: 1 / -1; background: #1e293b; color: white; padding: 24px 32px; border-radius: 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); position: relative; overflow: hidden; }
.rr-header-stats::before { content: ''; position: absolute; left: 0; top: 0; width: 8px; height: 100%; background: #f5750a; }
.rr-stat-group { display: flex; gap: 40px; }
.rr-stat-item { text-align: right; }
.rr-stat-label { font-size: 12px; opacity: 0.6; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.rr-stat-value { font-size: 32px; font-weight: 900; font-family: 'Roboto', sans-serif; }
.rr-stat-value.percent { color: #10b981; }

/* 排行榜 */
.rr-leaderboard { background: white; border-radius: 20px; padding: 24px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
.rr-leaderboard-title { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 800; margin-bottom: 24px; color: #1e293b; }
.rr-rank-card { display: flex; align-items: center; padding: 16px; border-radius: 16px; margin-bottom: 12px; transition: 0.2s; border: 1px solid #f1f5f9; }
.rr-rank-card:hover { transform: translateX(8px); background: #fff7ed; border-color: #fbd38d; }
.rr-rank-num { width: 40px; font-size: 20px; font-weight: 900; color: #94a3b8; font-style: italic; display: flex; align-items: center; justify-content: center; }
.rr-rank-medal { width: 40px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.rr-rank-info { flex: 1; margin-left: 12px; }
.rr-rank-name { font-weight: 700; color: #1e293b; font-size: 15px; }
.rr-rank-pts { text-align: center; margin-right: 16px; }
.rr-pts-val { font-size: 20px; font-weight: 900; color: #f5750a; line-height: 1; }
.rr-pts-unit { font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase; }
.rr-rank-stats { background: #f8fafc; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 700; color: #64748b; }
.rr-rank-net { width: 60px; text-align: center; }
.rr-net-val { font-weight: 800; color: #10b981; }
.rr-net-val.neg { color: #ef4444; }

/* 交叉對戰矩陣 */
.rr-matrix-container { background: white; border-radius: 20px; padding: 32px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow-x: auto; }
.rr-matrix-table { border-collapse: separate; border-spacing: 12px; margin: 0 auto; }
.rr-matrix-header { background: #f8fafc; padding: 12px 20px; border-radius: 12px; font-weight: 700; font-size: 13px; color: #64748b; min-width: 100px; text-align: center; }
.rr-matrix-row-label { background: #f8fafc; padding: 12px 20px; border-radius: 12px; font-weight: 700; font-size: 14px; color: #1e293b; text-align: right; min-width: 140px; }
.rr-matrix-cell { width: 100px; height: 60px; background: #f8fafc; border-radius: 16px; border: 2px solid transparent; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 800; color: #94a3b8; transition: 0.3s; }
.rr-matrix-cell.win { background: #10b981; color: white; border-color: #059669; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
.rr-matrix-cell.lose { background: white; color: #64748b; border: 1px dashed #cbd5e1; opacity: 0.6; }
.rr-matrix-cell.void { background: #f1f5f9; color: #cbd5e1; font-weight: 400; }
.rr-matrix-cell.scheduled { border-color: #f5750a; color: #f5750a; background: #fff7ed; cursor: pointer; }
"""
    css_final = css.replace('#1a73e8', '#f5750a').replace('#2563eb', '#f5750a') + dashboard_css

    # --- 3. JS 升級 (矩陣邏輯) ---
    matrix_logic = """
function renderRoundRobinDashboard(matches, container) {
    // 1. 提取所有隊伍
    const teams = Array.from(new Set(matches.flatMap(m => [m.teamA, m.teamB]))).sort();
    
    // 2. 初始化統計資料
    const stats = {};
    teams.forEach(t => { stats[t] = { pts: 0, w: 0, d: 0, l: 0, net: 0, played: 0 }; });
    
    // 3. 計算成績 (假設有分數欄位，目前先模擬已排定場次)
    const matrix = {};
    matches.forEach(m => {
        const scheduled = scheduledMatches.find(sm => sm.matchId === m.id);
        if (!matrix[m.teamA]) matrix[m.teamA] = {};
        if (!matrix[m.teamB]) matrix[m.teamB] = {};
        
        if (scheduled) {
            // 這裡未來可以加入比分: const scoreA = scheduled.scoreA || 0;
            matrix[m.teamA][m.teamB] = scheduled;
            matrix[m.teamB][m.teamA] = scheduled;
        }
    });

    const completedMatches = 0; // 未來接比分資料
    const totalMatches = matches.length;
    const percent = totalMatches > 0 ? Math.round((completedMatches / totalMatches) * 100) : 0;

    // 4. 生成 Dashboard 佈局
    container.innerHTML = `
        <div class="rr-dashboard">
            <div class="rr-header-stats">
                <div class="rr-stat-title">
                    <div style="font-size: 24px; font-weight: 900; letter-spacing: 1px;">ROUND ROBIN DASHBOARD</div>
                    <div style="font-size: 12px; opacity: 0.7;">${currentOverviewCategory} 賽事即時排行榜</div>
                </div>
                <div class="rr-stat-group">
                    <div class="rr-stat-item">
                        <div class="rr-stat-label">總比賽場次</div>
                        <div class="rr-stat-value">${totalMatches}</div>
                    </div>
                    <div class="rr-stat-item">
                        <div class="rr-stat-label">完成進度</div>
                        <div class="rr-stat-value percent">${percent}%</div>
                    </div>
                </div>
            </div>
            
            <div class="rr-leaderboard">
                <div class="rr-leaderboard-title">🏆 即時積分排名</div>
                ${teams.map((t, idx) => {
                    const s = stats[t];
                    const medals = ['🥇', '🥈', '🥉'];
                    return `
                        <div class="rr-rank-card">
                            ${idx < 3 ? `<div class="rr-rank-medal">${medals[idx]}</div>` : `<div class="rr-rank-num">#${idx+1}</div>`}
                            <div class="rr-rank-info">
                                <div class="rr-rank-name">${t}</div>
                                <div class="rr-rank-stats">W-D-L: ${s.w}-${s.d}-${s.l}</div>
                            </div>
                            <div class="rr-rank-pts">
                                <div class="rr-pts-val">${s.pts}</div>
                                <div class="rr-pts-unit">PTS</div>
                            </div>
                            <div class="rr-rank-net">
                                <div class="rr-net-val ${s.net < 0 ? 'neg' : ''}">${s.net > 0 ? '+' : ''}${s.net}</div>
                                <div class="rr-pts-unit">NET</div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>

            <div class="rr-matrix-container">
                <table class="rr-matrix-table">
                    <tr>
                        <th></th>
                        ${teams.map(t => `<th class="rr-matrix-header">${t}</th>`).join('')}
                    </tr>
                    ${teams.map(rowTeam => `
                        <tr>
                            <td class="rr-matrix-row-label">${rowTeam}</td>
                            ${teams.map(colTeam => {
                                if (rowTeam === colTeam) return `<td class="rr-matrix-cell void">/</td>`;
                                const match = matrix[rowTeam][colTeam];
                                if (match) {
                                    return `<td class="rr-matrix-cell scheduled" onclick="alert('比賽日: ${match.date}\\n時段: 第 ${match.periodIndex} 節')">📅</td>`;
                                }
                                return `<td class="rr-matrix-cell">0:0</td>`;
                            }).join('')}
                        </tr>
                    `).join('')}
                </table>
            </div>
        </div>
    `;
}
"""
    # 注入到 app.js
    js_final = js
    if "renderRoundRobinDashboard" not in js_final:
        js_final += matrix_logic
    
    # 修改 renderTournamentOverview 以調用新 Dashboard
    js_final = js_final.replace(
        "else renderRoundRobinGrid(grouped[currentOverviewCategory], container);",
        "else renderRoundRobinDashboard(grouped[currentOverviewCategory], container);"
    )

    # --- 4. 編譯 HTML ---
    import re
    matches_data = r('matches.json')
    schedules_data = r('schedules.json')
    
    js_header = "const EMBEDDED_MATCHES = " + matches_data + ";\nconst EMBEDDED_SCHEDULES = " + schedules_data + ";\n"
    
    clean_lines = []
    for line in html.splitlines():
        if any(x in line for x in ['rel="stylesheet"', 'app.js', 'firebase', 'firebase-config']): continue
        clean_lines.append(line)
    
    final_html = "\n".join(clean_lines)
    final_html = final_html.replace('</head>', '<style>\n' + css_final + '\n</style>\n</head>')
    final_html = final_html.replace('</body>', '<script>\n' + js_header + js_final + '\n</script>\n</body>')

    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("DONE! Upgraded to Matrix Dashboard.")

if __name__ == "__main__":
    upgrade_to_matrix_dashboard()
