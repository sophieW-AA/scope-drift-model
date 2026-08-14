# Update Confluence page 725460028 (Scope Drift) with non-technical status body.
# Uses CONFLUENCE_BASE_URL + CONFLUENCE_PAT_TOKEN from advanced-analytics-sophie/.env

$ErrorActionPreference = "Stop"
$PageId = "725460028"
$BodyFile = Join-Path $PSScriptRoot "..\docs\confluence-scope-drift-status.storage.html"
$DotEnv = "C:\Users\sophie.wilson\Documents\advanced-analytics-sophie\.env"

function Get-DotEnvValue {
  param([string]$Path, [string]$Key)
  foreach ($line in [System.IO.File]::ReadAllLines($Path)) {
    $trimmed = $line.Trim()
    if ($trimmed.Length -eq 0 -or $trimmed.StartsWith("#")) { continue }
    $m = [regex]::Match($trimmed, '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$')
    if (-not $m.Success) { continue }
    if ($m.Groups[1].Value -ne $Key) { continue }
    $v = $m.Groups[2].Value.Trim()
    if (($v.StartsWith('"') -and $v.EndsWith('"')) -or ($v.StartsWith("'") -and $v.EndsWith("'"))) {
      $v = $v.Substring(1, $v.Length - 2)
    }
    return $v
  }
  return $null
}

$baseUrl = (Get-DotEnvValue -Path $DotEnv -Key "CONFLUENCE_BASE_URL").TrimEnd("/")
$token = Get-DotEnvValue -Path $DotEnv -Key "CONFLUENCE_PAT_TOKEN"
if (-not $baseUrl -or -not $token) { throw "Missing CONFLUENCE_BASE_URL or CONFLUENCE_PAT_TOKEN in $DotEnv" }

$headers = @{
  Authorization = "Bearer $token"
  Accept        = "application/json"
}

function Search-Pages {
  param([string]$Cql)
  $uri = $baseUrl + "/rest/api/content/search?cql=" + [uri]::EscapeDataString($Cql) + "&limit=20"
  return Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
}

Write-Host "Searching for Toby taxonomy pages..."
$candidates = New-Object System.Collections.Generic.List[object]
$queries = @(
  'type=page AND space=DA AND title~"Taxonomy"',
  'type=page AND space=DA AND title~"Toby"',
  'type=page AND text~"Toby" AND title~"Taxonomy"',
  'type=page AND space=DA AND (title~"aa_taxonomy" OR title~"Article Taxonomy" OR title~"Publication Taxonomy")'
)
foreach ($q in $queries) {
  try {
    $r = Search-Pages -Cql $q
    foreach ($x in $r.results) {
      $candidates.Add([pscustomobject]@{ Id = [string]$x.id; Title = [string]$x.title; Webui = [string]$x._links.webui })
    }
  } catch {
    Write-Host ("Search failed: " + $_.Exception.Message)
  }
}

$unique = @{}
foreach ($c in $candidates) { $unique[$c.Id] = $c }
foreach ($c in $unique.Values) {
  Write-Host ("Found: " + $c.Id + " - " + $c.Title)
}

$toby = $null
foreach ($c in $unique.Values) {
  if ($c.Title -match '(?i)toby' -and $c.Title -match '(?i)taxonom') { $toby = $c; break }
}
if (-not $toby) {
  foreach ($c in $unique.Values) {
    if ($c.Title -match '(?i)(article|publication|cluster|aa).{0,40}taxonom') { $toby = $c; break }
  }
}
if (-not $toby) {
  foreach ($c in $unique.Values) {
    if ($c.Title -match '(?i)taxonom') { $toby = $c; break }
  }
}

if ($toby) {
  $tobyUrl = $baseUrl + $toby.Webui
  $safeTitle = [System.Net.WebUtility]::HtmlEncode($toby.Title)
  $tobyLinkHtml = '<p><ac:link><ri:page ri:content-title="' + $safeTitle + '" ri:space-key="DA" /></ac:link> (' + '<a href="' + $tobyUrl + '">' + $safeTitle + '</a>)</p>'
  Write-Host ("Using taxonomy page: " + $toby.Title + " (" + $toby.Id + ")")
} else {
  Write-Host "WARNING: could not auto-find Toby taxonomy page; leaving placeholder."
  $tobyLinkHtml = '<p><em>TBD - link Toby taxonomy Confluence page here.</em></p>'
}

$body = Get-Content -LiteralPath $BodyFile -Raw -Encoding UTF8
$body = $body.Replace("__TOBY_TAXONOMY_LINK__", $tobyLinkHtml)

$pageUri = $baseUrl + "/rest/api/content/" + $PageId + "?expand=body.storage,version,space,title"
$page = Invoke-RestMethod -Method Get -Uri $pageUri -Headers $headers
$nextVer = [int]$page.version.number + 1
Write-Host ("Updating '" + $page.title + "' from v" + $page.version.number + " to v" + $nextVer)

$payloadObj = [ordered]@{
  id      = $PageId
  type    = "page"
  title   = [string]$page.title
  space   = @{ key = [string]$page.space.key }
  body    = @{
    storage = @{
      value          = $body
      representation = "storage"
    }
  }
  version = @{
    number  = $nextVer
    message = "Non-technical status update; taxonomy labelling via Toby work"
  }
}
$payload = $payloadObj | ConvertTo-Json -Depth 8

$putUri = $baseUrl + "/rest/api/content/" + $PageId
$updated = Invoke-RestMethod -Method Put -Uri $putUri -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($payload)) -ContentType "application/json; charset=utf-8"
$link = $baseUrl + $updated._links.webui
Write-Host ("Updated page ID: " + $updated.id)
Write-Host ("Link: " + $link)
