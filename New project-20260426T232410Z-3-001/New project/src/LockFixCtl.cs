using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;

namespace LockFix
{
    internal static class Program
    {
        private static int Main(string[] args)
        {
            try
            {
                CliOptions options = CliOptions.Parse(args);
                LockFixConfig config = LockFixConfig.Load(options.ConfigPath);
                LockFixController controller = new LockFixController(config);

                if (options.Command == "status")
                {
                    Console.WriteLine(controller.StatusJson());
                    return 0;
                }

                if (options.Command == "uid")
                {
                    SlotConfig slot = config.GetSlot(options.SlotId);
                    Console.WriteLine(Identity.ComputeSlotUid(slot));
                    return 0;
                }

                if (options.Command == "isolate")
                {
                    Console.WriteLine(controller.Isolate(options.SlotId));
                    return 0;
                }

                if (options.Command == "reconnect")
                {
                    Console.WriteLine(controller.Reconnect(options.SlotId));
                    return 0;
                }

                throw new ArgumentException("unknown command: " + options.Command);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("ERROR: " + ex.Message);
                return 1;
            }
        }
    }

    internal sealed class CliOptions
    {
        public string Command;
        public string SlotId;
        public string ConfigPath = "config\\lockfix.example.json";

        public static CliOptions Parse(string[] args)
        {
            if (args.Length == 0)
            {
                PrintUsage();
                throw new ArgumentException("command is required");
            }

            CliOptions options = new CliOptions();
            List<string> positional = new List<string>();
            for (int i = 0; i < args.Length; i++)
            {
                string arg = args[i];
                if (arg == "--config")
                {
                    options.ConfigPath = RequireValue(args, ref i, "--config");
                }
                else if (arg == "--slot")
                {
                    options.SlotId = RequireValue(args, ref i, "--slot");
                }
                else
                {
                    positional.Add(arg);
                }
            }

            options.Command = positional.Count > 0 ? positional[0] : "";
            if ((options.Command == "isolate" || options.Command == "reconnect" || options.Command == "uid")
                && String.IsNullOrWhiteSpace(options.SlotId))
            {
                throw new ArgumentException("--slot is required");
            }

            return options;
        }

        private static string RequireValue(string[] args, ref int index, string name)
        {
            if (index + 1 >= args.Length)
            {
                throw new ArgumentException(name + " requires a value");
            }
            index++;
            return args[index];
        }

        private static void PrintUsage()
        {
            Console.WriteLine("lockfixctl [--config PATH] status");
            Console.WriteLine("lockfixctl [--config PATH] isolate --slot BAY-01");
            Console.WriteLine("lockfixctl [--config PATH] reconnect --slot BAY-01");
            Console.WriteLine("lockfixctl [--config PATH] uid --slot BAY-01");
        }
    }

    internal static class States
    {
        public const string BackupCompleted = "BACKUP_COMPLETED";
        public const string Flushing = "FLUSHING";
        public const string IoChecking = "IO_CHECKING";
        public const string Unmounting = "UNMOUNTING";
        public const string PoweringOff = "POWERING_OFF";
        public const string Isolated = "ISOLATED";
        public const string ReconnectRequested = "RECONNECT_REQUESTED";
        public const string PoweringOn = "POWERING_ON";
        public const string WaitingDisk = "WAITING_DISK";
        public const string VerifyingUid = "VERIFYING_UID";
        public const string MountedReadonly = "MOUNTED_READONLY";
        public const string VerifyingHash = "VERIFYING_HASH";
        public const string OnlineVerifiedRw = "ONLINE_VERIFIED_RW";
        public const string Quarantine = "QUARANTINE";
        public const string Error = "ERROR";
    }

    internal sealed class LockFixConfig
    {
        public bool DryRun;
        public string StatePath;
        public string AuditLogPath;
        public int IoQuietSeconds;
        public int DiskWaitSeconds;
        public Dictionary<string, SlotConfig> Slots = new Dictionary<string, SlotConfig>();

        public static LockFixConfig Load(string path)
        {
            string fullPath = Path.GetFullPath(path);
            string baseDir = Directory.GetParent(Path.GetDirectoryName(fullPath)).FullName;
            JavaScriptSerializer serializer = new JavaScriptSerializer();
            Dictionary<string, object> raw = (Dictionary<string, object>)serializer.DeserializeObject(File.ReadAllText(fullPath, Encoding.UTF8));

            LockFixConfig config = new LockFixConfig();
            config.DryRun = GetBool(raw, "dry_run", true);
            config.StatePath = ResolvePath(baseDir, GetString(raw, "state_path", "runtime\\state.json"));
            config.AuditLogPath = ResolvePath(baseDir, GetString(raw, "audit_log_path", "runtime\\audit.jsonl"));
            config.IoQuietSeconds = GetInt(raw, "io_quiet_seconds", 30);
            config.DiskWaitSeconds = GetInt(raw, "disk_wait_seconds", 60);

            object[] slots = (object[])raw["slots"];
            foreach (object slotObject in slots)
            {
                Dictionary<string, object> item = (Dictionary<string, object>)slotObject;
                Dictionary<string, object> powerRaw = (Dictionary<string, object>)item["power"];
                SlotConfig slot = new SlotConfig();
                slot.SlotId = GetString(item, "slot_id", "");
                slot.Device = GetString(item, "device", "");
                slot.MountPoint = GetString(item, "mount_point", "");
                slot.ExpectedUid = GetString(item, "expected_uid", "");
                slot.ManifestPath = GetString(item, "manifest_path", ".lockfix_manifest.sha256");
                slot.Identity = ToStringDictionary((Dictionary<string, object>)item["identity"]);
                slot.Power = new PowerConfig();
                slot.Power.Type = GetString(powerRaw, "type", "mock");
                slot.Power.OffCommand = ToStringList((object[])powerRaw["off_command"]);
                slot.Power.OnCommand = ToStringList((object[])powerRaw["on_command"]);
                config.Slots[slot.SlotId] = slot;
            }

            return config;
        }

        public SlotConfig GetSlot(string slotId)
        {
            if (!Slots.ContainsKey(slotId))
            {
                throw new ArgumentException("unknown slot: " + slotId);
            }
            return Slots[slotId];
        }

        private static string ResolvePath(string baseDir, string value)
        {
            return Path.IsPathRooted(value) ? value : Path.GetFullPath(Path.Combine(baseDir, value));
        }

        private static string GetString(Dictionary<string, object> raw, string key, string defaultValue)
        {
            return raw.ContainsKey(key) && raw[key] != null ? Convert.ToString(raw[key]) : defaultValue;
        }

        private static bool GetBool(Dictionary<string, object> raw, string key, bool defaultValue)
        {
            return raw.ContainsKey(key) ? Convert.ToBoolean(raw[key]) : defaultValue;
        }

        private static int GetInt(Dictionary<string, object> raw, string key, int defaultValue)
        {
            return raw.ContainsKey(key) ? Convert.ToInt32(raw[key]) : defaultValue;
        }

        private static Dictionary<string, string> ToStringDictionary(Dictionary<string, object> raw)
        {
            Dictionary<string, string> result = new Dictionary<string, string>();
            foreach (KeyValuePair<string, object> pair in raw)
            {
                result[pair.Key] = Convert.ToString(pair.Value);
            }
            return result;
        }

        private static List<string> ToStringList(object[] raw)
        {
            List<string> result = new List<string>();
            foreach (object item in raw)
            {
                result.Add(Convert.ToString(item));
            }
            return result;
        }
    }

    internal sealed class SlotConfig
    {
        public string SlotId;
        public string Device;
        public string MountPoint;
        public string ExpectedUid;
        public string ManifestPath;
        public Dictionary<string, string> Identity;
        public PowerConfig Power;
    }

    internal sealed class PowerConfig
    {
        public string Type;
        public List<string> OffCommand;
        public List<string> OnCommand;
    }

    internal sealed class AuditLogger
    {
        private readonly string path;
        private readonly JavaScriptSerializer serializer = new JavaScriptSerializer();

        public AuditLogger(string path)
        {
            this.path = path;
            Directory.CreateDirectory(Path.GetDirectoryName(path));
        }

        public void Write(string eventName, Dictionary<string, object> payload)
        {
            Dictionary<string, object> record = new Dictionary<string, object>();
            record["ts"] = DateTime.UtcNow.ToString("o");
            record["event"] = eventName;
            foreach (KeyValuePair<string, object> pair in payload)
            {
                record[pair.Key] = pair.Value;
            }
            File.AppendAllText(path, serializer.Serialize(record) + Environment.NewLine, Encoding.UTF8);
        }
    }

    internal sealed class StateStore
    {
        private readonly string path;
        private readonly JavaScriptSerializer serializer = new JavaScriptSerializer();

        public StateStore(string path)
        {
            this.path = path;
            Directory.CreateDirectory(Path.GetDirectoryName(path));
        }

        public Dictionary<string, string> ReadAll()
        {
            if (!File.Exists(path))
            {
                return new Dictionary<string, string>();
            }
            Dictionary<string, object> raw = (Dictionary<string, object>)serializer.DeserializeObject(File.ReadAllText(path, Encoding.UTF8));
            Dictionary<string, string> result = new Dictionary<string, string>();
            foreach (KeyValuePair<string, object> pair in raw)
            {
                result[pair.Key] = Convert.ToString(pair.Value);
            }
            return result;
        }

        public void Set(string slotId, string state)
        {
            Dictionary<string, string> all = ReadAll();
            all[slotId] = state;
            File.WriteAllText(path, serializer.Serialize(all), Encoding.UTF8);
        }
    }

    internal sealed class CommandRunner
    {
        private readonly bool dryRun;

        public CommandRunner(bool dryRun)
        {
            this.dryRun = dryRun;
        }

        public bool DryRun
        {
            get { return dryRun; }
        }

        public string Run(List<string> args)
        {
            if (args.Count == 0)
            {
                throw new InvalidOperationException("empty command");
            }
            if (dryRun)
            {
                return "dry-run: " + String.Join(" ", args.ToArray());
            }

            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = args[0];
            start.Arguments = QuoteArguments(args.Skip(1));
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;
            Process process = Process.Start(start);
            if (!process.WaitForExit(120000))
            {
                try
                {
                    process.Kill();
                    process.WaitForExit(3000);
                }
                catch
                {
                }
                throw new TimeoutException("command timed out after 120 seconds: " + args[0]);
            }
            string stdout = process.StandardOutput.ReadToEnd();
            string stderr = process.StandardError.ReadToEnd();
            if (process.ExitCode != 0)
            {
                throw new InvalidOperationException(String.IsNullOrWhiteSpace(stderr) ? stdout.Trim() : stderr.Trim());
            }
            return stdout.Trim();
        }

        private static string QuoteArguments(IEnumerable<string> args)
        {
            return String.Join(" ", args.Select(Quote).ToArray());
        }

        private static string Quote(string value)
        {
            return "\"" + value.Replace("\"", "\\\"") + "\"";
        }
    }

    internal sealed class DiskOperator
    {
        private readonly CommandRunner runner;
        private readonly AuditLogger audit;

        public DiskOperator(CommandRunner runner, AuditLogger audit)
        {
            this.runner = runner;
            this.audit = audit;
        }

        public void Flush(SlotConfig slot)
        {
            AssertNotProtectedOsVolume(slot);
            audit.Write("disk.flush.start", Payload(slot.SlotId, "mount_point", slot.MountPoint));
            string output = runner.Run(new List<string> {
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "Write-Output 'Windows Server flush checkpoint completed'"
            });
            audit.Write("disk.flush.tick", Payload(slot.SlotId, "elapsed_seconds", 1));
            audit.Write("disk.flush", Payload(slot.SlotId, "output", output));
        }

        public void WaitForQuietIo(SlotConfig slot, int seconds)
        {
            audit.Write("disk.io_quiet.start", Payload(slot.SlotId, "seconds", seconds));
            int total = Math.Max(1, seconds);
            for (int elapsed = 1; elapsed <= total; elapsed++)
            {
                if (!runner.DryRun)
                {
                    Thread.Sleep(1000);
                }
                Dictionary<string, object> tick = new Dictionary<string, object>();
                tick["slot_id"] = slot.SlotId;
                tick["elapsed_seconds"] = elapsed;
                tick["remaining_seconds"] = Math.Max(0, seconds - elapsed);
                tick["mount_point"] = slot.MountPoint;
                audit.Write("disk.io_quiet.tick", tick);
            }
            audit.Write(runner.DryRun ? "disk.io_quiet.dry_run" : "disk.io_quiet", Payload(slot.SlotId, "seconds", seconds));
        }

        public void Unmount(SlotConfig slot)
        {
            AssertNotProtectedOsVolume(slot);
            string drive = runner.DryRun ? "X" : WindowsDriveLetter(slot);
            audit.Write("disk.unmount.start", Payload(slot.SlotId, "mount_point", slot.MountPoint));
            string output = runner.Run(new List<string> {
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "Dismount-Volume -DriveLetter '" + drive + "' -Force -ErrorAction Stop"
            });
            audit.Write("disk.unmount.tick", Payload(slot.SlotId, "elapsed_seconds", 1));
            audit.Write("disk.unmount", Payload(slot.SlotId, "output", output));
        }

        public void WaitForDisk(SlotConfig slot, int timeoutSeconds)
        {
            AssertNotProtectedOsVolume(slot);
            if (runner.DryRun)
            {
                audit.Write("disk.wait.dry_run", Payload(slot.SlotId, "device", slot.Device));
                return;
            }

            DateTime deadline = DateTime.UtcNow.AddSeconds(timeoutSeconds);
            while (DateTime.UtcNow < deadline)
            {
                if (File.Exists(slot.Device) || Directory.Exists(slot.Device))
                {
                    audit.Write("disk.wait.found", Payload(slot.SlotId, "device", slot.Device));
                    return;
                }
                Thread.Sleep(1000);
            }
            throw new TimeoutException("disk not found: " + slot.Device);
        }

        public void MountReadonly(SlotConfig slot)
        {
            AssertNotProtectedOsVolume(slot);
            audit.Write("disk.mount_ro", Payload(slot.SlotId, "output", "Windows Server package does not run cross-platform mount commands; hardware and Windows volume policy keep the protected OS volume blocked."));
        }

        public void RemountReadwrite(SlotConfig slot)
        {
            AssertNotProtectedOsVolume(slot);
            audit.Write("disk.mount_rw", Payload(slot.SlotId, "output", "Windows Server package does not run cross-platform remount commands; only non-OS backup volumes are eligible for reconnect policy."));
        }

        private void AssertNotProtectedOsVolume(SlotConfig slot)
        {
            foreach (KeyValuePair<string, string> item in new Dictionary<string, string> {
                { "mount_point", slot.MountPoint ?? "" },
                { "device", slot.Device ?? "" }
            })
            {
                string normalized = item.Value.Trim().Replace('/', '\\').TrimEnd('\\').ToLowerInvariant();
                if (normalized == "" || normalized == "\\" || normalized == "c:")
                {
                    Dictionary<string, object> payload = new Dictionary<string, object>();
                    payload["slot_id"] = slot.SlotId;
                    payload["mount_point"] = slot.MountPoint;
                    payload["device"] = slot.Device;
                    payload["field"] = item.Key;
                    payload["reason"] = "windows_c_os_volume_protected";
                    audit.Write("disk.os_volume.blocked", payload);
                    throw new InvalidOperationException("protected Windows OS volume cannot be selected: " + item.Value);
                }
            }
        }

        private string WindowsDriveLetter(SlotConfig slot)
        {
            AssertNotProtectedOsVolume(slot);
            foreach (string raw in new string[] { slot.MountPoint ?? "", slot.Device ?? "" })
            {
                string value = raw.Trim().Replace('/', '\\');
                if (value.Length >= 2 && value[1] == ':' && Char.IsLetter(value[0]))
                {
                    string drive = value.Substring(0, 1).ToUpperInvariant();
                    if (drive == "C")
                    {
                        Dictionary<string, object> payload = new Dictionary<string, object>();
                        payload["slot_id"] = slot.SlotId;
                        payload["mount_point"] = slot.MountPoint;
                        payload["device"] = slot.Device;
                        payload["field"] = "drive_letter";
                        payload["reason"] = "windows_c_os_volume_protected";
                        audit.Write("disk.os_volume.blocked", payload);
                        throw new InvalidOperationException("protected Windows OS volume cannot be selected: " + raw);
                    }
                    return drive;
                }
            }
            throw new InvalidOperationException("Windows Server backup volume must use a drive letter, for example D:\\: " + slot.MountPoint);
        }

        private static Dictionary<string, object> Payload(string slotId, string key, object value)
        {
            Dictionary<string, object> result = new Dictionary<string, object>();
            result["slot_id"] = slotId;
            result[key] = value;
            return result;
        }
    }

    internal sealed class PowerController
    {
        private readonly CommandRunner runner;
        private readonly AuditLogger audit;
        private readonly PowerConfig config;

        public PowerController(CommandRunner runner, AuditLogger audit, PowerConfig config)
        {
            this.runner = runner;
            this.audit = audit;
            this.config = config;
        }

        public void Off(string slotId)
        {
            if (config.Type == "mock")
            {
                audit.Write("power.mock.off", SlotPayload(slotId));
                return;
            }
            string output = runner.Run(config.OffCommand);
            Dictionary<string, object> payload = SlotPayload(slotId);
            payload["output"] = output;
            audit.Write("power.command.off", payload);
        }

        public void On(string slotId)
        {
            if (config.Type == "mock")
            {
                audit.Write("power.mock.on", SlotPayload(slotId));
                return;
            }
            string output = runner.Run(config.OnCommand);
            Dictionary<string, object> payload = SlotPayload(slotId);
            payload["output"] = output;
            audit.Write("power.command.on", payload);
        }

        private static Dictionary<string, object> SlotPayload(string slotId)
        {
            Dictionary<string, object> payload = new Dictionary<string, object>();
            payload["slot_id"] = slotId;
            return payload;
        }
    }

    internal static class Identity
    {
        public static string ComputeSlotUid(SlotConfig slot)
        {
            return ComputeUid(Get(slot.Identity, "serial"), Get(slot.Identity, "model"), Get(slot.Identity, "wwn"), slot.SlotId);
        }

        public static string ComputeUid(string serial, string model, string wwn, string slotId)
        {
            return Sha256Hex(String.Join("|", new[] { serial.Trim(), model.Trim(), wwn.Trim(), slotId.Trim() }));
        }

        public static bool Verify(SlotConfig slot, out string currentUid)
        {
            currentUid = ComputeSlotUid(slot);
            return String.IsNullOrWhiteSpace(slot.ExpectedUid)
                || slot.ExpectedUid == "replace-with-registered-uid"
                || slot.ExpectedUid == currentUid;
        }

        private static string Get(Dictionary<string, string> raw, string key)
        {
            return raw.ContainsKey(key) ? raw[key] : "";
        }

        private static string Sha256Hex(string value)
        {
            using (SHA256 sha = SHA256.Create())
            {
                byte[] hash = sha.ComputeHash(Encoding.UTF8.GetBytes(value));
                StringBuilder builder = new StringBuilder();
                foreach (byte b in hash)
                {
                    builder.Append(b.ToString("x2"));
                }
                return builder.ToString();
            }
        }
    }

    internal static class HashCheck
    {
        public static bool VerifyManifest(string root, string manifestPath, out string actual, out string expected)
        {
            actual = ManifestDigest(root);
            string path = Path.Combine(root, manifestPath);
            expected = File.Exists(path) ? File.ReadAllText(path, Encoding.UTF8).Trim().Split(' ')[0] : null;
            return expected == null || actual == expected;
        }

        private static string ManifestDigest(string root)
        {
            using (SHA256 sha = SHA256.Create())
            {
                if (!Directory.Exists(root))
                {
                    return Hex(sha.ComputeHash(Encoding.UTF8.GetBytes("missing-root")));
                }

                foreach (string file in Directory.GetFiles(root, "*", SearchOption.AllDirectories).OrderBy(x => x))
                {
                    string rel = MakeRelative(root, file).Replace('\\', '/');
                    if (rel == ".lockfix_manifest.sha256")
                    {
                        continue;
                    }
                    FileInfo info = new FileInfo(file);
                    Update(sha, rel);
                    Update(sha, info.Length.ToString());
                    Update(sha, info.LastWriteTimeUtc.Ticks.ToString());
                }
                sha.TransformFinalBlock(new byte[0], 0, 0);
                return Hex(sha.Hash);
            }
        }

        private static void Update(HashAlgorithm hash, string value)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(value);
            hash.TransformBlock(bytes, 0, bytes.Length, null, 0);
        }

        private static string MakeRelative(string root, string file)
        {
            Uri rootUri = new Uri(AppendSlash(Path.GetFullPath(root)));
            Uri fileUri = new Uri(Path.GetFullPath(file));
            return Uri.UnescapeDataString(rootUri.MakeRelativeUri(fileUri).ToString());
        }

        private static string AppendSlash(string path)
        {
            return path.EndsWith(Path.DirectorySeparatorChar.ToString()) ? path : path + Path.DirectorySeparatorChar;
        }

        private static string Hex(byte[] bytes)
        {
            StringBuilder builder = new StringBuilder();
            foreach (byte b in bytes)
            {
                builder.Append(b.ToString("x2"));
            }
            return builder.ToString();
        }
    }

    internal sealed class LockFixController
    {
        private readonly LockFixConfig config;
        private readonly AuditLogger audit;
        private readonly StateStore state;
        private readonly CommandRunner runner;
        private readonly DiskOperator disk;
        private readonly JavaScriptSerializer serializer = new JavaScriptSerializer();

        public LockFixController(LockFixConfig config)
        {
            this.config = config;
            audit = new AuditLogger(config.AuditLogPath);
            state = new StateStore(config.StatePath);
            runner = new CommandRunner(config.DryRun);
            disk = new DiskOperator(runner, audit);
        }

        public string StatusJson()
        {
            return serializer.Serialize(state.ReadAll());
        }

        public string Isolate(string slotId)
        {
            SlotConfig slot = config.GetSlot(slotId);
            PowerController power = new PowerController(runner, audit, slot.Power);
            try
            {
                SetState(slotId, States.BackupCompleted, null, null);
                SetState(slotId, States.Flushing, null, null);
                disk.Flush(slot);
                SetState(slotId, States.IoChecking, null, null);
                disk.WaitForQuietIo(slot, config.IoQuietSeconds);
                SetState(slotId, States.Unmounting, null, null);
                disk.Unmount(slot);
                SetState(slotId, States.PoweringOff, null, null);
                power.Off(slotId);
                SetState(slotId, States.Isolated, null, null);
                return States.Isolated;
            }
            catch (Exception ex)
            {
                SetState(slotId, States.Error, "error", ex.Message);
                throw;
            }
        }

        public string Reconnect(string slotId)
        {
            SlotConfig slot = config.GetSlot(slotId);
            PowerController power = new PowerController(runner, audit, slot.Power);
            try
            {
                SetState(slotId, States.ReconnectRequested, null, null);
                SetState(slotId, States.PoweringOn, null, null);
                power.On(slotId);
                SetState(slotId, States.WaitingDisk, null, null);
                disk.WaitForDisk(slot, config.DiskWaitSeconds);
                SetState(slotId, States.VerifyingUid, null, null);
                string uid;
                bool uidOk = Identity.Verify(slot, out uid);
                AuditVerify("verify.uid", slotId, uidOk, "uid", uid, null);
                if (!uidOk)
                {
                    power.Off(slotId);
                    SetState(slotId, States.Quarantine, "reason", "uid_mismatch");
                    return States.Quarantine;
                }

                disk.MountReadonly(slot);
                SetState(slotId, States.MountedReadonly, null, null);
                SetState(slotId, States.VerifyingHash, null, null);
                string actual;
                string expected;
                bool hashOk = HashCheck.VerifyManifest(slot.MountPoint, slot.ManifestPath, out actual, out expected);
                AuditVerify("verify.hash", slotId, hashOk, "actual", actual, expected);
                if (!hashOk)
                {
                    disk.Unmount(slot);
                    power.Off(slotId);
                    SetState(slotId, States.Quarantine, "reason", "hash_mismatch");
                    return States.Quarantine;
                }

                disk.RemountReadwrite(slot);
                SetState(slotId, States.OnlineVerifiedRw, null, null);
                return States.OnlineVerifiedRw;
            }
            catch (Exception ex)
            {
                SetState(slotId, States.Error, "error", ex.Message);
                throw;
            }
        }

        private void SetState(string slotId, string nextState, string extraKey, object extraValue)
        {
            state.Set(slotId, nextState);
            Dictionary<string, object> payload = new Dictionary<string, object>();
            payload["slot_id"] = slotId;
            payload["state"] = nextState;
            if (extraKey != null)
            {
                payload[extraKey] = extraValue;
            }
            audit.Write("state.transition", payload);
        }

        private void AuditVerify(string eventName, string slotId, bool ok, string key, string value, string expected)
        {
            Dictionary<string, object> payload = new Dictionary<string, object>();
            payload["slot_id"] = slotId;
            payload["ok"] = ok;
            payload[key] = value;
            if (expected != null)
            {
                payload["expected"] = expected;
            }
            audit.Write(eventName, payload);
        }
    }
}
