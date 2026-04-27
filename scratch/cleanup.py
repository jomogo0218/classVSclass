"""
cleanup.py - Remove unnecessary files to slim down the project
"""
import os
import shutil

TO_DELETE_FILES = [
    # Temp/test/debug scripts in root
    'test_syntax.js',        # 205 KB! 僅用於語法測試，已無用
    'test_parse.py',
    'test_encoding.py',
    'check_diff.py',
    'check_dupes.py',
    'check_music_conflict.py',
    'report_dupes.py',
    'extract_table.py',
    'list_matches.py',
    'process_data.py',
    'build_local.py',
    'mega_build.py',
    'schedule_data.json',    # 87 KB - 不明來源的舊資料
    'app_v4.js',             # 17.5 KB - 舊版本
    'style_v4.css',          # 15.3 KB - 舊版本
    'matches.json.new',      # 空檔案
    'matches_cleaned.json',  # 中間產物
    'dupe_report.txt',       # 診斷用，已無需要
    'SUBJECT_USAGE_REPORT.txt',
    'FULL_NAME_REPORT.txt',
    'DUPLICATE_CHECKLIST.md',
    'RECOVERY_LOG_0422.md',
    'REQUIREMENTS.md',
    'PROJECT_STATUS.md',
    'CHANGELOG.md',          # 已整合到 git commit messages

    # Scratch folder - only keep essential tools
    'scratch/extracted.js',           # 138 KB - 舊的提取備份
    'scratch/extracted_final.js',     # 137 KB - 舊的提取備份
    'scratch/extracted_perfect.js',   # 140 KB - 舊的提取備份
    'scratch/restored_functions.js',  # 7.7 KB - 舊備份

    # All the old build scripts that were replaced by guaranteed_build.py
    'scratch/ultimate_v7_nuclear_build.py',
    'scratch/ultimate_v7_nuclear_build_v2.py',
    'scratch/ultimate_v10_full_restore.py',
    'scratch/ultimate_mega_integration.py',
    'scratch/ultimate_mega_integration_v2.py',
    'scratch/ultimate_stability_fix.py',
    'scratch/ultimate_fix.py',
    'scratch/absolute_no_error_build.py',
    'scratch/absolute_final_victory.py',
    'scratch/absolute_final_manual_build.py',
    'scratch/absolute_final_manual_build_v2.py',
    'scratch/perfect_v4_build.py',
    'scratch/final_clean_v11.py',
    'scratch/final_surgical_v8.py',
    'scratch/final_perfect_v6_build.py',
    'scratch/final_stitch.py',
    'scratch/final_perfect_stitch.py',
    'scratch/final_clean_stitch.py',
    'scratch/final_victory_brute_force.py',
    'scratch/final_victory_clean.py',
    'scratch/final_delivery_guaranteed.py',
    'scratch/final_stable_overhaul.py',
    'scratch/final_dashboard_fix.py',
    'scratch/final_polish_theme.py',
    'scratch/full_feature_restore_v9.py',
    'scratch/full_matrix_generator.py',
    'scratch/fix_and_enhance_v3.py',
    'scratch/build_organized_system.py',
    'scratch/reference_style_overhaul.py',
    'scratch/overhaul_app_js.py',
    'scratch/patch_appjs.py',
    'scratch/restore_core_and_build.py',
    'scratch/upgrade_matrix_dashboard.py',
    'scratch/upgrade_real_data.py',
    'scratch/mega_data_regeneration.py',
    'scratch/deep_data_update.py',
    'scratch/deep_clean_matches.py',
    'scratch/split_badminton_v5.py',
    'scratch/merge_badminton.py',
    'scratch/sync_xlsx.py',
    'scratch/update_app_js.py',
    'scratch/update_index.py',
    'scratch/update_index_html.py',
    'scratch/update_index_html_v2.py',
    'scratch/update_9th_period.py',
    'scratch/update_results.py',
    'scratch/consolidate_tabs.py',
    'scratch/count_duplicates.py',
    'scratch/fix_encoding.py',
    'scratch/clean_to_96.py',
    'scratch/clean_db.py',
    'scratch/check_88.py',
    'scratch/check_ids.py',
    'scratch/rewrite_print_slip.py',  # replaced by fix_and_inject.py
    'scratch/excel_data.txt',         # temp data cache
    'scratch/team_names.json',

    # Old Excel - superseded by 4_24 version
    'CHSH_Sports_Matches_2026_4_19.xlsx',
]

TO_DELETE_DIRS = [
    'image',   # screenshots used in docs only, not needed for app
]

deleted_size = 0
deleted_count = 0
failed = []

for f in TO_DELETE_FILES:
    if os.path.exists(f):
        size = os.path.getsize(f)
        os.remove(f)
        deleted_size += size
        deleted_count += 1
        print(f'DEL  {size/1024:7.1f} KB  {f}')
    else:
        print(f'SKIP (not found): {f}')

for d in TO_DELETE_DIRS:
    if os.path.exists(d):
        size = sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(d) for f in fs)
        shutil.rmtree(d)
        deleted_size += size
        deleted_count += 1
        print(f'DEL  {size/1024:7.1f} KB  {d}/ (dir)')

print()
print(f'Deleted {deleted_count} items, freed {deleted_size/1024:.0f} KB')
