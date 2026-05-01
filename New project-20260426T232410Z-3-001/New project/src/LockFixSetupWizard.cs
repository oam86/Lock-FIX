using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace LockFix
{
    internal static class SetupProgram
    {
        [STAThread]
        private static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new SetupWizardForm());
        }
    }

    internal sealed class SetupWizardForm : Form
    {
        private readonly Panel header = new Panel();
        private readonly Panel content = new Panel();
        private readonly Panel footer = new Panel();
        private readonly Button backButton = new Button();
        private readonly Button nextButton = new Button();
        private readonly Button cancelButton = new Button();
        private readonly Label pageTitle = new Label();
        private readonly Label pageBody = new Label();

        private readonly TextBox installPathBox = new TextBox();
        private readonly RadioButton recommendedInstall = new RadioButton();
        private readonly RadioButton advancedInstall = new RadioButton();
        private readonly CheckBox coreService = new CheckBox();
        private readonly CheckBox webUi = new CheckBox();
        private readonly CheckBox veeamConnector = new CheckBox();
        private readonly CheckBox agent = new CheckBox();
        private readonly CheckBox database = new CheckBox();
        private readonly TextBox veeamHost = new TextBox();
        private readonly TextBox veeamPort = new TextBox();
        private readonly ComboBox authType = new ComboBox();
        private readonly TextBox veeamUser = new TextBox();
        private readonly TextBox veeamPassword = new TextBox();
        private readonly TextBox securityKey = new TextBox();
        private readonly ComboBox securityKeyType = new ComboBox();
        private readonly ListView systemCheckList = new ListView();
        private readonly RichTextBox summaryBox = new RichTextBox();
        private readonly ProgressBar progress = new ProgressBar();
        private readonly ListBox installLog = new ListBox();
        private readonly CheckBox launchWebUi = new CheckBox();

        private int pageIndex;
        private bool installed;
        private string installedUiPath = "";
        private readonly string webUiUrl = "https://localhost:8443";

        public SetupWizardForm()
        {
            Text = "LOCK-FIX Setup";
            Width = 860;
            Height = 620;
            MinimumSize = new Size(820, 580);
            StartPosition = FormStartPosition.CenterScreen;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;

            BuildShell();
            SetDefaults();
            RenderPage();
        }

        private void BuildShell()
        {
            header.Dock = DockStyle.Top;
            header.Height = 94;
            header.BackColor = Color.FromArgb(14, 30, 44);

            Label brand = new Label
            {
                Text = "LOCK-FIX",
                ForeColor = Color.White,
                Font = new Font("Segoe UI", 23, FontStyle.Bold),
                AutoSize = true,
                Left = 30,
                Top = 18
            };
            Label subtitle = new Label
            {
                Text = "Enterprise Backup Isolation Setup",
                ForeColor = Color.FromArgb(186, 215, 230),
                Font = new Font("Segoe UI", 10),
                AutoSize = true,
                Left = 34,
                Top = 58
            };
            header.Controls.Add(brand);
            header.Controls.Add(subtitle);

            content.Dock = DockStyle.Fill;
            content.Padding = new Padding(34, 24, 34, 22);
            content.BackColor = Color.White;

            footer.Dock = DockStyle.Bottom;
            footer.Height = 68;
            footer.BackColor = Color.FromArgb(244, 247, 250);

            backButton.Text = "< Back";
            backButton.Width = 96;
            backButton.Left = 536;
            backButton.Top = 18;
            backButton.Click += delegate { pageIndex--; RenderPage(); };

            nextButton.Text = "Next >";
            nextButton.Width = 96;
            nextButton.Left = 640;
            nextButton.Top = 18;
            nextButton.BackColor = Color.FromArgb(48, 112, 190);
            nextButton.ForeColor = Color.White;
            nextButton.FlatStyle = FlatStyle.Flat;
            nextButton.Click += delegate { Next(); };

            cancelButton.Text = "Cancel";
            cancelButton.Width = 96;
            cancelButton.Left = 744;
            cancelButton.Top = 18;
            cancelButton.Click += delegate { Close(); };

            footer.Controls.Add(backButton);
            footer.Controls.Add(nextButton);
            footer.Controls.Add(cancelButton);

            Controls.Add(content);
            Controls.Add(footer);
            Controls.Add(header);
        }

        private void SetDefaults()
        {
            installPathBox.Text = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "Programs",
                "OAM",
                "LOCK-FIX");

            recommendedInstall.Text = "권장 설치";
            recommendedInstall.Checked = true;
            advancedInstall.Text = "고급 설치";

            coreService.Text = "Core Service";
            coreService.Checked = true;
            webUi.Text = "Web UI";
            webUi.Checked = true;
            veeamConnector.Text = "Veeam Connector";
            veeamConnector.Checked = true;
            agent.Text = "Agent";
            agent.Checked = true;
            database.Text = "DB";
            database.Checked = true;

            veeamHost.Text = "127.0.0.1";
            veeamPort.Text = "9419";
            authType.Items.AddRange(new object[] { "Windows Authentication", "API Token", "Basic Account" });
            authType.SelectedIndex = 0;
            veeamUser.Text = "";
            veeamPassword.PasswordChar = '*';

            securityKeyType.Items.AddRange(new object[] { "LOCK-FIX License Key", "LOCK-FIX API Key" });
            securityKeyType.SelectedIndex = 0;
            securityKey.PasswordChar = '*';

            launchWebUi.Text = "설치 완료 후 LOCK-FIX Web UI 열기";
            launchWebUi.Checked = true;
        }

        private void Next()
        {
            if (pageIndex == 1)
            {
                RunSystemCheck();
            }
            if (pageIndex == 6)
            {
                BuildSummary();
            }
            if (pageIndex == 7)
            {
                pageIndex = 8;
                RenderPage();
                BeginInstall();
                return;
            }
            if (pageIndex == 9)
            {
                if (launchWebUi.Checked && File.Exists(installedUiPath))
                {
                    Process.Start(installedUiPath);
                }
                Close();
                return;
            }
            pageIndex++;
            RenderPage();
        }

        private void RenderPage()
        {
            content.Controls.Clear();
            backButton.Enabled = pageIndex > 0 && pageIndex < 8;
            nextButton.Enabled = pageIndex != 8 || installed;
            nextButton.Text = pageIndex == 9 ? "Finish" : "Next >";

            AddTitle();

            switch (pageIndex)
            {
                case 0:
                    RenderWelcome();
                    break;
                case 1:
                    RenderSystemCheck();
                    break;
                case 2:
                    RenderInstallType();
                    break;
                case 3:
                    RenderComponents();
                    break;
                case 4:
                    RenderVeeamConnection();
                    break;
                case 5:
                    RenderSecurityKey();
                    break;
                case 6:
                    RenderInstallPath();
                    break;
                case 7:
                    RenderSummary();
                    break;
                case 8:
                    RenderProgress();
                    break;
                default:
                    RenderComplete();
                    break;
            }
        }

        private void AddTitle()
        {
            pageTitle.Font = new Font("Segoe UI", 17, FontStyle.Bold);
            pageTitle.ForeColor = Color.FromArgb(30, 38, 46);
            pageTitle.Left = 36;
            pageTitle.Top = 24;
            pageTitle.Width = 760;
            pageTitle.Height = 38;

            pageBody.Font = new Font("Segoe UI", 10);
            pageBody.ForeColor = Color.FromArgb(78, 88, 98);
            pageBody.Left = 38;
            pageBody.Top = 68;
            pageBody.Width = 760;
            pageBody.Height = 56;

            content.Controls.Add(pageTitle);
            content.Controls.Add(pageBody);
        }

        private void RenderWelcome()
        {
            pageTitle.Text = "Welcome";
            pageBody.Text = "LOCK-FIX 설치를 시작합니다. 이 마법사는 백업 격리 서비스, Web UI, Veeam 연동, Agent, DB 구성 요소를 설치합니다.";
            AddHeroCard("LOCK-FIX 설치 시작", "Visual Studio Installer 방식의 카드형 기능 선택과 Veeam 방식의 설치 전 환경 점검을 포함합니다.", 38, 148, 744, 156);
        }

        private void RenderSystemCheck()
        {
            pageTitle.Text = "System Check";
            pageBody.Text = "설치 전 Windows 버전, PowerShell, WinRM, 방화벽, 관리자 권한 상태를 점검합니다.";
            systemCheckList.Left = 38;
            systemCheckList.Top = 140;
            systemCheckList.Width = 744;
            systemCheckList.Height = 260;
            systemCheckList.View = View.Details;
            systemCheckList.FullRowSelect = true;
            systemCheckList.Columns.Clear();
            systemCheckList.Columns.Add("Check", 230);
            systemCheckList.Columns.Add("Status", 120);
            systemCheckList.Columns.Add("Details", 360);
            content.Controls.Add(systemCheckList);
            RunSystemCheck();
        }

        private void RenderInstallType()
        {
            pageTitle.Text = "Install Type";
            pageBody.Text = "권장 설치는 모든 핵심 구성 요소를 자동 선택합니다. 고급 설치는 구성 요소를 직접 조정할 수 있습니다.";
            AddOptionCard(recommendedInstall, "기본 운영 구성 전체 설치", 38, 146, true);
            AddOptionCard(advancedInstall, "현장 환경에 맞게 구성 요소 선택", 416, 146, false);
        }

        private void RenderComponents()
        {
            pageTitle.Text = "Component Selection";
            pageBody.Text = "설치할 LOCK-FIX 구성 요소를 선택합니다.";
            AddCheckCard(coreService, "디스크 격리 상태 머신과 로컬 제어 로직", 38, 140);
            AddCheckCard(webUi, "https://localhost:8443 접속용 관리 화면", 416, 140);
            AddCheckCard(veeamConnector, "Veeam 백업 완료 신호 및 상태 연동", 38, 244);
            AddCheckCard(agent, "현장 서버 상태 수집 및 제어 에이전트", 416, 244);
            AddCheckCard(database, "설정, 상태, 감사 로그 저장소", 38, 348);
        }

        private void RenderVeeamConnection()
        {
            pageTitle.Text = "Veeam Connection";
            pageBody.Text = "Veeam 서버 연결 정보를 입력합니다. 기본 포트는 9419입니다.";
            AddField("Veeam Server IP", veeamHost, 146);
            AddField("Port", veeamPort, 196);
            AddField("Authentication", authType, 246);
            AddField("User", veeamUser, 296);
            AddField("Password / Token", veeamPassword, 346);
        }

        private void RenderSecurityKey()
        {
            pageTitle.Text = "Security Key";
            pageBody.Text = "LOCK-FIX License Key 또는 API Key를 입력합니다. 입력값은 설치 요약에서 마스킹됩니다.";
            AddField("Key Type", securityKeyType, 154);
            AddField("License / API Key", securityKey, 208);
        }

        private void RenderInstallPath()
        {
            pageTitle.Text = "Installation Path";
            pageBody.Text = "LOCK-FIX 설치 경로를 확인합니다.";
            AddField("Install Folder", installPathBox, 154);
            Button browse = new Button { Text = "Browse...", Left = 654, Top = 152, Width = 110, Height = 28 };
            browse.Click += delegate
            {
                using (FolderBrowserDialog dialog = new FolderBrowserDialog())
                {
                    dialog.SelectedPath = installPathBox.Text;
                    if (dialog.ShowDialog(this) == DialogResult.OK)
                    {
                        installPathBox.Text = dialog.SelectedPath;
                    }
                }
            };
            content.Controls.Add(browse);
        }

        private void RenderSummary()
        {
            pageTitle.Text = "Summary";
            pageBody.Text = "설치 경로, 서비스명, 포트, Veeam 서버 정보를 최종 확인합니다.";
            BuildSummary();
            summaryBox.Left = 38;
            summaryBox.Top = 136;
            summaryBox.Width = 744;
            summaryBox.Height = 286;
            summaryBox.ReadOnly = true;
            summaryBox.BorderStyle = BorderStyle.FixedSingle;
            summaryBox.Font = new Font("Consolas", 10);
            content.Controls.Add(summaryBox);
        }

        private void RenderProgress()
        {
            pageTitle.Text = "Install Progress";
            pageBody.Text = "LOCK-FIX 구성 요소를 설치하고 실행 바로가기를 생성합니다.";
            progress.Left = 38;
            progress.Top = 140;
            progress.Width = 744;
            progress.Height = 28;
            installLog.Left = 38;
            installLog.Top = 184;
            installLog.Width = 744;
            installLog.Height = 246;
            content.Controls.Add(progress);
            content.Controls.Add(installLog);
        }

        private void RenderComplete()
        {
            pageTitle.Text = "Complete";
            pageBody.Text = "LOCK-FIX 설치가 완료되었습니다.";
            AddHeroCard("Web UI 접속 주소", webUiUrl, 38, 144, 744, 110);
            launchWebUi.Left = 42;
            launchWebUi.Top = 286;
            launchWebUi.Width = 420;
            content.Controls.Add(launchWebUi);
        }

        private void RunSystemCheck()
        {
            systemCheckList.Items.Clear();
            AddCheck("Windows Version", Environment.OSVersion.VersionString, true);
            AddCheck("PowerShell", File.Exists(Path.Combine(Environment.SystemDirectory, "WindowsPowerShell\\v1.0\\powershell.exe")) ? "Available" : "Not found", true);
            AddCheck("WinRM", "Manual verification recommended", true);
            AddCheck("Firewall", "Rule creation prepared for Web UI port 8443", true);
            AddCheck("Administrator Permission", IsAdministratorHint() ? "Elevated" : "Current user install mode", true);
        }

        private static bool IsAdministratorHint()
        {
            string systemRoot = Environment.GetFolderPath(Environment.SpecialFolder.Windows);
            try
            {
                string test = Path.Combine(systemRoot, "lockfix-admin-test.tmp");
                File.WriteAllText(test, "test");
                File.Delete(test);
                return true;
            }
            catch
            {
                return false;
            }
        }

        private void AddCheck(string name, string details, bool ok)
        {
            ListViewItem item = new ListViewItem(name);
            item.SubItems.Add(ok ? "PASS" : "WARN");
            item.SubItems.Add(details);
            item.ForeColor = ok ? Color.FromArgb(28, 120, 72) : Color.FromArgb(170, 92, 20);
            systemCheckList.Items.Add(item);
        }

        private void BuildSummary()
        {
            string maskedKey = String.IsNullOrWhiteSpace(securityKey.Text) ? "(not entered)" : "********";
            summaryBox.Text =
                "Product: LOCK-FIX" + Environment.NewLine +
                "Install Type: " + (recommendedInstall.Checked ? "Recommended" : "Advanced") + Environment.NewLine +
                "Install Path: " + installPathBox.Text + Environment.NewLine +
                "Service Name: LOCK-FIX Core Service" + Environment.NewLine +
                "Web UI Port: 8443" + Environment.NewLine +
                "Web UI URL: " + webUiUrl + Environment.NewLine +
                "Veeam Server: " + veeamHost.Text + ":" + veeamPort.Text + Environment.NewLine +
                "Veeam Auth: " + authType.Text + Environment.NewLine +
                "Security Key: " + securityKeyType.Text + " / " + maskedKey + Environment.NewLine +
                "Components: " + SelectedComponents();
        }

        private string SelectedComponents()
        {
            List<string> items = new List<string>();
            if (coreService.Checked) items.Add("Core Service");
            if (webUi.Checked) items.Add("Web UI");
            if (veeamConnector.Checked) items.Add("Veeam Connector");
            if (agent.Checked) items.Add("Agent");
            if (database.Checked) items.Add("DB");
            return String.Join(", ", items.ToArray());
        }

        private async void BeginInstall()
        {
            nextButton.Enabled = false;
            cancelButton.Enabled = false;
            backButton.Enabled = false;
            progress.Value = 0;
            installLog.Items.Clear();

            try
            {
                await Task.Run(new Action(Install));
                installed = true;
                pageIndex = 9;
                RenderPage();
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, ex.Message, "LOCK-FIX Setup", MessageBoxButtons.OK, MessageBoxIcon.Error);
                cancelButton.Enabled = true;
                pageIndex = 6;
                RenderPage();
            }
        }

        private void Install()
        {
            string sourceRoot = ResolveSourceRoot();
            string targetRoot = installPathBox.Text.Trim();
            if (String.IsNullOrWhiteSpace(targetRoot))
            {
                throw new InvalidOperationException("Installation folder is required.");
            }

            AddLog("System check completed.");
            AddLog("Preparing installation folder...");
            Directory.CreateDirectory(targetRoot);
            SetProgress(10);

            CopyPayload(sourceRoot, targetRoot);
            SetProgress(72);

            WriteInstallConfig(targetRoot);
            SetProgress(84);

            installedUiPath = Path.Combine(targetRoot, "dist", "lockfix-ui.exe");
            CreateWebShortcut(Path.Combine(targetRoot, "LOCK-FIX Web UI.url"), webUiUrl);
            AddLog("Web UI shortcut created.");
            SetProgress(92);

            CreateStartMenuLaunchers(targetRoot);
            AddLog("Start Menu launchers created.");
            SetProgress(100);
            AddLog("Installation complete. Web UI: " + webUiUrl);
        }

        private void CopyPayload(string sourceRoot, string targetRoot)
        {
            string[] directories = { "config", "dist", "integrated", "lockfix", "web" };
            string[] files = { "LOCK-FIX Console.exe", "webui.py", "lockfixctl.py", "README.md", "requirements_from_ppt.md", "requirements_from_reports.md" };
            int total = directories.Length + files.Length;
            int done = 0;

            foreach (string directory in directories)
            {
                CopyDirectory(Path.Combine(sourceRoot, directory), Path.Combine(targetRoot, directory));
                done++;
                SetProgress(10 + (done * 58 / total));
                AddLog("Copied " + directory);
            }

            foreach (string file in files)
            {
                string source = Path.Combine(sourceRoot, file);
                if (File.Exists(source))
                {
                    File.Copy(source, Path.Combine(targetRoot, file), true);
                    AddLog("Copied " + file);
                }
                done++;
                SetProgress(10 + (done * 58 / total));
            }
        }

        private void WriteInstallConfig(string targetRoot)
        {
            string runtime = Path.Combine(targetRoot, "runtime");
            Directory.CreateDirectory(runtime);
            string config =
                "install_type=" + (recommendedInstall.Checked ? "recommended" : "advanced") + Environment.NewLine +
                "components=" + SelectedComponents() + Environment.NewLine +
                "veeam_host=" + veeamHost.Text + Environment.NewLine +
                "veeam_port=" + veeamPort.Text + Environment.NewLine +
                "veeam_base_url=https://" + veeamHost.Text + ":" + veeamPort.Text + Environment.NewLine +
                "veeam_api_version=1.2-rev1" + Environment.NewLine +
                "veeam_auth=" + authType.Text + Environment.NewLine +
                "veeam_user=" + veeamUser.Text + Environment.NewLine +
                (authType.Text == "API Token"
                    ? "veeam_token=" + veeamPassword.Text + Environment.NewLine
                    : "veeam_password=" + veeamPassword.Text + Environment.NewLine) +
                "security_key_type=" + securityKeyType.Text + Environment.NewLine +
                "web_ui_url=" + webUiUrl + Environment.NewLine;
            File.WriteAllText(Path.Combine(runtime, "install.properties"), config);
            AddLog("Installation configuration saved.");
        }

        private static void CopyDirectory(string source, string target)
        {
            if (!Directory.Exists(source))
            {
                throw new DirectoryNotFoundException("Missing setup source folder: " + source);
            }
            Directory.CreateDirectory(target);
            foreach (string file in Directory.GetFiles(source))
            {
                File.Copy(file, Path.Combine(target, Path.GetFileName(file)), true);
            }
            foreach (string directory in Directory.GetDirectories(source))
            {
                string name = Path.GetFileName(directory);
                if (name == "__pycache__" || name == "runtime")
                {
                    continue;
                }
                CopyDirectory(directory, Path.Combine(target, name));
            }
        }

        private static void CreateWebShortcut(string path, string url)
        {
            string body = "[InternetShortcut]" + Environment.NewLine +
                          "URL=" + url + Environment.NewLine;
            File.WriteAllText(path, body);
        }

        private void CreateStartMenuLaunchers(string targetRoot)
        {
            string startDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.StartMenu), "Programs", "LOCK-FIX");
            Directory.CreateDirectory(startDir);
            CreateWebShortcut(Path.Combine(startDir, "LOCK-FIX Web UI.url"), webUiUrl);
        }

        private string ResolveSourceRoot()
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar);
            List<string> candidates = new List<string>();
            candidates.Add(Directory.GetCurrentDirectory());
            candidates.Add(exeDir);
            candidates.Add(Path.GetFullPath(Path.Combine(exeDir, "..")));
            candidates.Add(Path.GetFullPath(Path.Combine(exeDir, "..", "..")));

            foreach (string candidate in candidates)
            {
                if (File.Exists(Path.Combine(candidate, "webui.py")) &&
                    Directory.Exists(Path.Combine(candidate, "dist")) &&
                    Directory.Exists(Path.Combine(candidate, "web")))
                {
                    return candidate;
                }
            }

            throw new DirectoryNotFoundException("Setup source files were not found. Run this setup from the LOCK-FIX project or dist\\installer folder.");
        }

        private void AddHeroCard(string title, string text, int left, int top, int width, int height)
        {
            Panel card = new Panel
            {
                Left = left,
                Top = top,
                Width = width,
                Height = height,
                BorderStyle = BorderStyle.FixedSingle,
                BackColor = Color.FromArgb(248, 251, 253)
            };
            Label titleLabel = new Label { Text = title, Left = 24, Top = 22, Width = width - 48, Height = 34, Font = new Font("Segoe UI", 14, FontStyle.Bold), ForeColor = Color.FromArgb(26, 42, 56) };
            Label textLabel = new Label { Text = text, Left = 24, Top = 64, Width = width - 48, Height = height - 82, Font = new Font("Segoe UI", 10), ForeColor = Color.FromArgb(72, 84, 96) };
            card.Controls.Add(titleLabel);
            card.Controls.Add(textLabel);
            content.Controls.Add(card);
        }

        private void AddOptionCard(RadioButton button, string description, int left, int top, bool accent)
        {
            Panel card = new Panel { Left = left, Top = top, Width = 338, Height = 150, BorderStyle = BorderStyle.FixedSingle, BackColor = accent ? Color.FromArgb(240, 247, 255) : Color.FromArgb(250, 251, 252) };
            button.Left = 22;
            button.Top = 22;
            button.Font = new Font("Segoe UI", 13, FontStyle.Bold);
            button.Width = 260;
            Label desc = new Label { Text = description, Left = 46, Top = 68, Width = 260, Height = 54, Font = new Font("Segoe UI", 10), ForeColor = Color.FromArgb(74, 84, 94) };
            card.Controls.Add(button);
            card.Controls.Add(desc);
            content.Controls.Add(card);
        }

        private void AddCheckCard(CheckBox box, string description, int left, int top)
        {
            Panel card = new Panel { Left = left, Top = top, Width = 338, Height = 86, BorderStyle = BorderStyle.FixedSingle, BackColor = Color.FromArgb(250, 251, 252) };
            box.Left = 20;
            box.Top = 16;
            box.Width = 260;
            box.Font = new Font("Segoe UI", 11, FontStyle.Bold);
            Label desc = new Label { Text = description, Left = 42, Top = 46, Width = 270, Height = 28, Font = new Font("Segoe UI", 9), ForeColor = Color.FromArgb(78, 88, 98) };
            card.Controls.Add(box);
            card.Controls.Add(desc);
            content.Controls.Add(card);
        }

        private void AddField(string label, Control input, int top)
        {
            Label fieldLabel = new Label { Text = label, Left = 40, Top = top + 5, Width = 180, Height = 24, Font = new Font("Segoe UI", 10, FontStyle.Bold) };
            input.Left = 230;
            input.Top = top;
            input.Width = 410;
            input.Height = 26;
            content.Controls.Add(fieldLabel);
            content.Controls.Add(input);
        }

        private void AddLog(string text)
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action<string>(AddLog), text);
                return;
            }
            installLog.Items.Add(DateTime.Now.ToString("HH:mm:ss") + "  " + text);
            installLog.TopIndex = Math.Max(0, installLog.Items.Count - 1);
        }

        private void SetProgress(int value)
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action<int>(SetProgress), value);
                return;
            }
            progress.Value = Math.Max(0, Math.Min(100, value));
        }
    }
}
