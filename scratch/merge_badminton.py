
import os

def merge_all_badminton():
    print("Merging all badminton categories into one single tab...")
    
    path = 'd:/classVSclass/index_local.html'
    content = open(path, 'r', encoding='utf-8').read()

    # 1. 更新 renderTournamentOverview 側邊欄分組
    # 將所有包含「羽球」的類別都歸類到「羽球團體」
    sidebar_logic = """
    matchesData.forEach(m => {
        let sidebarCat = m.category;
        if (m.category.includes('羽球')) {
            sidebarCat = "羽球團體"; 
        }
        if (!grouped[sidebarCat]) grouped[sidebarCat] = [];
        grouped[sidebarCat].push(m);
    });

    const sortOrder = [
        "高二女排", "高二男排", 
        "高三女籃", "高三男籃", 
        "國二女排", "國二男排", 
        "國三女籃", "國三男籃", 
        "羽球團體"
    ];
"""

    # 2. 更新 renderBracketTree 邏輯，支援在同一個頁面渲染多組樹狀圖
    new_bracket_logic = """
function renderBracketTree(matches, container) {
    // 依據類別細分（高中/國中）
    const subGroups = {};
    matches.forEach(m => {
        const grade = m.category.includes('高中') ? '高中組' : '國中組';
        if (!subGroups[grade]) subGroups[grade] = [];
        subGroups[grade].push(m);
    });

    Object.keys(subGroups).sort().reverse().forEach(grade => {
        const subMatches = subGroups[grade];
        
        // 分組標題
        const groupHeader = document.createElement('div');
        groupHeader.className = 'overview-header-card';
        groupHeader.style.marginTop = '20px';
        groupHeader.innerHTML = `<h3 style="margin:0;color:#f5750a;">${grade} 晉級圖</h3>`;
        container.appendChild(groupHeader);

        const rounds = { 'R1': [], 'R2': [], 'SF': [], 'Final': [], '3rd': [] };
        const labelMap = { 'R1': '第一輪', 'R2': '第二輪', 'SF': '準決賽', 'Final': '決賽', '3rd': '季軍賽' };
        
        subMatches.forEach(m => {
            let r = 'R1';
            if (m.category.includes('2')) r = 'R2';
            if (m.category.includes('準')) r = 'SF';
            if (m.category.includes('季軍')) r = '3rd';
            if (m.category.includes('決賽') && !m.category.includes('準')) r = 'Final';
            if (rounds[r]) rounds[r].push(m);
        });

        const tree = document.createElement('div');
        tree.className = 'bracket-tree';
        ['R1', 'R2', 'SF', 'Final', '3rd'].forEach(rk => {
            if (!rounds[rk].length) return;
            const rd = document.createElement('div');
            rd.className = 'bracket-round';
            rd.innerHTML = `<div class='round-header'>${labelMap[rk]}</div>`;
            rounds[rk].forEach(m => {
                const s = scheduledMatches.find(sm => sm.matchId === m.id);
                const me = document.createElement('div');
                me.className = 'tree-match';
                me.innerHTML = `<div class='tree-team'><span>${m.teamA}</span></div><div class='tree-team'><span>${m.teamB}</span></div><div class='tree-footer'>🕒 ${s ? s.date + ' P' + s.periodIndex : '待排定'}</div>`;
                rd.appendChild(me);
            });
            tree.appendChild(rd);
        });
        container.appendChild(tree);
    });
}
"""

    # 執行替換
    import re
    # 替換側邊欄分組與排序
    content = re.sub(r"matchesData\.forEach\(m => \{[\s\S]*?const sortOrder = \[[\s\S]*?\];", sidebar_logic, content)
    
    # 替換 renderBracketTree 函數
    content = re.sub(r"function renderBracketTree\(matches, container\) \{[\s\S]*?container\.appendChild\(tree\);\s*\}", new_bracket_logic, content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("All badminton categories merged into one single dashboard.")

if __name__ == "__main__":
    merge_all_badminton()
