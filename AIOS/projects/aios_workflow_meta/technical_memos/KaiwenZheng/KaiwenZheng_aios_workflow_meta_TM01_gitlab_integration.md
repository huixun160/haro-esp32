# **Technical Memo 1 — AIOS Workflow GitLab Integration Project (v1)**





> This memo defines the **initial setup of GitLab-based collaboration** for the AIOS workflow.

> This is the **first memo of a new project**: migrating from local Git usage to **team-level GitLab coordination**.



------



**Title:** Initialize GitLab Integration and Branch Strategy for AIOS Workflow



**Project:** AIOS Workflow Infrastructure (New Project)



**Subsystem:** Build / System Integration / Collaboration Infrastructure



**Author:** AIOS Architecture Team



**Priority:** HIGH



**Date:** 2026-03-24



------





## **Background**





The AIOS workflow has recently been upgraded to support:



- multi-engineer collaboration
- multi-project execution
- memo-driven development
- shared knowledge (pitfalls, feedback, registry)





However, current collaboration is still based on:

```
local git per engineer
```

This creates major problems:



1. Engineers do not know what others have implemented
2. API definitions diverge silently
3. Pitfall knowledge is not synchronized
4. No single source of truth exists
5. System state is fragmented across machines





Given the high cost of iteration on feature phones (~30 min per cycle), this inefficiency compounds quickly.



Therefore:



> GitLab must become the **central coordination layer** for AIOS workflow.



------





## **Objective**





Establish a **GitLab-based collaboration system** integrated with AIOS workflow.



This memo must achieve:





### **1. Single Repository Setup**





All engineers work on:

```
git@192.168.0.92:feature-phone/fp-aios-kz.git
```

or:

```
http://192.168.0.92/feature-phone/fp-aios-kz.git
```



------





### **2. Branch Strategy**





Each engineer + project must map to a branch:

```
eng/<engineer>/<project>
```

Example:

```
eng/A/featurephone_secure
eng/B/dap_runtime
```



------





### **3. Workflow Integration**





- /aios-close must guide engineers to push changes
- commit must include TM reference
- feedback / docs / registry must be included in push





------





### **4. First-Time Setup Guidance**





Engineers must be able to:



- configure Git
- configure SSH key (macOS / Windows)
- alternatively use HTTP





------





## **Current State**





- AIOS workflow supports multi-engineer/project structure
- Manifest, agents, skills, hooks already exist
- Git usage is **local only**
- No enforced remote synchronization
- No standardized branch naming
- No onboarding guide for GitLab





------





## **Scope**





This memo includes:



1. GitLab remote configuration
2. Branch naming policy
3. /aios-close integration with Git instructions
4. SSH and HTTP setup instructions
5. README update





------





## **Out of Scope**





- CI/CD pipelines
- merge request policies
- automated testing
- permission system





------





## **Constraints**





1. Must support both macOS and Windows
2. Must work with internal GitLab server (192.168.0.92)
3. Must not require advanced Git knowledge
4. Must be executable by junior engineers





------





## **Expected Deliverables**







### **1. GitLab Integration Section in Manifest**





Update:

```
workflow/manifest.yaml
```

Add:

```
git:
  remote:
    ssh: git@192.168.0.92:feature-phone/fp-aios-kz.git
    http: http://192.168.0.92/feature-phone/fp-aios-kz.git
  branch_pattern: eng/{engineer}/{project}
```



------





### **2.** 

### **/aios-close**

###  **Enhancement**





Modify /aios-close to output:



- current engineer
- current project
- correct branch name
- GitLab push instructions





------





### **3. README_WORKFLOW.md (MANDATORY)**





Create or update:

```
AIOS/README_WORKFLOW.md
```



------





## **README — GitLab Setup Section**







### **Step 1 — Clone Repository**







#### **macOS / Linux (SSH recommended)**



```
git clone git@192.168.0.92:feature-phone/fp-aios-kz.git
```



#### **Windows (HTTP recommended if SSH not configured)**



```
git clone http://192.168.0.92/feature-phone/fp-aios-kz.git
```



------





### **Step 2 — Configure Git Identity**



```
git config --global user.name "YourName"
git config --global user.email "your@email.com"
```



------





### **Step 3 — Create Engineer Project Branch**



```
git checkout -B eng/<engineer>/<project>
```

Example:

```
git checkout -B eng/A/featurephone_secure
```



------





## **SSH Setup (macOS / Linux)**







### **Generate SSH Key**



```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter for default path.



------





### **Start SSH Agent**



```
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```



------





### **Copy Public Key**



```
cat ~/.ssh/id_ed25519.pub
```

Add it to GitLab:

```
GitLab → Settings → SSH Keys → Add Key
```



------





### **Test Connection**



```
ssh -T git@192.168.0.92
```



------





## **SSH Setup (Windows)**







### **Option A — Git Bash (Recommended)**



```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Then:

```
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```



------





### **Option B — Use HTTP (Simpler)**





No SSH required:

```
git clone http://192.168.0.92/feature-phone/fp-aios-kz.git
```



------





## **Step 4 — Commit and Push**



```
git add .
git commit -m "TM-001 initialize gitlab integration"
git pull --rebase origin eng/<engineer>/<project>
git push -u origin eng/<engineer>/<project>
```



------





## **Step 5 — Workflow Rule**





Every memo completion must include:



- code
- docs
- registry updates
- feedback file





And must be pushed to GitLab.



------





## **Verification Method**





- Repository successfully cloned
- SSH connection works (optional)
- Engineer branch created correctly
- Commit includes TM reference
- Push to GitLab successful
- /aios-close outputs correct instructions





------





## **Potential Risks**







### **Risk 1 — SSH misconfiguration**





Mitigation:



- Provide HTTP fallback





------





### **Risk 2 — Incorrect branch naming**





Mitigation:



- enforce via /aios-close + hook





------





### **Risk 3 — Engineers forget to push**





Mitigation:



- enforce via workflow rules





------





## **References**





- AIOS Workflow Architecture
- Technical Memo 40 — Multi-Engineer Workflow
- GitLab Internal Server (192.168.0.92)





------





# **Final Note**





This memo is the **starting point of team-scale execution**.



Before this:

```
AIOS = single-engineer system
```

After this:

```
AIOS = coordinated multi-engineer system
```

If GitLab is not enforced:



> everything else in the workflow will eventually collapse.



