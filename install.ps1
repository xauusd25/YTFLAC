# =====================================================================
#  YTFLAC Installer for Windows (PowerShell 5.1+ or PowerShell 7)
# =====================================================================
#  Install / update (paste into PowerShell):
#      irm https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.ps1 | iex
#
#  Uninstall:
#      $env:YTF_ACTION = 'uninstall'; irm https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.ps1 | iex
#
#  No admin rights needed. Python and ffmpeg are installed for you via uv;
#  ffmpeg is bundled by imageio-ffmpeg.
#  (This file is plain ASCII on purpose, so it works in every PowerShell.)
# =====================================================================

& {
    param([string]$ActionArg)

    $ErrorActionPreference = 'Stop'
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    } catch { }

    $Repo   = 'xauusd25/YTFLAC'
    $AppZip = "https://github.com/$Repo/archive/refs/heads/main.zip"
    $ErrLog = Join-Path $HOME 'ytflac_install_error.log'

    $Action = 'install'
    switch -Regex (([string]$ActionArg).ToLower()) {
        '^(uninstall|--uninstall|remove)$' { $Action = 'uninstall' }
        '^(update|--update)$'              { $Action = 'update' }
    }

    $env:Path = (Join-Path $HOME '.local\bin') + ';' + (Join-Path $HOME '.cargo\bin') + ';' + $env:Path

    # ---------- Console capabilities ----------
    function Enable-Vt {
        try {
            if (-not ('YtfNative.Console' -as [type])) {
                Add-Type -Namespace YtfNative -Name Console -ErrorAction Stop -MemberDefinition @'
[DllImport("kernel32.dll")] public static extern System.IntPtr GetStdHandle(int nStdHandle);
[DllImport("kernel32.dll")] public static extern bool GetConsoleMode(System.IntPtr hConsoleHandle, out uint lpMode);
[DllImport("kernel32.dll")] public static extern bool SetConsoleMode(System.IntPtr hConsoleHandle, uint dwMode);
'@
            }
            $h = [YtfNative.Console]::GetStdHandle(-11)
            [uint32]$mode = 0
            if (-not [YtfNative.Console]::GetConsoleMode($h, [ref]$mode)) { return $false }
            return [YtfNative.Console]::SetConsoleMode($h, ($mode -bor 4))
        } catch { return $false }
    }

    function U([int]$Code) { return [string][char]$Code }

    $esc = U 27
    $UseColor = $false
    try { $UseColor = [bool](Enable-Vt) } catch { }
    if (-not $UseColor -and $env:WT_SESSION) { $UseColor = $true }
    if ($PSVersionTable.PSVersion.Major -ge 7) { $UseColor = $true }

    if ($UseColor) {
        $N = $esc + '[0m'; $R = $esc + '[1;38;5;196m'; $G = $esc + '[1;38;5;82m'
        $Y = $esc + '[1;38;5;220m'; $C = $esc + '[1;38;5;51m'; $W = $esc + '[1;38;5;255m'
        $GRAY = $esc + '[38;5;244m'; $LAV = $esc + '[1;38;5;183m'; $TEAL = $esc + '[1;38;5;80m'
        $ClrLine = "`r" + $esc + '[K'
    } else {
        $N=''; $R=''; $G=''; $Y=''; $C=''; $W=''; $GRAY=''; $LAV=''; $TEAL=''; $ClrLine = "`r" + (' ' * 70) + "`r"
    }

    $CHK = U 0x2714; $CROSS = U 0x2718; $WARN = U 0x26A0; $PLAY = U 0x25B6
    $RULE = U 0x2501; $BAR_ON = U 0x25B0; $BAR_OFF = U 0x25B1
    $VBAR = U 0x2503; $ARROW = U 0x25B8
    $TOPL = U 0x250F; $BOTL = U 0x2517
    $Frames = @(0x280B,0x2819,0x2839,0x2838,0x283C,0x2834,0x2826,0x2827,0x2807,0x280F | ForEach-Object { U $_ })

    $LogoEnc = @(
        '   _  __ ___   __  ____  _______ ____'
        '  | |/ //   | / / / / / / / ___// __ \'
        '  |   // /| |/ / / / / / /\__ \/ / / /'
        ' /   |/ ___ / /_/ / /_/ /___/ / /_/ /'
        '/_/|_/_/  |_\____/\____//____/_____/'
    )

    # ---------- Helpers ----------
    $St = @{ Step = 0; Total = 1; Rc = ''; Notes = (New-Object System.Collections.ArrayList) }

    function Get-MiniBar([int]$Done) {
        $s = ''
        for ($i = 1; $i -le $St.Total; $i++) { if ($i -le $Done) { $s += $BAR_ON } else { $s += $BAR_OFF } }
        return $s
    }

    function Show-Header {
        Write-Host ''
        foreach ($l in $LogoEnc) { Write-Host (' ' + $LAV + $l + $N) }
        Write-Host ('              ' + $TEAL + 'FLAC Downloader Installer' + $N)
        Write-Host ''
    }

    function Show-Rule([int]$Width, [string]$Color) { Write-Host ($Color + ($RULE * $Width) + $N) }

    function Show-Done([string]$Msg) { $St.Step++; Write-Host (' ' + $G + $CHK + $N + ' ' + $G + (Get-MiniBar $St.Step) + $N + ' ' + $Msg) }
    function Show-Skip([string]$Msg) { $St.Step++; Write-Host (' ' + $Y + $WARN + $N + ' ' + $Y + (Get-MiniBar $St.Step) + $N + ' ' + $Msg) }

    function Invoke-Step([string]$Msg, [scriptblock]$Work, [object[]]$WorkArgs = @()) {
        $St.Step++
        $start = Get-Date
        $job = Start-Job -ScriptBlock $Work -ArgumentList $WorkArgs
        $i = 0; $out = @(); $failed = $false; $reason = ''
        try {
            while ($job.State -eq 'Running' -or $job.State -eq 'NotStarted') {
                $frame = $Frames[$i % $Frames.Count]
                Write-Host -NoNewline ($ClrLine + ' ' + $C + $frame + $N + ' ' + $GRAY + (Get-MiniBar ($St.Step - 1)) + $N + ' ' + $W + $Msg + $N)
                $i++; Start-Sleep -Milliseconds 100
            }
            $out = @(Receive-Job -Job $job -ErrorAction SilentlyContinue | ForEach-Object { "$_" })
            if ($job.State -ne 'Completed') { $failed = $true; try { $reason = [string]$job.ChildJobs[0].JobStateInfo.Reason.Message } catch { } }
        } finally { Remove-Job -Job $job -Force -ErrorAction SilentlyContinue }

        $secs = [int]((Get-Date) - $start).TotalSeconds
        if (-not $failed) {
            Write-Host ($ClrLine + ' ' + $G + $CHK + $N + ' ' + $G + (Get-MiniBar $St.Step) + $N + ' ' + $Msg + ' ' + $GRAY + "${secs}s" + $N)
            return
        }
        Write-Host ($ClrLine + ' ' + $R + $CROSS + $N + ' ' + $R + (Get-MiniBar ($St.Step - 1)) + $N + ' ' + $R + $Msg + $N)
        Write-Host ''
        Write-Host (' ' + $R + $TOPL + ($RULE * 2) + ' Error details ' + ($RULE * 14) + $N)
        $tail = @($out); if ($reason) { $tail += $reason }
        $tail = @($tail | Select-Object -Last 15)
        foreach ($l in $tail) { Write-Host (' ' + $R + $VBAR + $N + ' ' + $l) }
        Write-Host (' ' + $R + $BOTL + ($RULE * 30) + $N)
        try { Set-Content -Path $ErrLog -Value (@($out) + @($reason)) -Encoding UTF8 } catch { }
        Write-Host ''
        Write-Host (' ' + $Y + 'Full log saved: ' + $N + $W + $ErrLog + $N)
        Write-Host ''
        throw 'YTF_ABORT'
    }

    function Read-Choice {
        try { $reply = Read-Host; if ([string]::IsNullOrWhiteSpace($reply)) { return '1' }; return $reply.Trim() } catch { return '1' }
    }

    function Add-ToolBinToPath {
        $bin = ''
        try { $bin = ((& uv tool dir --bin) | Out-String).Trim() } catch { }
        if (-not $bin) { $bin = Join-Path $HOME '.local\bin' }
        $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
        if ($null -eq $userPath) { $userPath = '' }
        $present = $false
        foreach ($p in ($userPath -split ';')) { if ($p -and ($p.TrimEnd('\') -ieq $bin.TrimEnd('\'))) { $present = $true } }
        if (-not $present) {
            if ($userPath) { $newPath = $bin + ';' + $userPath } else { $newPath = $bin }
            [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        }
        $sessionHas = $false
        foreach ($p in ($env:Path -split ';')) { if ($p -and ($p.TrimEnd('\') -ieq $bin.TrimEnd('\'))) { $sessionHas = $true } }
        if (-not $sessionHas) { $env:Path = $bin + ';' + $env:Path }
    }

    # ---------- Step scripts ----------
    $UvWork = {
        $ErrorActionPreference = 'Continue'
        $ProgressPreference = 'SilentlyContinue'
        try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch { }
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
            $env:UV_NO_MODIFY_PATH = '1'
            Invoke-RestMethod -UseBasicParsing -Uri 'https://astral.sh/uv/install.ps1' | Invoke-Expression
            $env:Path = (Join-Path $HOME '.local\bin') + ';' + (Join-Path $HOME '.cargo\bin') + ';' + $env:Path
        }
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'uv was not found after installing it' }
        & uv --version
    }

    $AppWork = {
        param($Zip)
        $ErrorActionPreference = 'Continue'
        & uv tool install --force --reinstall --python 3.12 --with 'yt-dlp[default]' --with imageio-ffmpeg "ytflac @ $Zip" 2>&1 | ForEach-Object { "$_" }
        if ($LASTEXITCODE -ne 0) { throw "uv tool install failed (exit code $LASTEXITCODE)" }
    }

    $UninstallWork = {
        $ErrorActionPreference = 'Continue'
        if (Get-Command uv -ErrorAction SilentlyContinue) { & uv tool uninstall ytflac 2>&1 | ForEach-Object { "$_" } }
    }

    # ---------- Main ----------
    $oldEnc = $null
    try {
        try { $oldEnc = [Console]::OutputEncoding; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
        try { [Console]::CursorVisible = $false } catch { }

        Show-Header

        if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
            Write-Host (' ' + $Y + $WARN + ' This installer is for Windows' + $N)
            Write-Host (' ' + $GRAY + ' On Linux, macOS or Termux use install.sh instead.' + $N)
            return
        }

        if ($Action -eq 'install') {
            $existing = Get-Command ytf -ErrorAction SilentlyContinue
            if ($existing) {
                Write-Host (' ' + $GRAY + $CHK + ' YTFLAC is already installed at ' + $W + $existing.Source + $N)
                Write-Host -NoNewline (' Choose an action: ' + $C + '[1]' + $N + ' Reinstall/Update  ' + $C + '[2]' + $N + ' Uninstall  ' + $C + '[3]' + $N + ' Exit: ')
                try { [Console]::CursorVisible = $true } catch { }
                $choice = Read-Choice
                try { [Console]::CursorVisible = $false } catch { }
                switch ($choice) { '2' { $Action = 'uninstall' } '3' { Write-Host ''; return } default { $Action = 'update' } }
                Write-Host ''
            }
        }

        $sw = [Diagnostics.Stopwatch]::StartNew()

        if ($Action -eq 'uninstall') {
            $St.Total = 1
            Invoke-Step 'Removing YTFLAC' $UninstallWork
            Write-Host ''
            Show-Rule 45 $G
            Write-Host (' ' + $G + $CHK + ' YTFLAC removed' + $N)
            Show-Rule 45 $G
            Write-Host ''
            return
        }

        $St.Total = 3
        Invoke-Step 'Installing uv (Python manager)' $UvWork
        Invoke-Step 'Installing YTFLAC' $AppWork @($AppZip)
        Add-ToolBinToPath
        Show-Done 'Command added: ytf'

        $sw.Stop()
        Write-Host ''
        Show-Rule 45 $G
        Write-Host (' ' + $G + $CHK + ' Installation completed successfully' + $N + '  ' + $GRAY + '(' + [int]$sw.Elapsed.TotalSeconds + 's)' + $N)
        Show-Rule 45 $G
        Write-Host ''
        Write-Host (' ' + $Y + $PLAY + ' Start it by typing:' + $N)
        Write-Host ('    ' + $C + 'ytf' + $N)
        Write-Host ''
        Write-Host (' ' + $GRAY + 'Also available:' + $N + ' ytflac ' + [string][char]0x00B7 + ' ytf --check ' + [string][char]0x00B7 + ' ytf --help')
        foreach ($note in $St.Notes) { Write-Host ''; Write-Host (' ' + $Y + $ARROW + $N + ' ' + $note) }
        Write-Host ''
    } catch {
        if ($_.Exception.Message -ne 'YTF_ABORT') {
            Write-Host ''
            Write-Host (' ' + $R + $CROSS + ' Unexpected error: ' + $_.Exception.Message + $N)
            Write-Host ''
        }
    } finally {
        try { [Console]::CursorVisible = $true } catch { }
        if ($oldEnc) { try { [Console]::OutputEncoding = $oldEnc } catch { } }
    }
} $(if ($args.Count -gt 0) { [string]$args[0] } else { [string]$env:YTF_ACTION })