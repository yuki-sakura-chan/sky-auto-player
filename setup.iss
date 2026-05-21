[Setup]
AppName=Sap
AppVersion=1.0.0
DefaultDirName={autopf}\Sap
DefaultGroupName=Sap
OutputDir=dist/output
OutputBaseFilename=Sap-setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\gui.dist\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Sap"; Filename: "{app}\Sap.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\Sap"; Filename: "{app}\Sap.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\sap.exe"; Description: "启动 Sap"; Flags: nowait postinstall skipifsilent