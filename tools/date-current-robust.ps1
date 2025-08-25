#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Robust Date Current Generator
    Uses Node.js version with timeout protection, falls back to PowerShell version
    
.PARAMETER Format
    Format type: taskFolder, iso, readable, short
    
.EXAMPLE
    ./date-current-robust.ps1 iso
    ./date-current-robust.ps1 taskFolder
#>

param(
    [Parameter(Position=0)]
    [string]$Format = 'taskFolder'
)

$ErrorActionPreference = 'Stop'

function Get-DateWithNode {
    param([string]$Format)
    
    Write-Verbose "Trying Node.js version with timeout protection..."
    
    $job = Start-Job -ScriptBlock {
        param($Format)
        Set-Location $using:PWD
        node tools/date-current.cjs $Format
    } -ArgumentList $Format
    
    try {
        if (Wait-Job $job -Timeout 10) {
            $result = Receive-Job $job -ErrorAction SilentlyContinue
            if ($result -and $LASTEXITCODE -eq 0) {
                return $result
            }
        }
        else {
            Write-Verbose "Node.js version timed out"
            Stop-Job $job -Force
        }
    }
    finally {
        Remove-Job $job -Force -ErrorAction SilentlyContinue
    }
    
    return $null
}

function Get-DateWithPowerShell {
    param([string]$Format)
    
    Write-Verbose "Using PowerShell native version..."
    
    $now = Get-Date
    
    switch ($Format) {
        'taskFolder' {
            return $now.ToString('yyyy-MM-dd')
        }
        'iso' {
            return $now.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
        }
        'readable' {
            return $now.ToString('MMMM d, yyyy')
        }
        'short' {
            return $now.ToString('MMM d, yyyy')
        }
        default {
            throw "Unknown format: $Format. Available: taskFolder, iso, readable, short"
        }
    }
}

try {
    # Try Node.js version first (preferred for consistency)
    $result = Get-DateWithNode -Format $Format
    
    if (-not $result) {
        # Fall back to PowerShell version
        $result = Get-DateWithPowerShell -Format $Format
        Write-Verbose "Used PowerShell fallback"
    }
    else {
        Write-Verbose "Used Node.js version"
    }
    
    Write-Output $result
    exit 0
}
catch {
    Write-Error "Error generating date: $_"
    exit 1
}
