
import os

def upgrade_dashboard_with_real_data():
    print("Upgrading dashboard with real-time data calculation logic...")
    
    path = 'd:/classVSclass/index_local.html'
    content = open(path, 'r', encoding='utf-8').read()

    # 更新 renderRoundRobinDashboard 的實時計算邏輯
    real_data_logic = """
function renderRoundRobinDashboard(matches, container) {
    const teams = Array.from(new Set(matches.flatMap(m => [m.teamA, m.teamB]))).sort();
    const stats = {};
    teams.forEach(t => { stats[t] = { pts: 0, w: 0, d: 0, l: 0, net: 0, pf: 0, pa: 0, played: 0 }; });
    
    const matrix = {};
    matches.forEach(m => {
        if (!matrix[m.teamA]) matrix[m.teamA] = {};
        if (!matrix[m.teamB]) matrix[m.teamB] = {};
        
        // 紀錄比數到矩陣
        if (m.score) {
            matrix[m.teamA][m.teamB] = m.score;
            matrix[m.teamB][m.teamA] = m.score.split(':').reverse().join(':');
            
            const sa = m.scoreA || 0;
            const sb = m.scoreB || 0;
            
            stats[m.teamA].played++;
            stats[m.teamB].played++;
            stats[m.teamA].pf += sa; stats[m.teamA].pa += sb;
            stats[m.teamB].pf += sb; stats[m.teamB].pa += sa;
            
            if (m.winner === m.teamA) { stats[m.teamA].w++; stats[m.teamA].pts += 3; stats[m.teamB].l++; }
            else if (m.winner === m.teamB) { stats[m.teamB].w++; stats[m.teamB].pts += 3; stats[m.teamA].l++; }
            else { stats[m.teamA].d++; stats[m.teamB].d++; stats[m.teamA].pts += 1; stats[m.teamB].pts += 1; }
        }
    });

    // 計算淨勝分
    teams.forEach(t => { stats[t].net = stats[t].pf - stats[t].pa; });

    const total = matches.length;
    const completed = matches.filter(m => m.status === "✅ 已結束").length;
    const percent = Math.round((completed / total) * 100);

    container.innerHTML = `
        <div class="rr-dashboard">
            <div class="rr-header-stats">
                <div class="rr-stat-title">
                    <div style="font-size: 24px; font-weight: 900; color: #fff;">ROUND ROBIN DASHBOARD</div>
                    <div style="font-size: 12px; opacity: 0.7; color: #fff;">${currentOverviewCategory} 即時排行榜</div>
                </div>
                <div class="rr-stat-group">
                    <div class="rr-stat-item">
                        <div class="rr-stat-label" style="color: #fff;">總比賽場次</div>
                        <div class="rr-stat-value" style="color: #fff;">${total}</div>
                    </div>
                    <div class="rr-stat-item">
                        <div class="rr-stat-label" style="color: #fff;">完成進度</div>
                        <div class="rr-stat-value percent">${percent}%</div>
                    </div>
                </div>
            </div>
            
            <div class="rr-leaderboard">
                <div class="rr-leaderboard-title">🏆 即時積分排名</div>
                ${Object.entries(stats).sort((a,b) => b[1].pts - a[1].pts || b[1].net - a[1].net).map(([t, s], idx) => {
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
                    <tr><th></th>${teams.map(t => `<th class="rr-matrix-header">${t}</th>`).join('')}</tr>
                    ${teams.map(rowTeam => `
                        <tr>
                            <td class="rr-matrix-row-label">${rowTeam}</td>
                            ${teams.map(colTeam => {
                                if (rowTeam === colTeam) return `<td class="rr-matrix-cell void">/</td>`;
                                const score = matrix[rowTeam][colTeam];
                                if (score) {
                                    const isWin = matches.find(m => ((m.teamA===rowTeam && m.teamB===colTeam) || (m.teamA===colTeam && m.teamB===rowTeam)) && m.winner === rowTeam);
                                    return `<td class="rr-matrix-cell ${isWin ? 'win' : ''}">${score}</td>`;
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
    # 精準替換 renderRoundRobinDashboard 函數
    import re
    # 我們找到 function renderRoundRobinDashboard(matches, container) { ... }
    # 使用與之前類似的標記替換方式
    start_tag = "function renderRoundRobinDashboard(matches, container) {"
    start_idx = content.find(start_tag)
    # 找到該函數的結束 }
    end_idx = content.find("}", content.find("</table>", start_idx)) + 5
    
    content = content[:start_idx] + real_data_logic + content[end_idx:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Dashboard upgraded with real data logic!")

if __name__ == "__main__":
    upgrade_dashboard_with_real_data()
