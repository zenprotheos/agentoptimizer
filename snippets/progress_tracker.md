---
title: "Progress Tracker — Anti-Drift Template Design & Prompt Engineering"
created: "2025-08-27T13:30:00.000Z"
type: "snippet"
purpose: "Comprehensive prompt engineering design for progress tracker with anti-drift guardrails and markdown-only approach"
task: "Clean_GlobalDocs_Implementation"
status: "Active"
priority: "High"
tags: ["snippets", "progress-tracker", "prompt-engineering", "anti-drift", "guardrails"]
---

# Progress Tracker — Anti-Drift Template Design & Prompt Engineering

## 🎯 **Purpose**
Design a bulletproof progress tracker template that prevents AI drift, ensures consistent behavior, and uses markdown checkboxes (no JSON complexity). Based on successful patterns from `2025-08-27_workspace_reorganization_and_consistency_update.md`.

## 📋 **Key Anti-Drift Patterns Identified**

### **Pre-Action AI Reminder Structure**
1. **🚨 CRITICAL AI REMINDER - READ BEFORE EVERY ACTION** header
2. **📋 PRIMARY MISSION** - clear, specific objective
3. **🎯 KEY PRINCIPLES TO REMEMBER** - numbered list of core rules
4. **⚠️ MANDATORY ACTIONS AFTER EACH TASK** - checkbox protocol

### **Post-Completion AI Reminder Structure**
1. **🚨 POST-COMPLETION AI REMINDER** header
2. **✅ WHEN ALL TASKS COMPLETE** - numbered completion steps
3. **📋 BEFORE MARKING COMPLETE** - final validation checklist
4. **Remember:** statement - reinforces goal/purpose

### **Progress Tracking Pattern**
- Detailed phase breakdown with sub-checkboxes
- ✅ completion indicators vs [ ] pending
- **Completion Notes** sections with timestamps and specific achievements
- Cross-reference validation built into process

---

## 📐 **Comprehensive Agent Prompt Template**

### **Core Instruction Set (Copy-Paste for Agents)**

```markdown
You are a task execution assistant. Follow this template EXACTLY to create a progress tracker.

**USER REQUEST:** <<INSERT_USER_REQUEST_HERE>>

**YOUR TASK:** Create a markdown progress tracker following the anti-drift template below.

### ANTI-DRIFT TEMPLATE (Use this structure):

```markdown
---
title: "Progress Tracker: [TASK_NAME]"
created: "[ISO_TIMESTAMP]"
type: "planning"
purpose: "[ONE_SENTENCE_DESCRIPTION]"
task: "[PARENT_TASK_NAME]"
status: "Active"
priority: "[High/Medium/Low]"
tags: ["progress", "tracker", "[domain_tags]"]
---

# 🚨 **CRITICAL AI REMINDER - READ BEFORE EVERY ACTION** 🚨

## 📋 **PRIMARY MISSION**
[CLEAR_SINGLE_OBJECTIVE_STATEMENT]

## 🎯 **KEY PRINCIPLES TO REMEMBER**
1. **[PRINCIPLE_1]**: [DESCRIPTION]
2. **[PRINCIPLE_2]**: [DESCRIPTION]
3. **[PRINCIPLE_3]**: [DESCRIPTION]
4. **[PRINCIPLE_4]**: [DESCRIPTION]
5. **[PRINCIPLE_5]**: [DESCRIPTION]

## ⚠️ **MANDATORY ACTIONS AFTER EACH TASK**
- [ ] **Update This Progress Tracker**: Mark completed items as ✅
- [ ] **Cross-Reference Check**: Ensure no conflicts with other documents
- [ ] **Validation**: [TASK_SPECIFIC_VALIDATION]
- [ ] **Documentation Update**: Update relevant documentation with progress

---

# [TASK_NAME]

## 📊 **Current Status Assessment**

### **[ASSESSMENT_CATEGORY_1]**
- [ ] **[ITEM_1]**: [DESCRIPTION]
- [ ] **[ITEM_2]**: [DESCRIPTION]
  - Sub-item A
  - Sub-item B

### **[ASSESSMENT_CATEGORY_2]**
- [ ] **[ITEM_1]**: [DESCRIPTION] - ✅ **[STATUS]**
- [ ] **[ITEM_2]**: [DESCRIPTION] - ✅ **[STATUS]**

## 📋 **SYSTEMATIC EXECUTION CHECKLIST**

### **Phase 1: [PHASE_NAME]**
- [ ] **1.1** [SPECIFIC_ACTION]
- [ ] **1.2** [SPECIFIC_ACTION]
- [ ] **1.3** [SPECIFIC_ACTION]
  - [ ] Sub-action A
  - [ ] Sub-action B
  - [ ] Sub-action C

### **Phase 2: [PHASE_NAME]**
- [ ] **2.1** [SPECIFIC_ACTION]
- [ ] **2.2** [SPECIFIC_ACTION]

[CONTINUE_FOR_ALL_PHASES]

## 🔄 **PROGRESS TRACKING PROTOCOL**

### **After Each Completed Task:**
1. ✅ **Mark the checkbox above**
2. 📝 **Add completion notes below**
3. 🔍 **Check for conflicts with other documents**
4. 📋 **Update related documents if needed**
5. 🔄 **Regenerate indexes if structure changed**

### **Completion Notes Section**
**Phase 1 Notes:**
- [APPEND_COMPLETION_NOTES_HERE]

**Phase 2 Notes:**
- [APPEND_COMPLETION_NOTES_HERE]

## 🎯 **SUCCESS CRITERIA**

### **[CRITERIA_CATEGORY_1]**
- [ ] [SPECIFIC_MEASURABLE_OUTCOME]
- [ ] [SPECIFIC_MEASURABLE_OUTCOME]

### **[CRITERIA_CATEGORY_2]**
- [ ] [SPECIFIC_MEASURABLE_OUTCOME]
- [ ] [SPECIFIC_MEASURABLE_OUTCOME]

---

# 🚨 **POST-COMPLETION AI REMINDER** 🚨

## ✅ **WHEN ALL TASKS COMPLETE:**
1. **[FINAL_ACTION_1]**: [DESCRIPTION]
2. **[FINAL_ACTION_2]**: [DESCRIPTION]
3. **[FINAL_ACTION_3]**: [DESCRIPTION]
4. **[FINAL_ACTION_4]**: [DESCRIPTION]
5. **Mark This Task Complete**: Update status to "Completed"

## 📋 **BEFORE MARKING COMPLETE:**
- [ ] All checkboxes above are ✅ (100% completion confirmed)
- [ ] All completion notes filled in
- [ ] No conflicts remain between documents
- [ ] [TASK_SPECIFIC_VALIDATION_1]
- [ ] [TASK_SPECIFIC_VALIDATION_2]

**Remember: [REINFORCEMENT_OF_PRIMARY_GOAL]**
```

### AGENT INSTRUCTIONS:
1. Replace ALL bracketed placeholders with specific content
2. Generate 3-7 phases with 2-5 sub-tasks each
3. Make all actions SPECIFIC and MEASURABLE
4. Include domain-specific validation steps
5. Ensure the Primary Mission is crystal clear
6. Add relevant principles that prevent scope creep
7. Create Success Criteria that are binary (done/not done)
```

---

## 🛡️ **Anti-Drift Guardrails & Prompt Engineering Best Practices**

### **1. Specificity Enforcement**
- **Problem**: Vague instructions lead to agent confusion
- **Solution**: Use measurable, actionable verbs (Count, Move, Update, Validate, Generate)
- **Example**: "Review files" → "Count current root files and identify which exceed the 4-file limit"

### **2. Context Anchoring**
- **Problem**: Agents lose track of original objective
- **Solution**: Primary Mission statement that's impossible to misinterpret
- **Pattern**: "Apply [SPECIFIC_CONCEPT] to [SPECIFIC_TARGET] and ensure [SPECIFIC_OUTCOME]"

### **3. Cognitive Load Management**
- **Problem**: Too many simultaneous instructions cause errors
- **Solution**: Phase-based execution with clear dependencies
- **Pattern**: Phase 1 (Foundation) → Phase 2 (Implementation) → Phase 3 (Validation)

### **4. Validation Loops**
- **Problem**: Agents complete tasks without verification
- **Solution**: Mandatory validation steps built into every phase
- **Pattern**: Complete → Validate → Document → Cross-check

### **5. State Preservation**
- **Problem**: Agents forget previous work in long sessions
- **Solution**: Completion Notes with timestamps and specific achievements
- **Pattern**: "[ISO_TIMESTAMP] — [SPECIFIC_ACCOMPLISHMENT] with [EVIDENCE]"

### **6. Scope Boundary Enforcement**
- **Problem**: Feature creep and scope expansion
- **Solution**: Key Principles that explicitly limit scope
- **Example**: "Maximum 4 primary files in root directory" (hard constraint)

### **7. Error Recovery Patterns**
- **Problem**: Agents get stuck on failed steps
- **Solution**: Built-in fallback instructions and escalation paths
- **Pattern**: "If X fails, try Y. If Y fails, document the issue and continue."

---

## 📊 **Template Effectiveness Metrics**

### **Indicators of Success**
- [ ] Agent completes 95%+ of checklist items without human intervention
- [ ] Zero scope creep beyond defined boundaries
- [ ] All completion notes contain specific timestamps and achievements
- [ ] Cross-references remain accurate throughout execution
- [ ] Final deliverable matches Success Criteria exactly

### **Red Flags (Drift Indicators)**
- ❌ Vague completion notes ("completed successfully")
- ❌ Skipped validation steps
- ❌ Missing timestamps in progress updates
- ❌ Broken cross-references after file operations
- ❌ Scope expansion beyond Key Principles

---

## 🔧 **Implementation Guidelines**

### **File Placement**
- Store template at: `snippets/progress_tracker.md`
- Include full prompt in same file (no separate usage doc)
- Add example renders under `tasks/.../subtasks/example_*.md`

### **Agent Usage Pattern**
1. Human provides task description
2. Agent applies the prompt template (fills all brackets)
3. Agent saves rendered tracker to `tasks/YYYY-MM-DD_TaskName/subtasks/`
4. Agent executes phases, updating checkboxes and notes
5. Agent completes final validation before marking done

### **Quality Assurance**
- Every rendered tracker must pass the anti-drift checklist
- All placeholders must be replaced with specific content
- Success Criteria must be binary (measurable yes/no outcomes)
- Completion Notes must include evidence of work done

---

## 📚 **Example Scenarios & Variations**

### **Code Refactoring Task**
- Primary Mission: "Refactor X module for Y performance improvement"
- Key Principles: No breaking changes, maintain test coverage, preserve API
- Phases: Analysis → Planning → Implementation → Testing → Documentation

### **Documentation Organization**
- Primary Mission: "Reorganize docs for Z navigation improvement"
- Key Principles: Preserve links, maintain searchability, follow style guide
- Phases: Audit → Structure → Migration → Validation → Index Update

### **Feature Implementation**
- Primary Mission: "Implement X feature with Y requirements"
- Key Principles: Match specifications, include tests, update docs
- Phases: Design → Core Logic → Integration → Testing → Documentation

---

**Remember: The goal is bulletproof agent guidance that prevents drift, ensures completion, and maintains quality standards across all task types.**