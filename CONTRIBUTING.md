# Contributing

Contributions are welcome, especially for original genre engines, format routing, platform-aware validation patterns, production-pack tooling and reproducible quality checks.

Before opening a pull request:

1. Keep concrete story characters, scenes and dialogue original or properly licensed.
2. Do not commit private series Bibles, likeness／voice assets, credentials, cookies or generated media with unclear rights.
3. Keep `SKILL.md` focused on routing and hard rules; put detailed knowledge in `references/`.
4. Run `python -m py_compile scripts/drama_lint.py scripts/studio_lint.py`, `python -m unittest discover -s tests -v`, and validate all changed JSON files.
5. Add or update an eval case when changing a core behavior.
6. Date and cite volatile model capabilities, platform policies and rankings; do not encode them as permanent facts.

<!-- freedom-repository-guide:start -->
## 自由工坊：從一個成果到一個 PR

媒體與音樂公會的短劇敘事、製作包與剪輯交接技能來源。 保留上游 Skill、故事／Studio schemas、lint、範例和測試。

先看[本倉 Issues](https://github.com/FreeTWAI/ai-short-drama/issues)與[現有 PR](https://github.com/FreeTWAI/ai-short-drama/pulls)。提出問題、這一輪範圍、完成條件與可投入時間，在 Issue 認領並協調重疊工作；維護者已直接派工時不必重複等待，將約定連回交接即可。使用自己的 fork／分支，PR 送到 **FreeTWAI/ai-short-drama:main**。

交給 Agent 前先讓它讀 [AGENTS.md](AGENTS.md)。PR 寫明變更用途、使用者可見結果、驗證命令、限制與原 Issue；附上可公開的合成案例或重現方式。Issue／PR 是程式協作的記錄，平台名片與公會身分不取代 repo 維護者的審查。

原創劇本、授權素材與具日期模型能力分開保存。私人 Bible／角色／肖像素材不送平台；中央只連可公開成果與 repo。

### 這個模組怎麼驗證

選擇與修改範圍相符的既有入口：

```sh
python3 -m unittest discover -s tests -v
python3 scripts/studio_lint.py examples/studio-plan.example.json --studio-ready
```

命令列在這裡不表示本輪已執行。先核對依賴與環境，再記錄實際結果；缺工具、桌面、媒體或授權時寫 `not_run` 與原因，不能補造成功。純文件修改以連結／路徑核對與 `git diff --check` 為主。

### 署名與上游

工坊 Fork：上游產品／授權來源為 [Hao0321/ai-short-drama](https://github.com/Hao0321/ai-short-drama)；本次協作的 Issue／PR 送到 **FreeTWAI/ai-short-drama**，不是自動送往上游。 保留原作者與授權檔，另列真正完成文件、測試、設計、程式或協作的人。使用 AI 時如實交代協作範圍；只有實際 GitHub PR／review／合併紀錄可以作為對應貢獻證據，不能靠自填帳號推定。

自願貢獻不保證案源、XP、收益或雇用。若產生付費合作，由當事人另定條款與 Seller 外部收款；平台不代收。秘密、客戶資料、真實交易單據與未授權素材不進公開 Issue／PR。
<!-- freedom-repository-guide:end -->
