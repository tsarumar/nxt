$ErrorActionPreference = 'Stop'
$roboticsBundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $roboticsBundledPython) { $roboticsPython = $roboticsBundledPython }
else { $roboticsPython = (Get-Command python -ErrorAction Stop).Source }
$env:PYTHONIOENCODING = 'utf-8'
foreach ($roboticsName in @('lab_simulations.py','project_simulations.py','kinematics.py')) {
    & $roboticsPython (Join-Path $PSScriptRoot ('simulation\' + $roboticsName))
    if ($LASTEXITCODE -ne 0) { throw ('Simulation failed: ' + $roboticsName) }
}
Write-Output 'All simulations completed. Data and check records were regenerated in this package.'
