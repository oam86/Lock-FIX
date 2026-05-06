using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Threading;

namespace LockFix
{
    internal static class UiLauncher
    {
        private const string Url = "http://127.0.0.1:8088";
        private static string logPath = "";

        private static int Main(string[] args)
        {
            try
            {
                bool noBrowser = Array.IndexOf(args, "--no-browser") >= 0;
                bool exitAfterLaunch = Array.IndexOf(args, "--exit-after-launch") >= 0;
                string exeDir = AppDomain.CurrentDomain.BaseDirectory;
                string root = Directory.GetParent(exeDir.TrimEnd(Path.DirectorySeparatorChar)).FullName;
                logPath = Path.Combine(root, "runtime", "console.log");
                Directory.CreateDirectory(Path.GetDirectoryName(logPath));
                string config = Path.Combine(root, "config", "lockfix.example.json");
                Process serverProcess = null;

                Log("LOCK-FIX UI launcher starting.");
                Log("Root: " + root);
                Log("WebUI module: lockfix.webui_server");

                if (!File.Exists(Path.Combine(root, "lockfix", "webui_server.py")))
                {
                    throw new FileNotFoundException("lockfix.webui_server module not found", Path.Combine(root, "lockfix", "webui_server.py"));
                }

                if (!IsServerReady())
                {
                    serverProcess = StartServerWithRetry(root, config);
                }

                if (!noBrowser)
                {
                    OpenBrowser();
                }

                Log("LOCK-FIX PoC UI is running.");
                Log(Url);
                if (!exitAfterLaunch)
                {
                    Log("Console stays open while the local Web UI server is running.");
                    Log("Close this window to stop watching the launcher.");
                    KeepConsoleOpen(serverProcess);
                }
                return 0;
            }
            catch (Exception ex)
            {
                Log("LOCK-FIX UI launch failed: " + ex.Message);
                Log("Manual start:");
                Log("python -m lockfix.webui_server --host 127.0.0.1 --port 8088 --config config\\lockfix.example.json");
                Log("Console will stay open. Press Ctrl+C or close this window manually.");
                WaitForever();
                return 1;
            }
        }

        private static Process StartServer(string root, string config)
        {
            string python = FindPython(root);
            Log("Python: " + python);
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = python;
            start.Arguments = "-m lockfix.webui_server --host 127.0.0.1 --port 8088 --config " + Quote(config);
            start.WorkingDirectory = root;
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;
            Process process = new Process();
            process.StartInfo = start;
            process.OutputDataReceived += delegate(object sender, DataReceivedEventArgs e)
            {
                if (!String.IsNullOrEmpty(e.Data))
                {
                    Log("[webui] " + e.Data);
                }
            };
            process.ErrorDataReceived += delegate(object sender, DataReceivedEventArgs e)
            {
                if (!String.IsNullOrEmpty(e.Data))
                {
                    Log("[webui] " + e.Data);
                }
            };
            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();
            return process;
        }

        private static Process StartServerWithRetry(string root, string config)
        {
            Exception lastError = null;
            for (int attempt = 1; attempt <= 3; attempt++)
            {
                Process process = null;
                try
                {
                    Log("Web UI startup attempt " + attempt + " of 3.");
                    process = StartServer(root, config);
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

        private static string FindPython(string root)
        {
            string[] candidates = new string[]
            {
                Path.Combine(root, "python", "python.exe"),
                Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                    ".cache",
                    "codex-runtimes",
                    "codex-primary-runtime",
                    "dependencies",
                    "python",
                    "python.exe"
                ),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "LOCK-FIX", "python", "python.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "LOCK-FIX", "python", "python.exe")
            };

            foreach (string candidate in candidates)
            {
                if (File.Exists(candidate))
                {
                    return candidate;
                }
            }

            return "python";
        }

        private static void WaitForServer(Process serverProcess)
        {
            DateTime deadline = DateTime.UtcNow.AddSeconds(10);
            while (DateTime.UtcNow < deadline)
            {
                if (IsServerReady())
                {
                    return;
                }
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
                Log("Open this address manually if the browser did not open: " + Url);
            }
        }

        private static void KeepConsoleOpen(Process serverProcess)
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
            Log("LOCK-FIX Web UI server is no longer responding.");
            Log("Console will stay open. Press Ctrl+C or close this window manually.");
            WaitForever();
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
