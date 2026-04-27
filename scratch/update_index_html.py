import os

html_path = 'd:/classVSclass/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add the tab content before the script tag or the end of the body
tab_content = """
<!-- ===== 對戰總覽 Tab ===== -->
<div class="tab-content" id="tab-overview">
    <div class="app-layout" style="display:block; padding: 20px;">
        <div class="overview-header" style="margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="font-size: 24px; font-weight: 700; color: var(--text-1); margin-bottom: 4px;">🏆 賽事對戰總覽</h1>
                <p style="color: var(--text-3); font-size: 14px;">視覺化呈現循環賽對戰組合與淘汰賽晉級圖</p>
            </div>
            <div class="overview-filters" style="display: flex; gap: 12px;">
                <select id="overviewCategoryFilter" class="search-input" style="width: 250px; margin-bottom: 0;" onchange="renderTournamentOverview()">
                    <option value="all">顯示所有類別</option>
                </select>
            </div>
        </div>

        <div id="tournamentContainer" class="tournament-container">
            <!-- 這裡會動態渲染各個項目的對戰表 -->
        </div>
    </div>
</div>
"""

if '<!-- ===== 對戰總覽 Tab ===== -->' not in content:
    content = content.replace('<script src="app.js?v=LOCAL_MODE_V1"></script>', tab_content + '\n<script src="app.js?v=LOCAL_MODE_V1"></script>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
