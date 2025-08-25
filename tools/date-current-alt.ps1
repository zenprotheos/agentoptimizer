#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Date Current Generator - PowerShell Alternative
    Provides current date in formats useful for task workspace creation
    Alternative to Node.js version to avoid stall issues on Windows
    
.PARAMETER Format
    Format type: taskFolder, iso, readable, short
    
.EXAMPLE
    ./date-current-alt.ps1 iso
    ./date-current-alt.ps1 taskFolder
#>

param(
    [Parameter(Position=0)]
    [ValidateSet('taskFolder', 'iso', 'readable', 'short')]
    [string]$Format = 'taskFolder'
)

$ErrorActionPreference = 'Stop'

try {
    $now = Get-Date
    
    switch ($Format) {
        'taskFolder' {
            # Primary format for task folder naming: YYYY-MM-DD
            $result = $now.ToString('yyyy-MM-dd')
        }
        'iso' {
            # ISO format for front-matter timestamps
            $result = $now.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
        }
        'readable' {
            # Human readable format
            $result = $now.ToString('MMMM d, yyyy')
        }
        'short' {
            # Short format for quick reference
            $result = $now.ToString('MMM d, yyyy')
        }
        default {
            throw "Unknown format: $Format"
        }
    }
    
    Write-Output $result
    exit 0
}
catch {
    Write-Error "Error generating date: $_"
    Write-Error "Available formats: taskFolder, iso, readable, short"
    exit 1
}
