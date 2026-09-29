; ChordsEngine Windows installer
#define AppName "ChordsEngine"
#define AppVersion "0.2.0"
#define AppExe GetEnv("CHORDS_INSTALLER_EXE")
#define Variant GetEnv("CHORDS_INSTALLER_VARIANT")

[Setup]
AppId={{B7C2E2F0-4E4C-4F7B-A8B1-9C0D7E123456}
AppName={#AppName} {#Variant}
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\ChordsEngine\{#Variant}
DefaultGroupName={#AppName} {#Variant}
OutputDir=..\release
OutputBaseFilename=ChordsEngine-{#Variant}-Installer
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
Uninstallable=yes
DisableProgramGroupPage=yes

[Files]
Source: "..\release\{#AppExe}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ChordsEngine {#Variant}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\ChordsEngine {#Variant}"; Filename: "{app}\{#AppExe}"

[Code]
var
  ModelPage: TInputFileWizardPage;
  ModelTarget: string;

procedure InitializeWizard;
begin
  if '{#Variant}' = 'nomodel' then
  begin
    ModelPage := CreateInputFilePage(wpSelectDir,
      'בחירת מודל Whisper',
      'בחר את קובץ מודל Whisper שבו התוכנה תשתמש',
      'בחר קובץ ggml-*.bin. הוא יועתק לתיקיית המודלים של ChordsEngine.');
    ModelPage.Add('קובץ מודל:', 'קבצי מודל Whisper (*.bin)|*.bin|כל הקבצים (*.*)|*.*', '.bin');
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Src, DstDir, Dst: string;
begin
  Result := True;
  if ('{#Variant}' = 'nomodel') and (CurPageID = ModelPage.ID) then
  begin
    Src := ModelPage.Values[0];
    if (Src = '') or (not FileExists(Src)) then
    begin
      MsgBox('יש לבחור קובץ מודל קיים.', mbError, MB_OK);
      Result := False;
      exit;
    end;

    DstDir := ExpandConstant('{localappdata}\ChordsEngine\models');
    ForceDirectories(DstDir);
    Dst := AddBackslash(DstDir) + ExtractFileName(Src);

    if FileExists(Dst) then
    begin
      if MsgBox('המודל כבר קיים. להחליף אותו?', mbConfirmation, MB_YESNO) <> IDYES then
      begin
        Result := False;
        exit;
      end;
      DeleteFile(Dst);
    end;

    if not FileCopy(Src, Dst, False) then
    begin
      MsgBox('העתקת המודל נכשלה.', mbError, MB_OK);
      Result := False;
      exit;
    end;
    ModelTarget := Dst;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and ('{#Variant}' = 'nomodel') then
    MsgBox('ההתקנה הושלמה.' + #13#10 + 'המודל הועתק אל:' + #13#10 + ModelTarget, mbInformation, MB_OK);
end;
