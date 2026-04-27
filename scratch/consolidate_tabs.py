
import os

def consolidate_badminton_tabs():
    print("Consolidating Badminton tabs and reorganizing categories...")
    
    path = 'd:/classVSclass/index_local.html'
    content = open(path, 'r', encoding='utf-8').read()

    # 1. 更新 renderTournamentOverview 邏輯
    # 我們要修改它分組的方式，並加入自定義排序
    
    new_logic = """
function renderTournamentOverview() {
    const sidebar = document.getElementById('categorySidebar');
    if (!sidebar) return;
    sidebar.innerHTML = '';
    
    const grouped = {};
    matchesData.forEach(m => {
        let sidebarCat = m.category;
        // 如果包含「羽球」，則只取前面部分（合併第一輪、決賽等）
        if (m.category.includes('羽球')) {
            sidebarCat = m.category.split(' ')[0]; 
        }
        if (!grouped[sidebarCat]) grouped[sidebarCat] = [];
        grouped[sidebarCat].push(m);
    });

    // 定義自定義排序順序
    const sortOrder = [
        "高二女排", "高二男排", 
        "高三女籃", "高三男籃", 
        "高中羽球團體",
        "國二女排", "國二男排", 
        "國三女籃", "國三男籃", 
        "國中羽球團體"
    ];

    const cats = Object.keys(grouped).sort((a, b) => {
        let idxA = sortOrder.findIndex(o => a.startsWith(o));
        let idxB = sortOrder.findIndex(o => b.startsWith(o));
        if (idxA === -1) idxA = 99;
        if (idxB === -1) idxB = 99;
        return idxA - idxB;
    });

    cats.forEach(c => {
        const d = document.createElement('div');
        d.className = `category-tab ${currentOverviewCategory === c ? 'active' : ''}`;
        
        // 根據球種顯示圖示
        let icon = '🏆';
        if (c.includes('籃')) icon = '🏀';
        else if (c.includes('排')) icon = '🏐';
        else if (c.includes('羽')) icon = '🏸';
        
        // 顯示男女圖示
        let genderIcon = '';
        if (c.includes('女')) genderIcon = ' <span style="color:#ff6b6b;font-size:12px;">♀</span>';
        else if (c.includes('男')) genderIcon = ' <span style="color:#4dadff;font-size:12px;">♂</span>';

        d.innerHTML = `<span>${icon}</span> <span style="flex:1">${c}${genderIcon}</span>`;
        d.onclick = () => { 
            currentOverviewCategory = c; 
            renderTournamentOverview(); 
        };
        sidebar.appendChild(d);
    });

    if (!currentOverviewCategory && cats.length > 0) currentOverviewCategory = cats[0];
    
    if (currentOverviewCategory) {
        const title = document.getElementById('selectedCategoryTitle');
        const desc = document.getElementById('selectedCategoryDesc');
        const container = document.getElementById('tournamentContainer');
        
        if (title) title.innerHTML = `🏆 ${currentOverviewCategory}`;
        const isElim = currentOverviewCategory.includes('羽球');
        if (desc) desc.textContent = isElim ? '單淘汰晉級圖' : '循環賽數據儀表板';
        
        if (container) {
            container.innerHTML = '';
            if (isElim) renderBracketTree(grouped[currentOverviewCategory], container);
            else renderRoundRobinDashboard(grouped[currentOverviewCategory], container);
        }
    }
}
"""
    # 尋找舊的 renderTournamentOverview 並替換
    import re
    # 我們定位 function renderTournamentOverview() { ... }
    # 使用非貪婪匹配找到結束括號
    pattern = r"function renderTournamentOverview\(\) \{[\s\S]*?sidebar\.appendChild\(d\);\s*\}\);[\s\S]*?container\.appendChild\(g\);\s*\}\s*\}"
    # 由於代碼結構可能變動，我們用更保險的方式替換
    
    start_marker = "function renderTournamentOverview() {"
    end_marker = "renderRoundRobinDashboard(grouped[currentOverviewCategory], container);"
    
    start_idx = content.find(start_marker)
    # 尋找該函數結束的最後一個 }
    # 在我們的結構中，renderTournamentOverview 之後接著是 renderRoundRobinGrid 或 Dashboard
    # 我們找到 dashboard 調用的下一個 }
    end_search_idx = content.find(end_marker)
    if end_search_idx != -1:
        end_idx = content.find("}", content.find("}", end_search_idx) + 1) + 1
        content = content[:start_idx] + new_logic + content[end_idx:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Consolidation and reorganization complete!")

if __name__ == "__main__":
    consolidate_badminton_tabs()
