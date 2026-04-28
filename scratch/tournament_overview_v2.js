// ============================================================
// 全新對戰表總覽模組 (Tournament Overview Module v2)
// 功能：循環賽積分榜+矩陣、淘汰賽樹狀圖、新增/刪除賽程
// ============================================================

// overviewViewMode 視圖模式 ('bracket' | 'matrix' | 'standings' | 'list')
let overviewViewMode = 'standings';

// ─── 賽制類型辨識 ───────────────────────────────────────────
function getTournamentType(catMatches) {
    const cats = catMatches.map(m => m.category);
    if (cats.some(c => c.includes('循環') || c.includes('預賽'))) return 'roundrobin';
    if (cats.some(c => c.includes('第') || c.includes('輪') || c.includes('決賽') || c.includes('季軍'))) return 'elimination';
    return 'roundrobin';
}

// ─── 取得頂層賽事分類（去掉輪次後綴）──────────────────────────
function getTopLevelCategories() {
    const seen = new Set();
    matchesData.forEach(m => {
        const base = m.category
            .replace(/第\s*\d+\s*輪|準決賽|決賽|季軍賽|循環賽|預賽/g, '')
            .trim();
        seen.add(base || m.category);
    });
    return Array.from(seen).sort();
}

// ─── 取得某分類的全部場次 ──────────────────────────────────
function getCategoryMatches(baseCat) {
    return matchesData.filter(m => m.category.includes(baseCat));
}

// ─── 選擇分類 ────────────────────────────────────────────
function selectOverviewCategory(cat) {
    currentOverviewCategory = cat;
    const catMatches = getCategoryMatches(cat);
    const type = getTournamentType(catMatches);
    overviewViewMode = type === 'roundrobin' ? 'standings' : 'bracket';
    renderTournamentOverview();
}

function setOverviewViewMode(mode) {
    overviewViewMode = mode;
    renderTournamentOverview();
}

// ─── 主渲染入口 ──────────────────────────────────────────────
function renderTournamentOverview() {
    const sidebar  = document.getElementById('categorySidebar');
    const container = document.getElementById('tournamentContainer');
    if (!sidebar || !container) return;

    const categories = getTopLevelCategories();

    // ── 左側選單 ─────────────────────────────────────────────
    sidebar.innerHTML = `
        <div class="ov-sidebar-header">
            <span>賽事項目</span>
            <button class="ov-add-btn" onclick="openAddMatchModal()" title="新增比賽">＋</button>
        </div>
        ${categories.map(cat => {
            const catMs = getCategoryMatches(cat);
            const done  = catMs.filter(m => m.status.includes('已結束')).length;
            const type  = getTournamentType(catMs);
            const icon  = type === 'roundrobin' ? '⚽' : '🏆';
            const active = currentOverviewCategory === cat;
            return `<div class="ov-sidebar-item ${active ? 'ov-active' : ''}"
                        onclick="selectOverviewCategory('${cat.replace(/'/g,"\\'")}')">
                <div class="ov-item-main">
                    <span class="ov-item-icon">${getSportIcon ? getSportIcon(cat) : icon}</span>
                    <span class="ov-item-name">${cat}</span>
                </div>
                <div class="ov-item-meta">
                    <span class="ov-badge ${type === 'roundrobin' ? 'badge-rr' : 'badge-elim'}">${type === 'roundrobin' ? '循環' : '淘汰'}</span>
                    <span class="ov-progress">${done}/${catMs.length}</span>
                </div>
            </div>`;
        }).join('')}
    `;

    if (!currentOverviewCategory && categories.length > 0) {
        currentOverviewCategory = categories[0];
        renderTournamentOverview();
        return;
    }
    if (!currentOverviewCategory) {
        container.innerHTML = `<div class="ov-empty">尚無賽事資料</div>`;
        return;
    }

    const catMatches = getCategoryMatches(currentOverviewCategory);
    const type = getTournamentType(catMatches);
    const done  = catMatches.filter(m => m.status.includes('已結束')).length;
    const pct   = catMatches.length ? Math.round(done / catMatches.length * 100) : 0;

    // ── 主內容區 ─────────────────────────────────────────────
    container.innerHTML = `
        <div class="ov-content-wrap">
            <!-- 標題列 -->
            <div class="ov-header">
                <div class="ov-header-left">
                    <h2 class="ov-title">${currentOverviewCategory}</h2>
                    <div class="ov-subtitle">
                        <span class="ov-badge ${type === 'roundrobin' ? 'badge-rr' : 'badge-elim'}">${type === 'roundrobin' ? '循環賽制' : '淘汰賽制'}</span>
                        <span class="ov-stat-chip">共 ${catMatches.length} 場</span>
                        <span class="ov-stat-chip">已完成 ${done} 場</span>
                    </div>
                </div>
                <div class="ov-header-right">
                    <!-- 進度環 -->
                    <div class="ov-ring-wrap">
                        <svg viewBox="0 0 36 36" class="ov-ring">
                            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                fill="none" stroke="#e5e7eb" stroke-width="3"/>
                            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                fill="none" stroke="var(--ov-accent)" stroke-width="3"
                                stroke-dasharray="${pct}, 100"/>
                        </svg>
                        <span class="ov-ring-pct">${pct}%</span>
                    </div>
                </div>
            </div>

            <!-- 視圖切換 TAB -->
            <div class="ov-view-tabs">
                ${type === 'roundrobin' ? `
                <button class="ov-tab ${overviewViewMode==='standings'?'ov-tab-active':''}" onclick="setOverviewViewMode('standings')">🏅 積分榜</button>
                <button class="ov-tab ${overviewViewMode==='matrix'?'ov-tab-active':''}" onclick="setOverviewViewMode('matrix')">📊 對戰矩陣</button>
                ` : `
                <button class="ov-tab ${overviewViewMode==='bracket'?'ov-tab-active':''}" onclick="setOverviewViewMode('bracket')">🏆 賽程樹</button>
                `}
                <button class="ov-tab ${overviewViewMode==='list'?'ov-tab-active':''}" onclick="setOverviewViewMode('list')">📋 場次列表</button>
            </div>

            <!-- 內容區 -->
            <div class="ov-view-body" id="ovViewBody"></div>
        </div>
    `;

    // 渲染對應視圖
    const body = document.getElementById('ovViewBody');
    if (overviewViewMode === 'standings') renderOvStandings(catMatches, body);
    else if (overviewViewMode === 'matrix')   renderOvMatrix(catMatches, body);
    else if (overviewViewMode === 'bracket')  renderOvBracket(catMatches, body);
    else if (overviewViewMode === 'list')     renderOvList(catMatches, body);
}

// ══════════════════════════════════════════════════════════════
// 視圖 1：積分榜 (Standings)
// ══════════════════════════════════════════════════════════════
function renderOvStandings(matches, el) {
    const teams = Array.from(new Set(matches.flatMap(m => [m.teamA, m.teamB]))).sort();
    const stats = {};
    teams.forEach(t => { stats[t] = { pts:0, w:0, l:0, pf:0, pa:0, played:0 }; });

    matches.forEach(m => {
        if (!m.status.includes('已結束') || !m.score) return;
        const sa = Number(m.scoreA)||0, sb = Number(m.scoreB)||0;
        stats[m.teamA].played++; stats[m.teamB].played++;
        stats[m.teamA].pf += sa; stats[m.teamA].pa += sb;
        stats[m.teamB].pf += sb; stats[m.teamB].pa += sa;
        if (m.winner === m.teamA) { stats[m.teamA].w++; stats[m.teamA].pts+=3; stats[m.teamB].l++; }
        else if (m.winner === m.teamB) { stats[m.teamB].w++; stats[m.teamB].pts+=3; stats[m.teamA].l++; }
        else { stats[m.teamA].pts++; stats[m.teamB].pts++; }
    });

    const sorted = Object.entries(stats).sort((a,b) => {
        if (b[1].pts !== a[1].pts) return b[1].pts - a[1].pts;
        const diffA = a[1].pf - a[1].pa, diffB = b[1].pf - b[1].pa;
        return diffB - diffA;
    });

    const medals = ['🥇','🥈','🥉'];
    el.innerHTML = `
        <div class="ov-standings">
            <div class="ov-standings-head">
                <div>名次</div><div>班級</div><div>場次</div><div>勝</div><div>敗</div><div>得分</div><div>得失差</div><div>積分</div>
            </div>
            ${sorted.map(([team, s], i) => `
                <div class="ov-standings-row ${i===0?'rank-1':i===1?'rank-2':i===2?'rank-3':''}">
                    <div class="ov-rank">${medals[i] || (i+1)}</div>
                    <div class="ov-team-name">${team}</div>
                    <div>${s.played}</div>
                    <div class="ov-win">${s.w}</div>
                    <div class="ov-lose">${s.l}</div>
                    <div>${s.pf}:${s.pa}</div>
                    <div class="${s.pf-s.pa>=0?'ov-pos':'ov-neg'}">${s.pf-s.pa>=0?'+':''}${s.pf-s.pa}</div>
                    <div class="ov-pts">${s.pts}</div>
                </div>
            `).join('')}
        </div>
    `;
}

// ══════════════════════════════════════════════════════════════
// 視圖 2：對戰矩陣 (Matrix)
// ══════════════════════════════════════════════════════════════
function renderOvMatrix(matches, el) {
    const teams = Array.from(new Set(matches.flatMap(m => [m.teamA, m.teamB]))).sort();
    const matrix = {};
    matches.forEach(m => {
        if (!matrix[m.teamA]) matrix[m.teamA] = {};
        if (!matrix[m.teamB]) matrix[m.teamB] = {};
        if (m.status.includes('已結束') && m.score) {
            const sa = m.scoreA||0, sb = m.scoreB||0;
            matrix[m.teamA][m.teamB] = { score: `${sa}:${sb}`, win: m.winner === m.teamA, id: m.id };
            matrix[m.teamB][m.teamA] = { score: `${sb}:${sa}`, win: m.winner === m.teamB, id: m.id };
        } else if (m) {
            if (!matrix[m.teamA][m.teamB]) matrix[m.teamA][m.teamB] = { score: null, id: m.id };
            if (!matrix[m.teamB][m.teamA]) matrix[m.teamB][m.teamA] = { score: null, id: m.id };
        }
    });

    el.innerHTML = `
        <div class="ov-matrix-wrap">
            <table class="ov-matrix">
                <thead>
                    <tr>
                        <th class="ov-matrix-corner">↓ 主 \\ 客 →</th>
                        ${teams.map(t => `<th>${t}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${teams.map(row => `
                        <tr>
                            <td class="ov-matrix-label">${row}</td>
                            ${teams.map(col => {
                                if (row === col) return `<td class="ov-matrix-self">—</td>`;
                                const cell = matrix[row] && matrix[row][col];
                                if (!cell) return `<td class="ov-matrix-empty">-</td>`;
                                if (!cell.score) return `<td class="ov-matrix-pending" onclick="openEditScoreModal('${cell.id}')" title="點擊輸入比分">⏳</td>`;
                                return `<td class="ov-matrix-done ${cell.win?'ov-win-cell':'ov-lose-cell'}"
                                    onclick="openEditScoreModal('${cell.id}')" title="點擊修改比分">
                                    ${cell.score}
                                    ${cell.win ? '<span class="ov-win-dot">●</span>' : ''}
                                </td>`;
                            }).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// ══════════════════════════════════════════════════════════════
// 視圖 3：淘汰賽樹狀圖 (Bracket)
// ══════════════════════════════════════════════════════════════
function renderOvBracket(matches, el) {
    const roundOrder = ['第一輪','第二輪','第三輪','準決賽','決賽','季軍賽'];
    const roundsMap = {};
    matches.forEach(m => {
        let r = '第一輪';
        if (m.category.includes('第 2 輪') || m.category.includes('第二輪')) r = '第二輪';
        if (m.category.includes('第 3 輪') || m.category.includes('第三輪')) r = '第三輪';
        if (m.category.includes('準決賽')) r = '準決賽';
        if (m.category.includes('決賽') && !m.category.includes('準')) r = '決賽';
        if (m.category.includes('季軍')) r = '季軍賽';
        if (!roundsMap[r]) roundsMap[r] = [];
        roundsMap[r].push(m);
    });

    const rounds = roundOrder.filter(r => roundsMap[r]);

    el.innerHTML = `<div class="ov-bracket">${rounds.map(rKey => `
        <div class="ov-bracket-round">
            <div class="ov-round-label">${rKey}</div>
            <div class="ov-round-matches">
                ${roundsMap[rKey].map(m => {
                    const sch = scheduledMatches.find(sm => String(sm.matchId) === String(m.id));
                    const done = m.status.includes('已結束');
                    const PNAMES = ['早自習','第1節','第2節','第3節','第4節','第5節','第6節','第7節','課業輔導','精進學習'];
                    return `
                    <div class="ov-match-card ${done?'ov-match-done':''}" onclick="openEditScoreModal('${m.id}')">
                        <div class="ov-match-team ${m.winner===m.teamA?'ov-winner':''}">
                            <span class="ov-team-label">${m.teamA}</span>
                            <span class="ov-team-score">${done?(m.scoreA??'-'):''}</span>
                        </div>
                        <div class="ov-match-divider"></div>
                        <div class="ov-match-team ${m.winner===m.teamB?'ov-winner':''}">
                            <span class="ov-team-label">${m.teamB}</span>
                            <span class="ov-team-score">${done?(m.scoreB??'-'):''}</span>
                        </div>
                        <div class="ov-match-footer">
                            <span class="ov-match-id">#${String(m.id).slice(-3)}</span>
                            <div class="ov-match-actions">
                                ${sch ? `<span class="ov-sched-tag">📅 ${sch.date.slice(5)} ${PNAMES[sch.periodIndex]||'P'+sch.periodIndex}</span>
                                <button class="ov-print-btn" onclick="event.stopPropagation();printMatchSlipById('${m.id}')" title="列印通知單">🖨️</button>` : `<span class="ov-unsched-tag">⏳ 待排</span>`}
                                <button class="ov-del-btn" onclick="event.stopPropagation();confirmDeleteMatch('${m.id}')" title="刪除此場次">🗑️</button>
                            </div>
                        </div>
                    </div>`;
                }).join('')}
            </div>
        </div>
    `).join('')}</div>`;
}

// ══════════════════════════════════════════════════════════════
// 視圖 4：場次列表 (List)
// ══════════════════════════════════════════════════════════════
function renderOvList(matches, el) {
    const PNAMES = ['早自習','第1節','第2節','第3節','第4節','第5節','第6節','第7節','課業輔導','精進學習'];
    const groups = {};
    matches.forEach(m => {
        if (!groups[m.category]) groups[m.category] = [];
        groups[m.category].push(m);
    });

    el.innerHTML = `<div class="ov-list">
        ${Object.entries(groups).map(([cat, ms]) => `
            <div class="ov-list-group">
                <div class="ov-list-group-header">${cat} <span class="ov-group-count">${ms.length} 場</span></div>
                ${ms.map(m => {
                    const sch = scheduledMatches.find(sm => String(sm.matchId) === String(m.id));
                    const done = m.status.includes('已結束');
                    return `
                    <div class="ov-list-row ${done?'ov-list-done':''}">
                        <div class="ov-list-status">${done ? '✅' : sch ? '📅' : '⏳'}</div>
                        <div class="ov-list-teams">
                            <span class="${m.winner===m.teamA?'ov-list-winner':''}">${m.teamA}</span>
                            <span class="ov-vs">VS</span>
                            <span class="${m.winner===m.teamB?'ov-list-winner':''}">${m.teamB}</span>
                        </div>
                        <div class="ov-list-score">${done ? (m.score || `${m.scoreA}:${m.scoreB}`) : (sch ? `${sch.date.slice(5)} ${PNAMES[sch.periodIndex]||''}` : '待排')}</div>
                        <div class="ov-list-actions">
                            <button onclick="openEditScoreModal('${m.id}')" class="ov-list-btn" title="編輯">✏️</button>
                            ${sch ? `<button onclick="printMatchSlipById('${m.id}')" class="ov-list-btn" title="通知單">🖨️</button>` : ''}
                            <button onclick="confirmDeleteMatch('${m.id}')" class="ov-list-btn ov-list-del" title="刪除">🗑️</button>
                        </div>
                    </div>`;
                }).join('')}
            </div>
        `).join('')}
    </div>`;
}

// ══════════════════════════════════════════════════════════════
// 刪除比賽確認
// ══════════════════════════════════════════════════════════════
function confirmDeleteMatch(matchId) {
    const m = matchesData.find(x => String(x.id) === String(matchId));
    if (!m) return;
    if (!confirm(`確定要刪除此場次？\n\n【${m.category}】\n${m.teamA} VS ${m.teamB}\n\n此操作無法復原。`)) return;

    // 刪除排程
    const schIdx = scheduledMatches.findIndex(sm => String(sm.matchId) === String(matchId));
    if (schIdx >= 0) {
        scheduledMatches.splice(schIdx, 1);
        saveScheduledMatches();
        if (typeof removeScheduledMatchFromFirestore === 'function')
            removeScheduledMatchFromFirestore(matchId);
    }

    // 刪除賽事
    const mIdx = matchesData.findIndex(x => String(x.id) === String(matchId));
    if (mIdx >= 0) matchesData.splice(mIdx, 1);

    // Firestore 同步
    if (typeof db !== 'undefined' && db) {
        const idStr = String(matchId);
        db.collection('matches').doc(idStr).delete().catch(e => console.warn('Delete match skip:', e.message));
        db.collection('scheduledMatches').doc(idStr).delete().catch(e => console.warn('Delete sched skip:', e.message));
    }

    renderTournamentOverview();
    renderMatchList && renderMatchList();
}

// ══════════════════════════════════════════════════════════════
// 新增比賽 Modal
// ══════════════════════════════════════════════════════════════
function openAddMatchModal() {
    const cats = Array.from(new Set(matchesData.map(m => m.category))).sort();
    const catOpts = cats.map(c => `<option value="${c}">${c}</option>`).join('');

    const modal = document.createElement('div');
    modal.id = 'addMatchModal';
    modal.className = 'ov-modal-overlay';
    modal.innerHTML = `
        <div class="ov-modal">
            <div class="ov-modal-header">
                <h3>➕ 新增賽事場次</h3>
                <button onclick="this.closest('.ov-modal-overlay').remove()" class="ov-modal-close">✕</button>
            </div>
            <div class="ov-modal-body">
                <label>賽事類別</label>
                <select id="am-cat" style="width:100%">
                    ${catOpts}
                    <option value="__new__">── 輸入新類別 ──</option>
                </select>
                <input id="am-newcat" placeholder="新賽事類別名稱（如：高二男排 循環賽）" style="display:none;margin-top:6px;width:100%">

                <label style="margin-top:14px">隊伍 A（班級）</label>
                <input id="am-teamA" placeholder="例：高二信 方晙昊" style="width:100%">

                <label style="margin-top:14px">隊伍 B（班級）</label>
                <input id="am-teamB" placeholder="例：高二孝 顏怡勲" style="width:100%">

                <label style="margin-top:14px">賽制</label>
                <select id="am-type" style="width:100%">
                    <option value="⏳ 待打">⏳ 待打</option>
                    <option value="✅ 已結束">✅ 已結束</option>
                </select>
            </div>
            <div class="ov-modal-footer">
                <button onclick="this.closest('.ov-modal-overlay').remove()" class="ov-btn-cancel">取消</button>
                <button onclick="submitAddMatch()" class="ov-btn-confirm">新增</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    document.getElementById('am-cat').addEventListener('change', function() {
        document.getElementById('am-newcat').style.display = this.value === '__new__' ? 'block' : 'none';
    });
    modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
}

function submitAddMatch() {
    const catSel = document.getElementById('am-cat').value;
    const cat = catSel === '__new__' ? document.getElementById('am-newcat').value.trim() : catSel;
    const teamA = document.getElementById('am-teamA').value.trim();
    const teamB = document.getElementById('am-teamB').value.trim();
    const status = document.getElementById('am-type').value;

    if (!cat || !teamA || !teamB) { alert('請填寫所有欄位'); return; }
    if (teamA === teamB) { alert('兩隊不能相同'); return; }

    const newId = `match_${Date.now()}`;
    const newMatch = { id: newId, category: cat, teamA, teamB, status, score: '', scoreA: 0, scoreB: 0, winner: '' };
    matchesData.push(newMatch);

    // Firestore 同步
    if (typeof db !== 'undefined' && db) {
        db.collection('matches').doc(newId).set(newMatch).catch(e => console.warn('Add match sync:', e.message));
    }

    document.getElementById('addMatchModal')?.remove();
    currentOverviewCategory = cat.replace(/第\s*\d+\s*輪|準決賽|決賽|季軍賽|循環賽|預賽/g,'').trim() || cat;
    renderTournamentOverview();
    renderMatchList && renderMatchList();
    alert(`✅ 已新增：${teamA} VS ${teamB}`);
}
