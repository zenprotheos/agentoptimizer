# URL Testing Script for VoiceScribeAI
# Compatible with Cursor AI (uses PowerShell instead of curl)

param(
    [Parameter(Mandatory=$true)]
    [string]$Url,
    
    [Parameter(Mandatory=$false)]
    [int]$Timeout = 30,
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseMode
)

function Test-UrlAccessibility {
    param(
        [string]$TestUrl,
        [int]$TimeoutSeconds,
        [bool]$VerboseOutput
    )
    
    try {
        if ($VerboseOutput) {
            Write-Host "Testing URL: $TestUrl" -ForegroundColor Cyan
            Write-Host "Timeout: $TimeoutSeconds seconds" -ForegroundColor Gray
        }
        
        $response = Invoke-WebRequest -Uri $TestUrl -UseBasicParsing -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        
        $result = @{
            Success = $true
            StatusCode = $response.StatusCode
            StatusDescription = $response.StatusDescription
            ResponseLength = $response.Content.Length
            Headers = $response.Headers
            Url = $TestUrl
            TestTime = Get-Date
        }
        
        if ($VerboseOutput) {
            Write-Host "✅ SUCCESS" -ForegroundColor Green
            Write-Host "Status: $($result.StatusCode) $($result.StatusDescription)" -ForegroundColor Green
            Write-Host "Response Length: $($result.ResponseLength) bytes" -ForegroundColor Gray
        } else {
            Write-Host "✅ $TestUrl - $($result.StatusCode) $($result.StatusDescription)" -ForegroundColor Green
        }
        
        return $result
        
    } catch {
        $result = @{
            Success = $false
            Error = $_.Exception.Message
            StatusCode = $null
            Url = $TestUrl
            TestTime = Get-Date
        }
        
        if ($VerboseOutput) {
            Write-Host "❌ FAILED" -ForegroundColor Red
            Write-Host "Error: $($result.Error)" -ForegroundColor Red
        } else {
            Write-Host "❌ $TestUrl - FAILED: $($result.Error)" -ForegroundColor Red
        }
        
        return $result
    }
}

# Main execution
$testResult = Test-UrlAccessibility -TestUrl $Url -TimeoutSeconds $Timeout -VerboseOutput $VerboseMode.IsPresent

# Exit with appropriate code
if ($testResult.Success) { exit 0 } else { exit 1 }


