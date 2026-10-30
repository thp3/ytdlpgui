; Inno Setup script for the packaged PyInstaller folder
#define AppName "萬用影片下載器"
#ifndef AppVersion
  #define AppVersion "0.1.1"
#endif
#define AppExe "VideoDownloader.exe"

[Setup]
AppId={{6F3B2C1E-8A44-4D1B-9C57-2E0B7A9D4F10}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\VideoDownloader
DefaultGroupName={#AppName}
OutputDir=..\dist
OutputBaseFilename=VideoDownloader-Setup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExe}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "建立桌面捷徑"; GroupDescription: "額外工作:"; Flags: unchecked

[Files]
Source: "..\dist\VideoDownloader\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "啟動 {#AppName}"; Flags: nowait postinstall skipifsilent
