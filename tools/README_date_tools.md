# Date Tools - Windows Stall Solutions

## Problem
The `node tools/date-current.cjs iso` command occasionally stalls on Windows systems, causing Cursor agent workflows to hang.

## Solutions Created

### 1. Original Tool (Enhanced with Timeout Protection)
- **File**: `tools/date-current.cjs`
- **Usage**: `node tools/date-current.cjs iso`
- **Status**: Works when properly protected with timeouts
- **Issue**: Can stall when executed directly without protection

### 2. PowerShell Native Alternative
- **File**: `tools/date-current-alt.ps1`
- **Usage**: `powershell.exe -ExecutionPolicy Bypass -File tools/date-current-alt.ps1 iso`
- **Benefits**: 
  - No Node.js dependency
  - Native Windows execution
  - Fast and reliable
  - Same output formats as original

### 3. Robust Wrapper (Recommended)
- **File**: `tools/date-current-robust.ps1`
- **Usage**: `powershell.exe -ExecutionPolicy Bypass -File tools/date-current-robust.ps1 iso`
- **Strategy**: 
  - Tries Node.js version with 10-second timeout protection
  - Falls back to PowerShell native version if Node.js fails/stalls
  - Best of both worlds approach

## Format Support

All tools support these formats:
- `taskFolder`: `2025-08-25` (for folder naming)
- `iso`: `2025-08-25T06:04:45.863Z` (for timestamps)
- `readable`: `August 25, 2025` (human-readable)
- `short`: `Aug 25, 2025` (compact format)

## Recommended Usage

For maximum reliability in Windows environments:

```powershell
# Use the robust wrapper
powershell.exe -ExecutionPolicy Bypass -File tools/date-current-robust.ps1 iso

# Or use PowerShell alternative directly for guaranteed speed
powershell.exe -ExecutionPolicy Bypass -File tools/date-current-alt.ps1 iso
```

## Testing Results

All three approaches tested successfully:
- ✅ Original Node.js tool works with timeout protection
- ✅ PowerShell alternative works reliably
- ✅ Robust wrapper provides best user experience

Generated: 2025-08-25T06:04:45.863Z
