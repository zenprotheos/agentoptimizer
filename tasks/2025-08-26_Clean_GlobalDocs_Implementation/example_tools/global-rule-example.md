---
alwaysApply: true
title: "Global Cursor AI Rule for VoiceScribeAI"
created: "2025-08-27T02:10:00.000Z"
type: "example"
purpose: "Example global rule demonstrating task workflow and validation standards"
status: "Active"
summary: "Task workflow, validation, and documentation standards adapted for the VoiceScribeAI Flask app (port 5000)."
module: "global"
tags: ["rules", "workflow", "validation", "documentation"]
---

## Goal & Usage
Use these rules for all tasks in VoiceScribeAI. Prioritize internal MVP functionality first; UI polish and production hardening can follow.

## Quick Facts
- App: Flask (Python)
- Run: `python main.py`
- Local URL: `http://localhost:5000`
- Scripts live in `tools/`

## Must Read Before Any Task
- `docs/doc_index.md` (generate if missing): `node tools/indexing/build-index.cjs`
- `docs/CONTROL/Progress-Tracker.md` (global task tracker) 
- `docs/development/development_roadmap_2025.md` (current phase context)
- `docs/product_planning/README.md` (task-specific document guide)
- Mermaid standards: `\.cursor\rules\mermaid-rule.mdc`

Extract scope, current status, and relevant prior decisions before you start.

## Step 0.6: Product Planning Consultation (MANDATORY FOR IMPLEMENTATION TASKS)

### Task Type Detection and Document Requirements
**BEFORE implementing any feature, UI, or API, the AI agent MUST:**

1. **UI/UX Tasks** → MANDATORY: Read wireframes first
   - **Primary**: `docs/product_planning/09_mvp_wireframes.md`
   - **Supporting**: `docs/product_planning/05_information_architecture.md`
   - **Context**: `docs/product_planning/03_user_journey_map.md`
   - **Action**: Check current implementation against specified design, document deviations

2. **API Development Tasks** → MANDATORY: Follow technical blueprint
   - **Primary**: `docs/product_planning/07_technical_blueprint.md`
   - **Supporting**: `docs/product_planning/06_functional_specifications.md`
   - **Context**: `docs/product_planning/04_edge_cases_and_exceptions.md`
   - **Action**: Ensure API design matches specifications, update specs if requirements change

3. **Feature Implementation Tasks** → MANDATORY: Align with functional specs
   - **Primary**: `docs/product_planning/06_functional_specifications.md`
   - **Supporting**: `docs/product_planning/02_personas_and_jobs_to_be_done.md`
   - **Context**: `docs/product_planning/01_vision_and_success_criteria.md`
   - **Action**: Verify acceptance criteria are met, update specs if requirements evolve

### Implementation Alignment Protocol
**When implementation must deviate from specifications:**
1. **Document deviation reason** in task workspace troubleshooting document
2. **Update relevant planning document** to reflect new approach  
3. **Cross-reference changes** in multiple documents if needed
4. **Validate consistency** across all affected specifications

### Bidirectional Sync Requirements
**After completing implementation:**
1. **Compare final implementation** with original specifications
2. **Update planning documents** to reflect actual implementation
3. **Document lessons learned** for future specifications  
4. **Ensure consistency** across all related planning docs

## Roadmap Awareness & Intelligent Task Management (CRITICAL)

### Step 0.5: Roadmap Context Check (MANDATORY BEFORE ANY TASK)
**BEFORE starting ANY task, the AI agent MUST:**
1. **Read Progress-Tracker**: `docs/CONTROL/Progress-Tracker.md` for current roadmap context
2. **Identify Current Position**: Phase, week, milestone status, and completion percentages
3. **Review Next Steps Queue**: Check prioritized tasks in progress tracker
4. **Assess Roadmap Alignment**: Ensure user request aligns with current phase objectives

### Roadmap-Aware Task Suggestion Logic (ALWAYS APPLY)
**When user asks "what should we work on next?" or similar, ALWAYS:**

1. **Context Analysis**:
   - Read Progress-Tracker for current phase/week/milestone
   - Check roadmap documents for phase objectives
   - Identify completed vs pending milestone requirements

2. **Priority Assessment**:
   ```
   CRITICAL: Tasks blocking current milestone completion
   HIGH: Tasks enabling current milestone progress
   MEDIUM: Tasks preparing for next milestone
   LOW: Tasks from future phases
   DEFER: Tasks not in current roadmap scope
   ```

3. **Intelligent Response Format**:
   ```
   "Based on our current roadmap position ([Phase X, Week Y]), I recommend focusing on [specific task] because:
   
   📍 **Current Context**: [milestone name] is [X%] complete
   🎯 **Roadmap Alignment**: This task directly supports [phase objective]
   ⏱️ **Timeline Impact**: Completing this keeps us on track for [milestone/phase]
   
   Alternative: If you prefer to work on [user's request], we can do that, but [roadmap-aligned task] would be more strategic because [reasoning based on roadmap context]."
   ```

4. **Always Provide**:
   - Primary recommendation (roadmap-aligned)
   - Clear rationale based on current roadmap position
   - Alternative options if user request differs
   - Impact assessment on milestone/phase progress

### Enhanced Task Creation Protocol (MANDATORY)
**When creating ANY task workspace, ALWAYS:**

1. **Include Roadmap Context** in implementation-plan:
   ```markdown
   ## Roadmap Alignment
   **Current Phase**: [Phase name]
   **Current Milestone**: [Milestone name] 
   **Milestone Progress**: [X%] complete
   **Phase Objective**: [Description from roadmap]
   **Task Priority**: [CRITICAL/HIGH/MEDIUM/LOW based on roadmap]
   **Dependencies**: [List from roadmap analysis]
   
   ## Product Planning Alignment
   **Task Type**: [UI/UX | API | Feature | Architecture]
   **Primary Planning Document**: [Required document from Step 0.6]
   **Key Specifications**: [Summary of relevant specs]
   **Implementation Deviations**: [Document any required changes]
   **Bidirectional Sync Plan**: [How planning docs will be updated]
   ```

2. **Reference Phase Objectives**: Explicitly connect task scope to current phase goals
3. **Align Deliverables**: Ensure task outputs support milestone requirements AND product planning specifications
4. **Plan Specification Updates**: Include plan for updating product planning documents based on implementation results

### Progress Tracking & Updates (MANDATORY)
**After completing ANY task:**

1. **Update Progress-Tracker** with:
   - Task completion status and date
   - Milestone progress percentage update
   - Assessment of phase completion status
   - Updated Next Steps Queue

2. **Product Planning Synchronization**:
   - Compare final implementation with original specifications
   - Update relevant planning documents to reflect actual implementation
   - Document any specification changes in the planning docs
   - Ensure consistency across all affected planning documents

3. **Roadmap Alignment Check**:
   - Verify milestone progress is accurate
   - Check if phase transition is appropriate
   - Update roadmap alignment tracker
   - Flag any roadmap deviations

4. **Next Steps Suggestion**:
   - Automatically suggest next logical tasks
   - Prioritize based on updated roadmap context
   - Identify newly available tasks (dependency completion)
   - Recommend phase transition tasks if phase is complete

### Dynamic Priority Adjustment (SMART FEATURE)
**When user requests differ from roadmap priorities:**

1. **Rapid Impact Analysis**:
   - Assess request against current milestone requirements
   - Calculate delay impact on phase completion
   - Identify dependency conflicts

2. **Intelligent Options**:
   - **ALIGN**: Modify request to fit roadmap (if possible)
   - **DEFER**: Suggest scheduling for appropriate roadmap phase
   - **URGENT OVERRIDE**: If truly critical, document deviation and impact
   - **HYBRID**: Find compromise that advances both user need and roadmap

3. **Always Explain**: Provide clear reasoning for recommendations with roadmap context

### Automated Consistency Validation
**The AI agent continuously monitors:**
- Progress-Tracker vs actual task completion status
- Roadmap documents alignment with each other
- Milestone progress vs reported task completions
- Phase transition readiness based on completion criteria

**Auto-flag inconsistencies** and suggest corrections when detected.

## Step 0: Current Date
```bash
node tools/automation/date-current.cjs
```
Use the YYYY-MM-DD output for task naming, timestamps, and notes.

## Step 1: Minimal Pre-Task Scan
- Read `README.md` for run instructions
- Skim `docs/development/README.md` if present

## Step 2: Task Workspace (Docs-Only)
Create a timestamped task folder under `docs/tasks/`:

```
docs/tasks/YYYY-MM-DD_[TaskName]/
├── MASTER_Architecture_UMLs_[TaskName].md
├── implementation-plan_[TaskName].md
├── development-progress-tracker_[TaskName].md
├── troubleshooting_[TaskName].md
├── completion-summary_[TaskName].md
└── tests/
```

Notes:
- Include proper front-matter in every `.md` file
- For diagrams, follow your team Mermaid standards (if `docs/global_docs/ui_patterns/mermaid-diagram-standards.md` exists, conform to it)

### Step 2.1: Comprehensive UML Documentation (IMMEDIATELY after creating MASTER_Architecture_UMLs_[TaskName].md)
**IMMEDIATELY after creating** `MASTER_Architecture_UMLs_[TaskName].md`, update it with:
- **Comprehensive UML diagrams** showing ALL system interactions
- **Multiple root cause analysis** - never stop at first issue found
- **Race condition mapping** - identify ALL timing dependencies
- **Data flow analysis** - trace complete data lifecycle
- **State management audit** - map ALL state changes and conflicts

## Step 3: Implementation & Validation
- Start app: `python main.py`
- Prevent multiple servers: only one terminal runs the app
- URL check (PowerShell):
```powershell
tools/validation/url-test.ps1 -Url "http://localhost:5000" -VerboseMode
```
- Browser validation (manual): open `http://localhost:5000` and navigate key pages

### Step 3.5: MANDATORY AUTOMATED TESTING (BEFORE COMPLETION)
**CRITICAL: ALL TASKS MUST PASS AUTOMATED TESTS BEFORE MARKING COMPLETE**

#### Core Testing Requirements
1. **Create Task-Specific Test Script**: Every implementation task MUST create automated tests
2. **Test All Modified Functionality**: Every changed endpoint, UI component, and flow
3. **Test Existing Functionality**: Ensure changes don't break existing features
4. **Exit Code Validation**: Tests must return exit code 0 (success) or 1 (failure)

#### Testing Tools & Scripts
- **Task-Specific Test Location**: Create ALL tests in `docs/tasks/YYYY-MM-DD_[TaskName]/tests/`
- **Global Test Reference**: Existing `python tools/testing/test_upload_flow.py` remains for reference

#### Testing Script Template
```python
#!/usr/bin/env python3
"""
Test script for [FEATURE_NAME] functionality
Location: docs/tasks/YYYY-MM-DD_[TaskName]/tests/test_[feature].py
Tests [specific functionality] end-to-end
"""
import requests
import sys
import os
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:5000"

def test_[feature]():
    """Test [specific feature] functionality"""
    try:
        # Test implementation here
        response = requests.get(f"{BASE_URL}/api/[endpoint]", timeout=10)
        if response.status_code == 200:
            print("✅ [Feature] test passed")
            return True
        else:
            print(f"❌ [Feature] test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ [Feature] test error: {e}")
        return False

if __name__ == "__main__":
    success = test_[feature]()
    print(f"🎯 Test Result: {'✅ PASSED' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)
```

#### MANDATORY Pre-Completion Testing Checklist
**BEFORE marking any task complete, ALL must pass:**
- [ ] **Core functionality test**: Primary feature works as intended
- [ ] **API endpoints test**: All new/modified endpoints respond correctly  
- [ ] **Integration test**: Feature integrates properly with existing system
- [ ] **Regression test**: Existing functionality still works
- [ ] **Error handling test**: Graceful failure and error messages
- [ ] **Edge case test**: Boundary conditions and unusual inputs

#### Test Execution Protocol
1. **Run Tests BEFORE Documentation Updates**: Never document broken features
2. **Fix Issues Before Proceeding**: If tests fail, fix code, don't lower test standards
3. **Regression Testing**: Always test existing features weren't broken
4. **Exit on Failure**: If any test fails, task is NOT complete

#### Example Test Execution
```bash
# Navigate to task test directory
cd docs/tasks/YYYY-MM-DD_[TaskName]/tests/

# Run individual tests
python test_[feature].py
# Returns exit code 0 (success) or 1 (failure)

# Run all task tests
for test in test_*.py; do python "$test" || exit 1; done
```

**FAILURE TO RUN TESTS = INCOMPLETE TASK**
No task can be marked complete without passing automated tests.

### AssemblyAI Integration Rule
- When implementing or modifying AssemblyAI features, always consult the latest AssemblyAI API documentation (webhooks, transcription status, request/response schemas) and align parameters accordingly. Prefer webhook-driven workflows over polling where possible.

## Step 4: Documentation Maintenance
1) Rebuild index after any docs change:
```bash
node tools/indexing/build-index.cjs
```
2) Validate front-matter (safe to run anytime):
```bash
node tools/automation/intelligent-front-matter-validator.cjs --fix
```

3) Refresh TOCs where needed:
```bash
node tools/automation/enhanced-toc-updater.cjs --all --verbose
```

4) On-demand drift check (duplicates + maintenance):
```bash
node tools/automation/drift-check.cjs
```

## Completion Summary Content Standards (Required)
- For each task, the completion summary must include:
  - Capabilities implemented in this task (concise, user-facing list)
  - Manual test checklist (step-by-step) to validate features locally
  - References to automated tests in `tests/` subfolder (commands to run, what they cover)
  - Test execution results with exit codes and specific validation coverage
  - Known limitations or items deferred

## Code Cleanliness
- Single source of truth: delete dead or duplicated logic when discovered
- Keep names consistent; remove unused imports/code when touching files

### Anti-Drift Measures (Mandatory)
- Maintain `docs/CONTROL/Progress-Tracker.md` as the single source of truth for:
  - Implemented features, in-progress work, planned work
  - Critical issues and resolutions
  - Decisions and rationales
- For each task:
  - Add an entry to the tracker with date, scope, files changed, and validation status
  - Link the task workspace path under `docs/tasks/`
- Avoid duplicate files and parallel implementations; consolidate to the newest canonical file

### **Source of Truth Hierarchy (Critical)**
**ALWAYS update the canonical location - never create duplicates:**
1. **API Specifications & Data Models**: `docs/global_docs/specs/` (canonical)
2. **Architecture & Planning**: `docs/product_planning/` (canonical)
3. **Process & Rules**: `docs/RULES/` (canonical)
4. **Task Workspaces**: `docs/tasks/` (temporary, cleaned after user confirmation)
5. **Cross-reference only** - if information exists in canonical location, reference it, don't duplicate it

### Naming & Structure
- Prefer clear, descriptive names over abbreviations
- Group persisted data under `storage/`
- Keep app logic under root modules (`services/`, `models.py`, `routes.py`) and avoid creating parallel folders that duplicate purpose

## Validation Requirements
- Port availability and URL response validated via PowerShell script
- Index rebuilt and `docs/doc_index.md` updated
- Front-matter valid across changed docs
- TOCs updated where structure changed
- Manual smoke test via browser for key routes: `/`, `/recordings`, `/transcriptions`, `/settings`
 - Global docs sync: update canonical docs where applicable
   - Architecture & IA (product planning docs)
   - Specs & Contracts (`docs/global_docs/specs/`)
   - Process & Rules (`docs/RULES/`)

## Completion Checklist

### **Phase 1: Task Implementation**
- Date acquired via `date-current.cjs`
- Task workspace created in `docs/tasks/`
- App runs on port 5000 without conflicts
- URL test passes with `url-test.ps1`
- **All 5 core task documents continuously updated throughout development**

### **Phase 1.5: MANDATORY AUTOMATED TESTING** ⚠️ **CRITICAL GATE**
- **✅ REQUIRED**: All automated tests MUST pass before proceeding to Phase 2
- **Core functionality test**: Primary feature works as intended
- **API endpoints test**: All new/modified endpoints respond correctly  
- **Integration test**: Feature integrates properly with existing system
- **Regression test**: Existing functionality still works
- **Error handling test**: Graceful failure and error messages
- **Test scripts created**: Task-specific automated tests implemented in `tests/` subfolder
- **Exit code 0**: All tests return success status
- **🚫 NO EXCEPTIONS**: Cannot proceed without passing tests

### **Phase 2: Task Finalization** 
- **Step 1**: Finalize all 5 core task documents with complete information:
  - `MASTER_Architecture_UMLs_[TaskName].md` - Complete system analysis
  - `implementation-plan_[TaskName].md` - Detailed implementation approach
  - `development-progress-tracker_[TaskName].md` - Final progress status
  - `troubleshooting_[TaskName].md` - All issues and resolutions documented
  - `completion-summary_[TaskName].md` - Capabilities + manual test checklist **WITH TEST RESULTS**

### **Phase 3: Global Documentation Sync**
- **Step 2**: Extract from core task documents to update global documentation:
  - API specifications → `docs/global_docs/specs/`
  - Architecture changes → `docs/product_planning/`
  - Process improvements → `docs/RULES/`
- **Step 3**: Cross-reference alignment between task docs and global docs
- Index rebuilt and front-matter validated
- TOCs regenerated where appropriate
- `docs/CONTROL/Progress-Tracker.md` updated (task entry + status + test results)
- Drift check run (`node tools/automation/drift-check.cjs`) and issues resolved

### Task Workspace Document Policy (Structured Workflow)

#### **Core Task Documents (Always Maintained)**
- **Always keep and update these 5 core documents throughout task lifecycle:**
  1. `MASTER_Architecture_UMLs_[TaskName].md` - Comprehensive system analysis
  2. `implementation-plan_[TaskName].md` - Detailed implementation approach
  3. `development-progress-tracker_[TaskName].md` - Real-time progress tracking
  4. `troubleshooting_[TaskName].md` - Issues encountered and resolutions
  5. `completion-summary_[TaskName].md` - Final capabilities and validation checklist
- **These documents are NEVER deleted** - they provide lasting value for future reference

#### **Temporary Artifacts (Development Support)**
- Temporary artifacts allowed to assist complex work (e.g., test scripts, scratch analysis, debug files)
  - Name with a clear `temp-` prefix or `WIP-` prefix
  - Store under a `scratch/` subfolder
  - **CRITICAL**: Only delete temporary files AFTER user explicitly states task completion
  - Keep temporary files during active development for debugging and iteration

### **Task Completion & Global Documentation Workflow**
1. **During Task**: Continuously update the 5 core task documents as work progresses
2. **Upon Task Completion**: 
   - **Step 1**: Finalize all 5 core task documents with complete information
   - **Step 2**: Use core task documents as source material to update global documentation:
     - Extract specifications → Update `docs/global_docs/specs/`
     - Extract architecture changes → Update `docs/product_planning/`
     - Extract process improvements → Update `docs/RULES/`
   - **Step 3**: Cross-reference between task docs and global docs to ensure alignment
3. **Post-Completion Cleanup**: Only then remove temp files, outdated docs, and test artifacts
4. **Preserve Value**: Keep core task documents and any temporary artifacts that provide lasting documentation value

### **AI Agent Testing Protocol - Lessons Learned**
**Critical Insight**: User feedback revealed systematic testing inaccuracies where tests reported success but features failed in real browser usage.

#### **Mandatory Testing Sequence**:
1. **Task Workspace Analysis FIRST**:
   - ✅ ALWAYS read troubleshooting doc before implementing
   - ✅ ALWAYS read UML/architecture docs for context
   - ✅ ALWAYS document new issues in troubleshooting workspace
   
2. **Root Cause Investigation**:
   - ✅ Systematic analysis of actual error logs and user feedback
   - ✅ Code inspection for specific failure points
   - ✅ Understanding WHY tests passed but features failed
   
3. **Targeted Fix Implementation**:
   - ✅ Fix root cause, not symptoms
   - ✅ Update troubleshooting doc with solution details
   - ✅ Document technical implementation details
   
4. **Real-World Validation**:
   - ✅ Test actual user workflows, not just API endpoints
   - ✅ Browser-based testing for frontend issues
   - ✅ Integration testing across the full stack
   - ✅ Verify fixes solve the original user problem

#### **Testing Anti-Patterns to Avoid**:
❌ **API-Only Testing**: Backend APIs can pass while frontend fails
❌ **Isolated Component Testing**: Components may work alone but fail in integration
❌ **Mock-Heavy Testing**: Mocks may hide real integration issues
❌ **False Positive Acceptance**: Marking tasks complete without user validation

#### **User Feedback Integration Protocol**:
- **Iterative Validation**: Implement → User Test → Feedback → Fix → Repeat
- **Real Usage Scenarios**: Test actual user workflows, not theoretical ones
- **Systematic Issue Tracking**: Document all user-reported issues in task workspace
- **Learning from Failures**: Update global processes based on failure patterns

#### **Core Documents → Global Docs Mapping**
- `MASTER_Architecture_UMLs_` → `docs/global_docs/specs/` + `docs/product_planning/07_technical_blueprint.md`
- `implementation-plan_` → `docs/global_docs/specs/` (API/UI patterns)
- `completion-summary_` → `docs/CONTROL/Progress-Tracker.md` + feature documentation updates
- `troubleshooting_` → Best practices and lessons learned for future tasks


