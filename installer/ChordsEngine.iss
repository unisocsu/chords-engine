; ChordsEngine Windows installer
#define AppName "ChordsEngine"
#define AppVersion GetEnv("CHORDS_APP_VERSION")
#define AppExe GetEnv("CHORDS_INSTALLER_EXE")
#define TargetExe GetEnv("CHORDS_INSTALLER_TARGET_EXE")
#define Variant GetEnv("CHORDS_INSTALLER_VARIANT")
#define OutputName GetEnv("CHORDS_INSTALLER_OUTPUT")

[Setup]
AppId={{B7C2E2F0-4E4C-4F7B-A8B1-9C0D7E123456}
AppName={#AppName} {#Variant}
AppVersion={#AppVersion}
DefaultDirName={autopf}\ChordsEngine\{#Variant}
DefaultGroupName={#AppName} {#Variant}
OutputDir=..\release
OutputBaseFilename={#OutputName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\build\icon.ico
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
Uninstallable=yes
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no

[Files]
Source: "..\release\{#AppExe}"; DestDir: "{app}"; DestName: "{#TargetExe}"; Flags: ignoreversion

[Icons]
Name: "{group}\ChordsEngine {#Variant}"; Filename: "{app}\{#TargetExe}"
Name: "{autodesktop}\ChordsEngine {#Variant}"; Filename: "{app}\{#TargetExe}"

[Code]
var
  ModelPage: TInputFileWizardPage;
  ModelTarget: string;
  IsUpdateInstaller: Boolean;
  SavedModelPath: string;
  SavedModelName: string;

function FindNewestModelInDir(BaseDir: string): string;
var
  Rec: TFindRec;
  Child, Candidate: string;
  BestTime, T: Integer;
begin
  Result := '';
  if not DirExists(BaseDir) then exit;
  BestTime := 0;

  if FindFirst(AddBackslash(BaseDir) + '*.bin', Rec) then
  begin
    try
      repeat
        Candidate := AddBackslash(BaseDir) + Rec.Name;
        T := Rec.LastWriteTime;
        if (FileSize64(Candidate) > 100000) and ((Result = '') or (T > BestTime)) then
        begin
          Result := Candidate;
          BestTime := T;
        end;
      until not FindNext(Rec);
    finally
      FindClose(Rec);
    end;
  end;

  if FindFirst(AddBackslash(BaseDir) + '*', Rec) then
  begin
    try
      repeat
        if (Rec.Name <> '.') and (Rec.Name <> '..') and Rec.Attributes and FILE_ATTRIBUTE_DIRECTORY <> 0 then
        begin
          Child := AddBackslash(BaseDir) + Rec.Name;
          Candidate := FindNewestModelInDir(Child);
          if Candidate <> '' then
          begin
            T := FileSize64(Candidate);
            if (Result = '') or (T > FileSize64(Result)) then
              Result := Candidate;
          end;
        end;
      until not FindNext(Rec);
    finally
      FindClose(Rec);
    end;
  end;
end;

function FindExistingModel: string;
var
  ExistingDir, AppCache: string;
begin
  Result := '';
  ExistingDir := ExpandConstant('{app}\models');
  if DirExists(ExistingDir) then
    Result := FindNewestModelInDir(ExistingDir);

  if Result = '' then
  begin
    AppCache := ExpandConstant('{localappdata}\ChordsEngine\app');
    Result := FindNewestModelInDir(AppCache);
  end;
end;

procedure InitializeWizard;
begin
  IsUpdateInstaller := GetEnv('CHORDS_INSTALLER_MODE') = 'update';

  if (not IsUpdateInstaller) and ('{#Variant}' = 'nomodel') then
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
  if (not IsUpdateInstaller) and ('{#Variant}' = 'nomodel') and
     (CurPageID = ModelPage.ID) then
  begin
    Src := ModelPage.Values[0];
    if (Src = '') or (not FileExists(Src)) then
    begin
      MsgBox('יש לבחור קובץ מודל קיים.', mbError, MB_OK);
      Result := False;
      exit;
    end;

    DstDir := ExpandConstant('{app}\models');
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
var
  Src, TempModel, TargetDir, Target: string;
begin
  if (CurStep = ssInstall) and IsUpdateInstaller then
  begin
    Src := FindExistingModel;
    if Src <> '' then
    begin
      TempModel := AddBackslash(ExpandConstant('{tmp}')) + 'ChordsEngine-model.bin';
      if FileCopy(Src, TempModel, False) then
      begin
        SavedModelPath := TempModel;
        SavedModelName := ExtractFileName(Src);
      end
      else
        Log('Could not copy existing model to temporary update storage: ' + Src);
    end
    else
      Log('No existing Whisper model found during update; continuing without one.');
  end;

  if (CurStep = ssPostInstall) and IsUpdateInstaller and (SavedModelPath <> '') then
  begin
    TargetDir := ExpandConstant('{app}\models');
    ForceDirectories(TargetDir);
    Target := AddBackslash(TargetDir) + SavedModelName;
    if FileCopy(SavedModelPath, Target, False) then
      MsgBox('העדכון הושלם.' + #13#10 +
             'המודל הקיים נשמר והועבר לגרסה החדשה.', mbInformation, MB_OK)
    else
      MsgBox('התוכנה עודכנה, אך העברת המודל לגרסה החדשה נכשלה.' + #13#10 +
             'המודל נשמר זמנית ב:' + #13#10 + SavedModelPath, mbError, MB_OK);
  end;

  if (CurStep = ssPostInstall) and (not IsUpdateInstaller) and ('{#Variant}' = 'nomodel') then
    MsgBox('ההתקנה הושלמה.' + #13#10 + 'המודל הועתק אל:' + #13#10 + ModelTarget, mbInformation, MB_OK);
end;
