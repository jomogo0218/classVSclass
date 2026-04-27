import os

html_path = 'd:/classVSclass/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_tab_overview = """
<!-- ===== 對戰總覽 Tab ===== -->
<div class="tab-content" id="tab-overview">
    <div class="app-layout overview-layout">
        <aside class="category-sidebar" id="categorySidebar">
            <!-- 項目清單會由 JS 動態生成 -->
        </aside>
        
        <main class="overview-main">
            <div id="overviewHeader" style="margin-bottom: 24px;">
                <h1 id="selectedCategoryTitle" style="font-size: 24px; font-weight: 700; color: var(--text-1); margin-bottom: 4px;">請選擇賽事項目</h1>
                <p id="selectedCategoryDesc" style="color: var(--text-3); font-size: 14px;">點擊左側清單切換項目</p>
            </div>

            <div id="tournamentContainer" class="tournament-container">
                <!-- 這裡會根據選擇的項目動態渲染對戰表 -->
                <div class="empty-state">
                    <div class="empty-icon">🏆</div>
                    <p>請從左側選擇賽事項目</p>
                </div>
            </div>
        </main>
    </div>
</div>
"""

# Replace the previous tab-overview block
import re
pattern = r'<!-- ===== 對戰總覽 Tab ===== -->[\s\S]*?<!-- 側欄遮罩'
content = re.sub(pattern, new_tab_overview + '\n\n<!-- 側欄遮罩', content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
