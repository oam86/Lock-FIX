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

        private static int Main(string[] args)
        {
            try
            {
                bool noBrowser = Array.IndexOf(args, "--no-browser") >= 0;
                string exeDir = AppDomain.CurrentDomain.BaseDirectory;
                string root = Directory.GetParent(exeDir.TrimEnd(Path.DirectorySeparatorChar)).FullName;
                string webui = Path.Combine(root, "webui.py");
                string config = Path.Combine(root, "config", "lockfix.example.json");

                if (!File.Exists(webui))
                {
                    throw new FileNotFoundException("webui.py not found", webui);
                }

                if (!IsServerReady())
                {
                    StartServer(root, webui, config);
                    WaitForServer();
                }

                if (!noBrowser)
                {
                    OpenBrowser();
                }

                Console.WriteLine("LOCK-FIX PoC UI is running.");
                Console.WriteLine(Url);
                return 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("LOCK-FIX UI launch failed: " + ex.Message);
                Console.Error.WriteLine("Manual start:");
                Console.Error.WriteLine("python webui.py --host 127.0.0.1 --port 8088 --config config\\lockfix.example.json");
                return 1;
            }
        }

        private static void StartServer(string root, string webui, string config)
        {
            string python = FindPython();
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = python;
            start.Arguments = Quote(webui) + " --host 127.0.0.1 --port 8088 --config " + Quote(config);
            start.WorkingDirectory = root;
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.RedirectStandardOutput = false;
            start.RedirectStandardError = false;
            Process.Start(start);
        }

        private static string FindPython()
        {
            string bundled = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                ".cache",
                "codex-runtimes",
                "codex-primary-runtime",
                "dependencies",
                "python",
                "python.exe"
            );

            if (File.Exists(bundled))
            {
                return bundled;
            }

            return "python";
        }

        private static void WaitForServer()
        {
            DateTime deadline = DateTime.UtcNow.AddSeconds(10);
            while (DateTime.UtcNow < deadline)
            {
                if (IsServerReady())
                {
                    return;
                }
                Thread.Sleep(300);
            }
            throw new TimeoutException("local web server did not respond on " + Url);
        }

        private static bool IsServerReady()
        {
            try
            {
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(Url + "/api/summary");
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
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = Url;
            start.UseShellExecute = true;
            Process.Start(start);
        }

        private static string Quote(string value)
        {
            return "\"" + value.Replace("\"", "\\\"") + "\"";
        }
    }
}
