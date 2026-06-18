# Rule: Git Manual Commit + Push

AI must NOT execute `git add`, `git commit`, or `git push` commands directly.

Instead, AI must guide the engineer through manual git operations:

1. **Check git status** — Verify the repository is initialized (`git init` if needed)
2. **List changes** — Show the engineer what files were created/modified/deleted
3. **Suggest commit commands** — Provide the exact git commands to run:
   ```
   git add <files>
   git commit -m "<descriptive message>

   Memo: TM-<number>
   Author: <engineer>
   Project: <project>"
   ```
4. **Wait for commit confirmation** — Engineer must confirm that the commit was successful
5. **Suggest push commands** — After commit, provide push instructions:
   ```
   git push -u origin eng/<engineer>/<project>
   ```
   If first time, also suggest creating the branch:
   ```
   git checkout -B eng/<engineer>/<project>
   git push -u origin eng/<engineer>/<project>
   ```
6. **Wait for push confirmation** — Engineer must confirm push was successful
7. **Fallback** — If GitLab is unavailable, engineer may continue local-only and push later

> ⚠️ Push is mandatory when GitLab is available. All workflow artifacts (code, docs, registry, feedback) must be pushed.
