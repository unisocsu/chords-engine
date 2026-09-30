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
CreateUninstallRegKey={code:CreateUninstallEntry}
UpdateUninstallLogAppName=no
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no

[Files]
Source: "..\release\{#AppExe}"; DestDir: "{app}"; DestName: "{#TargetExe}"; Flags: ignoreversion

[Icons]
Name: "{group}\ChordsEngine {#Variant}"; Filename: "{app}\{#TargetExe}"
Name: "{autodesktop}\ChordsEngine {#Variant}"; Filename: "{app}\{#TargetExe}"

[Code]
function IsUpdateMode: Boolean;
begin
  Result := GetEnv('CHORDS_INSTALLER_MODE') = 'update';
end;

function CreateUninstallEntry: Boolean;
begin
  Result := not IsUpdateMode;
end;

const
  ModelTinyName = 'ggml-tiny-q5_1.bin';
  ModelTinyURL = 'https://huggingface.co/ggerganov/whisper.cpp/resolve/f281eb45af861ab5e5297d23694b7d46e090c02c/ggml-tiny-q5_1.bin';
  ModelTinySHA256 = '818710568da3ca15689e31a743197b520007872ff9576237bda97bd1b469c3d7';
  ModelBaseName = 'ggml-base-q5_1.bin';
  ModelBaseURL = 'https://huggingface.co/ggerganov/whisper.cpp/resolve/f281eb45af861ab5e5297d23694b7d46e090c02c/ggml-base-q5_1.bin';
  ModelBaseSHA256 = '422f1ae452ade6f30a004d7e5c6a43195e4433bc370bf23fac9cc591f01a8898';
  ModelSmallName = 'ggml-small-q5_1.bin';
  ModelSmallURL = 'https://huggingface.co/ggerganov/whisper.cpp/resolve/f281eb45af861ab5e5297d23694b7d0481c77/ggml-small-q5_1.bin';
  ModelSmallSHA256 = 'ae85e4a935d7a567bd102fe55afc16bb595bdb618e11b2fc7591bc08120411bb';
  ModelMediumName = 'ggml-medium-q5_0.bin';
  ModelMediumURL = 'https://huggingface.co/ggerganov/whisper.cpp/resolve/362722b3fdcd2300b58a8286933ead1c48619667/ggml-medium-q5_0.bin';
  ModelMediumSHA256 = '19fea4b380c3a618ec4723c3eef2eb785ffba0d0538cf43f8f235e7b3b34220f';

var
  ModelChoicePage: TInputOptionWizardPage;
  ModelPage: TInputFileWizardPage;
  DownloadPage: TDownloadWizardPage;
  ModelTarget: string;
  IsUpdateInstaller: Boolean;
  SavedModelPath: string;
  SavedModelName: string;

function FindNewestModelInDir(BaseDir: string): string;
var
  Rec: TFindRec;
  Child, Candidate: string;
  Size, BestSize: Int64;
begin
  Result := '';
  if not DirExists(BaseDir) then exit;
  BestSize := 0;

  if FindFirst(AddBackslash(BaseDir) + '*.bin', Rec) then
  begin
    try
      repeat
        Candidate := AddBackslash(BaseDir) + Rec.Name;
        if FileSize64(Candidate, Size) and (Size > 100000) and (Size > BestSize) then
        begin
          Result := Candidate;
          BestSize := Size;
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
        if (Rec.Name <> '.') and (Rec.Name <> '..') and
           ((Rec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0) then
        begin
          Child := AddBackslash(BaseDir) + Rec.Name;
          Candidate := FindNewestModelInDir(Child);
          if Candidate <> '' then
          begin
            if FileSize64(Candidate, Size) and (Size > BestSize) then
            begin
              Result := Candidate;
              BestSize := Size;
            end;
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

  if (not IsUpdateInstaller) and (('{#Variant}' = 'nomodel') or ('{#Variant}' = 'universal')) then
  begin
    ModelChoicePage := CreateInputOptionPage(wpSelectDir,
      'בחירת מודל Whisper',
      'בחר מודל ואופן התקנה',
      'בחר את גודל המודל ולאחר מכן אם להוריד אותו או לבחור קובץ מהמחשב.',
      True, False);
    ModelChoicePage.Add('Tiny — כ־32 MB');
    ModelChoicePage.Add('Base — כ־60 MB');
    ModelChoicePage.Add('Small — כ־190 MB');
    ModelChoicePage.Add('Medium — כ־539 MB');
    ModelChoicePage.Add('בחר קובץ מודל מהמחשב');
    ModelChoicePage.Add('הורד את המודל שנבחר מהאינטרנט');
    ModelChoicePage.SelectedValueIndex := 3;

    ModelPage := CreateInputFilePage(ModelChoicePage.ID,
      'בחירת מודל Whisper',
      'בחר את קובץ מודל Whisper שבו התוכנה תשתמש',
      'בחר קובץ ggml-*.bin. הוא יועתק לתיקיית המודלים של ChordsEngine.');
    ModelPage.Add('קובץ מודל:', 'קבצי מודל Whisper (*.bin)|*.bin|כל הקבצים (*.*)|*.*', '.bin');

    DownloadPage := CreateDownloadPage(
      'הורדת מודל Whisper',
      'מוריד את המודל שבחרת. נא להמתין לסיום ההורדה.',
      nil);
    DownloadPage.ShowBaseNameInsteadOfUrl := True;
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  if (not IsUpdateInstaller) and (('{#Variant}' = 'nomodel') or ('{#Variant}' = 'universal')) and Assigned(ModelChoicePage) then
    Result := (PageID = ModelPage.ID) and (ModelChoicePage.SelectedValueIndex < 4);
end;

function SelectedModelInfo(var Name, URL, SHA: string): Boolean;
begin
  Result := True;
  case ModelChoicePage.SelectedValueIndex of
    0: begin Name := ModelTinyName; URL := ModelTinyURL; SHA := ModelTinySHA256; end;
    1: begin Name := ModelBaseName; URL := ModelBaseURL; SHA := ModelBaseSHA256; end;
    2: begin Name := ModelSmallName; URL := ModelSmallURL; SHA := ModelSmallSHA256; end;
    3: begin Name := ModelMediumName; URL := ModelMediumURL; SHA := ModelMediumSHA256; end;
  else
    Result := False;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Src: string;
begin
  Result := True;
  if (not IsUpdateInstaller) and (('{#Variant}' = 'nomodel') or ('{#Variant}' = 'universal')) and (CurPageID = ModelPage.ID) and
     (ModelChoicePage.SelectedValueIndex = 4) then
  begin
    Src := ModelPage.Values[0];
    if (Src = '') or (not FileExists(Src)) then
    begin
      MsgBox('יש לבחור קובץ מודל קיים.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Src, TempModel, TargetDir, Target, ModelName, ModelURL, ModelSHA: string;
begin
  if (CurStep = ssInstall) and (not IsUpdateInstaller) and
     (('{#Variant}' = 'nomodel') or ('{#Variant}' = 'universal')) then
  begin
    TargetDir := ExpandConstant('{app}\models');
    ForceDirectories(TargetDir);

    if ModelChoicePage.SelectedValueIndex = 4 then
      Src := ModelPage.Values[0]
    else
    begin
      if not SelectedModelInfo(ModelName, ModelURL, ModelSHA) then
      begin
        MsgBox('לא נבחר מודל תקין.', mbError, MB_OK);
        Abort;
      end;
      DownloadPage.Clear;
      DownloadPage.Add(ModelURL, ModelName, ModelSHA);
      DownloadPage.Show;
      try
        DownloadPage.Download;
      except
        DownloadPage.Hide;
        MsgBox('הורדת המודל נכשלה.' + #13#10 + GetExceptionMessage, mbError, MB_OK);
        Abort;
      end;
      DownloadPage.Hide;
      Src := ExpandConstant('{tmp}\') + ModelName;
    end;

    Target := AddBackslash(TargetDir) + ExtractFileName(Src);
    if FileExists(Target) then
      DeleteFile(Target);
    if not FileCopy(Src, Target, False) then
    begin
      MsgBox('העתקת המודל נכשלה.', mbError, MB_OK);
      Abort;
    end;
    ModelTarget := Target;
  end;

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
      end;
    end;
  end;

  if (CurStep = ssPostInstall) and IsUpdateInstaller and (SavedModelPath <> '') then
  begin
    TargetDir := ExpandConstant('{app}\models');
    ForceDirectories(TargetDir);
    Target := AddBackslash(TargetDir) + SavedModelName;
    if not FileCopy(SavedModelPath, Target, False) then
      MsgBox('התוכנה עודכנה, אך העברת המודל נכשלה.', mbError, MB_OK);
  end;

  if (CurStep = ssPostInstall) and (not IsUpdateInstaller) and
     (('{#Variant}' = 'nomodel') or ('{#Variant}' = 'universal')) then
    MsgBox('ההתקנה הושלמה.' + #13#10 + 'המודל הותקן אל:' + #13#10 + ModelTarget, mbInformation, MB_OK);
end;
