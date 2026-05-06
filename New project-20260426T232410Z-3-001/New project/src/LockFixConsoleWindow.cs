using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Threading;

namespace LockFix
{
    internal static class ConsoleWindow
    {
        private const string Url = "http://127.0.0.1:8088";
        private static string logPath = "";

        private static int Main(string[] args)
        {
            Process serverProcess = null;
            try
            {
                Console.Title = "LOCK-FIX Console";
                Console.WriteLine("LOCK-FIX Web UI Console");
                Console.WriteLine();

                string root = ResolveRoot();
                logPath = Path.Combine(root, "runtime", "console.log");
                Directory.CreateDirectory(Path.GetDirectoryName(logPath));
                string config = Path.Combine(root, "config", "lockfix.example.json");
                string python = FindPython(root);

                Log("Root: " + root);
                Log("Python: " + python);
                Log("URL: " + Url);
                LoadVeeamEnvironment(root);
                Log("");

                if (!File.Exists(Path.Combine(root, "lockfix", "webui_server.py")))
                {
                    throw new FileNotFoundException("lockfix.webui_server module not found", Path.Combine(root, "lockfix", "webui_server.py"));
                }

                if (!IsServerReady())
                {
                    serverProcess = StartServerWithRetry(root, python, config);
                }

                Log("LOCK-FIX PoC UI is running.");
                Log(Url);
                Log("Keep this console open while using LOCK-FIX.");
                Log("Press Ctrl+C or close this window to stop the local console.");
                Log("");

                OpenBrowser();
                WatchServer(serverProcess);
                return 0;
            }
            catch (Exception ex)
            {
                Log("");
                Log("LOCK-FIX console failed:");
                Log(ex.Message);
                Log("");
                Log("Console will stay open. Press Ctrl+C or close this window manually.");
                WaitForever();
                return 1;
            }
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

        private static Process StartServer(string root, string python, string config)
        {
            Log("Starting local Web UI server...");
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = python;
            start.Arguments = "-u -m lockfix.webui_server --host 127.0.0.1 --port 8088 --config " + Quote(config);
            start.WorkingDirectory = root;
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;

            Process process = new Process();
            process.StartInfo = start;
            process.EnableRaisingEvents = true;
            process.OutputDataReceived += delegate(object sender, DataReceivedEventArgs e)
            {
                if (!String.IsNullOrEmpty(e.Data)) Log("[webui] " + e.Data);
            };
            process.ErrorDataReceived += delegate(object sender, DataReceivedEventArgs e)
            {
                if (!String.IsNullOrEmpty(e.Data)) Log("[webui] " + e.Data);
            };
            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();
            return process;
        }

        private static void LoadVeeamEnvironment(string root)
        {
            string propertiesPath = Path.Combine(root, "runtime", "install.properties");
            if (!File.Exists(propertiesPath))
            {
                if (String.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("LOCKFIX_VEEAM_PASSWORD")))
                {
                    Log("Veeam password environment variable is not set. Set LOCKFIX_VEEAM_PASSWORD before starting the console.");
                }
                return;
            }

            Dictionary<string, string> properties = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (string rawLine in File.ReadAllLines(propertiesPath))
            {
                string line = rawLine.Trim();
                if (line.Length == 0 || line.StartsWith("#")) continue;
                int separator = line.IndexOf('=');
                if (separator <= 0) continue;
                string key = line.Substring(0, separator).Trim();
                string value = line.Substring(separator + 1).Trim();
                properties[key] = value;
            }

            SetEnvIfPresent("LOCKFIX_VEEAM_BASE_URL", properties, "veeam_base_url");
            SetEnvIfPresent("LOCKFIX_VEEAM_API_VERSION", properties, "veeam_api_version");
            SetEnvIfPresent("LOCKFIX_VEEAM_USER", properties, "veeam_user");

            if (String.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("LOCKFIX_VEEAM_PASSWORD"))
                && properties.ContainsKey("veeam_password")
                && !String.IsNullOrWhiteSpace(properties["veeam_password"]))
            {
                Environment.SetEnvironmentVariable("LOCKFIX_VEEAM_PASSWORD", properties["veeam_password"]);
                Log("Veeam password loaded from installation settings into the Web UI process environment.");
            }
            else if (String.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("LOCKFIX_VEEAM_PASSWORD")))
            {
                Log("Veeam password environment variable is not set. Web UI Veeam calls will report the missing password_env value.");
            }
            else
            {
                Log("Veeam password environment variable is set for the Web UI process.");
            }
        }

        private static void SetEnvIfPresent(string environmentName, Dictionary<string, string> properties, string propertyName)
        {
            if (properties.ContainsKey(propertyName) && !String.IsNullOrWhiteSpace(properties[propertyName]))
            {
                Environment.SetEnvironmentVariable(environmentName, properties[propertyName]);
            }
        }

        private static Process StartServerWithRetry(string root, string python, string config)
        {
            Exception lastError = null;
            for (int attempt = 1; attempt <= 3; attempt++)
            {
                Process process = null;
                try
                {
                    Log("Web UI startup attempt " + attempt + " of 3.");
                    process = StartServer(root, python, config);
                    WaitForServer(process);
                    return process;
                }
                catch (Exception ex)
                {
                    lastError = ex;
                    Log("Startup attempt " + attempt + " failed: " + ex.Message);
                    KillTimedOutProcess(process);
                    Thread.Sleep(1000);
                }
            }
            throw lastError ?? new TimeoutException("local web server did not respond on " + Url);
        }

        private static void WaitForServer(Process serverProcess)
        {
            DateTime deadline = DateTime.UtcNow.AddSeconds(15);
            while (DateTime.UtcNow < deadline)
            {
                if (IsServerReady()) return;
                if (serverProcess != null && serverProcess.HasExited)
                {
                    throw new InvalidOperationException("local web server exited early with code " + serverProcess.ExitCode);
                }
                Thread.Sleep(300);
            }
            KillTimedOutProcess(serverProcess);
            throw new TimeoutException("local web server did not respond on " + Url);
        }

        private static void KillTimedOutProcess(Process serverProcess)
        {
            try
            {
                if (serverProcess != null && !serverProcess.HasExited)
                {
                    Log("Web UI subprocess startup timed out. Stopping process " + serverProcess.Id + ".");
                    serverProcess.Kill();
                    serverProcess.WaitForExit(3000);
                }
            }
            catch (Exception ex)
            {
                Log("Unable to stop timed-out Web UI subprocess: " + ex.Message);
            }
        }

        private static void WatchServer(Process serverProcess)
        {
            if (serverProcess != null)
            {
                serverProcess.WaitForExit();
                Log("LOCK-FIX Web UI server stopped with code " + serverProcess.ExitCode + ".");
                Log("Console will stay open. Press Ctrl+C or close this window manually.");
                WaitForever();
                return;
            }

            while (IsServerReady())
            {
                Thread.Sleep(2000);
            }
            Log("Existing LOCK-FIX Web UI server is no longer responding.");
            Log("Console will stay open. Press Ctrl+C or close this window manually.");
            WaitForever();
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
                if (candidate == "python" || File.Exists(candidate))
                {
                    return candidate;
                }
            }
            return "python";
        }

        private static void OpenBrowser()
        {
            try
            {
                ProcessStartInfo start = new ProcessStartInfo();
                start.FileName = Url;
                start.UseShellExecute = true;
                Process.Start(start);
            }
            catch (Exception ex)
            {
                Log("Open browser warning: " + ex.Message);
            }
        }

        private static void WaitForever()
        {
            while (true)
            {
                Thread.Sleep(60 * 1000);
            }
        }

        private static void Log(string message)
        {
            string line = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " " + message;
            Console.WriteLine(message);
            try
            {
                if (!String.IsNullOrEmpty(logPath))
                {
                    File.AppendAllText(logPath, line + Environment.NewLine);
                }
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
