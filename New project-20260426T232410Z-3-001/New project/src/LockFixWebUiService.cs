using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.ServiceProcess;
using System.Threading;

namespace LockFix
{
    public sealed class LockFixWebUiService : ServiceBase
    {
        private const string ServiceTitle = "LOCK-FIX Web UI";
        private const string Url = "http://127.0.0.1:8088";
        private volatile bool stopping;
        private Thread worker;
        private Process serverProcess;
        private string root = "";
        private string logPath = "";

        public LockFixWebUiService()
        {
            ServiceName = "LOCKFIXWebUI";
            CanStop = true;
            CanShutdown = true;
            AutoLog = true;
        }

        public static void Main()
        {
            ServiceBase.Run(new LockFixWebUiService());
        }

        protected override void OnStart(string[] args)
        {
            stopping = false;
            root = ResolveRoot();
            logPath = Path.Combine(root, "runtime", "webui-service.log");
            Directory.CreateDirectory(Path.GetDirectoryName(logPath));
            worker = new Thread(ServiceLoop);
            worker.IsBackground = true;
            worker.Start();
            Log(ServiceTitle + " started. URL: " + Url);
        }

        protected override void OnStop()
        {
            stopping = true;
            StopServer();
            if (worker != null && !worker.Join(5000))
            {
                Log("Service worker did not stop within timeout.");
            }
            Log(ServiceTitle + " stopped.");
        }

        private void ServiceLoop()
        {
            while (!stopping)
            {
                try
                {
                    if (!IsServerReady() && (serverProcess == null || serverProcess.HasExited))
                    {
                        StartServer();
                    }
                }
                catch (Exception ex)
                {
                    Log("Web UI service loop warning: " + ex.Message);
                }
                Thread.Sleep(3000);
            }
        }

        private void StartServer()
        {
            string python = FindPython(root);
            string config = Path.Combine(root, "config", "lockfix.example.json");
            LoadVeeamEnvironment();

            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = python;
            start.Arguments = "-u -m lockfix.webui_server --host 127.0.0.1 --port 8088 --config " + Quote(config);
            start.WorkingDirectory = root;
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;
            ApplyVeeamEnvironment(start);

            serverProcess = new Process();
            serverProcess.StartInfo = start;
            serverProcess.EnableRaisingEvents = true;
            serverProcess.OutputDataReceived += delegate(object sender, DataReceivedEventArgs e)
            {
                if (!String.IsNullOrWhiteSpace(e.Data)) Log("[webui] " + e.Data);
            };
            serverProcess.ErrorDataReceived += delegate(object sender, DataReceivedEventArgs e)
            {
                if (!String.IsNullOrWhiteSpace(e.Data)) Log("[webui] " + e.Data);
            };
            serverProcess.Start();
            serverProcess.BeginOutputReadLine();
            serverProcess.BeginErrorReadLine();
            Log("Started Web UI subprocess PID " + serverProcess.Id + " using " + python);
        }

        private void StopServer()
        {
            try
            {
                if (serverProcess != null && !serverProcess.HasExited)
                {
                    serverProcess.Kill();
                    serverProcess.WaitForExit(3000);
                    Log("Stopped Web UI subprocess.");
                }
            }
            catch (Exception ex)
            {
                Log("Unable to stop Web UI subprocess: " + ex.Message);
            }
        }

        private void ApplyVeeamEnvironment(ProcessStartInfo start)
        {
            foreach (KeyValuePair<string, string> item in ReadInstallProperties())
            {
                if (item.Key == "veeam_base_url") start.EnvironmentVariables["LOCKFIX_VEEAM_BASE_URL"] = item.Value;
                if (item.Key == "veeam_api_version") start.EnvironmentVariables["LOCKFIX_VEEAM_API_VERSION"] = item.Value;
                if (item.Key == "veeam_user") start.EnvironmentVariables["LOCKFIX_VEEAM_USER"] = item.Value;
                if (item.Key == "veeam_password") start.EnvironmentVariables["LOCKFIX_VEEAM_PASSWORD"] = item.Value;
                if (item.Key == "veeam_host") start.EnvironmentVariables["LOCKFIX_VEEAM_HOST"] = item.Value;
                if (item.Key == "veeam_port") start.EnvironmentVariables["LOCKFIX_VEEAM_PORT"] = item.Value;
            }
        }

        private void LoadVeeamEnvironment()
        {
            Dictionary<string, string> properties = ReadInstallProperties();
            if (properties.ContainsKey("veeam_base_url")) Environment.SetEnvironmentVariable("LOCKFIX_VEEAM_BASE_URL", properties["veeam_base_url"]);
            if (properties.ContainsKey("veeam_api_version")) Environment.SetEnvironmentVariable("LOCKFIX_VEEAM_API_VERSION", properties["veeam_api_version"]);
            if (properties.ContainsKey("veeam_user")) Environment.SetEnvironmentVariable("LOCKFIX_VEEAM_USER", properties["veeam_user"]);
            if (properties.ContainsKey("veeam_password")) Environment.SetEnvironmentVariable("LOCKFIX_VEEAM_PASSWORD", properties["veeam_password"]);
        }

        private Dictionary<string, string> ReadInstallProperties()
        {
            Dictionary<string, string> properties = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            string propertiesPath = Path.Combine(root, "runtime", "install.properties");
            if (!File.Exists(propertiesPath)) return properties;
            foreach (string rawLine in File.ReadAllLines(propertiesPath))
            {
                string line = rawLine.Trim();
                if (line.Length == 0 || line.StartsWith("#")) continue;
                int separator = line.IndexOf('=');
                if (separator <= 0) continue;
                properties[line.Substring(0, separator).Trim()] = line.Substring(separator + 1).Trim();
            }
            return properties;
        }

        private static string ResolveRoot()
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar);
            if (String.Equals(Path.GetFileName(exeDir), "dist", StringComparison.OrdinalIgnoreCase))
            {
                return Directory.GetParent(exeDir).FullName;
            }
            return exeDir;
        }

        private static string FindPython(string root)
        {
            string[] candidates = new string[]
            {
                Path.Combine(root, "python", "python.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "LOCK-FIX", "python", "python.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "LOCK-FIX", "python", "python.exe"),
                "python"
            };
            foreach (string candidate in candidates)
            {
                if (candidate == "python" || File.Exists(candidate)) return candidate;
            }
            return "python";
        }

        private static bool IsServerReady()
        {
            try
            {
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(Url + "/");
                request.Timeout = 1000;
                request.Method = "GET";
                using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
                {
                    return response.StatusCode == HttpStatusCode.OK;
                }
            }
            catch
            {
                return false;
            }
        }

        private void Log(string message)
        {
            try
            {
                File.AppendAllText(logPath, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " " + message + Environment.NewLine);
            }
            catch
            {
            }
        }

        private static string Quote(string value)
        {
            return "\"" + value.Replace("\"", "\\\"") + "\"";
        }
    }
}
