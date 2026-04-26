const slotList = document.querySelector("#slotList");
const loginScreen = document.querySelector("#loginScreen");
const loginForm = document.querySelector("#loginForm");
const loginEmail = document.querySelector("#loginEmail");
const loginPassword = document.querySelector("#loginPassword");
const loginError = document.querySelector("#loginError");
const passwordLogin = document.querySelector("#passwordLogin");
const qrLoginView = document.querySelector("#qrLoginView");
const qrLoginButton = document.querySelector("#qrLoginButton");
const qrCodeBox = document.querySelector("#qrCodeBox");
const qrTimer = document.querySelector("#qrTimer");
const appRoot = document.querySelector("#appRoot");
const logoutButton = document.querySelector("#logoutButton");
const logoutSideButton = document.querySelector("#logoutSideButton");
const sideItems = document.querySelectorAll(".side-item[data-view]");
const views = document.querySelectorAll(".view");
const monitoringChart = document.querySelector("#monitoringChart");
const monitoringTitle = document.querySelector("#monitoringTitle");
const monitoringStart = document.querySelector("#monitoringStart");
const monitoringEnd = document.querySelector("#monitoringEnd");
const chartMenuButton = document.querySelector("#chartMenuButton");
const chartZoomInButton = document.querySelector("#chartZoomInButton");
const chartZoomOutButton = document.querySelector("#chartZoomOutButton");
const downloadMenu = document.querySelector("#downloadMenu");
const metricFilterButtons = document.querySelectorAll(".metric-filter-button");
const cpuGauge = document.querySelector("#cpuGauge");
const memoryGauge = document.querySelector("#memoryGauge");
const diskGauge = document.querySelector("#diskGauge");
const networkGauge = document.querySelector("#networkGauge");
const sourceRoot = document.querySelector("#sourceRoot");
const sourceList = document.querySelector("#sourceList");
const dashboardCards = document.querySelector("#dashboardCards");
const dashboardNotificationTable = document.querySelector("#dashboardNotificationTable");
const dashboardLogsTable = document.querySelector("#dashboardLogsTable");
const dashboardTotalLogs = document.querySelector("#dashboardTotalLogs");
const reportOverallStatus = document.querySelector("#reportOverallStatus");
const reportAnalysis = document.querySelector("#reportAnalysis");
const reportGeneratedAt = document.querySelector("#reportGeneratedAt");
const reportRange = document.querySelector("#reportRange");
const reportCards = document.querySelector("#reportCards");
const reportTable = document.querySelector("#reportTable");
const reportCustomerTable = document.querySelector("#reportCustomerTable");
const reportServerTable = document.querySelector("#reportServerTable");
const reportInspectionTable = document.querySelector("#reportInspectionTable");
const notificationTable = document.querySelector("#notificationTable");
const detectStart = document.querySelector("#detectStart");
const detectEnd = document.querySelector("#detectEnd");
const detectCards = document.querySelector("#detectCards");
const detectDetectTable = document.querySelector("#detectDetectTable");
const detectWarningTable = document.querySelector("#detectWarningTable");
const detectLogsTable = document.querySelector("#detectLogsTable");
const logsStart = document.querySelector("#logsStart");
const logsEnd = document.querySelector("#logsEnd");
const logsTotal = document.querySelector("#logsTotal");
const logsHistoryTable = document.querySelector("#logsHistoryTable");
const licenseStatusTable = document.querySelector("#licenseStatusTable");
const licenseModal = document.querySelector("#licenseModal");
const licenseForm = document.querySelector("#licenseForm");
const licenseModalReason = document.querySelector("#licenseModalReason");
const licenseIp = document.querySelector("#licenseIp");
const licenseMac = document.querySelector("#licenseMac");
const licenseSampleKey = document.querySelector("#licenseSampleKey");
const licenseCustomer = document.querySelector("#licenseCustomer");
const licenseSupportCode = document.querySelector("#licenseSupportCode");
const licenseKeyInput = document.querySelector("#licenseKeyInput");
const licenseError = document.querySelector("#licenseError");
const networkStatusTitle = document.querySelector("#networkStatusTitle");
const networkStatusChart = document.querySelector("#networkStatusChart");
const networkTxRate = document.querySelector("#networkTxRate");
const networkRxRate = document.querySelector("#networkRxRate");
const networkTxTotal = document.querySelector("#networkTxTotal");
const networkRxTotal = document.querySelector("#networkRxTotal");
const networkTxFlow = document.querySelector("#networkTxFlow");
const networkRxFlow = document.querySelector("#networkRxFlow");
const auditTable = document.querySelector("#auditTable");
const slotTemplate = document.querySelector("#slotTemplate");
const refreshButton = document.querySelector("#refreshButton");
const modeBadge = document.querySelector("#modeBadge");
const configPath = document.querySelector("#configPath");
const auditPath = document.querySelector("#auditPath");
const lastUpdated = document.querySelector("#lastUpdated");
const integratedTitle = document.querySelector("#integratedTitle");
const integratedSubtitle = document.querySelector("#integratedSubtitle");
const integratedUpdated = document.querySelector("#integratedUpdated");
const systemStrip = document.querySelector("#systemStrip");
const metricStrip = document.querySelector("#metricStrip");
const moduleList = document.querySelector("#moduleList");
const detectList = document.querySelector("#detectList");
const noticeList = document.querySelector("#noticeList");
const networkList = document.querySelector("#networkList");
const licenseBox = document.querySelector("#licenseBox");
const systemTemplate = document.querySelector("#systemTemplate");
const languageSelect = document.querySelector("#languageSelect");
const themeSelect = document.querySelector("#themeSelect");
const settingsApplyButton = document.querySelector("#settingsApplyButton");
const settingsApplyStatus = document.querySelector("#settingsApplyStatus");
let qrToken = "";
let qrExpiresAt = 0;
let qrPollTimer = null;
let qrClockTimer = null;
let monitoringZoom = 1;
let latestMonitoringSeries = [];
let latestMonitoringData = null;
let activeMonitoringMetric = "cpu";
let uiSettings = {
  language: localStorage.getItem("lockfix.language") || "en",
  theme: localStorage.getItem("lockfix.theme") || "light",
};
let pendingUiSettings = { ...uiSettings };

const translations = {
  en: {
    "nav.monitoring": "Monitoring",
    "nav.report": "Report",
    "nav.dashboard": "Dashboard",
    "nav.detect": "Detect",
    "nav.notification": "Notification",
    "nav.logs": "Logs",
    "nav.contact": "Contact Service",
    "nav.license": "License",
    "nav.network": "Network Status",
    "nav.download": "Logs - Download",
    "nav.airgap": "Air-Gap",
    "nav.settings": "Settings",
    "nav.logout": "Logout",
    "settings.title": "Settings",
    "settings.subtitle": "Configure display language and screen theme.",
    "settings.languageTitle": "Language",
    "settings.languageDesc": "Choose the UI language for menus and labels.",
    "settings.themeTitle": "Theme",
    "settings.themeDesc": "Switch between white and black backgrounds.",
    "settings.themeLight": "White",
    "settings.themeDark": "Black",
    "settings.apply": "Apply",
    "settings.pending": "Select options, then click Apply.",
    "settings.applied": "Settings have been applied.",
    "monitoring.title": "Monitoring",
    "monitoring.subtitle": "Hardware usage status is updated every 5 seconds.",
    "report.title": "Report",
    "report.subtitle": "Analyzed report for current CPU, memory, disk, and network resource usage.",
    "airgap.title": "Air-Gap",
    "airgap.subtitle": "Monitor physical power cut-off, solenoid lock, and integrity verification status in real time.",
  },
  ko: {
    "nav.monitoring": "모니터링",
    "nav.report": "보고서",
    "nav.dashboard": "대시보드",
    "nav.detect": "탐지 내역",
    "nav.notification": "알림",
    "nav.logs": "로그",
    "nav.contact": "고객 센터",
    "nav.license": "라이선스",
    "nav.network": "네트워크 상태",
    "nav.download": "로그 다운로드",
    "nav.airgap": "에어갭",
    "nav.settings": "설정",
    "nav.logout": "로그아웃",
    "settings.title": "설정",
    "settings.subtitle": "표시 언어와 화면 테마를 설정합니다.",
    "settings.languageTitle": "언어",
    "settings.languageDesc": "메뉴와 주요 라벨에 사용할 언어를 선택합니다.",
    "settings.themeTitle": "테마",
    "settings.themeDesc": "흰색 배경 또는 검은색 배경으로 전환합니다.",
    "settings.themeLight": "흰색",
    "settings.themeDark": "검은색",
    "settings.apply": "적용",
    "settings.pending": "항목을 선택한 뒤 적용 버튼을 누르세요.",
    "settings.applied": "설정이 적용되었습니다.",
    "monitoring.title": "모니터링",
    "monitoring.subtitle": "하드웨어 사용 상태가 5초마다 업데이트됩니다.",
    "report.title": "보고서",
    "report.subtitle": "현재 CPU, 메모리, 디스크, 네트워크 자원 사용량 분석 보고서입니다.",
    "airgap.title": "에어갭",
    "airgap.subtitle": "물리적 전원 차단, 솔레노이드 잠금, 무결성 검증 상태를 실시간으로 확인합니다.",
  },
};

function t(key) {
  return translations[uiSettings.language]?.[key] || translations.en[key] || key;
}

function applyUiSettings() {
  document.documentElement.dataset.theme = uiSettings.theme;
  document.documentElement.lang = uiSettings.language === "ko" ? "ko" : "en";
  pendingUiSettings = { ...uiSettings };
  if (languageSelect) languageSelect.value = pendingUiSettings.language;
  if (themeSelect) themeSelect.value = pendingUiSettings.theme;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    node.textContent = t(key);
  });
}

function applyPendingUiSettings() {
  uiSettings = { ...pendingUiSettings };
  localStorage.setItem("lockfix.language", uiSettings.language);
  localStorage.setItem("lockfix.theme", uiSettings.theme);
  applyUiSettings();
  settingsApplyStatus.textContent = t("settings.applied");
  if (latestMonitoringData) {
    renderMonitoring(latestMonitoringData);
  }
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "request failed");
  }
  return payload;
}

async function checkSession() {
  const session = await requestJson("/api/session");
  setAuthenticated(session.authenticated);
  if (session.authenticated) {
    renderLicenseStatus(session.license);
    updateLicenseGate(session.license);
    await loadAll();
  }
}

function setAuthenticated(authenticated) {
  loginScreen.classList.toggle("login-hidden", authenticated);
  appRoot.classList.toggle("app-locked", !authenticated);
  if (!authenticated) {
    licenseModal.classList.add("hidden");
  }
  if (authenticated) {
    stopQrTimers();
  }
  if (!authenticated) {
    loginPassword.focus();
  }
}

async function login(event) {
  event.preventDefault();
  loginError.textContent = "";
  try {
    const payload = await requestJson("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: loginEmail.value.trim(),
        password: loginPassword.value,
      }),
    });
    setAuthenticated(payload.authenticated);
    await loadAll();
  } catch (error) {
    loginError.textContent = "Account or password is not valid.";
  }
}

async function logout() {
  await requestJson("/api/logout", { method: "POST" });
  setAuthenticated(false);
}

function showView(name) {
  if (name === "logout") {
    logout();
    return;
  }
  sideItems.forEach((item) => item.classList.toggle("active", item.dataset.view === name));
  views.forEach((view) => view.classList.remove("view-active"));
  const target = document.querySelector(`#${name}View`);
  if (target) {
    target.classList.add("view-active");
  }
}

async function startQrLogin() {
  loginError.textContent = "";
  try {
    const payload = await requestJson("/api/qr-login", { method: "POST" });
    qrToken = payload.token;
    qrExpiresAt = Date.now() + payload.expires_in * 1000;
    passwordLogin.classList.add("qr-hidden");
    qrLoginView.classList.remove("qr-hidden");
    qrLoginButton.textContent = "QR CODE LOGIN";
    renderQrPattern(payload.payload);
    updateQrTimer();
    stopQrTimers();
    qrClockTimer = setInterval(updateQrTimer, 1000);
    qrPollTimer = setInterval(checkQrLogin, 1500);
  } catch (error) {
    loginError.textContent = "QR login is not available.";
  }
}

async function confirmQrLogin() {
  if (!qrToken) {
    return;
  }
  const payload = await requestJson("/api/qr-login/confirm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: qrToken }),
  });
  if (payload.approved) {
    setAuthenticated(true);
    await loadAll();
  }
}

async function checkQrLogin() {
  if (!qrToken) {
    return;
  }
  let payload;
  try {
    payload = await requestJson(`/api/qr-login/status?token=${encodeURIComponent(qrToken)}`);
  } catch (error) {
    stopQrTimers();
    loginError.textContent = "QR login check failed.";
    return;
  }
  if (payload.expired) {
    stopQrTimers();
    qrTimer.textContent = "00:00";
    loginError.textContent = "QR login expired.";
  }
  if (payload.approved) {
    setAuthenticated(true);
    await loadAll();
  }
}

function stopQrTimers() {
  clearInterval(qrPollTimer);
  clearInterval(qrClockTimer);
  qrPollTimer = null;
  qrClockTimer = null;
}

function updateQrTimer() {
  const remaining = Math.max(0, Math.ceil((qrExpiresAt - Date.now()) / 1000));
  const minutes = String(Math.floor(remaining / 60)).padStart(2, "0");
  const seconds = String(remaining % 60).padStart(2, "0");
  qrTimer.textContent = `${minutes}:${seconds}`;
}

function renderQrPattern(seed) {
  qrCodeBox.replaceChildren();
  const size = 29;
  let hash = 2166136261;
  for (const char of seed) {
    hash ^= char.charCodeAt(0);
    hash = Math.imul(hash, 16777619);
  }

  for (let row = 0; row < size; row += 1) {
    for (let col = 0; col < size; col += 1) {
      const cell = document.createElement("span");
      const finder =
        isFinder(row, col, 0, 0) ||
        isFinder(row, col, 0, size - 7) ||
        isFinder(row, col, size - 7, 0);
      if (finder || pseudoBit(hash, row, col)) {
        cell.className = "qr-on";
      }
      qrCodeBox.appendChild(cell);
    }
  }
}

function isFinder(row, col, top, left) {
  const y = row - top;
  const x = col - left;
  if (y < 0 || y > 6 || x < 0 || x > 6) {
    return false;
  }
  return y === 0 || y === 6 || x === 0 || x === 6 || (y >= 2 && y <= 4 && x >= 2 && x <= 4);
}

function pseudoBit(hash, row, col) {
  const mixed = Math.imul(hash ^ (row * 374761393) ^ (col * 668265263), 2246822519);
  return ((mixed >>> ((row + col) % 16)) & 1) === 1;
}

function stateClass(state) {
  return `state-${state}`.replaceAll(" ", "_");
}

function renderMount(node, slot) {
  const mount = slot.mount || {};
  const usage = mount.usage;
  const status = node.querySelector(".mount-status");
  const percent = node.querySelector(".usage-percent");
  const fill = node.querySelector(".usage-fill");
  const used = node.querySelector(".usage-used");
  const free = node.querySelector(".usage-free");
  const total = node.querySelector(".usage-total");
  const note = node.querySelector(".usage-note");

  if (!mount.exists) {
    status.textContent = "留덉슫??寃쎈줈 ?놁쓬";
    status.className = "mount-status mount-bad";
    percent.textContent = "-";
    fill.style.width = "0%";
    used.textContent = "Used -";
    free.textContent = "Free -";
    total.textContent = "Total -";
    note.textContent = `${slot.mount_point} 경로가 아직 생성되지 않았습니다.`;
    return;
  }

  if (!usage) {
    status.textContent = "사용량 확인 불가";
    status.className = "mount-status mount-warn";
    percent.textContent = "-";
    fill.style.width = "0%";
    used.textContent = "Used -";
    free.textContent = "Free -";
    total.textContent = "Total -";
    note.textContent = mount.error || "디스크 사용량을 읽을 수 없습니다.";
    return;
  }

  status.textContent = mount.mounted ? "마운트됨" : "경로 존재 / 마운트 미확인";
  status.className = `mount-status ${mount.mounted ? "mount-good" : "mount-warn"}`;
  percent.textContent = `${usage.percent}%`;
  fill.style.width = `${Math.max(0, Math.min(usage.percent, 100))}%`;
  fill.className = `usage-fill ${usage.percent >= 90 ? "usage-danger" : usage.percent >= 75 ? "usage-warn" : ""}`;
  used.textContent = `Used ${usage.used_label}`;
  free.textContent = `Free ${usage.free_label}`;
  total.textContent = `Total ${usage.total_label}`;
  note.textContent = mount.mounted
    ? "OS가 마운트 포인트로 인식 중입니다."
    : "경로는 존재하지만 별도 마운트 포인트로는 확인되지 않았습니다.";
}

function renderSlots(summary) {
  modeBadge.textContent = summary.dry_run ? "DRY-RUN MOCK" : "LIVE CONTROL";
  configPath.textContent = summary.config_path;
  auditPath.textContent = summary.audit_log_path;
  slotList.replaceChildren();

  summary.slots.forEach((slot) => {
    const node = slotTemplate.content.cloneNode(true);
    node.querySelector(".slot-title").textContent = slot.slot_id;
    node.querySelector(".slot-device").textContent = slot.device;
    node.querySelector(".slot-power").textContent = `${slot.power_type} / ${slot.dry_run ? "dry-run" : "live"}`;
    node.querySelector(".slot-mount").textContent = slot.mount_point;
    node.querySelector(".slot-uid").textContent = slot.uid;
    renderMount(node, slot);

    const pill = node.querySelector(".state-pill");
    pill.textContent = slot.state;
    pill.classList.add(stateClass(slot.state));

    node.querySelector(".isolate-button").addEventListener("click", () => runAction("isolate", slot.slot_id));
    node.querySelector(".reconnect-button").addEventListener("click", () => runAction("reconnect", slot.slot_id));
    slotList.appendChild(node);
  });
}

function renderIntegrated(data) {
  integratedTitle.textContent = data.title;
  integratedSubtitle.textContent = data.subtitle;
  integratedUpdated.textContent = new Date().toLocaleString();

  systemStrip.replaceChildren();
  data.systems.forEach((system) => {
    const node = systemTemplate.content.cloneNode(true);
    node.querySelector(".system-name").textContent = system.name;
    node.querySelector(".system-role").textContent = system.role;
    node.querySelector(".system-status").textContent = system.status;
    node.querySelector(".system-status").classList.add(system.status === "NORMAL" ? "good-text" : "warn-text");
    node.querySelector(".system-endpoint").textContent = system.endpoint;
    const features = node.querySelector(".system-features");
    system.features.forEach((feature) => {
      const chip = document.createElement("span");
      chip.textContent = feature;
      features.appendChild(chip);
    });
    systemStrip.appendChild(node);
  });

  metricStrip.replaceChildren();
  data.metrics.forEach((metric) => {
    const item = document.createElement("div");
    item.className = `metric-card metric-${metric.level}`;
    item.innerHTML = `<span>${metric.name}</span><strong>${metric.value}</strong><em>${metric.unit}</em>`;
    metricStrip.appendChild(item);
  });

  moduleList.replaceChildren();
  data.modules.forEach((module) => {
    const item = document.createElement("div");
    item.className = "module-item";
    item.innerHTML = `<strong>${module.name}</strong><span>${module.state}</span><p>${module.description}</p>`;
    moduleList.appendChild(item);
  });

  detectList.replaceChildren();
  data.detections.forEach((event) => {
    const item = document.createElement("div");
    item.className = "event-item";
    item.innerHTML = `<strong>${event.event}</strong><span>${event.time} / ${event.source}</span><em>${event.severity}</em>`;
    detectList.appendChild(item);
  });

  noticeList.replaceChildren();
  data.notifications.forEach((notice) => {
    const item = document.createElement("div");
    item.className = "notice-item";
    item.innerHTML = `<strong>${notice.level}</strong><span>${notice.message}</span>`;
    noticeList.appendChild(item);
  });

  networkList.replaceChildren();
  data.network.forEach((network) => {
    const item = document.createElement("div");
    item.className = "network-item";
    item.innerHTML = `<strong>${network.target}</strong><span>${network.address}</span><em>${network.status}</em>`;
    networkList.appendChild(item);
  });

  licenseBox.innerHTML = `
    <strong>${data.license.product}</strong>
    <span>${data.license.license_key}</span>
    <p>${data.license.issued_at} - ${data.license.expires_at}</p>
    <em>${data.license.status}</em>
  `;
}

function renderDashboard(data) {
  const cardClasses = {
    detect: "dashboard-card-detect",
    warning: "dashboard-card-warning",
    logs: "dashboard-card-logs",
  };

  dashboardCards.replaceChildren();
  data.cards.forEach((card) => {
    const item = document.createElement("article");
    item.className = `dashboard-card ${cardClasses[card.id] || ""}`;
    item.innerHTML = `
      <div>
        <strong>${card.label}</strong>
        <span>${card.description}</span>
      </div>
      <b>${card.value}</b>
    `;
    dashboardCards.appendChild(item);
  });

  dashboardNotificationTable.replaceChildren();
  data.notifications.forEach((notice) => {
    const row = document.createElement("tr");
    const networkClass = notice.network_connection === "GOOD" ? "status-good" : "status-bad";
    row.innerHTML = `
      <td><a href="mailto:${notice.email}">${notice.email}</a></td>
      <td><span class="status-good">${notice.smtp_status}</span></td>
      <td><span class="${networkClass}">${notice.network_connection}</span></td>
      <td><span class="status-good">${notice.last_login}</span></td>
    `;
    dashboardNotificationTable.appendChild(row);
  });

  dashboardTotalLogs.textContent = `Total: ${data.total_logs} logs`;
  dashboardLogsTable.replaceChildren();
  data.logs.forEach((log) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><span class="log-type log-${log.type.toLowerCase()}">${log.type}</span></td>
      <td>${log.date.replace(" ", "<br>")}</td>
      <td>${log.content}</td>
    `;
    dashboardLogsTable.appendChild(row);
  });
}

function renderReport(data) {
  reportOverallStatus.textContent = data.summary.overall_status;
  reportAnalysis.textContent = data.summary.analysis;
  reportGeneratedAt.textContent = `Generated: ${data.generated_at}`;
  reportRange.textContent = `${data.range.start} - ${data.range.end}`;
  const customerRows = [
    ["Customer Name", data.customer.customer_name, "Inspection Date", data.customer.inspection_date],
    ["Customer Contact", data.customer.customer_contact, "Engineer", data.customer.engineer],
    ["Customer Email", data.customer.customer_email, "Engineer Contact", data.customer.engineer_contact],
  ];
  reportCustomerTable.innerHTML = customerRows.map((row) => `
    <tr><th>${row[0]}</th><td>${row[1]}</td><th>${row[2]}</th><td>${row[3]}</td></tr>
  `).join("");

  const serverRows = [
    ["OS Version", data.server.os_version, "CPU", data.server.cpu],
    ["Service", data.server.service, "Memory", data.server.memory],
    ["Model", data.server.model, "Disk", data.server.disk],
    ["S/N", data.server.serial, "Hostname", data.server.hostname],
  ];
  reportServerTable.innerHTML = serverRows.map((row) => `
    <tr><th>${row[0]}</th><td>${row[1]}</td><th>${row[2]}</th><td>${row[3]}</td></tr>
  `).join("");

  reportCards.replaceChildren();
  data.cards.forEach((card) => {
    const item = document.createElement("article");
    item.className = `report-card report-card-${card.status.toLowerCase().replaceAll(" ", "-")}`;
    item.innerHTML = `
      <span>${card.label}</span>
      <strong>${card.current}%</strong>
      <div>
        <b>Avg ${card.average}%</b>
        <b>Peak ${card.peak}%</b>
      </div>
      <em>${card.status}</em>
    `;
    reportCards.appendChild(item);
  });

  reportTable.replaceChildren();
  data.cards.forEach((card) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${card.label}</td>
      <td>${card.current}%</td>
      <td>${card.average}%</td>
      <td>${card.peak}%</td>
      <td>${card.threshold}%</td>
      <td><span class="${card.status === "Warning" ? "status-bad" : "status-good"}">${card.status}</span></td>
      <td>${card.recommendation}</td>
    `;
    reportTable.appendChild(row);
  });

  reportInspectionTable.replaceChildren();
  data.inspection_items.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.category}</td>
      <td>${item.item}</td>
      <td>${item.detail}</td>
      <td>${item.criteria}</td>
      <td>${item.metric}</td>
      <td><span class="${item.result === "Warning" ? "status-bad" : "status-good"}">${item.result}</span></td>
    `;
    reportInspectionTable.appendChild(row);
  });
}

function renderNotification(data) {
  notificationTable.replaceChildren();
  data.items.forEach((notice) => {
    const row = document.createElement("tr");
    const networkClass = notice.network_connection === "GOOD" ? "status-good" : "status-bad";
    row.innerHTML = `
      <td><a href="mailto:${notice.email}">${notice.email}</a></td>
      <td><span class="status-good">${notice.smtp_status}</span></td>
      <td><span class="${networkClass}">${notice.network_connection}</span></td>
      <td><span class="status-good">${notice.last_login}</span></td>
    `;
    notificationTable.appendChild(row);
  });
}

function renderDetect(data) {
  detectStart.textContent = data.range.start;
  detectEnd.textContent = data.range.end;
  detectCards.replaceChildren();
  const cardClasses = {
    detect: "dashboard-card-detect",
    warning: "dashboard-card-warning",
    logs: "dashboard-card-logs",
  };
  data.cards.forEach((card) => {
    const item = document.createElement("article");
    item.className = `dashboard-card detect-card ${cardClasses[card.id] || ""}`;
    item.innerHTML = `
      <div>
        <strong>${card.label}</strong>
        <span>${card.description}</span>
      </div>
      <b>${card.value}</b>
    `;
    detectCards.appendChild(item);
  });

  renderDetectRows(detectDetectTable, data.detect);
  renderDetectRows(detectWarningTable, data.warning);
  renderDetectRows(detectLogsTable, data.logs);
}

function renderDetectRows(target, items) {
  target.replaceChildren();
  if (!items.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="2">&nbsp;</td>`;
    target.appendChild(row);
    return;
  }
  items.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${item.date}</td><td>${item.event}</td>`;
    target.appendChild(row);
  });
}

function renderLogs(data) {
  logsStart.textContent = data.range.start;
  logsEnd.textContent = data.range.end;
  logsTotal.textContent = `Total: ${data.total_logs} logs`;
  logsHistoryTable.replaceChildren();
  data.items.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><span class="history-type history-${item.type.toLowerCase()}">${item.type}</span></td>
      <td>${item.date}</td>
      <td>${item.source}</td>
      <td><span class="severity-${item.severity.toLowerCase()}">${item.severity}</span></td>
      <td>${item.message}</td>
    `;
    logsHistoryTable.appendChild(row);
  });
}

function renderLicenseStatus(license) {
  if (!licenseStatusTable) return;
  const state = license.valid ? "Permanent License" : license.reason;
  licenseStatusTable.innerHTML = `
    <tr><th>고객사 정보</th><td>${license.customer || "-"}</td></tr>
    <tr><th>라이선스 키(Support Code)</th><td>${license.support_code || "-"}</td></tr>
    <tr><th>라이선스 상태</th><td class="${license.valid ? "license-ok" : "license-bad"}">${state}</td></tr>
    <tr><th>최초 사용 일자</th><td>${license.issued_at || "-"}</td></tr>
    <tr><th>만료 일자</th><td class="${license.days_left <= 30 ? "license-bad" : ""}">${license.expires_at || "-"}</td></tr>
    <tr><th>남은 일자</th><td>${license.valid ? `${license.days_left}일` : "-"}</td></tr>
    <tr><th>갱신 일자</th><td>${license.updated_at || "-"}</td></tr>
    <tr class="license-contact-row"><th>라이선스 문의</th><td><a href="https://www.oam.co.kr" target="_blank" rel="noreferrer">www.oam.co.kr</a><strong>| 1666 - 3736</strong></td></tr>
  `;
}

function updateLicenseGate(license) {
  renderLicenseStatus(license);
  const locked = !license.valid;
  licenseModal.classList.toggle("hidden", !locked);
  if (!locked) return;
  const reasonText = {
    not_registered: "라이선스 키를 등록해야 Web UI를 사용할 수 있습니다.",
    expired: "라이선스 사용 기간 365일이 만료되었습니다. 새 라이선스 키를 입력해 주세요.",
    invalid_key: "저장된 라이선스 키 확인이 필요합니다.",
    invalid_expiry: "라이선스 만료 일자 확인이 필요합니다.",
  };
  licenseModalReason.textContent = reasonText[license.reason] || "라이선스 확인이 필요합니다.";
  licenseIp.textContent = "고객사 + Support Code";
  licenseMac.textContent = "IP/MAC 변경 영향 없음";
  licenseSampleKey.textContent = license.sample_key || "-";
  licenseKeyInput.value = "";
  licenseError.textContent = "";
}

async function registerLicense(event) {
  event.preventDefault();
  licenseError.textContent = "";
  const payload = await requestJson("/api/license/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      customer: licenseCustomer.value,
      support_code: licenseSupportCode.value,
      license_key: licenseKeyInput.value,
    }),
  });
  if (!payload.ok) {
    licenseError.textContent = payload.error || "라이선스 등록에 실패했습니다.";
    if (payload.expected_sample) {
      licenseSampleKey.textContent = payload.expected_sample;
    }
    return;
  }
  updateLicenseGate(payload.license);
  await loadAll();
}

function renderNetworkStatus(data) {
  networkStatusTitle.textContent = data.title;
  networkTxRate.textContent = `${data.realtime.tx.current_mbps.toFixed(1)} Mbps`;
  networkRxRate.textContent = `${data.realtime.rx.current_mbps.toFixed(1)} Mbps`;
  networkTxTotal.textContent = `${data.realtime.tx.total_gb.toFixed(2)} GB`;
  networkRxTotal.textContent = `${data.realtime.rx.total_gb.toFixed(2)} GB`;
  drawFlowChart(networkTxFlow, data.realtime.tx.history, "tx");
  drawFlowChart(networkRxFlow, data.realtime.rx.history, "rx");
  drawNetworkChart(data.items, data.unit);
}

function drawFlowChart(target, values, type) {
  const width = 360;
  const height = 110;
  const pad = { left: 14, right: 14, top: 12, bottom: 18 };
  const chartWidth = width - pad.left - pad.right;
  const chartHeight = height - pad.top - pad.bottom;
  const maxValue = Math.max(...values, 1);
  const x = (index) => pad.left + (chartWidth * index) / Math.max(1, values.length - 1);
  const y = (value) => pad.top + chartHeight - (chartHeight * value) / maxValue;
  const path = values.map((value, index) => `${index === 0 ? "M" : "L"}${x(index).toFixed(1)},${y(value).toFixed(1)}`).join(" ");
  const area = `${path} L${x(values.length - 1).toFixed(1)},${pad.top + chartHeight} L${pad.left},${pad.top + chartHeight} Z`;
  const color = type === "tx" ? "#2388ff" : "#37dca0";
  target.innerHTML = `
    <defs>
      <linearGradient id="flowFill-${type}" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0%" stop-color="${color}" stop-opacity="0.22"></stop>
        <stop offset="100%" stop-color="${color}" stop-opacity="0.03"></stop>
      </linearGradient>
    </defs>
    <path d="${area}" fill="url(#flowFill-${type})"></path>
    <path d="${path}" fill="none" stroke="${color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
    <circle cx="${x(values.length - 1).toFixed(1)}" cy="${y(values[values.length - 1]).toFixed(1)}" r="5" fill="${color}"></circle>
  `;
}

function drawNetworkChart(items, unit) {
  const width = 980;
  const height = 360;
  const pad = { left: 64, right: 24, top: 26, bottom: 100 };
  const chartWidth = width - pad.left - pad.right;
  const chartHeight = height - pad.top - pad.bottom;
  const maxValue = Math.max(...items.flatMap((item) => [item.tx_gb, item.rx_gb]), 1);
  const y = (value) => pad.top + chartHeight - (chartHeight * value) / maxValue;
  const groupWidth = chartWidth / items.length;
  const barWidth = Math.max(6, Math.min(13, groupWidth * 0.28));

  const grid = [0, 0.25, 0.5, 0.75, 1].map((ratio) => {
    const value = maxValue * ratio;
    const yy = y(value);
    return `
      <line x1="${pad.left}" y1="${yy.toFixed(1)}" x2="${width - pad.right}" y2="${yy.toFixed(1)}" class="network-grid-line"></line>
      <text x="${pad.left - 10}" y="${(yy + 4).toFixed(1)}" class="network-axis-label" text-anchor="end">${value.toFixed(1)}</text>
    `;
  }).join("");

  const bars = items.map((item, index) => {
    const baseX = pad.left + index * groupWidth + groupWidth / 2;
    const txX = baseX - barWidth - 1;
    const rxX = baseX + 1;
    const txY = y(item.tx_gb);
    const rxY = y(item.rx_gb);
    const txH = pad.top + chartHeight - txY;
    const rxH = pad.top + chartHeight - rxY;
    return `
      <rect x="${txX.toFixed(1)}" y="${txY.toFixed(1)}" width="${barWidth}" height="${txH.toFixed(1)}" class="network-bar-tx"></rect>
      <rect x="${rxX.toFixed(1)}" y="${rxY.toFixed(1)}" width="${barWidth}" height="${rxH.toFixed(1)}" class="network-bar-rx"></rect>
      <text x="${baseX.toFixed(1)}" y="${height - 42}" class="network-x-label" text-anchor="end" transform="rotate(-48 ${baseX.toFixed(1)} ${height - 42})">${item.target}</text>
    `;
  }).join("");

  networkStatusChart.innerHTML = `
    <rect x="${pad.left}" y="${pad.top}" width="${chartWidth}" height="${chartHeight}" fill="#ffffff"></rect>
    ${grid}
    <line x1="${pad.left}" y1="${pad.top + chartHeight}" x2="${width - pad.right}" y2="${pad.top + chartHeight}" class="network-axis-line"></line>
    <text x="22" y="${height / 2}" class="network-axis-title" transform="rotate(-90 22 ${height / 2})">?꾩쟻 ?몃옒??(${unit})</text>
    ${bars}
    <text x="${pad.left + chartWidth / 2}" y="${height - 6}" class="network-axis-title" text-anchor="middle">IP 二쇱냼</text>
  `;
}

function renderMonitoring(data) {
  latestMonitoringData = data;
  monitoringTitle.textContent = uiSettings.language === "ko" ? "OAM - 하드웨어 사용량 모니터링" : data.title;
  monitoringStart.textContent = data.range.start.slice(0, 10).replaceAll(".", "-");
  monitoringEnd.textContent = data.range.end.slice(0, 10).replaceAll(".", "-");
  latestMonitoringSeries = data.series;
  drawLineChart(latestMonitoringSeries);
  renderGauge(cpuGauge, "CPU", data.current.cpu, "#2c90ff");
  renderGauge(memoryGauge, "Memory", data.current.memory, "#46b865");
  renderGauge(diskGauge, "Disk", data.current.disk, "#ffa52b");
  renderGauge(networkGauge, "Network", data.current.network, "#8b5cf6");
}
function renderSources(data) {
  const airGap = data.air_gap;
  sourceList.replaceChildren();
  if (!airGap) {
    sourceRoot.textContent = data.root;
    return;
  }

  sourceRoot.innerHTML = `
    <section class="airgap-hero">
      <div class="airgap-score">
        <span>Unified Security Score</span>
        <strong>${airGap.security_score.score}</strong>
        <em>${airGap.security_score.status}</em>
      </div>
      <p>${airGap.security_score.description}</p>
    </section>
  `;

  const kpi = document.createElement("section");
  kpi.className = "airgap-kpi-grid";
  kpi.innerHTML = airGap.kpis.map((item) => `
    <article class="airgap-kpi airgap-kpi-${item.id}">
      <i aria-hidden="true"></i>
      <div>
        <span>${item.title}</span>
        <strong>${item.value}</strong>
        <p>${item.detail}</p>
      </div>
    </article>
  `).join("");
  sourceList.appendChild(kpi);

  const timeline = document.createElement("section");
  timeline.className = "airgap-panel";
  timeline.innerHTML = `
    <div class="airgap-panel-head">
      <h2>Real-time Interlock Process</h2>
      <span>Power cut-off and lock sequence</span>
    </div>
    <div class="airgap-timeline">
      ${airGap.timeline.map((item) => `
        <article class="airgap-step ${item.state === "ACTIVE" ? "airgap-step-active" : ""}">
          <b>${item.step}</b>
          <strong>${item.title}</strong>
          <span>${item.state === "ACTIVE" ? "Safe state active" : "Complete"}</span>
        </article>
      `).join("")}
    </div>
  `;
  sourceList.appendChild(timeline);

  const bayMap = document.createElement("section");
  bayMap.className = "airgap-panel";
  bayMap.innerHTML = `
    <div class="airgap-panel-head">
      <h2>Drive Bay Map</h2>
      <span>Physical power and solenoid status by slot</span>
    </div>
    <div class="airgap-bay-grid">
      ${airGap.bays.map((bay) => `
        <article class="airgap-bay ${bay.lock.state === "LOCKED" ? "bay-locked" : "bay-ready"}">
          <div class="bay-top">
            <strong>${bay.slot}</strong>
            <span>${bay.lock.label}</span>
          </div>
          <div class="bay-visual">
            <i class="circuit-cut" aria-hidden="true"></i>
            <i class="bay-lock" aria-hidden="true"></i>
          </div>
          <dl>
            <div><dt>Power Cut-off</dt><dd>${bay.power.label}</dd></div>
            <div><dt>Solenoid</dt><dd>${bay.lock.description}</dd></div>
            <div><dt>UID</dt><dd>${bay.integrity.uid}</dd></div>
            <div><dt>Hash</dt><dd>${bay.integrity.hash}</dd></div>
          </dl>
        </article>
      `).join("")}
    </div>
  `;
  sourceList.appendChild(bayMap);

  const integrity = document.createElement("section");
  integrity.className = "airgap-bottom-grid";
  integrity.innerHTML = `
    <article class="airgap-panel">
      <div class="airgap-panel-head">
        <h2>Integrity Check Report</h2>
        <span>UID and SHA-256 verification history</span>
      </div>
      <div class="integrity-summary">
        <div><span>UID Match</span><strong>Drive #1 - Match</strong></div>
        <div><span>Hash Validation</span><strong>SHA-256 Hash - Valid</strong></div>
        <div><span>Anomaly Detection</span><strong class="integrity-ok">None</strong></div>
      </div>
      <table class="airgap-history">
        <thead><tr><th>Time</th><th>Target</th><th>UID</th><th>Hash</th></tr></thead>
        <tbody>
          ${airGap.integrity_history.map((item) => `
            <tr><td>${item.time}</td><td>${item.target}</td><td>${item.uid}</td><td>${item.hash}</td></tr>
          `).join("")}
        </tbody>
      </table>
    </article>
    <article class="airgap-panel emergency-panel">
      <div class="airgap-panel-head">
        <h2>${airGap.emergency.title}</h2>
        <span>Two-administrator approval required</span>
      </div>
      <p>${airGap.emergency.description}</p>
      <button type="button">${airGap.emergency.primary}</button>
      <strong>${airGap.emergency.secondary}</strong>
    </article>
  `;
  sourceList.appendChild(integrity);
}

function drawLineChart(series) {
  const width = 920;
  const height = 320;
  const pad = { left: 60, right: 18, top: 16, bottom: 50 };
  const chartWidth = width - pad.left - pad.right;
  const chartHeight = height - pad.top - pad.bottom;
  const visibleCount = Math.max(8, Math.round(series.length / monitoringZoom));
  const visibleSeries = series.slice(-visibleCount);
  const x = (index) => pad.left + (chartWidth * index) / Math.max(1, visibleSeries.length - 1);
  const y = (value) => pad.top + chartHeight - (chartHeight * value) / 100;
  const pointsFor = (key) => visibleSeries.map((item, index) => ({ x: x(index), y: y(item[key]) }));
  const smoothPathFor = (key) => {
    const points = pointsFor(key);
    if (!points.length) return "";
    if (points.length === 1) return `M${points[0].x.toFixed(1)},${points[0].y.toFixed(1)}`;
    let path = `M${points[0].x.toFixed(1)},${points[0].y.toFixed(1)}`;
    for (let index = 0; index < points.length - 1; index += 1) {
      const current = points[index];
      const next = points[index + 1];
      const previous = points[index - 1] || current;
      const following = points[index + 2] || next;
      const cp1x = current.x + (next.x - previous.x) / 6;
      const cp1y = current.y + (next.y - previous.y) / 6;
      const cp2x = next.x - (following.x - current.x) / 6;
      const cp2y = next.y - (following.y - current.y) / 6;
      path += ` C${cp1x.toFixed(1)},${cp1y.toFixed(1)} ${cp2x.toFixed(1)},${cp2y.toFixed(1)} ${next.x.toFixed(1)},${next.y.toFixed(1)}`;
    }
    return path;
  };

  const grid = [0, 20, 40, 60, 80, 100]
    .map((tick) => {
      const yy = y(tick).toFixed(1);
      return `<line x1="${pad.left}" y1="${yy}" x2="${width - pad.right}" y2="${yy}" class="grid-line"></line><text x="${pad.left - 12}" y="${Number(yy) + 4}" class="axis-label" text-anchor="end">${tick}.00%</text>`;
    })
    .join("");

  const labels = visibleSeries
    .filter((_, index) => index % Math.max(1, Math.ceil(visibleSeries.length / 6)) === 0 || index === visibleSeries.length - 1)
    .map((item) => {
      const realIndex = visibleSeries.indexOf(item);
      return `<text x="${x(realIndex)}" y="${height - 22}" class="axis-label" text-anchor="middle">${item.label.slice(0, 5)}</text>`;
    })
    .join("");

  const memoryPath = smoothPathFor("memory");
  const metricMeta = {
    cpu: { className: "line-cpu", path: smoothPathFor("cpu") },
    memory: { className: "line-memory", path: memoryPath },
    disk: { className: "line-disk", path: smoothPathFor("disk") },
    network: { className: "line-network", path: smoothPathFor("network") },
  };
  const activePath = metricMeta[activeMonitoringMetric] || metricMeta.cpu;
  const fillPath = activeMonitoringMetric === "memory"
    ? `<path d="${memoryPath} L${x(visibleSeries.length - 1)},${y(0)} L${x(0)},${y(0)} Z" fill="url(#memoryFill)"></path>`
    : "";
  monitoringChart.innerHTML = `
    <defs>
      <linearGradient id="memoryFill" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0%" stop-color="#25d984" stop-opacity="0.22" />
        <stop offset="100%" stop-color="#25d984" stop-opacity="0.03" />
      </linearGradient>
    </defs>
    <rect x="${pad.left}" y="${pad.top}" width="${chartWidth}" height="${chartHeight}" fill="#ffffff"></rect>
    ${grid}
    <text x="18" y="${height / 2}" class="axis-title" transform="rotate(-90 18 ${height / 2})">하드웨어 사용량</text>
    ${fillPath}
    <path d="${activePath.path}" class="line ${activePath.className}"></path>
    ${labels}
  `;
}
function renderGauge(target, label, value, color) {
  const radius = 62;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (circumference * value) / 100;
  target.innerHTML = `
    <svg viewBox="0 0 160 160">
      <circle cx="80" cy="80" r="${radius}" fill="none" stroke="#f0f0f0" stroke-width="10"></circle>
      <circle cx="80" cy="80" r="${radius}" fill="none" stroke="${color}" stroke-width="10" stroke-linecap="round" stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"></circle>
    </svg>
    <div class="gauge-label"><span>${label}</span><strong style="color:${color}">${value}%</strong></div>
  `;
}

function renderAudit(items) {
  auditTable.replaceChildren();
  if (!items.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="4">?꾩쭅 媛먯궗 濡쒓렇媛 ?놁뒿?덈떎.</td>`;
    auditTable.appendChild(row);
    return;
  }

  items.forEach((item) => {
    const row = document.createElement("tr");
    const result = item.state || item.reason || item.output || item.error || (item.ok === undefined ? "" : item.ok);
    row.innerHTML = `
      <td>${item.ts || "-"}</td>
      <td>${item.event || "-"}</td>
      <td>${item.slot_id || "-"}</td>
      <td>${String(result)}</td>
    `;
    auditTable.appendChild(row);
  });
}

async function loadAll() {
  const [summary, audit, integrated, monitoring, sources, dashboard, report, notification, detect, networkStatus, logs, license] = await Promise.all([
    requestJson("/api/summary"),
    requestJson("/api/audit"),
    requestJson("/api/integrated"),
    requestJson("/api/monitoring"),
    requestJson("/api/sources"),
    requestJson("/api/dashboard"),
    requestJson("/api/report"),
    requestJson("/api/notification"),
    requestJson("/api/detect"),
    requestJson("/api/network-status"),
    requestJson("/api/logs"),
    requestJson("/api/license"),
  ]);
  renderSlots(summary);
  renderAudit(audit.items);
  renderIntegrated(integrated);
  renderMonitoring(monitoring);
  renderSources(sources);
  renderDashboard(dashboard);
  renderReport(report);
  renderNotification(notification);
  renderDetect(detect);
  renderNetworkStatus(networkStatus);
  renderLogs(logs);
  renderLicenseStatus(license);
  updateLicenseGate(license);
  lastUpdated.textContent = new Date().toLocaleString();
}

async function runAction(action, slotId) {
  setBusy(true);
  try {
    await requestJson(`/api/${action}?slot=${encodeURIComponent(slotId)}`, { method: "POST" });
    await loadAll();
  } catch (error) {
    alert(error.message);
    await loadAll();
  } finally {
    setBusy(false);
  }
}

function setBusy(busy) {
  document.querySelectorAll("button").forEach((button) => {
    button.disabled = busy;
  });
}

refreshButton.addEventListener("click", loadAll);
loginForm.addEventListener("submit", login);
qrLoginButton.addEventListener("click", startQrLogin);
qrCodeBox.addEventListener("click", confirmQrLogin);
logoutButton.addEventListener("click", logout);
logoutSideButton.addEventListener("click", logout);
licenseForm.addEventListener("submit", registerLicense);
sideItems.forEach((item) => item.addEventListener("click", () => showView(item.dataset.view)));
chartMenuButton.addEventListener("click", () => downloadMenu.classList.toggle("open"));
chartZoomInButton.addEventListener("click", () => {
  monitoringZoom = Math.min(3, monitoringZoom + 0.5);
  drawLineChart(latestMonitoringSeries);
});
chartZoomOutButton.addEventListener("click", () => {
  monitoringZoom = Math.max(1, monitoringZoom - 0.5);
  drawLineChart(latestMonitoringSeries);
});
metricFilterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeMonitoringMetric = button.dataset.metric;
    metricFilterButtons.forEach((item) => item.classList.toggle("active", item === button));
    drawLineChart(latestMonitoringSeries);
  });
});
languageSelect.addEventListener("change", () => {
  pendingUiSettings.language = languageSelect.value;
  settingsApplyStatus.textContent = translations[pendingUiSettings.language]?.["settings.pending"] || translations.en["settings.pending"];
});
themeSelect.addEventListener("change", () => {
  pendingUiSettings.theme = themeSelect.value;
  settingsApplyStatus.textContent = translations[pendingUiSettings.language]?.["settings.pending"] || translations.en["settings.pending"];
});
settingsApplyButton.addEventListener("click", applyPendingUiSettings);
applyUiSettings();
checkSession();
setInterval(() => {
  if (!appRoot.classList.contains("app-locked")) {
    loadAll();
  }
}, 5000);

