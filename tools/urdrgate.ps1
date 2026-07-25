# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
#
# urdrgate.ps1 — run the gate twice and emit ONE compact line to paste back.
#
# The full PowerShell transcript of a gate run is ~5 KB of which about 100 bytes carry
# information. This runs the whole check and prints a single delimited block between
# <<<URDR and URDR>>> — copy that, nothing else. On failure it additionally prints ONLY the
# failing rows, which is exactly the part that needs reading.
#
#   .\tools\urdrgate.ps1                 # apply nothing, just verify
#   .\tools\urdrgate.ps1 -Patch x.patch  # git am the patch first, then verify
#   .\tools\urdrgate.ps1 -Push           # push on success
#
# Exit code 0 iff the gate passed AND both runs were byte-identical AND non-empty.

param(
    [string]$Patch = "",
    [switch]$Push,
    [switch]$Quiet
)

$ErrorActionPreference = "Continue"
$env:PYTHONHASHSEED = "0"
$env:PYTHONUTF8 = "1"

$applied = "none"
if ($Patch -ne "") {
    if (-not (Test-Path $Patch)) { Write-Host "<<<URDR`nERR=patch-not-found:$Patch`nURDR>>>"; exit 2 }
    $before = (git rev-parse --short HEAD)
    git am --keep-cr $Patch 2>&1 | Out-Null
    $after = (git rev-parse --short HEAD)
    if ($before -eq $after) {
        git am --abort 2>&1 | Out-Null
        Write-Host "<<<URDR`nERR=patch-failed-to-apply HEAD=$before`nURDR>>>"; exit 2
    }
    $applied = "$before->$after"
}

# two runs, same tree
py verify.py > gA.txt 2>&1
py verify.py > gB.txt 2>&1

$la = (Get-Item gA.txt).Length
$lb = (Get-Item gB.txt).Length
$ha = (Get-FileHash gA.txt).Hash
$hb = (Get-FileHash gB.txt).Hash
$ident = ($ha -eq $hb) -and ($la -gt 0)

$txt = Get-Content gB.txt -Raw
$verdict = if ($txt -match "GATE PASSED") { "PASSED" } elseif ($txt -match "GATE FAILED") { "FAILED" } else { "UNKNOWN" }
$fals = if ($txt -match "unit-falsifiers\s+(\d+) run, (\d+) red") { "$($Matches[1])/$($Matches[2])red" } else { "?" }
$rows = if ($txt -match "(\d+) unit falsifiers, (\d+) rows") { $Matches[2] } else { "?" }
$dc   = if ($txt -match "\[PASS\] doc-currency ") { "OK" } else { "STALE" }
$ds   = if ($txt -match "\[PASS\] doc-staleness ") { "OK" } elseif ($txt -match "doc-staleness ") { "STALE" } else { "-" }
$fail = ([regex]::Matches($txt, "(?m)^\[FAIL\]")).Count
$head = (git rev-parse --short HEAD)
$branch = (git rev-parse --abbrev-ref HEAD)

$pushed = "no"
if ($Push -and $verdict -eq "PASSED" -and $ident -and $fail -eq 0) {
    $out = (git push origin $branch 2>&1 | Out-String)
    $pushed = if ($out -match "->") { ($out | Select-String -Pattern "\s([0-9a-f]{7,}\.\.[0-9a-f]{7,})\s" ).Matches.Groups[1].Value } else { "up-to-date" }
}

Write-Host "<<<URDR"
Write-Host "HEAD=$head BR=$branch AM=$applied"
Write-Host "GATE=$verdict FAILROWS=$fail FALS=$fals ROWS=$rows DOCCUR=$dc DOCSTALE=$ds"
Write-Host "DET=$(if($ident){'BYTE-IDENTICAL'}else{'DIFFER'}) BYTES=$la/$lb A=$($ha.Substring(0,8)) B=$($hb.Substring(0,8))"
Write-Host "PUSH=$pushed"
if ($fail -gt 0) {
    Write-Host "-- failing rows --"
    Select-String gB.txt -Pattern "^\[FAIL\]" | ForEach-Object { Write-Host $_.Line.Substring(0, [Math]::Min(160, $_.Line.Length)) }
}
Write-Host "URDR>>>"

if ($verdict -eq "PASSED" -and $ident -and $fail -eq 0) { exit 0 } else { exit 1 }
