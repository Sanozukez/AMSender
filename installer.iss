; installer.iss
; Script Inno Setup para criar instalador do AMSender

#define MyAppName "AMSender"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Amatools"
#define MyAppURL "https://www.amatools.com.br"
#define MyAppExeName "AMSender.exe"
#define MyAppId "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"

[Setup]
; Informações básicas
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=installer
OutputBaseFilename=AMSender_Setup
SetupIconFile=image\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64compatible

; Informações de instalação
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableFinishedPage=no

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Executável principal
Source: "dist\AMSender.exe"; DestDir: "{app}"; Flags: ignoreversion
; Arquivos de configuração exemplo
Source: "config_example.env"; DestDir: "{app}"; Flags: ignoreversion
; README
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "GUIA_OAUTH.md"; DestDir: "{app}"; Flags: ignoreversion
; Pasta credentials (vazia, para o usuário colocar o credentials.json)
Source: "credentials\*"; DestDir: "{app}\credentials"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: DirExists("credentials")
; Pasta exemplos
Source: "exemplos\*"; DestDir: "{app}\exemplos"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: DirExists("exemplos")

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Verifica se Python está instalado (opcional - apenas informativo)
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Você pode adicionar verificações aqui se necessário
end;

// Cria diretórios necessários após instalação
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Cria diretórios necessários
    CreateDir(ExpandConstant('{app}\credentials'));
    CreateDir(ExpandConstant('{app}\comprovacoes'));
    CreateDir(ExpandConstant('{app}\logs'));
  end;
end;

