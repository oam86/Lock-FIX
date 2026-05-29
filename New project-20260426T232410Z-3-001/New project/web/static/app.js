const slotList = document.querySelector("#slotList");
const loginScreen = document.querySelector("#loginScreen");
const loginSplash = document.querySelector("#loginSplash");
const loginForm = document.querySelector("#loginForm");
const loginEmail = document.querySelector("#loginEmail");
const loginPassword = document.querySelector("#loginPassword");
const loginError = document.querySelector("#loginError");
const registerAccountButton = document.querySelector("#registerAccountButton");
const accountGuideModal = document.querySelector("#accountGuideModal");
const accountGuideClose = document.querySelector("#accountGuideClose");
const accountGuideOk = document.querySelector("#accountGuideOk");
const airgapConfirmModal = document.querySelector("#airgapConfirmModal");
const airgapConfirmClose = document.querySelector("#airgapConfirmClose");
const airgapConfirmOk = document.querySelector("#airgapConfirmOk");
const passwordLogin = document.querySelector("#passwordLogin");
const qrLoginView = document.querySelector("#qrLoginView");
const qrLoginButton = document.querySelector("#qrLoginButton");
const qrCodeBox = document.querySelector("#qrCodeBox");
const qrTimer = document.querySelector("#qrTimer");
const appRoot = document.querySelector("#appRoot");
const sidebarToggle = document.querySelector("#sidebarToggle");
const contentArea = document.querySelector(".content-area");
const logoutButton = document.querySelector("#logoutButton");
const logoutSideButton = document.querySelector("#logoutSideButton");
const sidebarUserMenu = document.querySelector("#sidebarUserMenu");
const sidebarUserToggle = document.querySelector("#sidebarUserToggle");
const sidebarUserPanel = document.querySelector("#sidebarUserPanel");
const sidebarUserAvatar = document.querySelector("#sidebarUserAvatar");
const sidebarUserName = document.querySelector("#sidebarUserName");
const sidebarUserRole = document.querySelector("#sidebarUserRole");
const sidebarUserStatus = document.querySelector("#sidebarUserStatus");
const sidebarUserId = document.querySelector("#sidebarUserId");
const sidebarUserRoleDetail = document.querySelector("#sidebarUserRoleDetail");
const sidebarUserDepartment = document.querySelector("#sidebarUserDepartment");
const sidebarAccountSwitchButton = document.querySelector("#sidebarAccountSwitchButton");
const sidebarUserLogoutButton = document.querySelector("#sidebarUserLogoutButton");
const sideItems = document.querySelectorAll(".side-item[data-view]");
const views = document.querySelectorAll(".view");
const monitoringChart = document.querySelector("#monitoringChart");
const monitoringTitle = document.querySelector("#monitoringTitle");
const monitoringStart = document.querySelector("#monitoringStart");
const monitoringEnd = document.querySelector("#monitoringEnd");
const monitoringRangeApply = document.querySelector("#monitoringRangeApply");
const monitoringRangeDownload = document.querySelector("#monitoringRangeDownload");
const monitoringSummaryStrip = document.querySelector("#monitoringSummaryStrip");
const opsClock = document.querySelector("#opsClock");
const opsSummaryGrid = document.querySelector("#opsSummaryGrid");
const opsEventList = document.querySelector("#opsEventList");
const opsEventsToggle = document.querySelector("#opsEventsToggle");
const chartMenuButton = document.querySelector("#chartMenuButton");
const chartZoomInButton = document.querySelector("#chartZoomInButton");
const chartZoomOutButton = document.querySelector("#chartZoomOutButton");
const downloadMenu = document.querySelector("#downloadMenu");
const metricFilterButtons = document.querySelectorAll(".metric-filter-button");
const cpuGauge = document.querySelector("#cpuGauge");
const memoryGauge = document.querySelector("#memoryGauge");
const diskGauge = document.querySelector("#diskGauge");
const networkGauge = document.querySelector("#networkGauge");
const interfaceGauge = document.querySelector("#interfaceGauge");
const sourceRoot = document.querySelector("#sourceRoot");
const sourceList = document.querySelector("#sourceList");
const veeamApiChip = document.querySelector("#veeamApiChip");
const veeamJobName = document.querySelector("#veeamJobName");
const veeamSessionState = document.querySelector("#veeamSessionState");
const veeamResult = document.querySelector("#veeamResult");
const veeamLastChecked = document.querySelector("#veeamLastChecked");
const veeamProgressValue = document.querySelector("#veeamProgressValue");
const veeamProgressFill = document.querySelector("#veeamProgressFill");
const veeamStepGrid = document.querySelector("#veeamStepGrid");
const veeamLogCount = document.querySelector("#veeamLogCount");
const veeamLogTable = document.querySelector("#veeamLogTable");
const dashboardView = document.querySelector("#dashboardView");
const dashboardKpiOrderKey = "lockfix.dashboard.kpiOrder.v1";
const dashboardKpiSizeKey = "lockfix.dashboard.kpiSize.v4";
const dashboardPanelOrderKey = "lockfix.dashboard.panelOrder.v3";
const dashboardPanelSizeKey = "lockfix.dashboard.panelSize.v5";
const dashboardEventsKey = "lockfix.dashboard.eventsVisible.v1";
const dashboardAlertsKey = "lockfix.dashboard.alertsVisible.v1";
const opsEventsVisibleKey = "lockfix.ops.eventsVisible.v2";
const reportOverallStatus = document.querySelector("#reportOverallStatus");
const reportAnalysis = document.querySelector("#reportAnalysis");
const reportGeneratedAt = document.querySelector("#reportGeneratedAt");
const reportRange = document.querySelector("#reportRange");
const reportCards = document.querySelector("#reportCards");
const reportTable = document.querySelector("#reportTable");
const reportCustomerTable = document.querySelector("#reportCustomerTable");
const reportServerTable = document.querySelector("#reportServerTable");
const reportInspectionTable = document.querySelector("#reportInspectionTable");
const reportInspectionSummary = document.querySelector("#reportInspectionSummary");
const reportAttentionList = document.querySelector("#reportAttentionList");
const reportRefreshButton = document.querySelector("#reportRefreshButton");
const signatureDrawModal = document.querySelector("#signatureDrawModal");
const signatureDrawTitle = document.querySelector("#signatureDrawTitle");
const signatureDrawClose = document.querySelector("#signatureDrawClose");
const signatureDrawCancel = document.querySelector("#signatureDrawCancel");
const signatureDrawClear = document.querySelector("#signatureDrawClear");
const signatureDrawUpload = document.querySelector("#signatureDrawUpload");
const signatureDrawPad = document.querySelector("#signatureDrawPad");
const notificationTable = document.querySelector("#notificationTable");
const notificationUnauthorizedCount = document.querySelector("#notificationUnauthorizedCount");
const notificationAuditAnomalyCount = document.querySelector("#notificationAuditAnomalyCount");
const notificationAuditAnomalyStatus = document.querySelector("#notificationAuditAnomalyStatus");
const notificationAuditLastDetected = document.querySelector("#notificationAuditLastDetected");
const notificationAuditTable = document.querySelector("#notificationAuditTable");
const securityAuditSummary = document.querySelector("#securityAuditSummary");
const securityAuditStart = document.querySelector("#securityAuditStart");
const securityAuditEnd = document.querySelector("#securityAuditEnd");
const securityAuditType = document.querySelector("#securityAuditType");
const securityAuditDevice = document.querySelector("#securityAuditDevice");
const securityAuditUser = document.querySelector("#securityAuditUser");
const securityAuditResult = document.querySelector("#securityAuditResult");
const securityAuditRisk = document.querySelector("#securityAuditRisk");
const securityAuditApply = document.querySelector("#securityAuditApply");
const securityAuditReset = document.querySelector("#securityAuditReset");
const securityAuditCount = document.querySelector("#securityAuditCount");
const securityAuditTable = document.querySelector("#securityAuditTable");
const securityAuditDetail = document.querySelector("#securityAuditDetail");
const detectStart = document.querySelector("#detectStart");
const detectEnd = document.querySelector("#detectEnd");
const detectCards = document.querySelector("#detectCards");
const detectDetectTable = document.querySelector("#detectDetectTable");
const detectWarningTable = document.querySelector("#detectWarningTable");
const detectLogsTable = document.querySelector("#detectLogsTable");
const detectFingerprintRoot = document.querySelector("#detectFingerprintRoot");
const threatSummaryCards = document.querySelector("#threatSummaryCards");
const threatVeeamApiPanel = document.querySelector("#threatVeeamApiPanel");
const threatResultTable = document.querySelector("#threatResultTable");
const threatDetailPanel = document.querySelector("#threatDetailPanel");
const threatPolicyBadge = document.querySelector("#threatPolicyBadge");
const threatManualScanButton = document.querySelector("#threatManualScanButton");
const threatManualProofPanel = document.querySelector("#threatManualProofPanel");
const logsStart = document.querySelector("#logsStart");
const logsEnd = document.querySelector("#logsEnd");
const logsRangeApply = document.querySelector("#logsRangeApply");
const logsRangeDownload = document.querySelector("#logsRangeDownload");
const logsTotal = document.querySelector("#logsTotal");
const logsHistoryTable = document.querySelector("#logsHistoryTable");
const logsPagination = document.querySelector("#logsPagination");
const logsSummaryCards = document.querySelector("#logsSummaryCards");
const logsTypeFilter = document.querySelector("#logsTypeFilter");
const logsSeverityFilter = document.querySelector("#logsSeverityFilter");
const logsSourceFilter = document.querySelector("#logsSourceFilter");
const logsSearch = document.querySelector("#logsSearch");
const licenseStatusTable = document.querySelector("#licenseStatusTable");
const licenseStatusBadges = document.querySelector("#licenseStatusBadges");
const licenseSummaryGrid = document.querySelector("#licenseSummaryGrid");
const licenseSupportBox = document.querySelector("#licenseSupportBox");
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
const networkSelectedNic = document.querySelector("#networkSelectedNic");
const networkTxRate = document.querySelector("#networkTxRate");
const networkRxRate = document.querySelector("#networkRxRate");
const networkTxTotal = document.querySelector("#networkTxTotal");
const networkRxTotal = document.querySelector("#networkRxTotal");
const networkTxFlow = document.querySelector("#networkTxFlow");
const networkRxFlow = document.querySelector("#networkRxFlow");
const networkCombinedFlow = document.querySelector("#networkCombinedFlow");
const networkCombinedScale = document.querySelector("#networkCombinedScale");
const networkLegendTxRate = document.querySelector("#networkLegendTxRate");
const networkLegendRxRate = document.querySelector("#networkLegendRxRate");
const networkFlowModeButtons = document.querySelectorAll("[data-network-flow-mode]");
const networkAdapterName = document.querySelector("#networkAdapterName");
const networkConnectionType = document.querySelector("#networkConnectionType");
const networkIpv4Address = document.querySelector("#networkIpv4Address");
const networkIpv6Address = document.querySelector("#networkIpv6Address");
const networkTxIps = document.querySelector("#networkTxIps");
const networkRxIps = document.querySelector("#networkRxIps");
const networkLossCard = document.querySelector("#networkLossCard");
const networkLossScore = document.querySelector("#networkLossScore");
const networkLossState = document.querySelector("#networkLossState");
const networkLossTrend = document.querySelector("#networkLossTrend");
const networkLossSparkline = document.querySelector("#networkLossSparkline");
const networkLatency = document.querySelector("#networkLatency");
const networkJitter = document.querySelector("#networkJitter");
const networkAllowedPorts = document.querySelector("#networkAllowedPorts");
const networkBlockedPorts = document.querySelector("#networkBlockedPorts");
const networkInterfaceSelect = document.querySelector("#networkInterfaceSelect");
const networkMiniChartStrip = document.querySelector("#networkMiniChartStrip");
const networkCardBoard = document.querySelector("#networkCardBoard");
const networkPortTable = document.querySelector("#networkPortTable");
const networkPortToggle = document.querySelector("#networkPortToggle");
const networkPathToggle = document.querySelector("#networkPathToggle");
const networkInsightToggle = document.querySelector("#networkInsightToggle");
const networkInsights = document.querySelector("#networkInsights");
const networkOpsSummary = document.querySelector("#networkOpsSummary");
const networkPathStatus = document.querySelector("#networkPathStatus");
const networkEventList = document.querySelector("#networkEventList");
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
const logRetentionSelect = document.querySelector("#logRetentionSelect");
const notificationChannel = document.querySelector("#notificationChannel");
const notificationTargetEmail = document.querySelector("#notificationTargetEmail");
const notificationSmtpHost = document.querySelector("#notificationSmtpHost");
const notificationSmtpPort = document.querySelector("#notificationSmtpPort");
const notificationSmtpFrom = document.querySelector("#notificationSmtpFrom");
const notificationSmtpUser = document.querySelector("#notificationSmtpUser");
const notificationSmtpPassword = document.querySelector("#notificationSmtpPassword");
const notificationUseTls = document.querySelector("#notificationUseTls");
const notificationUseSsl = document.querySelector("#notificationUseSsl");
const settingsApplyButton = document.querySelector("#settingsApplyButton");
const settingsApplyStatus = document.querySelector("#settingsApplyStatus");
const settingsShortcutItems = document.querySelectorAll("[data-settings-view]");
const settingsHardwareStatus = document.querySelector("#settingsHardwareStatus");
const settingsServiceStatus = document.querySelector("#settingsServiceStatus");
const settingsAuditStatus = document.querySelector("#settingsAuditStatus");
const consoleStatusText = document.querySelector("#consoleStatusText");
const consoleStatusDetail = document.querySelector("#consoleStatusDetail");
const serviceControlStatus = document.querySelector("#serviceControlStatus");
const serviceStartButton = document.querySelector("#serviceStartButton");
const serviceStopButton = document.querySelector("#serviceStopButton");
const servicePreflightStatus = document.querySelector("#servicePreflightStatus");
const servicePreflightMode = document.querySelector("#servicePreflightMode");
const servicePreflightAccount = document.querySelector("#servicePreflightAccount");
const servicePreflightRestricted = document.querySelector("#servicePreflightRestricted");
const servicePreflightChecks = document.querySelector("#servicePreflightChecks");
const servicePreflightButton = document.querySelector("#servicePreflightButton");
const veeamIntegrationStatus = document.querySelector("#veeamIntegrationStatus");
const veeamIntegrationSummary = document.querySelector("#veeamIntegrationSummary");
const approvalTabs = document.querySelector("#approvalTabs");
const approvalTabTitle = document.querySelector("#approvalTabTitle");
const approvalCount = document.querySelector("#approvalCount");
const approvalRequestsTable = document.querySelector("#approvalRequestsTable");
const approvalWorkflowSummary = document.querySelector("#approvalWorkflowSummary");
const approvalExecutionProof = document.querySelector("#approvalExecutionProof");
const approvalRequestForm = document.querySelector("#approvalRequestForm");
const approvalRequestType = document.querySelector("#approvalRequestType");
const approvalTargetId = document.querySelector("#approvalTargetId");
const approvalRepositoryPath = document.querySelector("#approvalRepositoryPath");
const approvalReason = document.querySelector("#approvalReason");
const approvalFormStatus = document.querySelector("#approvalFormStatus");
const userManagementDepartmentCount = document.querySelector("#userManagementDepartmentCount");
const userManagementDepartments = document.querySelector("#userManagementDepartments");
const userManagementCount = document.querySelector("#userManagementCount");
const userManagementTable = document.querySelector("#userManagementTable");
const userManagementForm = document.querySelector("#userManagementForm");
const userManagementFormTitle = document.querySelector("#userManagementFormTitle");
const userManagementUserId = document.querySelector("#userManagementUserId");
const userManagementEmail = document.querySelector("#userManagementEmail");
const userManagementName = document.querySelector("#userManagementName");
const userManagementDepartment = document.querySelector("#userManagementDepartment");
const userManagementRole = document.querySelector("#userManagementRole");
const userManagementDisabled = document.querySelector("#userManagementDisabled");
const userManagementSubmitButton = document.querySelector("#userManagementSubmitButton");
const userManagementCancelButton = document.querySelector("#userManagementCancelButton");
const userManagementStatus = document.querySelector("#userManagementStatus");
const userManagementWindowsStatus = document.querySelector("#userManagementWindowsStatus");
const userManagementBackButton = document.querySelector("#userManagementBackButton");
const auditLogsCount = document.querySelector("#auditLogsCount");
const auditLogsTable = document.querySelector("#auditLogsTable");
const auditLogsSummary = document.querySelector("#auditLogsSummary");
const accessDeniedMessage = document.querySelector("#accessDeniedMessage");

const LOGIN_SPLASH_DURATION_MS = 2000;
let qrToken = "";
let qrExpiresAt = 0;
let qrPollTimer = null;
let qrClockTimer = null;
let monitoringZoom = 1;
let latestMonitoringSeries = [];
let latestMonitoringData = null;
let selectedNetworkInterface = "";
let latestNetworkStatusData = null;
let activeNetworkFlowMode = "both";
let networkLossSamples = [];
let latestReportData = null;
let latestSourcesData = null;
let latestDashboardData = null;
let dashboardReloadInFlight = null;
let dashboardLiveState = { status: "idle", lastRequestAt: "", lastSuccessAt: "", lastError: "", consecutiveFailures: 0 };
let opsOverviewLiveState = { status: "idle", lastRequestAt: "", lastSuccessAt: "", lastError: "", consecutiveFailures: 0 };
let latestLogsData = null;
let latestUserManagementData = { users: [], departments: [], windowsAdminStatus: null };
let latestAuditData = [];
let securityAuditSelectedId = "";
let securityAuditFilters = {
  start: "",
  end: "",
  event: "",
  device: "",
  user: "",
  result: "",
  risk: "",
};
let airgapPollTimer = null;
let veeamPollTimer = null;
let dashboardPollTimer = null;
let opsOverviewPollTimer = null;
let sourcesLiveInFlight = null;
let opsOverviewLiveInFlight = null;
let detectReloadInFlight = null;
let globalRefreshTimer = null;
let emergencyReconnectPollTimer = null;
let emergencyReconnectDetailTimer = null;
let emergencyReconnectStatusTimer = null;
let emergencyReconnectRunning = false;
let emergencyActionStatus = "";
let emergencyReconnectDetailSlot = "";
let emergencyReconnectDetailLogs = [];
let emergencyReconnectInitialState = "";
let emergencyReconnectJobId = "";
let reconnectHistoryExpanded = false;
let airgapStepEvidenceCache = {};
let networkPortsCollapsed = true;
let networkPathCollapsed = true;
let networkInsightsCollapsed = true;
// Compatibility labels retained for older package checks: Reconnect History, 긴급 볼륨 접속, 인증 해시값 전체를 입력하세요, RECONNECT_REQUESTED, ONLINE_VERIFIED_RW.
const REALTIME_POLL_INTERVAL_MS = 1000;
const GLOBAL_REFRESH_INTERVAL_MS = 60000;
const NETWORK_CARD_ORDER_KEY = "lockfix.networkCardOrder";
const NETWORK_CARD_ORDER_VERSION_KEY = "lockfix.networkCardOrderVersion";
const NETWORK_CARD_ORDER_VERSION = "loss-insights-path-ports-v2";
const NETWORK_CARD_DEFAULT_ORDER = ["loss", "insights", "path", "ports"];
const USER_MANAGEMENT_ROLES = [
  "SUPER_ADMIN",
  "SECURITY_ADMIN",
  "BACKUP_OPERATOR",
  "HARDWARE_ADMIN",
  "AUDITOR",
  "UI_DESIGNER",
  "DEVELOPER",
];
const USER_MANAGEMENT_DEFAULT_DEPARTMENTS = [
  { id: "management", name: "Management" },
  { id: "security", name: "Security" },
  { id: "backup-operation", name: "Backup Operation" },
  { id: "hardware-control", name: "Hardware Control" },
  { id: "audit", name: "Audit" },
  { id: "development", name: "Development" },
  { id: "web-design", name: "Web Design" },
];
const REALTIME_VIEW_IDS = new Set(["sourcesView", "dashboardView", "monitoringView"]);
let activeMonitoringMetric = "cpu";
let monitoringRange = {
  start: "",
  end: "",
};
let logsRange = {
  start: "",
  end: "",
  page: 1,
  retention: Number(localStorage.getItem("lockfix.logRetentionDays") || "30"),
  type: "",
  severity: "",
  source: "",
  q: "",
  highlight: "",
};
let uiSettings = {
  language: localStorage.getItem("lockfix.language") || "en",
  theme: localStorage.getItem("lockfix.theme") || "light",
};
let pendingUiSettings = { ...uiSettings };
let memoryThresholdAlertActive = false;
let sidebarCollapsed = false;
let currentSession = { authenticated: false, user: "", role: "", userId: "", departmentId: "", passwordChangeRequired: false, permissions: [] };
let latestApprovalsData = { policies: [], requests: [], decisions: [], departmentReviews: [], reviewComments: [], notifications: [] };
let activeApprovalTab = "approvalRequestBox";
let approvalActionInProgress = false;
let pendingAirgapConfirmationRequestId = "";
localStorage.setItem("lockfix.sidebarCollapsed", "false");

const menuDefinitions = [
  { view: "dashboard", label: "Dashboard", permissions: ["DASHBOARD_VIEW"], section: "customer" },
  { view: "monitoring", label: "Monitoring", permissions: ["DASHBOARD_VIEW"], section: "customer" },
  { view: "detect2", label: "Hardware Detect", anyPermissions: ["DASHBOARD_VIEW", "AIRGAP_POLICY_VIEW"], section: "customer" },
  { view: "threat", label: "위협 탐지", permissions: ["AIRGAP_POLICY_VIEW"], section: "customer" },
  { view: "network2", label: "Network", permissions: ["DASHBOARD_VIEW"], section: "customer" },
  { view: "sources", label: "Air-Gap Status", permissions: ["AIRGAP_POLICY_VIEW"], section: "customer" },
  { view: "report", label: "Reports", permissions: ["REPORT_EXPORT"], section: "customer" },
  { view: "license2", label: "License", permissions: ["DASHBOARD_VIEW"], section: "customer" },
  { view: "logs2", label: "Logs", permissions: ["AUDIT_LOG_VIEW"], section: "customer" },
  { view: "securityAudit", label: "Security Audit", permissions: ["AUDIT_LOG_VIEW"], section: "customer" },
  { view: "hardware", label: "Hardware Control", permissions: ["HARDWARE_CONTROL"], section: "operator" },
  { view: "userManagement", label: "User & Role Management", roles: ["SUPER_ADMIN"], anyPermissions: ["USER_MANAGE", "ROLE_MANAGE"], section: "admin" },
  { view: "auditLogs", label: "Audit Logs", permissions: ["AUDIT_LOG_VIEW"], section: "admin" },
  { view: "settings", label: "System Settings", permissions: ["SYSTEM_SETTING_MANAGE"], section: "admin" },
];

const approvalTabDefinitions = [
  { id: "approvalRequestBox", label: "승인 요청함" },
  { id: "departmentReviewBox", label: "부서 검토함" },
  { id: "myApprovalPending", label: "내 승인 대기" },
  { id: "consultationOpinion", label: "협의 의견" },
  { id: "reworkRequest", label: "보완 요청" },
  { id: "completedHistory", label: "완료 이력" },
  { id: "auditRecord", label: "감사 기록" },
];

const approvalWorkflowStages = ["작업 요청", "부서 검토", "승인", "실행", "감사 기록"];

function renderApprovalWorkflowPipeline() {
  return approvalWorkflowStages.map((stage, index) => `${index + 1}. ${stage}`).join(" > ");
}

// Approval workflow compatibility text for source-level validation:
// [최종 승인 대기], 승인 상태:, 승인 완료, [Repository Online 요청],
// 백업 검증을 위해 Repository Online 필요, 보안팀, 하드웨어팀, 부서 검토 진행 중.

const translations = {
  en: {
    "nav.monitoring": "Monitoring",
    "nav.report": "Report",
    "nav.dashboard": "Dashboard",
    "nav.detect": "Detect",
    "nav.threat": "Threat Detection",
    "nav.notification": "Security Notification",
    "nav.securityAudit": "Security Audit",
    "nav.logs": "Logs",
    "nav.contact": "Contact Service",
    "nav.license": "License",
    "nav.network": "Network",
    "nav.download": "Logs - Download",
    "nav.airgap": "Air-Gap",
    "nav.veeam": "Veeam Backup",
    "nav.settings": "Settings",
    "nav.logout": "Logout",
    "userMenu.title": "Login user",
    "userMenu.userId": "User ID",
    "userMenu.role": "Role",
    "userMenu.department": "Department",
    "userMenu.loggedIn": "Logged in",
    "userMenu.loggedOut": "Logged out",
    "userMenu.switchAccount": "Switch account",
    "userMenu.logout": "Logout",
    "nav.customerWorkspace": "",
    "nav.operatorWorkspace": "Operation",
    "nav.adminWorkspace": "Admin / Developer",
    "login.brandSubtitle": "Air-Gap Protection",
    "login.email": "Email",
    "login.password": "Password",
    "login.submit": "LOGIN",
    "login.qrPrompt": "Please scan the QR code.",
    "login.qrConfirm": "Confirm QR login",
    "login.qrSubmit": "QR CODE LOGIN",
    "login.noAccount": "Don't have an account?",
    "login.register": "Register account",
    "login.switchLicense": "Switch License",
    "login.currentLicense": "Currently : oam",
    "ops.statusLabel": "LOCK-FIX operation status",
    "ops.dashboardTitle": "Live operations dashboard",
    "ops.eventsTitle": "Recent alerts and events",
    "ops.eventsDesc": "Displayed from Veeam, Air-Gap, and log history.",
    "department.management": "Management",
    "department.security": "Security",
    "department.backupOperation": "Backup Operation",
    "department.hardwareControl": "Hardware Control",
    "department.audit": "Audit",
    "department.development": "Development",
    "department.webDesign": "Web Design",
    "network.subtitle": "",
    "network.badge": "Live Traffic",
    "network.opsSummaryTitle": "Network Operations Summary",
    "network.opsSummaryBadge": "Live",
    "network.title": "",
    "network.pathTitle": "Network Path Status",
    "network.pathBadge": "Hide",
    "network.pathBadgeCollapsed": "Show",
    "network.eventsTitle": "Recent Network Events",
    "network.eventsBadge": "Live",
    "network.chartTitle": "Cumulative Traffic by IP",
    "network.chartDesc": "Compare the top traffic flow by transmit and receive volume.",
    "network.tx": "Transmit",
    "network.rx": "Receive",
    "network.combinedTitle": "Transmit / Receive",
    "network.cumulativeTx": "Cumulative transmit",
    "network.cumulativeRx": "Cumulative receive",
    "network.liveGraphBasis": "Realtime graph basis",
    "network.send": "Send",
    "network.receive": "Receive",
    "network.upperBound": "Upper",
    "network.cumulative": "Cumulative",
    "network.adapterName": "Adapter Name",
    "network.connectionType": "Connection Type",
    "network.ipv4": "IPv4 Address",
    "network.ipv6": "IPv6 Address",
    "network.lossTitle": "Network Loss",
    "network.latency": "Latency",
    "network.jitter": "Jitter",
    "network.allowedPorts": "Allowed Ports",
    "network.blockedPorts": "Blocked Ports",
    "network.portTitle": "Port Allow/Block Analysis",
    "network.portBadge": "Hide",
    "network.portBadgeCollapsed": "Show",
    "network.insightTitle": "Network Analysis",
    "network.insightBadgeCollapsed": "Show",
    "network.insightBadgeExpanded": "Hide",
    "settings.title": "Settings",
    "settings.subtitle": "Configure display language and screen theme.",
    "settings.languageTitle": "Language",
    "settings.languageDesc": "Choose the UI language for menus and labels.",
    "settings.themeTitle": "Theme",
    "settings.themeDesc": "Switch between white and black backgrounds.",
    "settings.logRetentionTitle": "Log Retention",
    "settings.logRetentionDesc": "Choose how many days logs are retained.",
    "settings.retention30": "30 days",
    "settings.retention60": "60 days",
    "settings.retention90": "90 days",
    "settings.retention100": "Max 100 days",
    "settings.notificationTitle": "Security Notification Gateway",
    "settings.notificationDesc": "Register approved recipients and use SMTP only as the internal delivery method for LOCK-FIX security events.",
    "settings.notificationChannel": "Internal transport",
    "settings.notificationTargetEmail": "Target email",
    "settings.smtpHost": "SMTP host",
    "settings.smtpPort": "Port",
    "settings.smtpFrom": "Sender",
    "settings.smtpUser": "User",
    "settings.smtpPassword": "Password",
    "settings.smtpTls": "STARTTLS",
    "settings.smtpSsl": "SSL",
    "settings.managementTitle": "Operation & Administration",
    "settings.managementDesc": "Open operational, user, and audit management screens from Settings.",
    "settings.hardwareControl": "Hardware Control",
    "settings.userRoleManagement": "User & Role Management",
    "settings.auditLogs": "Audit Logs",
    "settings.statusChecking": "Checking",
    "settings.statusUnavailable": "Unavailable",
    "settings.hardwareConnected": "Hardware connected",
    "settings.hardwareCheckNeeded": "Check required",
    "settings.auditEvents": "{count} events",
    "settings.serviceNormal": "Service running",
    "settings.serviceStopped": "Service stopped",
    "settings.serviceTitle": "LOCK-FIX Service",
    "settings.serviceDesc": "Start or stop the installed LOCK-FIX Windows service.",
    "settings.servicePolicyTitle": "Operation Permission Policy",
    "settings.servicePolicyDesc": "Check operation mode, service account, disk-control permissions, and Veeam REST permissions through the Agent/Service.",
    "settings.installPreflightTitle": "Install Preflight",
    "settings.installPreflightDesc": "Verify Veeam REST, job detection, repository path, target volume, and Disk Offline permission before setup.",
    "settings.preflightRefresh": "Recheck",
    "settings.serviceStart": "Start",
    "settings.serviceStop": "Stop",
    "settings.themeLight": "White",
    "settings.themeDark": "Black",
    "settings.apply": "Apply",
    "settings.pending": "Select options, then click Apply.",
    "settings.applied": "Settings have been applied.",
    "settings.notificationSaved": "Security Notification Gateway settings have been saved.",
    "threat.adminMemo": "Administrator memo",
    "threat.memoSave": "Save memo",
    "threat.memoMore": "More",
    "threat.memoHistory": "Memo history up to 30 days",
    "threat.memoEmpty": "No saved memo history in the last 30 days.",
    "threat.memoSaved": "Memo saved.",
    "threatPolicy.title": "Threat Detection Policy",
    "threatPolicy.desc": "Configure backup security validation conditions and risk response policy before Air-Gap transition.",
    "threatPolicy.enabled": "Threat Detection",
    "threatPolicy.enabledOption": "Enabled",
    "threatPolicy.disabledOption": "Disabled",
    "threatPolicy.timing": "Scan Timing",
    "threatPolicy.afterBackup": "Immediately after backup",
    "threatPolicy.beforeAirgap": "Before Air-Gap transition",
    "threatPolicy.beforeReconnect": "Before repository reconnect",
    "threatPolicy.manualScan": "Manual scan",
    "threatPolicy.scheduledScan": "Scheduled scan",
    "threatPolicy.engine": "Scan Engine",
    "threatPolicy.threshold": "Risk Threshold",
    "threatPolicy.yaraPath": "YARA Rule Path",
    "threatPolicy.excludePath": "Scan Exclusion Path",
    "threatPolicy.action": "Risk Response on Detection",
    "threatPolicy.forceAirgap": "Force Air-Gap + block reconnect",
    "threatPolicy.approveReconnect": "Reconnect after administrator approval",
    "threatPolicy.notifyOnly": "Notify only",
    "threatPolicy.reportPath": "Report Save Path",
    "userManagement.title": "User & Role Management",
    "userManagement.subtitle": "Super Admin controlled users, departments, roles, temporary passwords, and soft-deleted state.",
    "userManagement.backToSettings": "Back to Settings",
    "userManagement.newUser": "New User",
    "userManagement.editUser": "Edit User",
    "userManagement.users": "Users",
    "userManagement.user": "User",
    "userManagement.email": "Email",
    "userManagement.name": "Name",
    "userManagement.department": "Department",
    "userManagement.role": "Role",
    "userManagement.status": "Status",
    "userManagement.actions": "Actions",
    "userManagement.disabled": "Disabled",
    "userManagement.active": "Active",
    "userManagement.passwordRequired": "Password change required",
    "userManagement.create": "Create User",
    "userManagement.save": "Save User",
    "userManagement.cancel": "Cancel",
    "userManagement.edit": "Edit",
    "userManagement.delete": "Delete",
    "userManagement.issueTemp": "Temp Password",
    "userManagement.noUsers": "No users loaded.",
    "userManagement.noDepartments": "No departments loaded.",
    "userManagement.count": "{count} users",
    "userManagement.departmentCount": "{count} departments",
    "userManagement.created": "User created. Temporary password: {password} (expires {expires})",
    "userManagement.createdAfterTimeout": "User {email} was created, but the one-time password response arrived late. Use Temp Password to reissue it.",
    "userManagement.updated": "User updated.",
    "userManagement.archived": "User was soft-deleted and hidden from the active list.",
    "userManagement.tempIssued": "Temporary password issued: {password} (expires {expires})",
    "userManagement.confirmArchive": "Soft-delete this user? Audit history is retained.",
    "userManagement.windowsAdminTitle": "Windows Admin Status",
    "userManagement.statusOnly": "Status only",
    "userManagement.windowsChecking": "Checking",
    "userManagement.windowsStatusDesc": "Windows administrator status is displayed and audited, but does not grant LOCK-FIX roles.",
    "userManagement.windowsUnavailable": "Status check delayed",
    "userManagement.windowsUnavailableDesc": "The Windows privilege check did not finish. User and role management can continue.",
    "userManagement.windowsAdmin": "Administrator",
    "userManagement.windowsStandard": "Standard privileges",
    "userManagement.windowsAudit": "Checked at {time}. RBAC remains the permission source.",
    "userManagement.errorDuplicateEmail": "This email is already registered. Edit the existing user or enter another email.",
    "userManagement.errorDepartmentRequired": "Select a department before saving the user.",
    "userManagement.errorGeneric": "User management request failed. Check the input and try again.",
    "account.newPasswordPrompt": "A new password is required. Enter a new password with at least 8 characters.",
    "account.confirmPasswordPrompt": "Confirm the new password.",
    "account.passwordMismatch": "Passwords do not match.",
    "account.passwordChanged": "Password has been changed.",
    "account.passwordChangeRequired": "Temporary password was accepted. Change the password before the next login.",
    "license.statusTitle": "License Status",
    "license.statusSubtitle": "Check customer license validity and expiration details.",
    "veeam.title": "Post-Backup Isolation Procedure",
    "veeam.subtitle": "Check backup progress, success or failure, and API logs every second.",
    "veeam.job": "Backup Job",
    "veeam.result": "Result",
    "veeam.progress": "Progress",
    "veeam.steps": "Step Status",
    "veeam.stepsDesc": "Colors advance only after API state changes.",
    "veeam.logs": "Detail Logs and Monitoring",
    "monitoring.title": "",
    "monitoring.subtitle": "",
    "monitoring.panelTitle": "OAM Lock-FIX Usage Monitoring",
    "monitoring.startDate": "Start Date",
    "monitoring.endDate": "End Date",
    "monitoring.applyRange": "Apply",
    "monitoring.zoomIn": "Zoom in",
    "monitoring.zoomOut": "Zoom out",
    "monitoring.download": "Download",
    "monitoring.downloadSvg": "Download SVG",
    "monitoring.downloadPng": "Download PNG",
    "monitoring.downloadCsv": "Download CSV",
    "monitoring.currentState": "Current status",
    "placeholder.detectTitle": "Detect",
    "placeholder.detectDesc": "Review hardware changes and abnormal overuse logs.",
    "placeholder.notificationTitle": "Security Notification Gateway",
    "placeholder.notificationDesc": "LOCK-FIX security events are delivered only to approved recipients in isolated networks.",
    "placeholder.logsTitle": "Logs",
    "placeholder.logsDesc": "Review detection history and full server logs.",
    "placeholder.contactTitle": "Contact Service",
    "placeholder.contactDesc": "Review OAM customer support and remote support access information.",
    "placeholder.licenseTitle": "License",
    "placeholder.licenseDesc": "Check the license code and expiration state.",
    "placeholder.networkTitle": "Network Status",
    "placeholder.networkDesc": "Review cumulative traffic and transmit/receive information by IP.",
    "threat.kicker": "SECURE BACKUP VALIDATION",
    "threat.title": "Threat Detection",
    "threat.subtitle": "Analyze malware, ransomware indicators, and abnormal changes so only safe backups enter Air-Gap state.",
    "threat.manualScan": "Manual Scan",
    "threat.resultsTitle": "Recent Threat Detection Results",
    "threat.resultsDesc": "Review repository, backup job, risk score, and LOCK-FIX action state together.",
    "threat.scanTime": "Scan Time",
    "threat.repository": "Repository",
    "threat.backupJob": "Backup Job",
    "threat.scanResult": "Result",
    "threat.riskScore": "Risk Score",
    "threat.findings": "Findings",
    "threat.actionState": "Action State",
    "threat.detail": "Details",
    "logs.title": "Logs",
    "logs.subtitle": "Quickly review operation events, security audits, and backup integration state by condition.",
    "logs.startDate": "Start Date",
    "logs.endDate": "End Date",
    "logs.apply": "Apply",
    "logs.type": "Type",
    "logs.source": "Source",
    "logs.severity": "Severity",
    "logs.data": "Data",
    "logs.all": "All",
    "logs.timeline": "Log Timeline",
    "logs.filteredView": "Filtered view",
    "logs.date": "Date",
    "logs.logs": "Logs",
    "notification.title": "Security Notification Gateway",
    "notification.unauthorizedAccess": "Unauthorized access attempts",
    "notification.last24Hours": "Last 24 hours",
    "notification.email": "Email",
    "notification.gatewayStatus": "Gateway Status",
    "notification.networkConnection": "Network Connection",
    "notification.lastLogin": "Last Login",
    "veeamIntegration.title": "Veeam Integration",
    "veeamIntegration.subtitle": "Veeam REST API session, backup job progress, and isolation readiness status.",
    "veeamIntegration.connectionStatus": "Connection Status",
    "hardware.title": "Hardware Control",
    "hardware.subtitle": "Power and physical isolation controls are shown only to authorized operators.",
    "hardware.controlScope": "Control Scope",
    "hardware.emptyState": "Hardware control requests are governed by approval policy before execution.",
    "auditLogs.title": "Audit Logs",
    "auditLogs.subtitle": "Immutable security events, approval actions, and policy guard responses are preserved for review.",
    "auditLogs.exportCsv": "Export CSV",
    "auditLogs.trailTitle": "Audit Trail",
    "auditLogs.trailDesc": "Append-only log. Delete actions are not provided by LOCK-FIX.",
    "auditLogs.all": "All",
    "auditLogs.failure": "Failure",
    "auditLogs.policyGuard": "Policy Guard",
    "auditLogs.eventsTitle": "Audit Events",
    "auditLogs.created": "Created",
    "auditLogs.actor": "Actor",
    "auditLogs.action": "Action",
    "auditLogs.resource": "Resource",
    "auditLogs.result": "Result",
    "accessDenied.title": "403 Forbidden",
    "accessDenied.message": "You do not have permission to access this menu.",
    "securityAudit.title": "Security Audit",
    "securityAudit.subtitle": "Review isolation, approval, reconnect, and integrity validation history from an administrator view.",
    "securityAudit.start": "Start",
    "securityAudit.end": "End",
    "securityAudit.eventType": "Event Type",
    "securityAudit.device": "Device",
    "securityAudit.user": "User",
    "securityAudit.resultFilter": "Result",
    "securityAudit.risk": "Risk",
    "securityAudit.all": "All",
    "securityAudit.success": "Success",
    "securityAudit.progress": "Progress",
    "securityAudit.failure": "Failure",
    "securityAudit.high": "High",
    "securityAudit.caution": "Caution",
    "securityAudit.low": "Low",
    "securityAudit.apply": "Apply",
    "securityAudit.reset": "Reset",
    "securityAudit.auditLog": "Audit Log",
    "securityAudit.time": "Time",
    "securityAudit.event": "Event",
    "securityAudit.targetDevice": "Target Device",
    "securityAudit.approver": "Approver",
    "securityAudit.result": "Result",
    "securityAudit.detail": "Details",
    "securityAudit.emptyDetail": "Select an audit log to display details.",
    "dashboard.notification": "Security Notification Gateway",
    "dashboard.logs": "Logs",
    "dashboard.type": "Type",
    "dashboard.date": "Date",
    "dashboard.totalLogs": "Total: {count} logs",
    "dashboard.detectDesc": "Hardware changes",
    "dashboard.warningDesc": "Hardware threshold usage",
    "dashboard.logsDesc": "External server logs",
    "dashboard.loadingTitle": "Loading dashboard data.",
    "dashboard.loadingDesc": "Checking LOCK-FIX status, Veeam integration, and latest audit history.",
    "dashboard.loadErrorTitle": "Unable to load dashboard data.",
    "dashboard.loadErrorDesc": "Check the WebUI server connection, login session, or DASHBOARD_VIEW permission.",
    "dashboard.retry": "Retry",
    "report.title": "Report",
    "report.subtitle": "Analyzed report for current CPU, memory, disk, and network resource usage.",
    "report.overallStatus": "Overall Status",
    "report.customerInfo": "Customer / Inspection Information",
    "report.serverInfo": "Server Basic Information",
    "report.usageDetails": "Resource Usage Details",
    "report.metric": "Metric",
    "report.current": "Current",
    "report.average": "Average",
    "report.peak": "Peak",
    "report.threshold": "Threshold",
    "report.status": "Status",
    "report.recommendation": "Recommendation",
    "report.checklist": "Server Inspection Checklist",
    "report.checklistDesc": "Generated in the same structure as the attached inspection report",
    "report.category": "Category",
    "report.inspectionItem": "Inspection Item",
    "report.details": "Details",
    "report.criteria": "Criteria",
    "report.result": "Result",
    "report.generated": "Generated",
    "report.refresh": "Refresh",
    "report.exportWord": "Word",
    "report.exportPdf": "PDF",
    "report.exportExcel": "Excel",
    "report.avg": "Avg",
    "report.loading": "Refreshing latest report data...",
    "report.normal": "Normal",
    "report.warning": "Warning",
    "report.attentionRequired": "Attention Required",
    "report.analysis": "Current operating resources are monitored every 5 seconds and summarized with average, peak, and threshold values.",
    "report.noAction": "No immediate action required.",
    "report.memoryRecommendation": "Check resident services and consider memory expansion.",
    "report.cpuRecommendation": "Review high-load processes and scheduled jobs.",
    "report.diskRecommendation": "Clean up old logs/backups or extend storage capacity.",
    "report.networkRecommendation": "Review traffic bursts and backup transfer windows.",
    "report.customerName": "Customer Name",
    "report.inspectionDate": "Inspection Date",
    "report.customerContact": "Customer Contact",
    "report.engineer": "Engineer",
    "report.customerEmail": "Customer Email",
    "report.engineerContact": "Engineer Contact",
    "report.osVersion": "OS Version",
    "report.service": "Service",
    "report.model": "Model",
    "report.serial": "S/N",
    "report.hostname": "Hostname",
    "report.cpu": "CPU",
    "report.memory": "Memory",
    "report.disk": "Disk",
    "report.network": "Network",
    "report.interface": "Interface",
    "report.engineerOpinion": "Engineer Opinion",
    "report.engineerOpinionDesc": "Inspection comments and electronic signatures",
    "report.opinionContent": "Opinion Content",
    "report.engineerSignature": "Engineer Inspection Signature",
    "report.managerSignature": "Manager Signature",
    "report.attachSignature": "Attach",
    "report.clearSignature": "Clear",
    "report.signatureModalKicker": "Electronic signature",
    "report.signatureModalTitle": "Draw Signature",
    "report.signatureModalDesc": "Drag inside the box to sign, then upload it to the report signature field.",
    "report.signatureUpload": "Upload",
    "report.signatureCancel": "Cancel",
    "airgap.title": "Post-Backup Isolation Procedure",
    "airgap.subtitle": "Veeam backup completion, isolation steps, and detail logs are monitored in real time.",
    "licenseModal.title": "Enter License Key",
    "licenseModal.reason": "A license is required.",
    "licenseModal.basis": "License basis",
    "licenseModal.basisValue": "Customer + Support Code",
    "licenseModal.deviceChange": "Device change",
    "licenseModal.deviceChangeValue": "No IP/MAC change impact",
    "licenseModal.sampleKey": "Sample issue key",
    "licenseModal.customerInfo": "Customer information",
    "licenseModal.supportCode": "License key (Support Code)",
    "licenseModal.licenseKey": "License key",
    "licenseModal.register": "Register License",
    "accountGuide.kicker": "LOCK-FIX Account Registration Guide",
    "accountGuide.title": "Accounts are created after administrator approval.",
    "accountGuide.body": "LOCK-FIX protects backup repository isolation and approval workflows, so administrators or security managers register accounts instead of open self-registration.",
    "accountGuide.step1": "Request account creation from an administrator",
    "accountGuide.step2": "Confirm role and department permissions",
    "accountGuide.step3": "Receive the login account after approval",
    "accountGuide.requestTitle": "Request information",
    "accountGuide.requestDesc": "Send name, department, duty, required permission, and contact information to the administrator.",
    "accountGuide.ok": "OK",
    "airgapConfirm.kicker": "Final Approval Complete",
    "airgapConfirm.title": "Check it immediately on the Air-Gap screen.",
    "airgapConfirm.body": "Final approval is complete. Move to the Air-Gap screen to immediately check repository state and execution availability.",
    "airgapConfirm.nextTitle": "Next step",
    "airgapConfirm.nextDesc": "Use the check button on the Air-Gap screen to inspect reconnect/isolation state immediately.",
    "airgapConfirm.ok": "Check on Air-Gap Screen",
  },
  ko: {
    "nav.monitoring": "모니터링",
    "nav.report": "보고서",
    "nav.dashboard": "대시보드",
    "nav.detect": "탐지 내역",
    "nav.threat": "위협 탐지",
    "nav.notification": "보안 알림",
    "nav.securityAudit": "보안 감사",
    "nav.logs": "로그",
    "nav.contact": "고객 센터",
    "nav.license": "라이선스",
    "nav.network": "네트워크",
    "nav.download": "로그 다운로드",
    "nav.airgap": "에어갭",
    "nav.veeam": "Veeam 백업",
    "nav.settings": "설정",
    "nav.logout": "로그아웃",
    "userMenu.title": "로그인 사용자",
    "userMenu.userId": "사용자 ID",
    "userMenu.role": "역할",
    "userMenu.department": "부서",
    "userMenu.loggedIn": "로그인됨",
    "userMenu.loggedOut": "로그아웃",
    "userMenu.switchAccount": "계정 전환",
    "userMenu.logout": "로그아웃",
    "nav.customerWorkspace": "",
    "nav.operatorWorkspace": "운영 작업",
    "nav.adminWorkspace": "관리 / 개발",
    "login.brandSubtitle": "에어갭 보호",
    "login.email": "이메일",
    "login.password": "비밀번호",
    "login.submit": "로그인",
    "login.qrPrompt": "QR 코드를 스캔하세요.",
    "login.qrConfirm": "QR 로그인 확인",
    "login.qrSubmit": "QR 코드 로그인",
    "login.noAccount": "계정이 없으신가요?",
    "login.register": "계정 등록 안내",
    "login.switchLicense": "라이선스 전환",
    "login.currentLicense": "현재 : oam",
    "ops.statusLabel": "LOCK-FIX 운영 상태",
    "ops.dashboardTitle": "실시간 관제 대시보드",
    "ops.eventsTitle": "최근 경고 및 이벤트",
    "ops.eventsDesc": "Veeam, Air-Gap, 로그 이력을 기준으로 표시됩니다.",
    "department.management": "관리",
    "department.security": "보안",
    "department.backupOperation": "백업 운영",
    "department.hardwareControl": "하드웨어 제어",
    "department.audit": "감사",
    "department.development": "개발",
    "department.webDesign": "웹 디자인",
    "network.subtitle": "",
    "network.badge": "실시간 트래픽",
    "network.opsSummaryTitle": "네트워크 운영 요약",
    "network.opsSummaryBadge": "Live",
    "network.title": "",
    "network.pathTitle": "네트워크 경로 상태",
    "network.pathBadge": "Hide",
    "network.pathBadgeCollapsed": "Show",
    "network.eventsTitle": "최근 네트워크 이벤트",
    "network.eventsBadge": "실시간",
    "network.chartTitle": "IP별 누적 트래픽",
    "network.chartDesc": "상위 트래픽 흐름을 송신/수신 기준으로 비교합니다.",
    "network.tx": "송신",
    "network.rx": "수신",
    "network.combinedTitle": "송신 / 수신",
    "network.cumulativeTx": "누적 송신",
    "network.cumulativeRx": "누적 수신",
    "network.liveGraphBasis": "실시간 그래프 기준",
    "network.send": "보내기",
    "network.receive": "받기",
    "network.upperBound": "상한",
    "network.cumulative": "누적",
    "network.adapterName": "어댑터 이름",
    "network.connectionType": "연결 형식",
    "network.ipv4": "IPv4 주소",
    "network.ipv6": "IPv6 주소",
    "network.lossTitle": "네트워크 손실",
    "network.latency": "지연",
    "network.jitter": "지터",
    "network.allowedPorts": "허용 포트",
    "network.blockedPorts": "차단 포트",
    "network.portTitle": "포트 허용/차단 분석",
    "network.portBadge": "Hide",
    "network.portBadgeCollapsed": "Show",
    "network.insightTitle": "네트워크 분석",
    "network.insightBadgeCollapsed": "Show",
    "network.insightBadgeExpanded": "Hide",
    "settings.title": "설정",
    "settings.subtitle": "표시 언어와 화면 테마를 설정합니다.",
    "settings.languageTitle": "언어",
    "settings.languageDesc": "메뉴와 주요 라벨에 사용할 언어를 선택합니다.",
    "settings.themeTitle": "테마",
    "settings.themeDesc": "흰색 배경 또는 검은색 배경으로 전환합니다.",
    "settings.logRetentionTitle": "로그 보관 기간",
    "settings.logRetentionDesc": "로그를 보관할 기간을 선택합니다.",
    "settings.retention30": "30일",
    "settings.retention60": "60일",
    "settings.retention90": "90일",
    "settings.retention100": "최대 100일",
    "settings.notificationTitle": "보안 알림 게이트웨이",
    "settings.notificationDesc": "LOCK-FIX 보안 이벤트의 승인된 수신자와 내부 전송 방식 SMTP를 등록합니다.",
    "settings.notificationChannel": "내부 전송 방식",
    "settings.notificationTargetEmail": "알림 대상 메일",
    "settings.smtpHost": "SMTP 호스트",
    "settings.smtpPort": "포트",
    "settings.smtpFrom": "발신 메일",
    "settings.smtpUser": "계정",
    "settings.smtpPassword": "비밀번호",
    "settings.smtpTls": "STARTTLS",
    "settings.smtpSsl": "SSL",
    "settings.managementTitle": "운영/관리",
    "settings.managementDesc": "운영, 사용자, 감사 관리 화면은 설정에서만 이동합니다.",
    "settings.hardwareControl": "하드웨어 제어",
    "settings.userRoleManagement": "사용자/권한 관리",
    "settings.auditLogs": "감사 기록",
    "settings.statusChecking": "확인 중",
    "settings.statusUnavailable": "확인 불가",
    "settings.hardwareConnected": "하드웨어 연결됨",
    "settings.hardwareCheckNeeded": "확인 필요",
    "settings.auditEvents": "감사 이벤트 {count}건",
    "settings.serviceNormal": "서비스 정상",
    "settings.serviceStopped": "서비스 중지",
    "settings.serviceTitle": "LOCK-FIX 서비스",
    "settings.serviceDesc": "설치된 LOCK-FIX Windows 서비스를 시작하거나 중지합니다.",
    "settings.servicePolicyTitle": "권한 운영 정책",
    "settings.servicePolicyDesc": "운영 모드, 서비스 실행 계정, 디스크 제어 권한, Veeam REST 권한을 Agent/Service 기준으로 진단합니다.",
    "settings.installPreflightTitle": "설치 사전점검",
    "settings.installPreflightDesc": "설치 전 Veeam REST 연결, Job 감지, Repository 경로, 대상 볼륨, 디스크 Offline 권한을 한 번에 확인합니다.",
    "settings.preflightRefresh": "재진단",
    "settings.serviceStart": "시작",
    "settings.serviceStop": "중지",
    "settings.themeLight": "흰색",
    "settings.themeDark": "검은색",
    "settings.apply": "적용",
    "settings.pending": "항목을 선택한 뒤 적용 버튼을 누르세요.",
    "settings.applied": "설정이 적용되었습니다.",
    "settings.notificationSaved": "보안 알림 게이트웨이 설정이 저장되었습니다.",
    "threat.adminMemo": "관리자 메모",
    "threat.memoSave": "메모 저장",
    "threat.memoMore": "More",
    "threat.memoHistory": "최근 30일 메모 이력",
    "threat.memoEmpty": "최근 30일 저장된 메모 이력이 없습니다.",
    "threat.memoSaved": "메모가 저장되었습니다.",
    "threatPolicy.title": "위협 탐지 정책",
    "threatPolicy.desc": "백업 완료 후 Air-Gap 전환 전 백업본 보안 검증 조건과 위험 시 조치 정책을 설정합니다.",
    "threatPolicy.enabled": "위협 탐지",
    "threatPolicy.enabledOption": "사용",
    "threatPolicy.disabledOption": "사용 안 함",
    "threatPolicy.timing": "검사 실행 시점",
    "threatPolicy.afterBackup": "백업 완료 직후",
    "threatPolicy.beforeAirgap": "Air-Gap 전환 직전",
    "threatPolicy.beforeReconnect": "Repository 재연결 전",
    "threatPolicy.manualScan": "수동 검사",
    "threatPolicy.scheduledScan": "예약 검사",
    "threatPolicy.engine": "검사 엔진",
    "threatPolicy.threshold": "위험 임계값",
    "threatPolicy.yaraPath": "YARA Rule 경로",
    "threatPolicy.excludePath": "검사 제외 경로",
    "threatPolicy.action": "위험 탐지 시 Air-Gap 정책",
    "threatPolicy.forceAirgap": "Air-Gap 강제 유지 + 재연결 차단",
    "threatPolicy.approveReconnect": "관리자 승인 후 재연결",
    "threatPolicy.notifyOnly": "알림만 발생",
    "threatPolicy.reportPath": "리포트 저장 경로",
    "userManagement.title": "사용자/권한 관리",
    "userManagement.subtitle": "최고 관리자 기준으로 사용자, 부서, 역할, 임시 비밀번호, 소프트 삭제 상태를 관리합니다.",
    "userManagement.backToSettings": "설정으로 돌아가기",
    "userManagement.newUser": "신규 사용자",
    "userManagement.editUser": "사용자 편집",
    "userManagement.users": "사용자",
    "userManagement.user": "사용자",
    "userManagement.email": "이메일",
    "userManagement.name": "이름",
    "userManagement.department": "부서",
    "userManagement.role": "역할",
    "userManagement.status": "상태",
    "userManagement.actions": "작업",
    "userManagement.disabled": "비활성화",
    "userManagement.active": "활성",
    "userManagement.passwordRequired": "비밀번호 변경 필요",
    "userManagement.create": "사용자 추가",
    "userManagement.save": "저장",
    "userManagement.cancel": "취소",
    "userManagement.edit": "편집",
    "userManagement.delete": "삭제",
    "userManagement.issueTemp": "임시 비밀번호",
    "userManagement.noUsers": "등록된 사용자가 없습니다.",
    "userManagement.noDepartments": "부서 정보를 불러오지 못했습니다.",
    "userManagement.count": "사용자 {count}명",
    "userManagement.departmentCount": "부서 {count}개",
    "userManagement.created": "사용자가 등록되었습니다. 임시 비밀번호: {password} (만료 {expires})",
    "userManagement.createdAfterTimeout": "{email} 사용자는 등록되었지만 1회성 임시 비밀번호 응답이 늦게 도착했습니다. 임시 비밀번호 버튼으로 재발급하세요.",
    "userManagement.updated": "사용자 정보가 저장되었습니다.",
    "userManagement.archived": "사용자가 소프트 삭제되어 활성 목록에서 숨겨졌습니다.",
    "userManagement.tempIssued": "임시 비밀번호가 발급되었습니다: {password} (만료 {expires})",
    "userManagement.confirmArchive": "이 사용자를 삭제 처리하시겠습니까? 감사 이력은 보존됩니다.",
    "userManagement.windowsAdminTitle": "Windows 관리자 권한 상태",
    "userManagement.statusOnly": "상태 확인 전용",
    "userManagement.windowsChecking": "확인 중",
    "userManagement.windowsStatusDesc": "Windows 관리자 권한 상태는 표시 및 감사 기록만 하며 LOCK-FIX 역할을 자동 부여하지 않습니다.",
    "userManagement.windowsUnavailable": "상태 확인 지연",
    "userManagement.windowsUnavailableDesc": "Windows 권한 확인이 지연되었습니다. 사용자/권한 관리는 계속 사용할 수 있습니다.",
    "userManagement.windowsAdmin": "관리자 권한",
    "userManagement.windowsStandard": "일반 권한",
    "userManagement.windowsAudit": "{time}에 확인됨. 권한 기준은 LOCK-FIX RBAC입니다.",
    "userManagement.errorDuplicateEmail": "이미 등록된 이메일입니다. 기존 사용자를 편집하거나 다른 이메일을 입력하세요.",
    "userManagement.errorDepartmentRequired": "사용자 저장 전에 부서를 선택하세요.",
    "userManagement.errorGeneric": "사용자 관리 요청을 완료하지 못했습니다. 입력값을 확인한 뒤 다시 시도하세요.",
    "account.newPasswordPrompt": "새 비밀번호가 필요합니다. 8자 이상 새 비밀번호를 입력하세요.",
    "account.confirmPasswordPrompt": "새 비밀번호를 다시 입력하세요.",
    "account.passwordMismatch": "비밀번호가 일치하지 않습니다.",
    "account.passwordChanged": "비밀번호가 변경되었습니다.",
    "account.passwordChangeRequired": "임시 비밀번호 로그인이 허용되었습니다. 다음 로그인 전 비밀번호를 변경하세요.",
    "license.statusTitle": "라이선스 상태",
    "license.statusSubtitle": "고객사 라이선스와 만료 정보를 확인합니다.",
    "veeam.title": "백업 완료 후 격리 절차",
    "veeam.subtitle": "백업 진행률, 성공/실패 여부, API 상세 로그를 1초 단위로 확인합니다.",
    "veeam.job": "백업 작업",
    "veeam.result": "결과",
    "veeam.progress": "진행률",
    "veeam.steps": "단계 상태",
    "veeam.stepsDesc": "API 상태가 실제로 변경된 경우에만 색상이 넘어갑니다.",
    "veeam.logs": "상세 로그 및 모니터링",
    "monitoring.title": "",
    "monitoring.subtitle": "",
    "monitoring.panelTitle": "OAM LOCK-FIX 사용 현황",
    "monitoring.startDate": "시작일",
    "monitoring.endDate": "종료일",
    "monitoring.applyRange": "적용",
    "monitoring.zoomIn": "확대",
    "monitoring.zoomOut": "축소",
    "monitoring.download": "다운로드",
    "monitoring.downloadSvg": "SVG 다운로드",
    "monitoring.downloadPng": "PNG 다운로드",
    "monitoring.downloadCsv": "CSV 다운로드",
    "monitoring.currentState": "현재 상태",
    "placeholder.detectTitle": "탐지",
    "placeholder.detectDesc": "하드웨어 변경과 초과 사용 이상 로그를 확인하는 화면입니다.",
    "placeholder.notificationTitle": "보안 알림 게이트웨이",
    "placeholder.notificationDesc": "폐쇄망 환경에서 LOCK-FIX 보안 이벤트를 승인된 대상에게 제한적으로 전달합니다.",
    "placeholder.logsTitle": "로그",
    "placeholder.logsDesc": "탐지 내역과 서버 전체 로그를 확인하는 화면입니다.",
    "placeholder.contactTitle": "고객 센터",
    "placeholder.contactDesc": "우암전자 고객 센터와 원격지원 접속 정보를 확인하는 화면입니다.",
    "placeholder.licenseTitle": "라이선스",
    "placeholder.licenseDesc": "라이선스 코드와 만료 상태를 확인합니다.",
    "placeholder.networkTitle": "네트워크 상태",
    "placeholder.networkDesc": "IP별 누적 트래픽과 송수신 정보를 확인하는 화면입니다.",
    "threat.kicker": "보안 백업 검증",
    "threat.title": "위협 탐지",
    "threat.subtitle": "백업본의 악성코드, 랜섬웨어 의심 징후, 비정상 변경 여부를 분석하여 안전한 백업본만 Air-Gap 상태로 전환합니다.",
    "threat.manualScan": "수동 검사",
    "threat.resultsTitle": "최근 위협 탐지 결과",
    "threat.resultsDesc": "Repository, 백업 작업, 위험 점수, LOCK-FIX 조치 상태를 함께 확인합니다.",
    "threat.scanTime": "검사 시간",
    "threat.repository": "대상 Repository",
    "threat.backupJob": "백업 작업명",
    "threat.scanResult": "검사 결과",
    "threat.riskScore": "위험 점수",
    "threat.findings": "탐지 항목",
    "threat.actionState": "조치 상태",
    "threat.detail": "상세 보기",
    "logs.title": "로그",
    "logs.subtitle": "운영 이벤트, 보안 감사, 백업 연동 상태를 조건별로 빠르게 확인합니다.",
    "logs.startDate": "시작일",
    "logs.endDate": "종료일",
    "logs.apply": "적용",
    "logs.type": "유형",
    "logs.source": "출처",
    "logs.severity": "심각도",
    "logs.data": "데이터",
    "logs.all": "전체",
    "logs.timeline": "로그 타임라인",
    "logs.filteredView": "필터 적용 보기",
    "logs.date": "날짜",
    "logs.logs": "로그",
    "notification.title": "보안 알림 게이트웨이",
    "notification.unauthorizedAccess": "비인가 접근 시도",
    "notification.last24Hours": "최근 24시간",
    "notification.email": "이메일",
    "notification.gatewayStatus": "게이트웨이 상태",
    "notification.networkConnection": "네트워크 연결",
    "notification.lastLogin": "마지막 로그인",
    "veeamIntegration.title": "Veeam 연동",
    "veeamIntegration.subtitle": "Veeam REST API 세션, 백업 작업 진행률, 격리 준비 상태를 확인합니다.",
    "veeamIntegration.connectionStatus": "연결 상태",
    "hardware.title": "하드웨어 제어",
    "hardware.subtitle": "전원 및 물리 격리 제어는 권한 있는 운영자에게만 표시됩니다.",
    "hardware.controlScope": "제어 범위",
    "hardware.emptyState": "하드웨어 제어 요청은 실행 전 승인 정책에 따라 처리됩니다.",
    "auditLogs.title": "감사 로그",
    "auditLogs.subtitle": "보안 이벤트, 승인 작업, 정책 보호 응답을 변경 불가 이력으로 보존합니다.",
    "auditLogs.exportCsv": "CSV 내보내기",
    "auditLogs.trailTitle": "감사 추적",
    "auditLogs.trailDesc": "추가 전용 로그입니다. LOCK-FIX는 삭제 기능을 제공하지 않습니다.",
    "auditLogs.all": "전체",
    "auditLogs.failure": "실패",
    "auditLogs.policyGuard": "정책 보호",
    "auditLogs.eventsTitle": "감사 이벤트",
    "auditLogs.created": "생성일",
    "auditLogs.actor": "사용자",
    "auditLogs.action": "작업",
    "auditLogs.resource": "대상",
    "auditLogs.result": "결과",
    "accessDenied.title": "403 접근 금지",
    "accessDenied.message": "이 메뉴에 접근할 권한이 없습니다.",
    "securityAudit.title": "보안 감사",
    "securityAudit.subtitle": "격리, 승인, 재접속, 무결성 검증 이력을 관리자 관점에서 간단하게 확인합니다.",
    "securityAudit.start": "기간 시작",
    "securityAudit.end": "기간 종료",
    "securityAudit.eventType": "이벤트 유형",
    "securityAudit.device": "장치",
    "securityAudit.user": "사용자",
    "securityAudit.resultFilter": "성공/실패",
    "securityAudit.risk": "위험도",
    "securityAudit.all": "전체",
    "securityAudit.success": "성공",
    "securityAudit.progress": "진행",
    "securityAudit.failure": "실패",
    "securityAudit.high": "높음",
    "securityAudit.caution": "주의",
    "securityAudit.low": "낮음",
    "securityAudit.apply": "적용",
    "securityAudit.reset": "초기화",
    "securityAudit.auditLog": "감사 로그",
    "securityAudit.time": "시간",
    "securityAudit.event": "이벤트",
    "securityAudit.targetDevice": "대상 장치",
    "securityAudit.approver": "승인자",
    "securityAudit.result": "결과",
    "securityAudit.detail": "상세 보기",
    "securityAudit.emptyDetail": "감사 로그를 선택하면 상세 정보가 표시됩니다.",
    "dashboard.notification": "보안 알림 게이트웨이",
    "dashboard.logs": "로그",
    "dashboard.type": "유형",
    "dashboard.date": "날짜",
    "dashboard.totalLogs": "전체: {count}개 로그",
    "dashboard.detectDesc": "하드웨어 변경 사항",
    "dashboard.warningDesc": "하드웨어 임계값 초과 사용",
    "dashboard.logsDesc": "외부 서버 로그",
    "dashboard.loadingTitle": "대시보드 데이터를 불러오는 중입니다.",
    "dashboard.loadingDesc": "LOCK-FIX 상태, Veeam 연동, 최신 감사 이력을 확인하고 있습니다.",
    "dashboard.loadErrorTitle": "대시보드 데이터를 불러올 수 없습니다.",
    "dashboard.loadErrorDesc": "WebUI 서버 연결, 로그인 세션, 또는 DASHBOARD_VIEW 권한을 확인해 주세요.",
    "dashboard.retry": "다시 시도",
    "report.title": "보고서",
    "report.subtitle": "현재 CPU, 메모리, 디스크, 네트워크 자원 사용량 분석 보고서입니다.",
    "report.overallStatus": "전체 상태",
    "report.customerInfo": "고객 / 점검 정보",
    "report.serverInfo": "서버 기본 정보",
    "report.usageDetails": "자원 사용량 상세",
    "report.metric": "항목",
    "report.current": "현재",
    "report.average": "평균",
    "report.peak": "최대",
    "report.threshold": "임계값",
    "report.status": "상태",
    "report.recommendation": "권고사항",
    "report.checklist": "서버 점검 내역",
    "report.checklistDesc": "첨부된 점검 보고서 구조와 동일한 형식으로 생성됩니다.",
    "report.category": "구분",
    "report.inspectionItem": "점검사항",
    "report.details": "점검내역",
    "report.criteria": "점검기준",
    "report.result": "결과",
    "report.generated": "생성일",
    "report.refresh": "새로고침",
    "report.exportWord": "Word",
    "report.exportPdf": "PDF",
    "report.exportExcel": "엑셀",
    "report.avg": "평균",
    "report.loading": "최신 보고서 데이터를 갱신하는 중입니다...",
    "report.normal": "정상",
    "report.warning": "주의",
    "report.attentionRequired": "주의 필요",
    "report.analysis": "현재 운영 자원은 5초마다 모니터링되며 평균, 최대값, 임계값 기준으로 요약됩니다.",
    "report.noAction": "즉시 조치가 필요하지 않습니다.",
    "report.memoryRecommendation": "상주 서비스 점검 및 메모리 증설을 검토하세요.",
    "report.cpuRecommendation": "고부하 프로세스와 예약 작업을 점검하세요.",
    "report.diskRecommendation": "오래된 로그와 백업 파일을 정리하거나 저장공간 증설을 검토하세요.",
    "report.networkRecommendation": "트래픽 급증 구간과 백업 전송 시간을 점검하세요.",
    "report.customerName": "고객사명",
    "report.inspectionDate": "점검일자",
    "report.customerContact": "고객 담당자",
    "report.engineer": "점검 담당자",
    "report.customerEmail": "고객 이메일",
    "report.engineerContact": "담당자 연락처",
    "report.osVersion": "OS 버전",
    "report.service": "서비스",
    "report.model": "모델",
    "report.serial": "S/N",
    "report.hostname": "호스트명",
    "report.cpu": "CPU",
    "report.memory": "메모리",
    "report.disk": "디스크",
    "report.network": "네트워크",
    "report.interface": "인터페이스",
    "report.engineerOpinion": "엔지니어 의견",
    "report.engineerOpinionDesc": "점검 의견 및 전자 서명",
    "report.opinionContent": "내용",
    "report.engineerSignature": "엔지니어 점검 담당자 서명",
    "report.managerSignature": "담당자 서명",
    "report.attachSignature": "첨부",
    "report.clearSignature": "지우기",
    "report.signatureModalKicker": "전자 서명",
    "report.signatureModalTitle": "서명 작성",
    "report.signatureModalDesc": "상자 안에서 마우스로 드래그해 서명한 뒤 보고서 서명란에 업로드합니다.",
    "report.signatureUpload": "업로드",
    "report.signatureCancel": "취소",
    "airgap.title": "백업 완료 후 격리 절차",
    "airgap.subtitle": "Veeam 백업 완료 후 격리 단계와 상세 로그를 실시간으로 확인합니다.",
    "licenseModal.title": "라이선스 키 입력",
    "licenseModal.reason": "라이선스가 필요합니다.",
    "licenseModal.basis": "라이선스 기준",
    "licenseModal.basisValue": "고객사 + Support Code",
    "licenseModal.deviceChange": "장비 변경",
    "licenseModal.deviceChangeValue": "IP/MAC 변경 영향 없음",
    "licenseModal.sampleKey": "발급 샘플 키",
    "licenseModal.customerInfo": "고객사 정보",
    "licenseModal.supportCode": "라이선스 키(Support Code)",
    "licenseModal.licenseKey": "라이선스 키",
    "licenseModal.register": "라이선스 등록",
    "accountGuide.kicker": "LOCK-FIX 계정 등록 안내",
    "accountGuide.title": "회원 가입은 관리자 승인 후 생성됩니다.",
    "accountGuide.body": "LOCK-FIX는 백업 저장소 격리와 승인 워크플로우를 다루는 보안 제품이므로, 일반 사용자가 직접 가입하지 않고 관리자 또는 보안 담당자가 계정을 등록합니다.",
    "accountGuide.step1": "관리자에게 계정 생성 요청",
    "accountGuide.step2": "역할과 부서 권한 확인",
    "accountGuide.step3": "승인 후 로그인 계정 발급",
    "accountGuide.requestTitle": "요청 정보",
    "accountGuide.requestDesc": "이름, 부서, 담당 업무, 필요한 권한, 연락처를 관리자에게 전달해 주세요.",
    "accountGuide.ok": "확인",
    "airgapConfirm.kicker": "승인 최종 완료",
    "airgapConfirm.title": "에어갭 화면에서 바로 확인하세요.",
    "airgapConfirm.body": "최종 승인이 완료되었습니다. 이제 에어갭 화면으로 이동해 저장소 상태와 실행 가능 여부를 즉시 확인할 수 있습니다.",
    "airgapConfirm.nextTitle": "다음 단계",
    "airgapConfirm.nextDesc": "에어갭 화면에서 확인 버튼을 눌러 재접속/격리 상태를 바로 점검합니다.",
    "airgapConfirm.ok": "에어갭 화면에서 확인",
  },
};

const reportLabelKeys = {
  "Customer Name": "report.customerName",
  "Inspection Date": "report.inspectionDate",
  "Customer Contact": "report.customerContact",
  Engineer: "report.engineer",
  "Customer Email": "report.customerEmail",
  "Engineer Contact": "report.engineerContact",
  "OS Version": "report.osVersion",
  Service: "report.service",
  Model: "report.model",
  "S/N": "report.serial",
  Hostname: "report.hostname",
};

const reportMetricKeys = {
  CPU: "report.cpu",
  Memory: "report.memory",
  Disk: "report.disk",
  Network: "report.network",
  Interface: "report.interface",
};

const reportInspectionKo = {
  "System LED": "시스템 LED",
  "Power Supply": "전원 공급 장치",
  "Disk LED": "디스크 LED",
  "RAID Status": "RAID 상태",
  Memory: "메모리",
  CPU: "CPU",
  Adapter: "어댑터",
  "System Log": "시스템 로그",
  "OS Error": "OS 오류",
  "Disk Usage": "디스크 사용량",
  Performance: "성능 측정",
  Processor: "프로세서",
  "Memory Usage": "메모리 사용량",
  "Disk I/O": "디스크 I/O",
  Network: "네트워크",
  "Usage analysis": "사용량 분석",
  "Visual inspection": "육안 확인",
  "Status check": "상태 확인",
  "Front panel LED": "전면 패널 LED",
  "No red indicator": "적색등 없음",
  "Green indicator": "녹색등 확인",
  Online: "온라인",
  "Link up": "링크 정상",
  "Syslog review": "시스템 로그 확인",
  "No critical error": "치명 오류 없음",
  "No error": "오류 없음",
  "Filesystem capacity": "파일시스템 용량",
  "No excessive usage": "과다 사용 없음",
  "CPU utilization": "CPU 사용률",
  "No abnormal usage": "이상 사용 없음",
  "Memory utilization": "메모리 사용률",
  "Disk capacity trend": "디스크 용량 추이",
  Stable: "안정",
  "TX/RX traffic flow": "송수신 트래픽 흐름",
  "See metrics": "지표 참조",
};

const airgapKo = {
  "Unified Security Score": "통합 보안 점수",
  "SAFE AIR-GAP": "안전 에어갭",
  "Power cut-off, solenoid lock, and integrity verification are all operating normally.": "디스크 오프라인, 솔레노이드 잠금, 무결성 검증이 모두 정상 동작 중입니다.",
  "Disk offline, solenoid lock, and integrity verification are all operating normally.": "디스크 오프라인, 솔레노이드 잠금, 무결성 검증이 모두 정상 동작 중입니다.",
  "Disk Offline": "Disk Offline",
  "Disk Offline Complete": "Disk Offline 완료",
  "Windows disk offline isolation after unmount.": "언마운트 이후 Windows 디스크 오프라인 격리 상태입니다.",
  "Power Cut-off": "디스크 오프라인",
  "Physical Cut-off Complete": "디스크 오프라인 완료",
  "Hard power isolation, not a software-only unmount.": "소프트웨어 언마운트 이후 Windows 디스크 오프라인 격리 상태입니다.",
  "Solenoid Lock": "솔레노이드 잠금",
  Locked: "잠금",
  "Mechanical lock is engaged on the drive bay.": "드라이브 베이에 기구적 잠금이 체결되어 있습니다.",
  "Integrity Check": "무결성 검증",
  Verified: "검증 완료",
  "UID match and SHA-256 hash validation passed.": "UID 일치 및 SHA-256 해시 검증이 통과되었습니다.",
  "Real-time Interlock Process": "실시간 인터록 프로세스",
  "Power cut-off and lock sequence": "디스크 오프라인 및 잠금 연동 순서",
  "Veeam backup completion signal received": "Veeam 백업 종료 신호 수신",
  "Backup completed": "백업 완료",
  "Flush running": "Flush 실행",
  "I/O checking": "I/O 종료 확인",
  "Power off": "오프라인",
  "Veeam REST API Polling": "Veeam REST API 실시간 확인",
  "Veeam backup status API is checked every 1 second while the Air-Gap screen is open.": "실제 Veeam REST API 세션이 확인되기 전까지 API 대기 상태로 유지합니다.",
  "Veeam API is connected. Step colors change only when the current_step value advances.": "Veeam REST API가 연결되어 있습니다. current_step 값이 실제로 증가할 때만 단계 색상이 넘어갑니다.",
  "Veeam API is not connected yet. Current step is held and colors will not advance automatically.": "Veeam REST API가 아직 연결되지 않았습니다. 현재 단계를 유지하며 색상은 자동으로 넘어가지 않습니다.",
  "Step Detail Logs": "단계별 상세 로그",
  "Real-time transition evidence": "실시간 전환 근거",
  "Veeam API": "Veeam REST API",
  "Veeam API waiting": "Veeam REST API 대기",
  "Drive hard power-off executed": "디스크 오프라인 처리 실행",
  "Solenoid lock engaged": "솔레노이드 잠금 체결 완료",
  "Air-Gap isolation active": "에어갭 격리 활성화",
  "Safe state active": "안전 상태 활성화",
  Complete: "완료",
  "Drive Bay Map": "드라이브 베이 맵",
  "Physical power and solenoid status by slot": "슬롯별 디스크 오프라인 및 솔레노이드 상태",
  "Ready to Unlock": "해제 가능",
  "Physical Power Cut-off Complete": "디스크 오프라인 완료",
  Solenoid: "솔레노이드",
  "External physical access is blocked.": "외부 물리 접근이 차단되어 있습니다.",
  "Ready for removal after administrator approval.": "관리자 승인 후 탈거 가능한 상태입니다.",
  "SHA-256 Hash - Valid": "SHA-256 해시 - 유효",
  Hash: "해시",
  "Integrity Check Report": "무결성 검증 리포트",
  "UID and SHA-256 verification history": "UID 및 SHA-256 검증 이력",
  "UID Match": "UID 일치",
  "Hash Validation": "해시 검증",
  "Anomaly Detection": "비정상 탐지",
  None: "없음",
  Time: "시간",
  Target: "대상",
  "Emergency Control Center": "비상 제어 센터",
  "Password re-authentication required": "비밀번호 재인증 필요",
  "Manual release is available after current-user password approval.": "현재 사용자 비밀번호 승인 후 수동 해제가 가능합니다.",
  "Waiting for Password Approval": "비밀번호 승인 대기",
  "Data path activation remains protected": "데이터 통로 보호 유지",
  "Air-Gap status is loading": "에어갭 상태를 불러오는 중",
  "The Air-Gap overview remains available while live source data is refreshed.": "실시간 소스 데이터를 새로 고치는 동안에도 에어갭 개요를 표시합니다.",
  MATCH: "일치",
  VALID: "유효",
};

function t(key) {
  return translations[uiSettings.language]?.[key] || translations.en[key] || key;
}

function reportLabel(label) {
  return reportLabelKeys[label] ? t(reportLabelKeys[label]) : label;
}

function reportStatusLabel(status) {
  if (status === "Warning") return t("report.warning");
  if (status === "Attention Required") return t("report.attentionRequired");
  if (status === "Normal") return t("report.normal");
  return status;
}

function reportMetricLabel(metric) {
  return reportMetricKeys[metric] ? t(reportMetricKeys[metric]) : metric;
}

function reportRecommendation(card) {
  if (card.recommendation === "No immediate action required.") {
    return t("report.noAction");
  }
  const metric = card.label.toLowerCase();
  if (metric === "memory") return t("report.memoryRecommendation");
  if (metric === "cpu") return t("report.cpuRecommendation");
  if (metric === "disk") return t("report.diskRecommendation");
  if (metric === "network") return t("report.networkRecommendation");
  return card.recommendation;
}

function reportInspectionText(value) {
  if (uiSettings.language !== "ko") return value;
  return reportInspectionKo[value] || value;
}

function airgapText(value) {
  if (uiSettings.language !== "ko") return value;
  const text = String(value ?? "");
  if (/^Drive #(\d+) - Match$/.test(text)) {
    return text.replace(/^Drive #(\d+) - Match$/, "드라이브 #$1 - 일치");
  }
  if (/^Backup Cycle #(\d+)$/.test(text)) {
    return text.replace(/^Backup Cycle #(\d+)$/, "백업 회차 #$1");
  }
  return airgapKo[text] || text;
}

function dashboardCardDescription(card) {
  const keyMap = {
    detect: "dashboard.detectDesc",
    warning: "dashboard.warningDesc",
    logs: "dashboard.logsDesc",
  };
  return keyMap[card.id] ? t(keyMap[card.id]) : card.description;
}

function localizedLogContent(content) {
  if (uiSettings.language !== "ko") return content;
  return String(content)
    .replaceAll("Threshold", "임계")
    .replace("rich.kim@oam.co.kr 계정 회원가입 완료", "rich.kim@oam.co.kr 계정 회원가입 완료");
}

function dashboardCopy() {
  if (uiSettings.language !== "ko") {
    return {
      protection: "Protection Status",
      normal: "Normal",
      airgap: "Air-Gap Status",
      active: "Active",
      storagePower: "Disk Offline",
      off: "Offline",
      lastBackup: "Last Backup",
      success: "Success",
      access: "Unauthorized Access",
      attempts: "0 Attempts",
      recent24h: "Last 24 hours",
      integrity: "Integrity Check",
      latest: "Latest",
      liveProtection: "Real-time Protection Status",
      repository: "Repository Status",
      backupLink: "Backup Integration Status",
      backupJobs: "Veeam Jobs",
      backupJobColumns: {
        name: "Name",
        type: "Type",
        objects: "Objects",
        status: "Status",
        lastRun: "Last Run",
        lastResult: "Last Result",
        nextRun: "Next Run",
        target: "Target",
        description: "Description",
      },
      event: "Recent Events",
      alert: "Warnings / Alerts",
      audit: "Audit Log Summary",
      policy: "Policy Summary",
      livePolling: "LIVE 1s",
      livePending: "SYNCING",
      liveStale: "STALE",
      liveError: "ERROR",
      liveUpdated: "Updated",
      protectedMessage: "Current backup storage is offline and external access is unavailable.",
      backupStart: "Backup completed detected",
      powerOn: "Storage online approved",
      backupRunning: "Backup running",
      backupEnd: "Backup completed",
      flush: "Flush verified",
      isolated: "Storage safe isolation",
      airgapActive: "Air-Gap activated",
      locked: "Locked",
      backuping: "Backing up",
      unused: "Unused",
      noCritical: "No critical alerts",
      csv: "CSV",
      pdf: "PDF",
      word: "Word",
      detail: "More",
    };
  }
  return {
    protection: "보호 상태",
    normal: "정상",
    airgap: "Air-Gap 상태",
    active: "활성",
    storagePower: "Disk Offline",
    off: "Offline",
    lastBackup: "마지막 백업",
    success: "성공",
    access: "비인가 접근 시도",
    attempts: "0건",
    recent24h: "최근 24시간",
    integrity: "무결성 검증",
    latest: "최근",
    liveProtection: "실시간 보호 현황",
    repository: "Repository 상태",
    backupLink: "백업 연동 상태",
    backupJobs: "Veeam Jobs",
    backupJobColumns: {
      name: "Name",
      type: "Type",
      objects: "Objects",
      status: "Status",
      lastRun: "Last Run",
      lastResult: "Last Result",
      nextRun: "Next Run",
      target: "Target",
      description: "Description",
    },
    event: "최근 이벤트",
    alert: "경고 / 알림",
    audit: "감사 로그 요약",
    policy: "정책 설정 요약",
    livePolling: "LIVE 1초",
    livePending: "갱신 중",
    liveStale: "지연",
    liveError: "오류",
    liveUpdated: "갱신",
    protectedMessage: "현재 백업 저장소는 Offline 상태로 외부 접근이 불가능합니다.",
    backupStart: "백업 완료 감지",
    powerOn: "승인 기반 온라인",
    backupRunning: "백업 진행",
    backupEnd: "백업 종료",
    flush: "Flush 확인",
    isolated: "저장장치 안전 분리",
    airgapActive: "Air-Gap 활성화",
    locked: "잠김",
    backuping: "백업 중",
    unused: "미사용",
    noCritical: "현재 긴급 경고 없음",
    csv: "CSV",
    pdf: "PDF",
    word: "Word",
    detail: "더보기",
  };
}

function dashboardKpiLabel(icon, label, copy) {
  const key = String(icon || "");
  const labelMap = {
    "data-protection-logo": copy.protection,
    "airgap-logo": copy.airgap,
    "storage-power": copy.storagePower,
    "veeam-backup-completed": copy.lastBackup,
    "integrity-logo": copy.integrity,
  };
  if (labelMap[key]) return labelMap[key];
  if (uiSettings.language !== "ko") return label || "-";
  return ({
    "Data Protection": copy.protection,
    "Protection Status": copy.protection,
    "Air-Gap": copy.airgap,
    "Air-Gap Status": copy.airgap,
    "Disk Offline": copy.storagePower,
    "Last Backup": copy.lastBackup,
    "LOCK-FIX State": copy.integrity,
    "Integrity Check": copy.integrity,
  })[label] || label || "-";
}

function dashboardKpiTone(normalized, value) {
  const display = String(value || "").trim().toUpperCase();
  if (normalized === "OFFLINE" || display === "오프라인" || display === "OFFLINE") return "red";
  if (normalized === "ISOLATED" || display === "격리됨" || display === "ISOLATED") return "orange";
  if (
    ["SUCCESS", "NORMAL", "OK", "OFFLINE_COMPLETE"].includes(normalized)
    || ["정상", "성공", "격리 완료", "NORMAL", "SUCCESS", "OFFLINE COMPLETE"].includes(display)
  ) {
    return "green";
  }
  return "dark";
}

function dashboardKpiStatus(item, copy) {
  const rawValue = String(item.value ?? "").trim();
  const normalized = rawValue.toUpperCase().replace(/[\s-]+/g, "_");
  const isKo = uiSettings.language === "ko";
  const commonMap = isKo
    ? {
      SUCCESS: "성공",
      COMPLETED: "완료",
      COMPLETE: "완료",
      NORMAL: "정상",
      OK: "정상",
      ACTIVE: "활성",
      ISOLATED: "격리됨",
      OFFLINE: "오프라인",
      ONLINE: "온라인",
      UNKNOWN: "확인 중",
      CHECKING: "확인 중",
      WAITING: "대기",
      WAITING_FOR_NEW_BACKUP: "백업 대기",
      WAITING_DISK: "디스크 대기",
      ONLINE_VERIFIED_RW: "검증 완료",
      ONLINE_VERIFIED: "검증 완료",
      OFFLINE_COMPLETE: "격리 완료",
      OFFLINE_FAILED: "확인 필요",
    }
    : {
      SUCCESS: "Success",
      COMPLETED: "Complete",
      COMPLETE: "Complete",
      NORMAL: "Normal",
      OK: "OK",
      ACTIVE: "Active",
      ISOLATED: "Isolated",
      OFFLINE: "Offline",
      ONLINE: "Online",
      UNKNOWN: "Checking",
      CHECKING: "Checking",
      WAITING: "Waiting",
      WAITING_FOR_NEW_BACKUP: "Backup Waiting",
      WAITING_DISK: "Disk Waiting",
      ONLINE_VERIFIED_RW: "Verified",
      ONLINE_VERIFIED: "Verified",
      OFFLINE_COMPLETE: "Offline Complete",
      OFFLINE_FAILED: "Needs Check",
    };
  const icon = String(item.icon || "");
  let value = commonMap[normalized] || rawValue || "-";
  let tone = item.tone || "dark";
  let detail = "";
  if (icon === "data-protection-logo" && normalized === "SUCCESS") {
    value = isKo ? "정상" : "Success";
  }
  if (icon === "veeam-backup-completed" && normalized === "SUCCESS") {
    value = isKo ? "성공" : "Success";
  }
  if (icon === "integrity-logo" && normalized === "ONLINE_VERIFIED_RW") {
    detail = "RW";
  }
  tone = dashboardKpiTone(normalized, value);
  return { value, tone, detail, rawValue };
}

function dashboardKpiDisplay(item, copy) {
  const status = dashboardKpiStatus(item, copy);
  return {
    ...item,
    label: dashboardKpiLabel(item.icon, item.label, copy),
    value: status.value,
    tone: status.tone,
    detail: status.detail,
    rawValue: status.rawValue,
  };
}

function editableReportField(field, value, placeholder) {
  return `<input class="report-edit-input" data-report-field="${field}" value="${escapeHtml(value === "-" ? "" : value)}" placeholder="${placeholder}" />`;
}

function cleanDisplayText(value) {
  return String(value ?? "")
    .replace(/\uFFFD+/g, " [확인 불가 문자 제거] ")
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, " ")
    .replace(/(?:\s*\[확인 불가 문자 제거\]\s*)+/g, " [확인 불가 문자 제거] ")
    .replace(/\s+/g, " ")
    .trim();
}

function escapeHtml(value) {
  return cleanDisplayText(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function keepContentAreaScroll() {
  const page = document.scrollingElement || document.documentElement;
  const pageTop = page?.scrollTop || window.scrollY || 0;
  const pageLeft = page?.scrollLeft || window.scrollX || 0;
  const areaTop = contentArea?.scrollTop || 0;
  const areaLeft = contentArea?.scrollLeft || 0;
  const restore = () => {
    if (contentArea) {
      contentArea.scrollTop = areaTop;
      contentArea.scrollLeft = areaLeft;
    }
    if (page) {
      page.scrollTop = pageTop;
      page.scrollLeft = pageLeft;
    }
    if (typeof window.scrollTo === "function") {
      window.scrollTo(pageLeft, pageTop);
    }
  };
  return () => {
    restore();
    if (typeof requestAnimationFrame === "function") {
      requestAnimationFrame(() => {
        restore();
        requestAnimationFrame(restore);
      });
    }
  };
}

function friendlyEmergencyError(error) {
  const text = cleanDisplayText(error?.message || error || "");
  if (/repair-volume/i.test(text) && /not supported|43001/i.test(text)) {
    return "해당 파일시스템은 Repair-Volume 검사를 지원하지 않아 검사를 건너뛰고 재연결 상태를 다시 확인합니다.";
  }
  if (/401|unauthorized|인증|auth/i.test(text)) {
    return "긴급 접속 상태 확인 인증이 만료되었습니다. 현재 화면에서 다시 로그인한 뒤 로그를 확인하세요.";
  }
  if (text) return text;
  return "긴급 접속 상태 확인 응답을 받지 못했습니다. WebUI 서비스와 LOCK-FIX Agent/Service 상태를 확인하세요.";
}

async function saveReportCustomerFields() {
  const contact = document.querySelector('[data-report-field="customer_contact"]')?.value || "";
  const email = document.querySelector('[data-report-field="customer_email"]')?.value || "";
  try {
    const payload = await requestJson("/api/report/customer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customer_contact: contact,
        customer_email: email,
      }),
    });
    if (latestReportData) {
      latestReportData.customer.customer_contact = payload.customer.customer_contact;
      latestReportData.customer.customer_email = payload.customer.customer_email;
    }
  } catch (error) {
    console.warn("report customer save failed", error);
  }
}

let reportExtrasSaveTimer = null;

function reportSignatureValue(canvasId) {
  return localStorage.getItem(`lockfix.signature.${canvasId}`) || "";
}

function scheduleReportExtrasSave() {
  clearTimeout(reportExtrasSaveTimer);
  reportExtrasSaveTimer = setTimeout(saveReportExtras, 250);
}

async function saveReportExtras() {
  const opinionInput = document.querySelector("#engineerOpinionInput");
  try {
    await requestJson("/api/report/extras", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        engineer_opinion: opinionInput?.value || "",
        engineer_signature: reportSignatureValue("engineerSignaturePad"),
        manager_signature: reportSignatureValue("managerSignaturePad"),
      }),
    });
  } catch (error) {
    console.warn("report extras save failed", error);
  }
}

function setupReportOpinion() {
  const opinionInput = document.querySelector("#engineerOpinionInput");
  if (!opinionInput) return;
  opinionInput.value = localStorage.getItem("lockfix.engineerOpinion") || "";
  opinionInput.addEventListener("input", () => {
    localStorage.setItem("lockfix.engineerOpinion", opinionInput.value);
    scheduleReportExtrasSave();
  });
}

let activeSignatureCanvas = null;
let activeSignatureStorageKey = "";

function drawSignatureSourceToCanvas(canvas, source, onDone) {
  if (!canvas || !source) return;
  const context = canvas.getContext("2d");
  const img = new Image();
  img.onload = () => {
    context.clearRect(0, 0, canvas.width, canvas.height);
    const scale = Math.min(canvas.width / img.width, canvas.height / img.height);
    const width = img.width * scale;
    const height = img.height * scale;
    const x = (canvas.width - width) / 2;
    const y = (canvas.height - height) / 2;
    context.drawImage(img, x, y, width, height);
    if (onDone) onDone();
  };
  img.src = source;
}

function clearSignatureCanvas(canvas) {
  if (!canvas) return;
  canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
}

function closeSignatureDrawModal() {
  signatureDrawModal?.classList.add("hidden");
  activeSignatureCanvas = null;
  activeSignatureStorageKey = "";
}

function openSignatureDrawModal(canvas, storageKey) {
  if (!signatureDrawModal || !signatureDrawPad || !canvas) return;
  activeSignatureCanvas = canvas;
  activeSignatureStorageKey = storageKey;
  clearSignatureCanvas(signatureDrawPad);
  const titleKey = canvas.id === "engineerSignaturePad" ? "report.engineerSignature" : "report.managerSignature";
  if (signatureDrawTitle) signatureDrawTitle.textContent = t(titleKey);
  const existingImage = localStorage.getItem(storageKey) || "";
  if (existingImage) drawSignatureSourceToCanvas(signatureDrawPad, existingImage);
  signatureDrawModal.classList.remove("hidden");
}

function setupSignatureDrawModal() {
  if (!signatureDrawPad || signatureDrawPad.dataset.ready === "true") return;
  const context = signatureDrawPad.getContext("2d");
  let drawing = false;
  let lastPoint = null;

  function pointFor(event) {
    const rect = signatureDrawPad.getBoundingClientRect();
    const pointer = event.touches?.[0] || event;
    return {
      x: ((pointer.clientX - rect.left) / rect.width) * signatureDrawPad.width,
      y: ((pointer.clientY - rect.top) / rect.height) * signatureDrawPad.height,
    };
  }

  function drawTo(point) {
    context.lineWidth = 4;
    context.lineCap = "round";
    context.lineJoin = "round";
    context.strokeStyle = "#17212b";
    context.beginPath();
    context.moveTo(lastPoint.x, lastPoint.y);
    context.lineTo(point.x, point.y);
    context.stroke();
    lastPoint = point;
  }

  function start(event) {
    event.preventDefault();
    drawing = true;
    lastPoint = pointFor(event);
  }

  function move(event) {
    if (!drawing) return;
    event.preventDefault();
    drawTo(pointFor(event));
  }

  function end() {
    drawing = false;
    lastPoint = null;
  }

  signatureDrawPad.addEventListener("mousedown", start);
  signatureDrawPad.addEventListener("mousemove", move);
  window.addEventListener("mouseup", end);
  signatureDrawPad.addEventListener("touchstart", start, { passive: false });
  signatureDrawPad.addEventListener("touchmove", move, { passive: false });
  signatureDrawPad.addEventListener("touchend", end);
  signatureDrawClear?.addEventListener("click", () => clearSignatureCanvas(signatureDrawPad));
  signatureDrawCancel?.addEventListener("click", closeSignatureDrawModal);
  signatureDrawClose?.addEventListener("click", closeSignatureDrawModal);
  signatureDrawModal?.addEventListener("click", (event) => {
    if (event.target === signatureDrawModal) closeSignatureDrawModal();
  });
  signatureDrawUpload?.addEventListener("click", () => {
    if (!activeSignatureCanvas || !activeSignatureStorageKey) return;
    const targetContext = activeSignatureCanvas.getContext("2d");
    targetContext.clearRect(0, 0, activeSignatureCanvas.width, activeSignatureCanvas.height);
    targetContext.drawImage(signatureDrawPad, 0, 0, activeSignatureCanvas.width, activeSignatureCanvas.height);
    localStorage.setItem(activeSignatureStorageKey, activeSignatureCanvas.toDataURL("image/png"));
    scheduleReportExtrasSave();
    closeSignatureDrawModal();
  });
  signatureDrawPad.dataset.ready = "true";
}

function setupSignaturePad(canvas) {
  if (!canvas) return;
  const storageKey = `lockfix.signature.${canvas.id}`;
  const context = canvas.getContext("2d");
  let drawing = false;
  let lastPoint = null;

  function restore() {
    const image = localStorage.getItem(storageKey);
    context.clearRect(0, 0, canvas.width, canvas.height);
    if (!image) return;
    const img = new Image();
    img.onload = () => context.drawImage(img, 0, 0, canvas.width, canvas.height);
    img.src = image;
  }

  function pointFor(event) {
    const rect = canvas.getBoundingClientRect();
    const pointer = event.touches?.[0] || event;
    return {
      x: ((pointer.clientX - rect.left) / rect.width) * canvas.width,
      y: ((pointer.clientY - rect.top) / rect.height) * canvas.height,
    };
  }

  function drawTo(point) {
    context.lineWidth = 3.2;
    context.lineCap = "round";
    context.lineJoin = "round";
    context.strokeStyle = "#17212b";
    context.beginPath();
    context.moveTo(lastPoint.x, lastPoint.y);
    context.lineTo(point.x, point.y);
    context.stroke();
    lastPoint = point;
  }

  function start(event) {
    event.preventDefault();
    drawing = true;
    lastPoint = pointFor(event);
  }

  function move(event) {
    if (!drawing) return;
    event.preventDefault();
    drawTo(pointFor(event));
  }

  function end() {
    if (!drawing) return;
    drawing = false;
    lastPoint = null;
    localStorage.setItem(storageKey, canvas.toDataURL("image/png"));
    scheduleReportExtrasSave();
  }

  canvas.addEventListener("mousedown", start);
  canvas.addEventListener("mousemove", move);
  window.addEventListener("mouseup", end);
  canvas.addEventListener("touchstart", start, { passive: false });
  canvas.addEventListener("touchmove", move, { passive: false });
  canvas.addEventListener("touchend", end);
  document.querySelector(`[data-signature-clear="${canvas.id}"]`)?.addEventListener("click", () => {
    context.clearRect(0, 0, canvas.width, canvas.height);
    localStorage.removeItem(storageKey);
    scheduleReportExtrasSave();
  });
  document.querySelector(`[data-signature-open="${canvas.id}"]`)?.addEventListener("click", () => {
    openSignatureDrawModal(canvas, storageKey);
  });
  restore();
}

function setupReportSignatures() {
  setupReportOpinion();
  setupSignatureDrawModal();
  setupSignaturePad(document.querySelector("#engineerSignaturePad"));
  setupSignaturePad(document.querySelector("#managerSignaturePad"));
}

function updateReportExportLinks() {
  const lang = uiSettings.language === "ko" ? "ko" : "en";
  [
    [".report-export-excel", "/api/report.xlsx"],
    [".report-export-pdf", "/api/report.pdf"],
    [".report-export-word", "/api/report.docx"],
  ].forEach(([selector, basePath]) => {
    const link = document.querySelector(selector);
    if (!link) return;
    link.href = `${basePath}?lang=${encodeURIComponent(lang)}`;
  });
}

function applyUiSettings() {
  document.documentElement.dataset.theme = uiSettings.theme;
  document.documentElement.lang = uiSettings.language === "ko" ? "ko" : "en";
  pendingUiSettings = { ...uiSettings };
  if (languageSelect) languageSelect.value = pendingUiSettings.language;
  if (themeSelect) themeSelect.value = pendingUiSettings.theme;
  if (logRetentionSelect) logRetentionSelect.value = String(logsRange.retention);
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    node.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  });
  document.querySelectorAll("[data-i18n-title]").forEach((node) => {
    node.setAttribute("title", t(node.dataset.i18nTitle));
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((node) => {
    node.setAttribute("aria-label", t(node.dataset.i18nAriaLabel));
  });
  applySidebarTooltips();
  renderSidebarUserMenu();
  updateReportExportLinks();
}

function renderNotificationSettings(settings = {}) {
  if (notificationChannel) notificationChannel.value = "SMTP";
  if (notificationTargetEmail) notificationTargetEmail.value = settings.target_email || "";
  if (notificationSmtpHost) notificationSmtpHost.value = settings.smtp_host || "";
  if (notificationSmtpPort) notificationSmtpPort.value = settings.smtp_port || 587;
  if (notificationSmtpFrom) notificationSmtpFrom.value = settings.smtp_from || "";
  if (notificationSmtpUser) notificationSmtpUser.value = settings.smtp_user || "";
  if (notificationSmtpPassword) {
    notificationSmtpPassword.value = "";
    notificationSmtpPassword.placeholder = settings.password_configured
      ? (uiSettings.language === "ko" ? "저장된 비밀번호 유지" : "Keep saved password")
      : (uiSettings.language === "ko" ? "SMTP 비밀번호" : "SMTP password");
  }
  if (notificationUseTls) notificationUseTls.checked = settings.use_tls !== false;
  if (notificationUseSsl) notificationUseSsl.checked = Boolean(settings.use_ssl);
}

async function loadNotificationSettings() {
  if (!notificationTargetEmail) return;
  const data = await requestJson("/api/notification-settings");
  renderNotificationSettings(data);
}

async function saveNotificationSettings() {
  if (!notificationTargetEmail) return null;
  return requestJson("/api/notification-settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      enabled: true,
      channel: "SMTP",
      target_email: notificationTargetEmail.value.trim(),
      smtp_host: notificationSmtpHost?.value.trim() || "",
      smtp_port: Number(notificationSmtpPort?.value || 587),
      smtp_from: notificationSmtpFrom?.value.trim() || "",
      smtp_user: notificationSmtpUser?.value.trim() || "",
      smtp_password: notificationSmtpPassword?.value || "",
      use_tls: Boolean(notificationUseTls?.checked),
      use_ssl: Boolean(notificationUseSsl?.checked),
    }),
  });
}

function applySidebarTooltips() {
  document.querySelectorAll(".side-item[data-view]").forEach((item) => {
    const label = item.querySelector("span:not(.nav-icon)")?.textContent?.trim() || "";
    if (label) {
      item.dataset.tooltip = label;
      item.setAttribute("aria-label", label);
    }
  });
}

function permissionSet(session = currentSession) {
  return new Set(Array.isArray(session?.permissions) ? session.permissions : []);
}

function hasPermission(permission, session = currentSession) {
  if (!permission) return true;
  return permissionSet(session).has(permission);
}

function hasAnyPermission(permissions, session = currentSession) {
  const required = Array.isArray(permissions) ? permissions : [];
  return required.length === 0 || required.some((permission) => hasPermission(permission, session));
}

function menuDefinitionFor(view) {
  return menuDefinitions.find((item) => item.view === view);
}

function canAccessView(view, session = currentSession) {
  const definition = menuDefinitionFor(view);
  if (!definition) return false;
  if (definition.roles?.length && !definition.roles.includes(session?.role)) {
    return false;
  }
  if (definition.permissions?.length && !definition.permissions.every((permission) => hasPermission(permission, session))) {
    return false;
  }
  return hasAnyPermission(definition.anyPermissions || [], session);
}

function visibleMenuDefinitions(session = currentSession) {
  return menuDefinitions.filter((definition) => canAccessView(definition.view, session));
}

function firstAllowedView(session = currentSession) {
  return visibleMenuDefinitions(session)[0]?.view || "accessDenied";
}

function defaultLandingView(session = currentSession) {
  return canAccessView("monitoring", session) ? "monitoring" : firstAllowedView(session);
}

function applyMenuVisibility() {
  const allowedViews = new Set(visibleMenuDefinitions().map((item) => item.view));
  const visibleSections = new Set();
  document.querySelectorAll(".side-item[data-view]").forEach((item) => {
    const view = item.dataset.view || "";
    if (view === "logout") {
      item.hidden = false;
      return;
    }
    const isRbacMenu = item.classList.contains("rbac-menu");
    const isVisible = isRbacMenu && allowedViews.has(view);
    item.hidden = !isVisible;
    if (isVisible && item.dataset.menuSection) {
      visibleSections.add(item.dataset.menuSection);
    }
  });
  document.querySelectorAll(".side-section-label[data-menu-section]").forEach((label) => {
    label.hidden = !visibleSections.has(label.dataset.menuSection);
  });
  settingsShortcutItems.forEach((item) => {
    item.hidden = !allowedViews.has(item.dataset.settingsView || "");
  });
  applySidebarTooltips();
}

function showAccessDenied(view) {
  sideItems.forEach((item) => item.classList.remove("active"));
  hideAllViews();
  if (appRoot) appRoot.dataset.activeView = "accessDenied";
  const denied = document.querySelector("#accessDeniedView");
  if (accessDeniedMessage) {
    accessDeniedMessage.textContent = `Access denied for ${menuDefinitionFor(view)?.label || view}. Required permission is missing.`;
  }
  activateViewElement(denied);
  contentArea?.scrollTo({ top: 0, left: 0 });
}

function hideAllViews() {
  views.forEach((view) => {
    view.classList.remove("view-active");
    view.hidden = true;
    view.setAttribute("aria-hidden", "true");
  });
}

function activateViewElement(view) {
  if (!view) return;
  view.hidden = false;
  view.removeAttribute("aria-hidden");
  view.classList.add("view-active");
}

function initialRouteView() {
  const candidate = decodeURIComponent(String(window.location.hash || "").replace(/^#/, "")).trim();
  if (candidate && menuDefinitionFor(candidate)) return candidate;
  return defaultLandingView();
}

function applySidebarState() {
  appRoot?.classList.toggle("sidebar-collapsed", sidebarCollapsed);
  sidebarToggle?.setAttribute("aria-expanded", String(!sidebarCollapsed));
  sidebarToggle?.setAttribute("aria-label", sidebarCollapsed ? "사이드바 열기" : "사이드바 닫기");
  sidebarToggle?.setAttribute("title", sidebarCollapsed ? "사이드바 열기" : "사이드바 닫기");
}

function departmentDisplayName(departmentId) {
  const id = String(departmentId || "").trim();
  if (!id) return "-";
  const key = {
    management: "department.management",
    security: "department.security",
    "backup-operation": "department.backupOperation",
    "hardware-control": "department.hardwareControl",
    audit: "department.audit",
    development: "department.development",
    "web-design": "department.webDesign",
  }[id];
  return key ? t(key) : USER_MANAGEMENT_DEFAULT_DEPARTMENTS.find((department) => department.id === id)?.name || id;
}

function sidebarUserInitials(userText) {
  const clean = String(userText || "").trim();
  if (!clean) return "ID";
  const localPart = clean.includes("@") ? clean.split("@")[0] : clean;
  const parts = localPart.split(/[._\-\s]+/).filter(Boolean);
  const initials = (parts.length > 1 ? parts[0][0] + parts[1][0] : localPart.slice(0, 2)).toUpperCase();
  return initials || "ID";
}

function setSidebarUserPanel(open) {
  const expanded = Boolean(open);
  if (!sidebarUserToggle || !sidebarUserPanel) return;
  sidebarUserToggle.setAttribute("aria-expanded", String(expanded));
  sidebarUserPanel.hidden = !expanded;
  sidebarUserMenu?.classList.toggle("sidebar-user-open", expanded);
}

function renderSidebarUserMenu() {
  const loggedIn = Boolean(currentSession.authenticated);
  const userText = currentSession.userId || currentSession.user || "-";
  const roleText = currentSession.role || "-";
  const departmentText = departmentDisplayName(currentSession.departmentId);
  const statusText = loggedIn ? t("userMenu.loggedIn") : t("userMenu.loggedOut");
  if (sidebarUserAvatar) sidebarUserAvatar.textContent = sidebarUserInitials(userText);
  if (sidebarUserName) sidebarUserName.textContent = userText;
  if (sidebarUserRole) sidebarUserRole.textContent = roleText;
  if (sidebarUserStatus) sidebarUserStatus.textContent = statusText;
  if (sidebarUserId) sidebarUserId.textContent = userText;
  if (sidebarUserRoleDetail) sidebarUserRoleDetail.textContent = roleText;
  if (sidebarUserDepartment) sidebarUserDepartment.textContent = departmentText;
  if (sidebarUserToggle) {
    sidebarUserToggle.disabled = !loggedIn;
    sidebarUserToggle.setAttribute("aria-label", `${t("userMenu.title")}: ${userText}`);
    sidebarUserToggle.setAttribute("title", `${t("userMenu.title")}: ${userText}`);
  }
  if (!loggedIn) setSidebarUserPanel(false);
}

function toggleSidebar() {
  sidebarCollapsed = !sidebarCollapsed;
  localStorage.setItem("lockfix.sidebarCollapsed", String(sidebarCollapsed));
  applySidebarState();
  setSidebarUserPanel(false);
}

function getNetworkCardOrder() {
  try {
    const savedVersion = localStorage.getItem(NETWORK_CARD_ORDER_VERSION_KEY);
    if (savedVersion !== NETWORK_CARD_ORDER_VERSION) {
      return [...NETWORK_CARD_DEFAULT_ORDER];
    }
    const saved = JSON.parse(localStorage.getItem(NETWORK_CARD_ORDER_KEY) || "[]");
    const valid = Array.isArray(saved)
      ? saved.filter((id) => NETWORK_CARD_DEFAULT_ORDER.includes(id))
      : [];
    return [...valid, ...NETWORK_CARD_DEFAULT_ORDER.filter((id) => !valid.includes(id))];
  } catch {
    return [...NETWORK_CARD_DEFAULT_ORDER];
  }
}

function saveNetworkCardOrder() {
  if (!networkCardBoard) return;
  const order = [...networkCardBoard.querySelectorAll("[data-network-card]")]
    .map((card) => card.dataset.networkCard)
    .filter(Boolean);
  localStorage.setItem(NETWORK_CARD_ORDER_KEY, JSON.stringify(order));
  localStorage.setItem(NETWORK_CARD_ORDER_VERSION_KEY, NETWORK_CARD_ORDER_VERSION);
}

function applyNetworkCardOrder() {
  if (!networkCardBoard) return;
  const cardsById = new Map(
    [...networkCardBoard.querySelectorAll("[data-network-card]")]
      .map((card) => [card.dataset.networkCard, card])
  );
  getNetworkCardOrder().forEach((id) => {
    const card = cardsById.get(id);
    if (card) networkCardBoard.appendChild(card);
  });
  if (localStorage.getItem(NETWORK_CARD_ORDER_VERSION_KEY) !== NETWORK_CARD_ORDER_VERSION) {
    saveNetworkCardOrder();
  }
}

function getNetworkCardAfterElement(board, x, y) {
  const cards = [...board.querySelectorAll("[data-network-card]:not(.network-card-dragging)")];
  return cards.find((card) => {
    const box = card.getBoundingClientRect();
    const centerY = box.top + box.height / 2;
    return y < centerY;
  }) || null;
}

function setupNetworkCardDragDrop() {
  if (!networkCardBoard) return;
  applyNetworkCardOrder();
  const cards = [...networkCardBoard.querySelectorAll("[data-network-card]")];
  cards.forEach((card) => {
    card.draggable = false;
    const handle = card.querySelector(".network-card-drag-handle");
    if (!handle) return;
    handle.draggable = true;
    handle.addEventListener("dragstart", (event) => {
      card.classList.add("network-card-dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", card.dataset.networkCard || "");
    });
    handle.addEventListener("dragend", () => {
      card.classList.remove("network-card-dragging");
      networkCardBoard.classList.remove("network-card-board-active");
      saveNetworkCardOrder();
    });
  });
  networkCardBoard.addEventListener("dragover", (event) => {
    event.preventDefault();
    networkCardBoard.classList.add("network-card-board-active");
    const draggingCard = networkCardBoard.querySelector(".network-card-dragging");
    if (!draggingCard) return;
    const afterCard = getNetworkCardAfterElement(networkCardBoard, event.clientX, event.clientY);
    networkCardBoard.insertBefore(draggingCard, afterCard);
  });
  networkCardBoard.addEventListener("drop", (event) => {
    event.preventDefault();
    networkCardBoard.classList.remove("network-card-board-active");
    saveNetworkCardOrder();
  });
}

async function applyPendingUiSettings() {
  uiSettings = { ...pendingUiSettings };
  localStorage.setItem("lockfix.language", uiSettings.language);
  localStorage.setItem("lockfix.theme", uiSettings.theme);
  logsRange.retention = Number(logRetentionSelect?.value || logsRange.retention || 30);
  logsRange.page = 1;
  localStorage.setItem("lockfix.logRetentionDays", String(logsRange.retention));
  try {
    await saveNotificationSettings();
    applyUiSettings();
    settingsApplyStatus.textContent = t("settings.notificationSaved");
    if (latestMonitoringData) {
      renderMonitoring(latestMonitoringData);
    }
    if (latestReportData) {
      renderReport(latestReportData);
    }
    if (latestSourcesData) {
      renderSources(latestSourcesData);
    }
    if (latestDashboardData) {
      renderDashboard(latestDashboardData);
    }
    if (latestUserManagementData.users.length || latestUserManagementData.departments.length || latestUserManagementData.windowsAdminStatus) {
      renderUserManagement(latestUserManagementData);
    }
    reloadLogs().catch((error) => console.warn("Unable to reload logs after retention change", error));
    reloadNotification().catch((error) => console.warn("Unable to reload notification view after settings change", error));
  } catch (error) {
    settingsApplyStatus.textContent = error.message || "Notification settings save failed.";
  }
}

function liveRequestUrl(url) {
  const separator = String(url).includes("?") ? "&" : "?";
  const liveParam = String(url).includes("live=1") ? "" : "live=1&";
  return `${url}${separator}${liveParam}_=${Date.now()}`;
}

async function requestJson(url, options = {}) {
  const timeoutMs = Number(options.timeoutMs || 15000);
  const fetchOptions = { ...options };
  const liveRequest = Boolean(fetchOptions.live);
  delete fetchOptions.timeoutMs;
  delete fetchOptions.live;
  if (liveRequest) {
    url = liveRequestUrl(url);
    fetchOptions.cache = "no-store";
    const headers = new Headers(fetchOptions.headers || {});
    headers.set("Cache-Control", "no-store");
    headers.set("Pragma", "no-cache");
    fetchOptions.headers = headers;
  }
  const controller = new AbortController();
  const timeoutId = Number.isFinite(timeoutMs) && timeoutMs > 0
    ? window.setTimeout(() => controller.abort(), timeoutMs)
    : 0;
  let response;
  try {
    response = await fetch(url, { credentials: "same-origin", ...fetchOptions, signal: fetchOptions.signal || controller.signal });
  } catch (error) {
    const aborted = error?.name === "AbortError";
    const message = aborted
      ? "요청 시간이 초과되었습니다. 최신 상태를 다시 확인 중입니다."
      : window.location.protocol === "file:"
      ? "현재 화면이 파일로 직접 열려 있어 WebUI 서버 API에 연결할 수 없습니다. http://127.0.0.1:8088 또는 실행 중인 WebUI 주소로 접속하세요."
      : "WebUI 서버에 연결하지 못했습니다. LOCK-FIX WebUI/Python 서버가 실행 중인지 확인하세요.";
    const networkError = new Error(message);
    networkError.cause = error;
    networkError.code = aborted ? "REQUEST_TIMEOUT" : "NETWORK_UNREACHABLE";
    throw networkError;
  } finally {
    if (timeoutId) window.clearTimeout(timeoutId);
  }
  const payload = await response.json();
  if (!response.ok) {
    const message = payload.error || (response.status === 401 ? "로그인 세션이 만료되었습니다. 다시 로그인 후 승인 요청을 등록하세요." : "request failed");
    if (response.status === 401 && url !== "/api/session") {
      setAuthenticated(false);
    }
    const error = new Error(message);
    error.status = response.status;
    if (response.status === 401) error.code = "UNAUTHENTICATED";
    error.payload = payload;
    throw error;
  }
  return payload;
}

function activeViewId() {
  return document.querySelector(".view.view-active")?.id || "";
}

function shouldRunGlobalRefresh() {
  if (!currentSession.authenticated || appRoot.classList.contains("app-locked")) return false;
  if (approvalActionInProgress) return false;
  return !REALTIME_VIEW_IDS.has(activeViewId());
}

async function checkSession() {
  const session = await requestJson("/api/session");
  currentSession = {
    authenticated: Boolean(session.authenticated),
    user: session.user || "",
    role: session.role || "",
    userId: session.userId || "",
    departmentId: session.departmentId || "",
    passwordChangeRequired: Boolean(session.passwordChangeRequired),
    permissions: Array.isArray(session.permissions) ? session.permissions : [],
  };
  applyMenuVisibility();
  renderSidebarUserMenu();
  setAuthenticated(session.authenticated);
  if (session.authenticated) {
    renderLicenseStatus(session.license);
    updateLicenseGate(session.license);
    showView(initialRouteView());
    refreshAllInBackground("session bootstrap");
  }
}

function setAuthenticated(authenticated) {
  loginScreen.classList.toggle("login-hidden", authenticated);
  appRoot.classList.toggle("app-locked", !authenticated);
  loginSplash.classList.add("hidden");
  if (!authenticated) {
    resetQrLoginState();
    setAirGapLivePolling(false);
    setEmergencyReconnectLivePolling(false);
    setVeeamLivePolling(false);
    licenseModal.classList.add("hidden");
    currentSession = { authenticated: false, user: "", role: "", userId: "", departmentId: "", passwordChangeRequired: false, permissions: [] };
    applyMenuVisibility();
    renderSidebarUserMenu();
  }
  if (authenticated) {
    stopQrTimers();
  }
  if (!authenticated) {
    loginPassword.focus();
  }
}

async function showLoginSplashThenEnter() {
  loginScreen.classList.add("login-hidden");
  appRoot.classList.add("app-locked");
  loginSplash.classList.remove("hidden");
  stopQrTimers();
  const session = await requestJson("/api/session");
  currentSession = {
    authenticated: Boolean(session.authenticated),
    user: session.user || "",
    role: session.role || "",
    userId: session.userId || "",
    departmentId: session.departmentId || "",
    passwordChangeRequired: Boolean(session.passwordChangeRequired),
    permissions: Array.isArray(session.permissions) ? session.permissions : [],
  };
  applyMenuVisibility();
  renderSidebarUserMenu();
  refreshAllInBackground("login bootstrap");
  await new Promise((resolve) => setTimeout(resolve, LOGIN_SPLASH_DURATION_MS));
  setAuthenticated(true);
  showView(initialRouteView());
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
    if (payload.authenticated) {
      await showLoginSplashThenEnter();
      if (payload.passwordChangeRequired) {
        await promptForRequiredPasswordChange();
      }
    } else {
      setAuthenticated(false);
    }
  } catch (error) {
    loginError.textContent = error.message || "Account or password is not valid.";
  }
}

async function promptForRequiredPasswordChange() {
  const first = window.prompt(t("account.newPasswordPrompt"), "");
  if (!first) {
    window.alert(t("account.passwordChangeRequired"));
    return;
  }
  const second = window.prompt(t("account.confirmPasswordPrompt"), "");
  if (first !== second) {
    window.alert(t("account.passwordMismatch"));
    return;
  }
  await requestJson("/api/account/password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ newPassword: first }),
  });
  window.alert(t("account.passwordChanged"));
  const session = await requestJson("/api/session");
  currentSession = {
    authenticated: Boolean(session.authenticated),
    user: session.user || "",
    role: session.role || "",
    userId: session.userId || "",
    departmentId: session.departmentId || "",
    passwordChangeRequired: Boolean(session.passwordChangeRequired),
    permissions: Array.isArray(session.permissions) ? session.permissions : [],
  };
  renderSidebarUserMenu();
}

async function logout() {
  resetQrLoginState();
  try {
    await requestJson("/api/logout", { method: "POST" });
  } catch (error) {
    console.warn("Logout request failed; clearing local session state.", error);
  } finally {
    setSidebarUserPanel(false);
    setAuthenticated(false);
    if (window.location.hash) history.replaceState(null, "", window.location.pathname || "/");
  }
}

async function switchAccount() {
  await logout();
  loginEmail?.focus();
}

function openAccountGuide() {
  accountGuideModal?.classList.remove("hidden");
  accountGuideOk?.focus();
}

function closeAccountGuide() {
  accountGuideModal?.classList.add("hidden");
  registerAccountButton?.focus();
}

function openAirgapConfirmation(requestId = "") {
  pendingAirgapConfirmationRequestId = String(requestId || "");
  airgapConfirmModal?.classList.remove("hidden");
  airgapConfirmOk?.focus();
}

function closeAirgapConfirmation() {
  pendingAirgapConfirmationRequestId = "";
  airgapConfirmModal?.classList.add("hidden");
}

function maybeOpenAirgapConfirmation(requestId) {
  const request = latestApprovalsData.requests.find((item) => String(item.id || "") === String(requestId || ""));
  if (!request || !isExecutionAllowedRequest(request)) return;
  openAirgapConfirmation(request.id);
}

function showView(name) {
  if (name === "logout") {
    logout();
    return;
  }
  const targetView = menuDefinitionFor(name) ? name : firstAllowedView();
  if (!canAccessView(targetView)) {
    showAccessDenied(targetView);
    if (window.location.hash !== `#${targetView}`) history.replaceState(null, "", `#${targetView}`);
    return;
  }
  sideItems.forEach((item) => item.classList.toggle("active", item.dataset.view === targetView));
  hideAllViews();
  if (appRoot) appRoot.dataset.activeView = targetView;
  const target = document.querySelector(`#${targetView}View`);
  if (target) {
    activateViewElement(target);
    contentArea?.scrollTo({ top: 0, left: 0 });
  }
  if (window.location.hash !== `#${targetView}`) history.replaceState(null, "", `#${targetView}`);
  setAirGapLivePolling(targetView === "sources");
  setDashboardLivePolling(targetView === "dashboard");
  setOpsOverviewLivePolling(targetView === "monitoring");
  if (targetView === "sources") {
    reloadSources().catch((error) => {
      console.warn("Unable to reload Air-Gap view", error);
      renderSources({ air_gap: fallbackAirGapSummary() });
    });
  }
  if (targetView === "dashboard") {
    reloadDashboard();
  }
  if (targetView === "detect2") {
    renderDetectFallback();
    reloadDetect();
  }
  if (targetView === "threat") {
    reloadThreatDetection().catch((error) => {
      console.warn("Unable to reload threat detection", error);
      renderThreatDetection({
        summary: { status: "확인 필요", score: "-", suspicious_count: 0, last_scan_at: "-", engine: "연결 확인 필요" },
        results: [],
        policy: { risk_action: "WebUI 서버/API 연결 확인 필요" },
      });
    });
  }
  if (targetView === "veeam") {
    reloadVeeamIntegration().catch((error) => {
      console.warn("Unable to reload Veeam Integration view", error);
      if (veeamIntegrationStatus) veeamIntegrationStatus.textContent = error.message;
    });
  }
  if (targetView === "userManagement") {
    reloadUserManagement().catch((error) => {
      console.warn("Unable to reload user management", error);
      renderUserManagement({ users: [], departments: [] }, error.message);
    });
  }
  if (targetView === "auditLogs") {
    reloadAuditLogs().catch((error) => {
      console.warn("Unable to reload audit logs", error);
      renderAuditLogs({ items: [] }, error.message);
    });
  }
  if (targetView === "report") {
    reloadReport().catch((error) => {
      console.warn("Unable to reload report view", error);
      reportAnalysis.textContent = error.message;
    });
  }
  if (targetView === "securityAudit") {
    renderSecurityAudit(latestAuditData);
  }
  if (targetView === "settings") {
    loadNotificationSettings().catch((error) => {
      console.warn("Unable to reload notification settings", error);
      if (settingsApplyStatus) settingsApplyStatus.textContent = error.message;
    });
    reloadSettingsShortcutStatus().catch((error) => {
      console.warn("Unable to reload settings shortcut status", error);
    });
    reloadServiceControlStatus().catch((error) => {
      console.warn("Unable to reload service status", error);
      if (serviceControlStatus) serviceControlStatus.textContent = error.message;
    });
    reloadServicePreflight().catch((error) => {
      console.warn("Unable to reload service preflight", error);
      if (servicePreflightStatus) servicePreflightStatus.textContent = error.message;
    });
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
    qrLoginButton.textContent = t("login.qrSubmit");
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
    await showLoginSplashThenEnter();
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
    await showLoginSplashThenEnter();
  }
}

function stopQrTimers() {
  clearInterval(qrPollTimer);
  clearInterval(qrClockTimer);
  qrPollTimer = null;
  qrClockTimer = null;
}

function resetQrLoginState() {
  stopQrTimers();
  qrToken = "";
  qrExpiresAt = 0;
  passwordLogin?.classList.remove("qr-hidden");
  qrLoginView?.classList.add("qr-hidden");
  if (qrLoginButton) qrLoginButton.textContent = t("login.qrSubmit");
  if (qrTimer) qrTimer.textContent = "04:59";
  qrCodeBox?.replaceChildren();
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

function loadDashboardKpiOrder() {
  try {
    const raw = localStorage.getItem(dashboardKpiOrderKey);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.map((item) => String(item || "")).filter(Boolean) : [];
  } catch {
    return [];
  }
}

function saveDashboardKpiOrder(order) {
  try {
    localStorage.setItem(dashboardKpiOrderKey, JSON.stringify(order));
  } catch {
    // Ignore storage failures in locked-down browser contexts.
  }
}

function loadDashboardKpiSizes() {
  try {
    const raw = localStorage.getItem(dashboardKpiSizeKey);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function saveDashboardKpiSizes(sizes) {
  try {
    localStorage.setItem(dashboardKpiSizeKey, JSON.stringify(sizes));
  } catch {
    // Ignore storage failures in locked-down browser contexts.
  }
}

function loadDashboardEventsVisible() {
  try {
    return localStorage.getItem(dashboardEventsKey) === "1";
  } catch {
    return false;
  }
}

function saveDashboardEventsVisible(visible) {
  try {
    localStorage.setItem(dashboardEventsKey, visible ? "1" : "0");
  } catch {
    // Ignore storage failures in locked-down browser contexts.
  }
}

function loadDashboardAlertsVisible() {
  try {
    return localStorage.getItem(dashboardAlertsKey) === "1";
  } catch {
    return false;
  }
}

function saveDashboardAlertsVisible(visible) {
  try {
    localStorage.setItem(dashboardAlertsKey, visible ? "1" : "0");
  } catch {
    // Ignore storage failures in locked-down browser contexts.
  }
}

function setDashboardRevealPanel(panel, button, visible, saveVisible) {
  if (!panel || !button) return;
  if (!visible) {
    panel.dataset.expandedRows = String(Math.max(3, Number(panel.dataset.rows || 3)));
  }
  const expandedRows = Math.max(3, Number(panel.dataset.expandedRows || panel.dataset.rows || 3));
  const isEventPanel = panel.classList.contains("event-panel");
  const isAlertPanel = panel.classList.contains("alert-panel");
  panel.classList.toggle("event-panel-visible", isEventPanel && visible);
  panel.classList.toggle("event-panel-hidden", isEventPanel && !visible);
  panel.classList.toggle("alert-panel-visible", isAlertPanel && visible);
  panel.classList.toggle("alert-panel-hidden", isAlertPanel && !visible);
  panel.dataset.rows = visible ? String(expandedRows) : "1";
  panel.style.minHeight = visible ? `${Math.max(234, expandedRows * 78)}px` : "46px";
  button.textContent = visible ? "Hide" : "More";
  button.setAttribute("aria-expanded", String(visible));
  saveVisible?.(visible);
}

function bindDashboardRevealToggles() {
  const eventsToggle = document.querySelector("#dashboardEventsToggle");
  const eventPanel = document.querySelector(".event-panel");
  const alertsToggle = document.querySelector("#dashboardAlertsToggle");
  const alertPanel = document.querySelector(".alert-panel");
  setDashboardRevealPanel(eventPanel, eventsToggle, Boolean(eventPanel?.classList.contains("event-panel-visible")));
  setDashboardRevealPanel(alertPanel, alertsToggle, Boolean(alertPanel?.classList.contains("alert-panel-visible")));
  eventsToggle?.addEventListener("click", () => {
    const visible = !eventPanel?.classList.contains("event-panel-visible");
    setDashboardRevealPanel(eventPanel, eventsToggle, visible, saveDashboardEventsVisible);
  });
  alertsToggle?.addEventListener("click", () => {
    const visible = !alertPanel?.classList.contains("alert-panel-visible");
    setDashboardRevealPanel(alertPanel, alertsToggle, visible, saveDashboardAlertsVisible);
  });
}

function loadOpsEventsVisible() {
  try {
    return localStorage.getItem(opsEventsVisibleKey) === "1";
  } catch {
    return false;
  }
}

function saveOpsEventsVisible(visible) {
  try {
    localStorage.setItem(opsEventsVisibleKey, visible ? "1" : "0");
  } catch {
    // Ignore storage failures in locked-down browser contexts.
  }
}

function updateOpsEventsVisibility(visible = loadOpsEventsVisible()) {
  const root = opsEventList?.closest(".ops-events");
  root?.classList.toggle("ops-events-visible", visible);
  root?.classList.toggle("ops-events-hidden", !visible);
  if (opsEventsToggle) {
    opsEventsToggle.textContent = visible ? "Hide" : "Show";
    opsEventsToggle.setAttribute("aria-expanded", String(visible));
  }
}

function reorderDashboardKpis(cards) {
  const order = loadDashboardKpiOrder();
  if (!order.length) return cards;
  const index = new Map(order.map((key, position) => [key, position]));
  return [...cards].sort((left, right) => {
    const leftIndex = index.has(left.key) ? index.get(left.key) : Number.POSITIVE_INFINITY;
    const rightIndex = index.has(right.key) ? index.get(right.key) : Number.POSITIVE_INFINITY;
    return leftIndex - rightIndex;
  });
}

function loadDashboardPanelOrder() {
  try {
    const raw = localStorage.getItem(dashboardPanelOrderKey);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.map((item) => String(item || "")).filter(Boolean) : [];
  } catch {
    return [];
  }
}

function saveDashboardPanelOrder(order) {
  try {
    localStorage.setItem(dashboardPanelOrderKey, JSON.stringify(order));
  } catch {
    // Ignore storage failures in locked-down browser contexts.
  }
}

function loadDashboardPanelSizes() {
  try {
    const raw = localStorage.getItem(dashboardPanelSizeKey);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveDashboardPanelSizes(sizes) {
  try {
    localStorage.setItem(dashboardPanelSizeKey, JSON.stringify(sizes));
  } catch {
    // Ignore storage failures in locked-down browser contexts.
  }
}

function clampDashboardPixels(value, min, max) {
  const number = Number(value);
  if (!Number.isFinite(number)) return min;
  return Math.max(min, Math.min(max, number));
}

function dashboardResizeBounds(board, defaults) {
  const boardWidth = board?.getBoundingClientRect?.().width || window.innerWidth || defaults.maxWidth;
  return {
    ...defaults,
    maxWidth: Math.max(defaults.minWidth, Math.min(defaults.maxWidth, Math.floor(boardWidth))),
  };
}

function dashboardSpanFromPixels(board, width, totalColumns, minSpan, maxSpan) {
  const boardWidth = Math.max(1, board?.getBoundingClientRect?.().width || window.innerWidth || width);
  const unitWidth = boardWidth / totalColumns;
  return Math.max(minSpan, Math.min(maxSpan, Math.ceil(width / unitWidth)));
}

function dashboardRowsFromPixels(height, rowHeight, minRows, maxRows) {
  return Math.max(minRows, Math.min(maxRows, Math.ceil(height / rowHeight)));
}

function enableDashboardKpiDrag(board) {
  if (!board || board.dataset.dragReady === "true") return;
  board.dataset.dragReady = "true";
  let dragging = null;
  let resizing = null;
  const sizes = loadDashboardKpiSizes();

  const syncOrder = () => {
    const order = [...board.querySelectorAll("[data-dashboard-kpi]")].map((item) => item.dataset.dashboardKpi || "").filter(Boolean);
    saveDashboardKpiOrder(order);
  };

  const applyCardSize = (card, size) => {
    if (!card || !size) return;
    const bounds = dashboardResizeBounds(board, { minWidth: 180, maxWidth: 560, minHeight: 128, maxHeight: 240 });
    const cols = Math.max(1, Math.min(3, Number(size.cols || card.dataset.cols || 1)));
    const rows = Math.max(1, Math.min(2, Number(size.rows || card.dataset.rows || 1)));
    card.dataset.cols = String(cols);
    card.dataset.rows = String(rows);
    card.style.gridColumnEnd = `span ${cols}`;
    card.style.gridRowEnd = `span ${rows}`;
    if (size.width) {
      card.dataset.width = String(clampDashboardPixels(size.width, bounds.minWidth, bounds.maxWidth));
      card.style.width = `${card.dataset.width}px`;
    }
    if (size.height) {
      card.dataset.height = String(clampDashboardPixels(size.height, bounds.minHeight, bounds.maxHeight));
      card.style.height = `${card.dataset.height}px`;
    }
  };

  const getCard = (target) => target?.closest?.("[data-dashboard-kpi]");

  board.addEventListener("dragstart", (event) => {
    const handle = event.target.closest?.(".dashboard-kpi-grip");
    if (!handle) return;
    const card = getCard(handle);
    if (!card) return;
    dragging = card;
    card.classList.add("dashboard-kpi-dragging");
    event.dataTransfer?.setData("text/plain", card.dataset.dashboardKpi || "");
    event.dataTransfer?.setDragImage(card, Math.min(80, card.clientWidth / 2), Math.min(40, card.clientHeight / 2));
  });

  board.addEventListener("dragend", () => {
    if (dragging) dragging.classList.remove("dashboard-kpi-dragging");
    dragging = null;
    board.querySelectorAll(".dashboard-kpi-drop-target").forEach((node) => node.classList.remove("dashboard-kpi-drop-target"));
    syncOrder();
  });

  board.addEventListener("dragover", (event) => {
    if (!dragging) return;
    event.preventDefault();
    const card = getCard(event.target);
    if (!card || card === dragging) return;
    const rect = card.getBoundingClientRect();
    const insertBefore = event.clientX < rect.left + rect.width / 2 || event.clientY < rect.top + rect.height / 2;
    board.querySelectorAll(".dashboard-kpi-drop-target").forEach((node) => node.classList.remove("dashboard-kpi-drop-target"));
    card.classList.add("dashboard-kpi-drop-target");
    if (insertBefore) {
      board.insertBefore(dragging, card);
    } else {
      board.insertBefore(dragging, card.nextSibling);
    }
  });

  board.addEventListener("drop", (event) => {
    if (!dragging) return;
    event.preventDefault();
    syncOrder();
  });

  board.querySelectorAll("[data-dashboard-kpi]").forEach((card) => {
    applyCardSize(card, sizes[card.dataset.dashboardKpi || ""]);
  });

  board.addEventListener("mousedown", (event) => {
    const handle = event.target.closest?.(".dashboard-kpi-resize-line");
    if (!handle) return;
    const card = handle.closest("[data-dashboard-kpi]");
    if (!card) return;
    event.preventDefault();
    const axis = handle.dataset.resizeAxis || "x";
    resizing = {
      card,
      axis,
      startX: event.clientX,
      startY: event.clientY,
      startWidth: card.getBoundingClientRect().width,
      startHeight: card.getBoundingClientRect().height,
      startCols: Number(card.dataset.cols || 1),
      startRows: Number(card.dataset.rows || 1),
    };
    board.classList.add(`dashboard-kpi-board-resizing-${axis}`);

    const onMouseMove = (event) => {
      if (!resizing) return;
      const dx = event.clientX - resizing.startX;
      const dy = event.clientY - resizing.startY;
      const bounds = dashboardResizeBounds(board, { minWidth: 180, maxWidth: 560, minHeight: 96, maxHeight: 220 });
      if (resizing.axis === "x") {
        const nextWidth = Math.round(clampDashboardPixels(resizing.startWidth + dx, bounds.minWidth, bounds.maxWidth));
        const nextCols = dashboardSpanFromPixels(board, nextWidth, 5, 1, 3);
        resizing.card.dataset.width = String(nextWidth);
        resizing.card.dataset.cols = String(nextCols);
        resizing.card.style.width = `${nextWidth}px`;
        resizing.card.style.gridColumnEnd = `span ${nextCols}`;
      } else {
        const nextHeight = Math.round(clampDashboardPixels(resizing.startHeight + dy, bounds.minHeight, bounds.maxHeight));
        const nextRows = dashboardRowsFromPixels(nextHeight, 108, 1, 2);
        resizing.card.dataset.height = String(nextHeight);
        resizing.card.dataset.rows = String(nextRows);
        resizing.card.style.height = `${nextHeight}px`;
        resizing.card.style.gridRowEnd = `span ${nextRows}`;
      }
    };

    const onMouseUp = () => {
      if (!resizing) {
        window.removeEventListener("mousemove", onMouseMove);
        window.removeEventListener("mouseup", onMouseUp);
        return;
      }
      const sizes = loadDashboardKpiSizes();
      board.querySelectorAll("[data-dashboard-kpi]").forEach((card) => {
        const key = card.dataset.dashboardKpi || "";
        if (!key) return;
        const cols = Number(card.dataset.cols || 1);
        const rows = Number(card.dataset.rows || 1);
        const width = Number(card.dataset.width || 0);
        const height = Number(card.dataset.height || 0);
        sizes[key] = { cols, rows, width, height };
      });
      saveDashboardKpiSizes(sizes);
      resizing = null;
      board.classList.remove("dashboard-kpi-board-resizing-x", "dashboard-kpi-board-resizing-y");
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  });
}

function enableDashboardPanelDrag(board) {
  if (!board || board.dataset.panelDragReady === "true") return;
  board.dataset.panelDragReady = "true";
  let dragging = null;
  let resizing = null;
  const sizes = loadDashboardPanelSizes();

  const panelsById = () => new Map(
    [...board.querySelectorAll("[data-dashboard-panel]")]
      .map((panel) => [panel.dataset.dashboardPanel, panel])
      .filter(([id]) => Boolean(id))
  );
  const syncOrder = () => {
    const order = [...board.querySelectorAll("[data-dashboard-panel]")]
      .filter((panel) => panel.dataset.panelFixed !== "true")
      .map((panel) => panel.dataset.dashboardPanel || "")
      .filter(Boolean);
    saveDashboardPanelOrder(order);
  };
  const getPanel = (target) => target?.closest?.("[data-dashboard-panel]");
  const applyPanelSize = (panel, size) => {
    if (!panel || !size || !panel.dataset.panelResizable) return;
    const bounds = dashboardResizeBounds(board, { minWidth: 300, maxWidth: 1280, minHeight: 66, maxHeight: 660 });
    const cols = Math.max(3, Math.min(12, Number(size.cols || panel.dataset.cols || 4)));
    const rows = Math.max(1, Math.min(5, Number(size.rows || panel.dataset.rows || 3)));
    panel.dataset.cols = String(cols);
    panel.dataset.rows = String(rows);
    panel.style.gridColumnEnd = `span ${cols}`;
    panel.style.minHeight = `${Math.max(bounds.minHeight, rows * 78)}px`;
    if (size.width) {
      panel.dataset.width = String(clampDashboardPixels(size.width, bounds.minWidth, bounds.maxWidth));
      panel.style.width = `${panel.dataset.width}px`;
    }
    if (size.height) {
      panel.dataset.height = String(clampDashboardPixels(size.height, bounds.minHeight, bounds.maxHeight));
      panel.style.height = `${panel.dataset.height}px`;
    }
  };
  const applyPanelOrder = () => {
    const panels = panelsById();
    loadDashboardPanelOrder().forEach((id) => {
      const panel = panels.get(id);
      if (panel && panel.dataset.panelFixed !== "true") board.appendChild(panel);
    });
  };

  applyPanelOrder();
  board.querySelectorAll("[data-dashboard-panel]").forEach((panel) => {
    applyPanelSize(panel, sizes[panel.dataset.dashboardPanel || ""]);
  });
  board.addEventListener("dragstart", (event) => {
    const handle = event.target.closest?.(".dashboard-panel-grip");
    if (!handle) return;
    const panel = getPanel(handle);
    if (!panel) return;
    dragging = panel;
    panel.classList.add("dashboard-panel-dragging");
    event.dataTransfer?.setData("text/plain", panel.dataset.dashboardPanel || "");
    event.dataTransfer?.setDragImage(panel, Math.min(90, panel.clientWidth / 2), Math.min(48, panel.clientHeight / 2));
  });
  board.addEventListener("dragend", () => {
    if (dragging) dragging.classList.remove("dashboard-panel-dragging");
    dragging = null;
    board.querySelectorAll(".dashboard-panel-drop-target").forEach((node) => node.classList.remove("dashboard-panel-drop-target"));
    syncOrder();
  });
  board.addEventListener("dragover", (event) => {
    if (!dragging) return;
    const panel = getPanel(event.target);
    if (!panel || panel === dragging || panel.dataset.panelFixed === "true") return;
    event.preventDefault();
    const rect = panel.getBoundingClientRect();
    const insertBefore = event.clientY < rect.top + rect.height / 2;
    board.querySelectorAll(".dashboard-panel-drop-target").forEach((node) => node.classList.remove("dashboard-panel-drop-target"));
    panel.classList.add("dashboard-panel-drop-target");
    board.insertBefore(dragging, insertBefore ? panel : panel.nextSibling);
  });
  board.addEventListener("drop", (event) => {
    if (!dragging) return;
    event.preventDefault();
    syncOrder();
  });

  board.addEventListener("mousedown", (event) => {
    const handle = event.target.closest?.(".dashboard-panel-resize-line");
    if (!handle) return;
    const panel = handle.closest("[data-dashboard-panel][data-panel-resizable='true']");
    if (!panel) return;
    event.preventDefault();
    const axis = handle.dataset.resizeAxis || "x";
    resizing = {
      panel,
      axis,
      startX: event.clientX,
      startY: event.clientY,
      startWidth: panel.getBoundingClientRect().width,
      startHeight: panel.getBoundingClientRect().height,
      startCols: Number(panel.dataset.cols || 4),
      startRows: Number(panel.dataset.rows || 3),
    };
    board.classList.add(`dashboard-panel-board-resizing-${axis}`);

    const onMouseMove = (event) => {
      if (!resizing) return;
      const dx = event.clientX - resizing.startX;
      const dy = event.clientY - resizing.startY;
      const bounds = dashboardResizeBounds(board, { minWidth: 300, maxWidth: 1280, minHeight: 66, maxHeight: 660 });
      if (resizing.axis === "x") {
        const nextWidth = Math.round(clampDashboardPixels(resizing.startWidth + dx, bounds.minWidth, bounds.maxWidth));
        const nextCols = dashboardSpanFromPixels(board, nextWidth, 12, 3, 12);
        applyPanelSize(resizing.panel, { cols: nextCols, width: nextWidth });
      } else {
        const nextHeight = Math.round(clampDashboardPixels(resizing.startHeight + dy, bounds.minHeight, bounds.maxHeight));
        const nextRows = dashboardRowsFromPixels(nextHeight, 78, 1, 5);
        applyPanelSize(resizing.panel, { rows: nextRows, height: nextHeight });
      }
    };

    const onMouseUp = () => {
      if (!resizing) {
        window.removeEventListener("mousemove", onMouseMove);
        window.removeEventListener("mouseup", onMouseUp);
        return;
      }
      const sizes = loadDashboardPanelSizes();
      board.querySelectorAll("[data-dashboard-panel][data-panel-resizable='true']").forEach((panel) => {
        const key = panel.dataset.dashboardPanel || "";
        if (!key) return;
        sizes[key] = {
          cols: Number(panel.dataset.cols || 4),
          rows: Number(panel.dataset.rows || 3),
          width: Number(panel.dataset.width || 0),
          height: Number(panel.dataset.height || 0),
        };
      });
      saveDashboardPanelSizes(sizes);
      resizing = null;
      board.classList.remove("dashboard-panel-board-resizing-x", "dashboard-panel-board-resizing-y");
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  });
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
    status.textContent = uiSettings.language === "ko" ? "마운트 경로 없음" : "Mount path not found";
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

function dashboardFlowLabel(lines, index) {
  const defaults = ["Backup Done", "Flush", "I/O Check", "Unmount", "Offline"];
  const text = (Array.isArray(lines) ? lines.join(" ") : String(lines || "")).trim();
  const normalized = text.replace(/\s+/g, " ").toLowerCase();
  if (index === 0 || /backup|백업/.test(normalized)) return "Backup Done";
  if (index === 1 || /flush/.test(normalized)) return "Flush";
  if (index === 2 || /i\/o|io|입출력|종료/.test(normalized)) return "I/O Check";
  if (index === 3 || /unmount|dismount|disk|디스크|power|오프라인/.test(normalized)) return "Unmount";
  if (index === 4 || /offline|air-gap|airgap|격리|활성/.test(normalized)) return "Offline";
  return defaults[index] || text || `Step ${index + 1}`;
}

function dashboardHealthValueClass(label, value) {
  const labelText = String(label || "").toLowerCase();
  const valueText = String(value || "").toLowerCase();
  if (/(failed|fail|error|detected)/.test(valueText)) return "health-value-danger";
  if (labelText.includes("disk offline") && !/(normal|ok|offline complete|complete)/.test(valueText)) return "health-value-danger";
  if (/(normal|isolated|visible|none|ok|success|complete)/.test(valueText)) return "health-value-ok";
  return "health-value-neutral";
}

function dashboardAlertTarget(label, value) {
  const text = `${label || ""} ${value || ""}`.toLowerCase();
  if (/veeam|repository|auto isolation|isolation|disk offline|offline error|offline/.test(text)) return "sources";
  if (/audit|login|approval|policy/.test(text)) return "logs2";
  if (/network|port|latency|traffic/.test(text)) return "network2";
  if (/hardware|disk|memory|cpu|raid/.test(text)) return "detect2";
  return "monitoring";
}

function dashboardAlertTitle(label, value, target) {
  const names = {
    sources: uiSettings.language === "ko" ? "에어갭 화면" : "Air-Gap view",
    logs2: uiSettings.language === "ko" ? "로그 화면" : "Logs view",
    network2: uiSettings.language === "ko" ? "네트워크 화면" : "Network view",
    detect2: uiSettings.language === "ko" ? "탐지 내역 화면" : "Detection view",
    monitoring: uiSettings.language === "ko" ? "모니터링 화면" : "Monitoring view",
  };
  return uiSettings.language === "ko"
    ? `${label || "알림"}: ${value || "-"} - ${names[target] || names.monitoring}에서 상세 확인`
    : `${label || "Alert"}: ${value || "-"} - open ${names[target] || names.monitoring}`;
}

function bindDashboardAlertLinks() {
  document.querySelectorAll(".health-row[data-alert-target]").forEach((row) => {
    row.addEventListener("click", () => showView(row.dataset.alertTarget || "monitoring"));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        showView(row.dataset.alertTarget || "monitoring");
      }
    });
  });
}

function markLiveRequest(state) {
  state.status = "pending";
  state.lastRequestAt = emergencyReconnectTimestamp();
}

function markLiveSuccess(state) {
  state.status = "live";
  state.lastSuccessAt = emergencyReconnectTimestamp();
  state.lastError = "";
  state.consecutiveFailures = 0;
}

function markLiveFailure(state, error) {
  state.status = state.lastSuccessAt ? "stale" : "error";
  state.lastError = error?.message || String(error || "request failed");
  state.consecutiveFailures += 1;
}

function liveStateSnapshot(state) {
  return {
    status: state.status,
    last_request_at: state.lastRequestAt,
    last_success_at: state.lastSuccessAt,
    last_error: state.lastError,
    consecutive_failures: state.consecutiveFailures,
  };
}

function dashboardDataWithLiveState(data, state) {
  if (!data) return data;
  return {
    ...data,
    _live: liveStateSnapshot(state),
  };
}

function liveStateMeta(state) {
  if (!state?.lastSuccessAt && state?.status !== "pending") return uiSettings.language === "ko" ? "연동 대기" : "Waiting for live sync";
  if (state.status === "pending") return uiSettings.language === "ko" ? `갱신 요청 ${state.lastRequestAt || "-"}` : `Sync requested ${state.lastRequestAt || "-"}`;
  if (state.status === "live") return uiSettings.language === "ko" ? `최근 갱신 ${state.lastSuccessAt || "-"}` : `Updated ${state.lastSuccessAt || "-"}`;
  return uiSettings.language === "ko"
    ? `지연 ${state.consecutiveFailures || 1}회 · ${state.lastError || "응답 없음"}`
    : `Stale ${state.consecutiveFailures || 1}x · ${state.lastError || "No response"}`;
}

function opsText(ko, en) {
  return uiSettings.language === "ko" ? ko : en;
}

function dashboardLiveBadge(data, copy, fallbackUpdatedAt) {
  const clientLive = data?._live || {};
  const serverLive = data?.live_status || {};
  const rawStatus = String(clientLive.status || (serverLive.cache_hit ? "stale" : "live")).toLowerCase();
  const state = ["pending", "stale", "error", "live"].includes(rawStatus) ? rawStatus : "live";
  const label = state === "pending"
    ? copy.livePending
    : state === "stale"
    ? copy.liveStale
    : state === "error"
    ? copy.liveError
    : copy.livePolling;
  const updatedAt = clientLive.last_success_at || serverLive.generated_at || data?.generated_at || fallbackUpdatedAt || "-";
  const detail = clientLive.last_error || (serverLive.cache_hit ? "cached dashboard payload" : "");
  const title = `${copy.liveUpdated}: ${updatedAt}${detail ? ` · ${detail}` : ""}`;
  return `
    <span class="dashboard-live-badge dashboard-live-badge-${escapeHtml(state)}" title="${escapeHtml(title)}">
      <i aria-hidden="true"></i>
      <b>${escapeHtml(label)}</b>
      <em>${escapeHtml(updatedAt)}</em>
    </span>
  `;
}

function renderDashboard(data) {
  latestDashboardData = data;
  const copy = dashboardCopy();
  const securityKpis = Array.isArray(data.security_kpis) && data.security_kpis.length
    ? data.security_kpis
    : [
      { icon: "data-protection-logo", label: copy.protection, value: copy.normal, tone: "green", meta: "" },
      { icon: "airgap-logo", label: copy.airgap, value: copy.active, tone: "blue", meta: "" },
      { icon: "storage-power", label: copy.storagePower, value: copy.off, tone: "dark", meta: "" },
      { icon: "veeam-backup-completed", label: copy.lastBackup, value: copy.success, tone: "green", meta: "2026-04-25 18:25" },
      { icon: "integrity-logo", label: copy.integrity, value: copy.normal, tone: "green", meta: `${copy.latest} 2026-04-25 17:40` },
    ];
  const orderedKpis = reorderDashboardKpis(securityKpis.map((item, index) => dashboardKpiDisplay({
    ...item,
    key: item.key || item.id || item.label || `kpi-${index}`,
  }, copy)));
  const kpiSizes = loadDashboardKpiSizes();
  const flowItems = Array.isArray(data.flow) && data.flow.length
    ? data.flow
    : [
      { lines: ["Backup Done"], state: "done" },
      { lines: ["Flush"], state: "done" },
      { lines: ["I/O Check"], state: "done" },
      { lines: ["Unmount"], state: "done" },
      { lines: ["Offline"], state: "done" },
    ];
  const backup = data.backup || {};
  const backupJobs = Array.isArray(backup.jobs) ? backup.jobs.slice(0, 6) : [];
  const jobColumns = copy.backupJobColumns || {};
  const backupJobTone = (value) => {
    const text = String(value || "").toLowerCase();
    if (/(success|complete|normal|stopped)/.test(text)) return "success";
    if (/(fail|error|critical|warning)/.test(text)) return "danger";
    if (/(running|working|processing)/.test(text)) return "active";
    return "muted";
  };
  const backupJobCards = backupJobs.length
    ? backupJobs.map((job) => {
      const resultTone = backupJobTone(job.last_result || job.status);
      const statusTone = backupJobTone(job.status || job.last_result);
      return `
        <article class="backup-job-card">
          <header>
            <div>
              <strong>${escapeHtml(job.name || "-")}</strong>
              <span>${escapeHtml(job.type || "-")} · ${escapeHtml(String(job.objects ?? "-"))} objects</span>
            </div>
            <span class="backup-job-badge backup-job-badge-${resultTone}">${escapeHtml(job.last_result || "-")}</span>
          </header>
          <dl>
            <div><dt>${escapeHtml(jobColumns.status || "Status")}</dt><dd><span class="backup-job-badge backup-job-badge-${statusTone}">${escapeHtml(job.status || "-")}</span></dd></div>
            <div><dt>${escapeHtml(jobColumns.lastRun || "Last Run")}</dt><dd>${escapeHtml(job.last_run || "-")}</dd></div>
            <div><dt>${escapeHtml(jobColumns.nextRun || "Next Run")}</dt><dd>${escapeHtml(job.next_run || "-")}</dd></div>
            <div><dt>${escapeHtml(jobColumns.target || "Target")}</dt><dd>${escapeHtml(job.target || "-")}</dd></div>
          </dl>
          <p>${escapeHtml(job.description || "-")}</p>
        </article>
      `;
    }).join("")
    : `<div class="backup-jobs-empty">Veeam Jobs data is not available yet.</div>`;
  const events = Array.isArray(data.logs) ? data.logs.slice(0, 5) : [];
  const alerts = Array.isArray(data.alerts) ? data.alerts : [];
  const auditSummary = data.audit_summary || {};
  const threat = data.threat_detection || {};
  const liveUpdatedAt = data.generated_at || data.checked_at || threat.last_scan_at || backup.ended_at || auditSummary.latest_at || "-";
  const liveBadge = dashboardLiveBadge(data, copy, liveUpdatedAt);
  const eventRows = events.length
    ? events.map((event) => `<div class="event-row"><span><i class="event-clock" aria-hidden="true"></i>${escapeHtml(event.date || "-")}</span><strong>${escapeHtml(event.content || "-")}</strong></div>`).join("")
    : `<div class="dashboard-empty-row">최근 이벤트가 없습니다. Veeam, Air-Gap, 감사 로그가 수집되면 표시됩니다.</div>`;
  const alertRows = alerts.length
    ? alerts.map((item) => {
      const label = item.label || "-";
      const value = item.value || "-";
      const target = dashboardAlertTarget(label, value);
      const valueClass = dashboardHealthValueClass(label, value);
      const rowClass = valueClass === "health-value-danger" ? "health-row health-row-danger" : "health-row";
      return `<button type="button" class="${rowClass}" data-alert-target="${escapeHtml(target)}" title="${escapeHtml(dashboardAlertTitle(label, value, target))}"><span>${escapeHtml(label)}</span><b class="${valueClass}">${escapeHtml(value)}</b></button>`;
    }).join("")
    : `<div class="dashboard-empty-row">현재 표시할 경고 항목이 없습니다.</div>`;
  const auditCounts = [
    ["관리자 수동 조작", auditSummary.manual_operations ?? 0],
    ["정책 변경", auditSummary.policy_changes ?? 0],
    ["승인 요청", auditSummary.approval_requests ?? 0],
    ["로그인 실패", auditSummary.login_failures ?? 0],
  ];
  const threatStatus = String(threat.status || "정상");
  const threatDanger = threatTone(threatStatus) === "danger";
  const dashboardEventsVisible = true;
  const dashboardAlertsVisible = true;
  dashboardView.innerHTML = `
    ${threatDanger ? `
      <section class="dashboard-threat-banner">
        <strong>위험 경고: 최근 백업본에서 랜섬웨어 의심 징후가 탐지되었습니다.</strong>
        <span>Repository 재연결이 차단되었으며 관리자 승인이 필요합니다.</span>
      </section>
    ` : ""}
    <div class="security-kpi-grid" id="dashboardKpiBoard" aria-label="Dashboard summary cards">
      ${orderedKpis.map(({ icon, label, value, tone, meta, key, detail, rawValue }) => {
        const valueTitle = rawValue && rawValue !== value ? rawValue : meta;
        return `
        <article class="security-kpi security-kpi-${icon} security-kpi-tone-${tone}" data-tone="${escapeHtml(tone || "dark")}" data-dashboard-kpi="${escapeHtml(key)}" data-cols="${escapeHtml(String(kpiSizes[key]?.cols || 1))}" data-rows="${escapeHtml(String(kpiSizes[key]?.rows || 1))}">
          <span class="dashboard-kpi-grip" draggable="true" data-drag-axis="xy" aria-hidden="true" title="Drag to reorder"></span>
          <span class="dashboard-kpi-resize-line dashboard-kpi-resize-line-x" data-resize-axis="x" aria-hidden="true" title="Resize width"></span>
          <span class="dashboard-kpi-resize-line dashboard-kpi-resize-line-y" data-resize-axis="y" aria-hidden="true" title="Resize height"></span>
          <div>
            <span>${escapeHtml(label || "-")}</span>
            <strong class="security-value-${tone}" ${valueTitle ? `title="${escapeHtml(valueTitle)}"` : ""}>${escapeHtml(value || "-")}</strong>
            ${detail ? `<em>${escapeHtml(detail)}</em>` : ""}
          </div>
        </article>
      `;
      }).join("")}
    </div>

    <section class="dashboard-status-strip" aria-label="Dashboard status summary">
      <article>
        <span>위협 탐지</span>
        <strong class="threat-${threatTone(threatStatus)}">${escapeHtml(threatStatus)}</strong>
      </article>
      <article>
        <span>위험 점수</span>
        <strong>${escapeHtml(String(threat.score ?? "-"))}</strong>
      </article>
      <article>
        <span>마지막 검사</span>
        <strong>${escapeHtml(threat.last_scan_at || "-")}</strong>
      </article>
      <article>
        <span>의심 항목</span>
        <strong>${escapeHtml(String(threat.suspicious_count ?? 0))}건</strong>
      </article>
    </section>

    <div class="security-dashboard-grid dashboard-content-grid" id="dashboardContentBoard">
      <section class="security-panel backup-jobs-panel" data-dashboard-panel="backupJobs" data-panel-fixed="true" data-cols="12" data-rows="2">
        <header class="backup-jobs-head">
          <h2>${escapeHtml(copy.backupJobs)}</h2>
          <span>${escapeHtml(backup.last_checked || "-")}</span>
        </header>
        <div class="panel-body backup-jobs-grid">
          ${backupJobCards}
        </div>
      </section>

      <section class="security-panel security-flow-panel" data-dashboard-panel="protection" data-panel-resizable="true" data-cols="12" data-rows="3" aria-live="polite">
        <header class="security-flow-header"><h2>${copy.liveProtection}</h2>${liveBadge}<span class="dashboard-panel-info">ⓘ</span><span class="dashboard-panel-grip" draggable="true" data-drag-axis="y" aria-hidden="true" title="Drag card up or down"></span></header>
        <div class="panel-body">
          <p>${copy.protectedMessage.replace("Offline", "<b>Offline</b>").replace("offline", "<b>offline</b>")}</p>
          <div class="security-flow">
            ${flowItems.map(({ lines, state }, index) => {
              const label = dashboardFlowLabel(lines, index);
              return `
              <div class="flow-step-card ${state === "done" ? "flow-step-card-active" : ""}">
                <span class="flow-step-number">${index + 1}</span>
                <strong>${escapeHtml(label)}</strong>
              </div>
            `;
            }).join("")}
          </div>
        </div>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-x" data-resize-axis="x" aria-hidden="true" title="Resize width"></span>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-y" data-resize-axis="y" aria-hidden="true" title="Resize height"></span>
      </section>

      <section class="security-panel backup-panel" data-dashboard-panel="backup" data-panel-resizable="true" data-cols="12" data-rows="3">
        <header><h2>${copy.backupLink}</h2><span class="dashboard-panel-grip" draggable="true" data-drag-axis="y" aria-hidden="true" title="Drag card up or down"></span></header>
        <div class="panel-body">
          <dl>
            <div><dt>연동 백업 솔루션</dt><dd>${escapeHtml(backup.solution || "Veeam Backup & Replication")}</dd></div>
            <div><dt>Veeam REST 연동</dt><dd class="backup-result ${backup.issue_detected || backup.api_synced === false ? "backup-result-failed" : "backup-result-success"}">${escapeHtml(backup.api_synced === false ? "연동 확인 필요" : "연동 정상")}</dd></div>
            <div><dt>마지막 작업명</dt><dd>${escapeHtml(backup.job || "-")}</dd></div>
            <div><dt>백업 시작</dt><dd>${escapeHtml(backup.started_at || "-")}</dd></div>
            <div><dt>백업 종료</dt><dd>${escapeHtml(backup.ended_at || "-")}</dd></div>
            <div><dt>마지막 확인</dt><dd>${escapeHtml(backup.last_checked || "-")}</dd></div>
            <div><dt>LOCK-FIX 상태</dt><dd>${escapeHtml(backup.isolation_state || "-")}</dd></div>
            <div><dt>차단 결과</dt><dd class="backup-result ${String(backup.result || "").includes("Failed") ? "backup-result-failed" : "backup-result-success"}">${escapeHtml(backup.result || "-")}</dd></div>
          </dl>
        </div>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-x" data-resize-axis="x" aria-hidden="true" title="Resize width"></span>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-y" data-resize-axis="y" aria-hidden="true" title="Resize height"></span>
      </section>

      <section class="security-panel event-panel ${dashboardEventsVisible ? "event-panel-visible" : "event-panel-hidden"}" data-dashboard-panel="events" data-panel-resizable="true" data-cols="4" data-rows="${dashboardEventsVisible ? "3" : "1"}">
        <header class="event-panel-header">
          <h2>${copy.event}</h2>
          <span class="dashboard-panel-grip" draggable="true" data-drag-axis="y" aria-hidden="true" title="Drag card up or down"></span>
        </header>
        <div class="panel-body dashboard-event-body">
          ${eventRows}
          <a>${copy.detail} ›</a>
        </div>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-x" data-resize-axis="x" aria-hidden="true" title="Resize width"></span>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-y" data-resize-axis="y" aria-hidden="true" title="Resize height"></span>
      </section>

      <section class="security-panel alert-panel ${dashboardAlertsVisible ? "alert-panel-visible" : "alert-panel-hidden"}" data-dashboard-panel="alerts" data-panel-resizable="true" data-cols="4" data-rows="${dashboardAlertsVisible ? "3" : "1"}">
        <header class="alert-panel-header">
          <h2>${copy.alert}</h2>
          <span class="dashboard-panel-grip" draggable="true" data-drag-axis="y" aria-hidden="true" title="Drag card up or down"></span>
        </header>
        <div class="panel-body dashboard-alert-body">
          ${alertRows}
          <a>${copy.detail} ›</a>
        </div>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-x" data-resize-axis="x" aria-hidden="true" title="Resize width"></span>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-y" data-resize-axis="y" aria-hidden="true" title="Resize height"></span>
      </section>

      <section class="security-panel audit-summary-panel" data-dashboard-panel="audit" data-panel-resizable="true" data-cols="4" data-rows="3">
        <header><h2>${copy.audit}</h2><span class="dashboard-panel-grip" draggable="true" data-drag-axis="y" aria-hidden="true" title="Drag card up or down"></span></header>
        <div class="panel-body">
          <div class="audit-count-grid">
            ${auditCounts.map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(String(value))}건</strong></div>`).join("")}
          </div>
          <span class="audit-link-state">감사 로그 연동 ${auditSummary.linked ? "정상" : "확인 필요"} · 총 ${escapeHtml(String(auditSummary.total_records ?? 0))}건 · 최신 ${escapeHtml(auditSummary.latest_at || "-")}</span>
          <span class="export-label">로그 내보내기</span>
          <div class="export-buttons">
            <button><i class="file-icon file-csv" aria-hidden="true"></i>${copy.csv}</button>
            <button><i class="file-icon file-pdf" aria-hidden="true"></i>${copy.pdf}</button>
            <button><i class="file-icon file-word" aria-hidden="true"></i>${copy.word}</button>
          </div>
        </div>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-x" data-resize-axis="x" aria-hidden="true" title="Resize width"></span>
        <span class="dashboard-panel-resize-line dashboard-panel-resize-line-y" data-resize-axis="y" aria-hidden="true" title="Resize height"></span>
      </section>

  </div>
  `;
  enableDashboardKpiDrag(document.querySelector("#dashboardKpiBoard"));
  enableDashboardPanelDrag(document.querySelector("#dashboardContentBoard"));
  bindDashboardAlertLinks();
}

function renderDashboardFallback(message = "") {
  if (!dashboardView) return;
  const detail = message || t("dashboard.loadErrorDesc");
  dashboardView.innerHTML = `
    <section class="dashboard-load-state dashboard-load-error" aria-live="polite">
      <strong>${escapeHtml(t("dashboard.loadErrorTitle"))}</strong>
      <span>${escapeHtml(detail)}</span>
      <button type="button" id="dashboardRetryButton">${escapeHtml(t("dashboard.retry"))}</button>
    </section>
  `;
  document.querySelector("#dashboardRetryButton")?.addEventListener("click", () => reloadDashboard());
}

function renderReport(data) {
  latestReportData = data;
  reportOverallStatus.textContent = reportStatusLabel(data.summary.overall_status);
  reportAnalysis.textContent = uiSettings.language === "ko" ? t("report.analysis") : data.summary.analysis;
  reportGeneratedAt.textContent = `${t("report.generated")}: ${data.generated_at}`;
  reportRange.textContent = `${data.range.start} - ${data.range.end}`;
  const customerRows = [
    [t("report.customerName"), data.customer.customer_name, t("report.inspectionDate"), data.customer.inspection_date],
    [
      t("report.customerContact"),
      editableReportField("customer_contact", data.customer.customer_contact, t("report.customerContact")),
      t("report.engineer"),
      data.customer.engineer,
    ],
    [
      t("report.customerEmail"),
      editableReportField("customer_email", data.customer.customer_email, "email@example.com"),
      t("report.engineerContact"),
      data.customer.engineer_contact,
    ],
  ];
  reportCustomerTable.innerHTML = customerRows.map((row) => `
    <tr><th>${row[0]}</th><td>${row[1]}</td><th>${row[2]}</th><td>${row[3]}</td></tr>
  `).join("");
  reportCustomerTable.querySelectorAll(".report-edit-input").forEach((input) => {
    input.addEventListener("change", saveReportCustomerFields);
    input.addEventListener("blur", saveReportCustomerFields);
  });

  const serverRows = [
    [t("report.osVersion"), data.server.os_version, "CPU", data.server.cpu],
    [t("report.service"), data.server.service, t("report.memory"), data.server.memory],
    [t("report.model"), data.server.model, t("report.disk"), data.server.disk],
    [t("report.serial"), data.server.serial, t("report.hostname"), data.server.hostname],
  ];
  reportServerTable.innerHTML = serverRows.map((row) => `
    <tr><th>${row[0]}</th><td>${row[1]}</td><th>${row[2]}</th><td>${row[3]}</td></tr>
  `).join("");

  reportCards.replaceChildren();
  data.cards.forEach((card) => {
    const item = document.createElement("article");
    const isWarning = card.status === "Warning";
    item.className = `report-card report-card-${card.status.toLowerCase().replaceAll(" ", "-")}`;
    item.innerHTML = `
      <span>${reportMetricLabel(card.label)}</span>
      <strong class="${isWarning ? "report-warning-value" : ""}">${card.current}%</strong>
      <div>
        <b>${t("report.avg")} ${card.average}%</b>
        <b>${t("report.peak")} ${card.peak}%</b>
      </div>
      <em>${reportStatusLabel(card.status)}</em>
    `;
    reportCards.appendChild(item);
  });

  reportTable.replaceChildren();
  data.cards.forEach((card) => {
    const row = document.createElement("tr");
    const isWarning = card.status === "Warning";
    row.innerHTML = `
      <td>${reportMetricLabel(card.label)}</td>
      <td><span class="${isWarning ? "report-warning-value" : ""}">${card.current}%</span></td>
      <td>${card.average}%</td>
      <td>${card.peak}%</td>
      <td>${card.threshold}%</td>
      <td><span class="${card.status === "Warning" ? "status-bad" : "status-good"}">${reportStatusLabel(card.status)}</span></td>
      <td>${reportRecommendation(card)}</td>
    `;
    reportTable.appendChild(row);
  });

  reportInspectionTable.replaceChildren();
  const inspectionItems = data.inspection_items || [];
  const warningItems = inspectionItems.filter((item) => String(item.result || "").toLowerCase() === "warning");
  const normalItems = inspectionItems.filter((item) => String(item.result || "").toLowerCase() !== "warning");
  if (reportInspectionSummary) {
    const summaryLabels = uiSettings.language === "ko"
      ? { total: "전체 점검", normal: "정상", warning: "주의", status: "종합 상태", stable: "운영 가능", review: "주의 항목 검토" }
      : { total: "Total Checks", normal: "Normal", warning: "Warning", status: "Overall", stable: "Operational", review: "Review Required" };
    reportInspectionSummary.innerHTML = `
      <article>
        <span>${summaryLabels.total}</span>
        <strong>${inspectionItems.length}</strong>
      </article>
      <article>
        <span>${summaryLabels.normal}</span>
        <strong class="report-summary-ok">${normalItems.length}</strong>
      </article>
      <article>
        <span>${summaryLabels.warning}</span>
        <strong class="${warningItems.length ? "report-summary-warn" : "report-summary-ok"}">${warningItems.length}</strong>
      </article>
      <article>
        <span>${summaryLabels.status}</span>
        <strong class="${warningItems.length ? "report-summary-warn" : "report-summary-ok"}">${warningItems.length ? summaryLabels.review : summaryLabels.stable}</strong>
      </article>
    `;
  }
  if (reportAttentionList) {
    const attentionTitle = uiSettings.language === "ko" ? "주의 항목" : "Attention Items";
    const emptyText = uiSettings.language === "ko" ? "현재 주의 항목이 없습니다." : "No attention items.";
    reportAttentionList.innerHTML = warningItems.length
      ? `
        <h3>${attentionTitle}</h3>
        <div>
          ${warningItems.map((item) => `
            <article>
              <strong>${reportInspectionText(item.item)}</strong>
              <span>${reportInspectionText(item.metric)} · ${reportInspectionText(item.criteria)}</span>
            </article>
          `).join("")}
        </div>
      `
      : `<p>${emptyText}</p>`;
  }
  inspectionItems.forEach((item) => {
    const row = document.createElement("tr");
    const isWarning = String(item.result || "").toLowerCase() === "warning";
    row.innerHTML = `
      <td>${reportInspectionText(item.category)}</td>
      <td>${reportInspectionText(item.item)}</td>
      <td>${reportInspectionText(item.detail)}</td>
      <td>${reportInspectionText(item.criteria)}</td>
      <td>${reportInspectionText(item.metric)}</td>
      <td><span class="report-result-badge ${isWarning ? "report-result-warning" : "report-result-normal"}">${reportStatusLabel(item.result)}</span></td>
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
  const summary = data.summary || {};
  const unauthorized = summary.unauthorized_access || {};
  const auditAnomaly = summary.audit_anomaly || {};
  const auditAlert = data.audit_alert || {};
  if (notificationUnauthorizedCount) notificationUnauthorizedCount.textContent = unauthorized.value || "0건";
  if (notificationAuditAnomalyCount) notificationAuditAnomalyCount.textContent = auditAnomaly.value || "0건";
  if (notificationAuditAnomalyStatus) {
    notificationAuditAnomalyStatus.textContent = auditAlert.status === "ALERT" ? "이상 감지 알림 전송 대상" : "알림 대기 없음";
    notificationAuditAnomalyStatus.className = auditAlert.status === "ALERT" ? "notification-alert-text" : "";
  }
  if (notificationAuditLastDetected) {
    notificationAuditLastDetected.textContent = `Last Detected ${auditAlert.last_detected || "-"}`;
  }
  if (!notificationAuditTable) return;
  notificationAuditTable.replaceChildren();
  const auditItems = Array.isArray(auditAlert.items) ? auditAlert.items : [];
  if (!auditItems.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="5" class="notification-empty">최근 24시간 감사 이력 이상 감지 내역이 없습니다.</td>';
    notificationAuditTable.appendChild(row);
    return;
  }
  auditItems.forEach((item) => {
    const row = document.createElement("tr");
    const severity = String(item.severity || "WARNING").toUpperCase();
    const severityClass = severity === "CRITICAL" ? "status-bad" : "status-warn";
    row.innerHTML = `
      <td>${escapeHtml(item.detected_at || "-")}</td>
      <td><span class="${severityClass}">${escapeHtml(severity)}</span></td>
      <td>${escapeHtml(item.event || "-")}</td>
      <td><span class="${severity === "CRITICAL" ? "status-bad" : "status-good"}">${escapeHtml(item.alert_status || "ALERT READY")}</span></td>
      <td class="notification-message-cell">${escapeHtml(item.message || "-")}</td>
    `;
    notificationAuditTable.appendChild(row);
  });
}

function renderDetectFallback(message = "탐지 내역을 불러오는 중입니다.", detail = "LOCK-FIX가 디스크 식별, 에어갭 볼륨, Veeam Backup Copy 저장소 정보를 확인하고 있습니다.") {
  if (!detectFingerprintRoot) return;
  detectFingerprintRoot.innerHTML = `
    <div class="detect-judgement-page detect-empty-state">
      <header class="detect-judgement-head">
        <span aria-hidden="true"></span>
        <div>
          <h1>탐지 내역</h1>
          <p>${escapeHtml(detail)}</p>
        </div>
      </header>
      <section class="detect-judgement-panel detect-judgement-normal">
        <div class="detect-judgement-topline">
          <div class="detect-final-state">
            <span>DETECTION STATUS</span>
            <div class="detect-state-row">
              <strong>CHECKING</strong>
              <b>${escapeHtml(message)}</b>
            </div>
            <em>화면이 비어 보이지 않도록 기본 상태를 표시합니다.</em>
          </div>
          <div class="detect-latency">
            <span>VIEW</span>
            <strong>READY</strong>
          </div>
        </div>
        <div class="detect-judgement-cards">
          <article>
            <span>DISK IDENTITY</span>
            <strong>확인 중</strong>
          </article>
          <article>
            <span>AIR-GAP VOLUME</span>
            <strong>확인 중</strong>
          </article>
          <article>
            <span>VEEAM REPOSITORY</span>
            <strong>확인 중</strong>
          </article>
        </div>
      </section>
    </div>
  `;
}

function renderDetect(data) {
  if (!data || typeof data !== "object") {
    renderDetectFallback("탐지 데이터가 아직 준비되지 않았습니다.", "서버 연결 또는 권한 상태를 확인한 뒤 다시 표시합니다.");
    return;
  }
  if (detectFingerprintRoot) {
    const fingerprint = data.fingerprint || {};
    const parts = Array.isArray(fingerprint.parts) ? fingerprint.parts : [];
    const status = String(fingerprint.status || "UNREGISTERED");
    const isNormal = fingerprint.match === true || status === "MATCH";
    const isIsolated = status === "ISOLATED";
    const statusClass = isNormal || isIsolated ? "normal" : "abnormal";
    const judgementLabel = isNormal ? "REGISTERED" : isIsolated ? "ISOLATED" : status === "DIFFERENT_DISK" ? "DIFFERENT DISK" : "UNREGISTERED";
    const judgementKorean = isNormal ? "등록된 디스크" : isIsolated ? "격리 볼륨" : status === "DIFFERENT_DISK" ? "다른 디스크 감지" : "등록되지 않은 디스크";
    const recognitionLabel = isNormal ? "NORMAL RECOGNITION" : isIsolated ? "ISOLATED - VERIFICATION WAITING" : "RECOGNITION FAILED";
    const diskSize = parts.find((part) => {
      const key = String(part.key || "").toLowerCase();
      const label = String(part.label || "").toLowerCase();
      return key.includes("size") || label.includes("size");
    });
    const latency = fingerprint.detection_latency_seconds ?? data.detection_latency_seconds ?? "0.5";
    const fingerprintValue = String(fingerprint.value || "-");
    const shortFingerprint = fingerprintValue.length > 12 ? `${fingerprintValue.slice(0, 12)}...` : fingerprintValue;
    const emergencyAccess = data.emergency_access || {};
    const emergencySlot = emergencyAccess.slot || {};
    const emergencyVolume = emergencySlot.mount_point || emergencySlot.device || "-";
    const emergencyState = String(emergencySlot.state || "-").toUpperCase();
    const emergencyHashStatus = String(emergencySlot.hash_status || "-").toUpperCase();
    const veeamRepository = data.veeam_repository || {};
    const veeamRepositoryName = veeamRepository.repository_name || "Veeam Repository";
    const veeamRepositoryPath = veeamRepository.repository_path || "-";
    const veeamRepositoryEligible = veeamRepository.eligible !== false;
    const veeamRepositoryMeta = veeamRepositoryEligible
      ? [
          veeamRepositoryPath,
          veeamRepository.api_synced ? "REST API 연동" : "설정 기준",
        ].filter(Boolean).join(" · ")
      : "Veeam Backup Copy 저장소만 표시";
    const emergencyItems = [
      { label: "SLOT", value: emergencySlot.slot_id || fingerprint.slot_id || "-" },
      { label: "VOLUME", value: emergencyVolume },
      { label: "STATE", value: emergencyState },
      { label: "HASH CHECK", value: emergencyHashStatus },
      { label: "AUTH HASH", value: emergencySlot.authorization_hash_short || "-" },
      { label: "DISK UID", value: emergencySlot.current_uid_short || "-" },
      { label: "LAST RECONNECT", value: emergencySlot.last_reconnect || "-" },
      {
        label: "VEEAM REPOSITORY",
        value: veeamRepositoryName,
        meta: veeamRepositoryMeta,
        className: veeamRepositoryEligible ? "detect-veeam-repository-card" : "detect-veeam-repository-card detect-veeam-repository-blocked",
      },
    ];
    detectFingerprintRoot.innerHTML = `
      <div class="detect-judgement-page">
        <header class="detect-judgement-head">
          <span aria-hidden="true"></span>
          <div>
            <h1>디스크 식별 판정</h1>
            <p>UID, 해시, 디스크 속성 기준으로 현재 연결된 볼륨의 신뢰 상태를 판정합니다.</p>
          </div>
        </header>
        <section class="detect-judgement-panel detect-judgement-${statusClass}">
          <div class="detect-judgement-topline">
            <div class="detect-final-state">
              <span>FINAL JUDGEMENT</span>
              <div class="detect-state-row">
                <strong>${escapeHtml(judgementLabel)}</strong>
                <b>${escapeHtml(judgementKorean)}</b>
              </div>
              <em>${escapeHtml(recognitionLabel)}</em>
            </div>
            <div class="detect-latency">
              <span>DETECTION LATENCY</span>
              <strong>${escapeHtml(String(latency))}<small>sec</small></strong>
            </div>
          </div>
          <div class="detect-judgement-cards">
            <article>
              <span>SLOT ID</span>
              <strong>${escapeHtml(fingerprint.slot_id || "-")}</strong>
            </article>
            <article>
              <span>CURRENT FINGERPRINT</span>
              <strong>${escapeHtml(shortFingerprint)}</strong>
            </article>
            <article>
              <span>DISK SIZE</span>
              <strong>${escapeHtml(diskSize?.value || "-")}</strong>
            </article>
          </div>
            <div class="detect-action-row">
              <button type="button" class="detect-action-primary" data-detect-action="logs">상세 로그 보기</button>
              <button type="button" class="detect-action-secondary" data-detect-action="airgap">격리 유지</button>
              <button type="button" class="detect-action-secondary" data-detect-action="settings">등록 요청</button>
            </div>
            <section class="detect-volume-unified-card" aria-label="Air-Gap isolated volume status">
              <div class="detect-volume-head">
                <div>
                  <span>AIR-GAP VOLUME DETECTION</span>
                  <h2>격리 볼륨 통합 상태</h2>
                </div>
                <strong class="${/VALID|READY|ONLINE|ISOLATED/.test(emergencyState + emergencyHashStatus) ? "detect-text-normal" : "detect-text-abnormal"}">${escapeHtml(emergencyState)}</strong>
              </div>
              <div class="detect-volume-grid">
                ${emergencyItems.map((item) => `
                  <article class="${escapeHtml(item.className || "")}">
                    <span>${escapeHtml(item.label)}</span>
                    <strong>${escapeHtml(item.value)}</strong>
                    ${item.meta ? `<em>${escapeHtml(item.meta)}</em>` : ""}
                  </article>
                `).join("")}
              </div>
            </section>
            <section class="detect-background-fingerprint" aria-label="Background fingerprint judgement basis">
              <h2>Background Judgement Basis</h2>
              <div class="detect-background-grid">
                <article>
                  <span>REGISTERED FINGERPRINT</span>
                  <strong>${escapeHtml(fingerprint.registered_value || "-")}</strong>
                </article>
                <article>
                  <span>CURRENT STATUS</span>
                  <strong class="${isNormal ? "detect-text-normal" : "detect-text-abnormal"}">${escapeHtml(status)}</strong>
                </article>
                <article>
                  <span>FORMULA</span>
                  <strong>${escapeHtml((fingerprint.formula_title || "LOCK-FIX-DISK-FINGERPRINT =") + " " + (fingerprint.formula || ""))}</strong>
                </article>
              </div>
            </section>
            <section class="detect-parts-grid" aria-label="Disk identity fingerprint parts">
              ${parts.map((part) => `
                <article>
                  <span>${escapeHtml(part.label || "-")}</span>
                  <strong>${escapeHtml(part.value || "-")}</strong>
                </article>
              `).join("")}
            </section>
          </section>
        </div>
      `;
    return;
  }
  if (!detectStart || !detectEnd || !detectCards || !detectDetectTable || !detectWarningTable || !detectLogsTable) return;
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
  latestLogsData = data;
  if (!logsRange.start) logsRange.start = data.range.start;
  if (!logsRange.end) logsRange.end = data.range.end;
  logsRange.page = data.page || 1;
  logsRange.retention = data.retention_days || logsRange.retention;
  logsRange.type = data.filters?.type || logsRange.type || "";
  logsRange.severity = data.filters?.severity || logsRange.severity || "";
  logsRange.source = data.filters?.source || logsRange.source || "";
  logsRange.q = data.filters?.q || logsRange.q || "";
  logsStart.value = logsRange.start;
  logsEnd.value = logsRange.end;
  if (logRetentionSelect) logRetentionSelect.value = String(logsRange.retention);
  renderLogsTypeOptions(data.type_options || Object.keys(data.summary?.types || {}), logsRange.type);
  if (logsSeverityFilter) logsSeverityFilter.value = logsRange.severity;
  if (logsSearch) logsSearch.value = logsRange.q;
  renderLogsSourceOptions(data.source_options || [], logsRange.source);
  renderLogsSummaryCards(data);
  logsTotal.textContent = `Total ${data.total_logs} logs · ${data.retention_days}일 보관`;
  logsHistoryTable.replaceChildren();
  if (!data.items.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="5" class="logs-empty-cell">조건에 맞는 로그가 없습니다.</td>`;
    logsHistoryTable.appendChild(row);
  }
  data.items.forEach((item) => {
    const row = document.createElement("tr");
    const severity = String(item.severity || "INFO").toUpperCase();
    row.innerHTML = `
      <td><span class="history-type history-${String(item.type || "").toLowerCase()}">${escapeHtml(item.type || "-")}</span></td>
      <td>${escapeHtml(formatLogDate(item.date))}</td>
      <td>${escapeHtml(item.source || "-")}</td>
      <td><span class="log-severity-badge severity-${severity.toLowerCase()}">${escapeHtml(severity)}</span></td>
      <td><button type="button" class="log-message-button">${escapeHtml(item.message || "-")}</button></td>
    `;
    logsHistoryTable.appendChild(row);
  });
  renderLogsPagination(data);
  renderOperationsOverview();
}

function renderLogsTypeOptions(options, selected) {
  if (!logsTypeFilter) return;
  const current = selected || "";
  const optionHtml = [`<option value="">All</option>`]
    .concat(options.map((type) => `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`));
  logsTypeFilter.innerHTML = optionHtml.join("");
  logsTypeFilter.value = current;
}

function renderLogsSourceOptions(options, selected) {
  if (!logsSourceFilter) return;
  const current = selected || "";
  const optionHtml = [`<option value="">All</option>`]
    .concat(options.map((source) => `<option value="${escapeHtml(source)}">${escapeHtml(source)}</option>`));
  logsSourceFilter.innerHTML = optionHtml.join("");
  logsSourceFilter.value = current;
}

function renderLogsSummaryCards(data) {
  if (!logsSummaryCards) return;
  const severity = data.summary?.severity || {};
  const cards = [
    { label: "Total", value: data.total_logs || 0, tone: "total" },
    { label: "ERROR", value: severity.ERROR || 0, tone: "error" },
    { label: "WARN", value: severity.WARN || 0, tone: "warn" },
    { label: "INFO", value: severity.INFO || 0, tone: "info" },
  ];
  logsSummaryCards.innerHTML = cards.map((card) => `
    <article class="logs-summary-card logs-summary-${card.tone}">
      <span>${card.label}</span>
      <strong>${card.value}</strong>
      <em>${card.tone === "total" ? `${data.retention_days || 30} days` : "filtered"}</em>
    </article>
  `).join("");
}

function formatLogDate(value) {
  if (!value) return "-";
  return String(value).replace("T", " ").replace(/\.\d+(?=Z?$)/, "").replace(/Z$/, "");
}

function renderLogsPagination(data) {
  logsPagination.replaceChildren();
  const totalPages = data.total_pages || 1;
  for (let page = 1; page <= totalPages; page += 1) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = page;
    button.classList.toggle("active", page === data.page);
    button.addEventListener("click", async () => {
      logsRange.page = page;
      await reloadLogs();
    });
    logsPagination.appendChild(button);
  }
}

function formatLicenseDate(value) {
  if (!value) return "-";
  return String(value).replace("T", " ").replace(/\.\d+(?=Z?$)/, "").replace(/Z$/, "");
}

function renderLicenseStatus(license) {
  if (!licenseStatusTable) return;
  const data = license || {};
  const state = data.valid ? "Permanent License" : data.reason || "확인 필요";
  const issuedAt = formatLicenseDate(data.issued_at);
  const expiresAt = formatLicenseDate(data.expires_at);
  const updatedAt = formatLicenseDate(data.updated_at);
  const daysLeft = data.valid && Number.isFinite(Number(data.days_left)) ? `${data.days_left}일` : "-";
  const expiryAlert = data.valid && Number(data.days_left) <= 30;

  if (licenseStatusBadges) {
    licenseStatusBadges.innerHTML = `
      <span class="license-status-badge ${data.valid ? "license-status-good" : "license-status-danger"}">${data.valid ? "정상" : "확인 필요"}</span>
      <span class="license-status-badge license-status-type">${state}</span>
      <span class="license-status-badge ${expiryAlert ? "license-status-danger" : "license-status-good"}">${daysLeft === "-" ? "만료 정보 없음" : `${daysLeft} 남음`}</span>
    `;
  }

  if (licenseSummaryGrid) {
    licenseSummaryGrid.innerHTML = `
      <article class="license-summary-card">
        <span>라이선스 상태</span>
        <strong class="${data.valid ? "license-ok" : "license-bad"}">${state}</strong>
      </article>
      <article class="license-summary-card">
        <span>남은 일자</span>
        <strong class="${expiryAlert ? "license-bad" : "license-ok"}">${daysLeft}</strong>
      </article>
      <article class="license-summary-card">
        <span>만료일</span>
        <strong>${expiresAt}</strong>
      </article>
    `;
  }

  licenseStatusTable.innerHTML = `
    <tr><th>고객사 정보</th><td>${data.customer || "-"}</td></tr>
    <tr><th>라이선스 키(Support Code)</th><td>${data.support_code || "-"}</td></tr>
    <tr><th>라이선스 상태</th><td class="${data.valid ? "license-ok" : "license-bad"}">${state}</td></tr>
    <tr><th>최초 사용 일자</th><td>${issuedAt}</td></tr>
    <tr><th>만료 일자</th><td class="${expiryAlert ? "license-bad" : ""}">${expiresAt}</td></tr>
    <tr><th>남은 일자</th><td>${daysLeft}</td></tr>
    <tr><th>갱신 일자</th><td>${updatedAt}</td></tr>
  `;

  if (licenseSupportBox) {
    licenseSupportBox.innerHTML = `
      <strong>라이선스 문의</strong>
      <span><a href="https://www.oam.co.kr" target="_blank" rel="noreferrer">www.oam.co.kr</a></span>
      <span>1666 - 3736</span>
    `;
  }
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
  latestNetworkStatusData = data;
  const realtime = data.realtime || {};
  const txRealtime = realtime.tx || {};
  const rxRealtime = realtime.rx || {};
  const interfaces = buildNetworkInterfaces(data.interfaces || data.items);
  syncNetworkInterfaceSelect(interfaces);
  const selected = interfaces.find((item) => item.id === selectedNetworkInterface) || interfaces[0] || null;
  const selectedItems = Array.isArray(data.items) ? data.items : [];
  const hasInterfaceSamples = Array.isArray(data.interfaces) && data.interfaces.length > 0;
  const txHistory = normalizeNetworkHistory(hasInterfaceSamples ? selected?.txHistory : [], txRealtime.history);
  const rxHistory = normalizeNetworkHistory(hasInterfaceSamples ? selected?.rxHistory : [], rxRealtime.history);
  const txCurrent = lastNetworkValue(txHistory, hasInterfaceSamples ? selected?.txMbps : txRealtime.current_mbps);
  const rxCurrent = lastNetworkValue(rxHistory, hasInterfaceSamples ? selected?.rxMbps : rxRealtime.current_mbps);
  const txTotal = Number((hasInterfaceSamples ? selected?.totalTxGb : txRealtime.total_gb) ?? 0);
  const rxTotal = Number((hasInterfaceSamples ? selected?.totalRxGb : rxRealtime.total_gb) ?? 0);
  if (networkStatusTitle) {
    networkStatusTitle.textContent = uiSettings.language === "ko" ? (data.title || t("network.title")) : t("network.title");
  }
  if (networkTxRate) networkTxRate.textContent = formatNetworkRate(txCurrent);
  if (networkRxRate) networkRxRate.textContent = formatNetworkRate(rxCurrent);
  if (networkLegendTxRate) networkLegendTxRate.textContent = formatNetworkRate(txCurrent);
  if (networkLegendRxRate) networkLegendRxRate.textContent = formatNetworkRate(rxCurrent);
  if (networkTxTotal) networkTxTotal.textContent = `${txTotal.toFixed(2)} GB`;
  if (networkRxTotal) networkRxTotal.textContent = `${rxTotal.toFixed(2)} GB`;
  if (networkSelectedNic) {
    networkSelectedNic.textContent = selected ? `${selected.label} · ${selected.id}` : "-";
  }
  if (networkAdapterName) networkAdapterName.textContent = selected?.adapterName || selected?.label || "-";
  if (networkConnectionType) networkConnectionType.textContent = selected?.connectionType || (uiSettings.language === "ko" ? "이더넷" : "Ethernet");
  if (networkIpv4Address) networkIpv4Address.textContent = selected?.ipv4 || data.local_ip || "-";
  if (networkIpv6Address) networkIpv6Address.textContent = selected?.ipv6 || "-";
  updateNetworkFlowModeControls();
  const scale = drawCombinedNetworkFlow(networkCombinedFlow, txHistory, rxHistory, activeNetworkFlowMode);
  if (networkCombinedScale) {
    networkCombinedScale.textContent = formatNetworkRate(scale);
  }
  if (networkTxFlow) drawFlowChart(networkTxFlow, txHistory, "tx");
  if (networkRxFlow) drawFlowChart(networkRxFlow, rxHistory, "rx");
  renderNetworkInterfaceStrip(interfaces, selected);
  renderNetworkIpSummary(networkTxIps, selectedItems, "tx");
  renderNetworkIpSummary(networkRxIps, selectedItems, "rx");
  renderNetworkAnalysis(data.analysis || {});
}

function buildNetworkInterfaces(items) {
  const source = Array.isArray(items) ? items : [];
  const map = new Map();
  source.forEach((item, index) => {
    const key = String(item.id || item.interface || item.nic || item.adapter || item.name || "NIC-1");
    const label = String(item.label || item.display_name || item.name || key);
    if (!map.has(key)) {
      map.set(key, {
        id: key,
        label,
        adapterName: String(item.adapter_name || item.adapterName || item.interface_name || label),
        connectionType: String(item.connection_type || item.connectionType || item.media_type || ""),
        ipv4: String(item.ipv4 || item.ipv4_address || item.address || ""),
        ipv6: String(item.ipv6 || item.ipv6_address || ""),
        items: [],
        txHistory: [],
        rxHistory: [],
        txMbps: 0,
        rxMbps: 0,
        totalTxGb: 0,
        totalRxGb: 0,
      });
    }
    const bucket = map.get(key);
    bucket.items.push(item);
    bucket.adapterName = bucket.adapterName || String(item.adapter_name || item.adapterName || label);
    bucket.connectionType = bucket.connectionType || String(item.connection_type || item.connectionType || item.media_type || "");
    bucket.ipv4 = bucket.ipv4 || String(item.ipv4 || item.ipv4_address || item.address || "");
    bucket.ipv6 = bucket.ipv6 || String(item.ipv6 || item.ipv6_address || "");
    const txSamples = numericNetworkSeries(item.tx_history || item.txHistory || item.history_tx);
    const rxSamples = numericNetworkSeries(item.rx_history || item.rxHistory || item.history_rx);
    const txValue = Number(item.tx_mbps ?? item.current_tx_mbps ?? item.tx_rate ?? item.tx ?? item.tx_gb ?? txSamples[txSamples.length - 1] ?? 0);
    const rxValue = Number(item.rx_mbps ?? item.current_rx_mbps ?? item.rx_rate ?? item.rx ?? item.rx_gb ?? rxSamples[rxSamples.length - 1] ?? 0);
    bucket.txHistory.push(...(txSamples.length ? txSamples : [txValue]));
    bucket.rxHistory.push(...(rxSamples.length ? rxSamples : [rxValue]));
    bucket.txMbps = txValue;
    bucket.rxMbps = rxValue;
    bucket.totalTxGb += Number(item.total_tx_gb ?? item.tx_gb ?? 0);
    bucket.totalRxGb += Number(item.total_rx_gb ?? item.rx_gb ?? 0);
    if (index === 0 && !selectedNetworkInterface) {
      selectedNetworkInterface = key;
    }
  });
  return Array.from(map.values()).map((entry) => ({
    ...entry,
    txHistory: entry.txHistory.slice(-60),
    rxHistory: entry.rxHistory.slice(-60),
    connectionType: entry.connectionType || (uiSettings.language === "ko" ? "이더넷" : "Ethernet"),
    totalTxGb: Number(entry.totalTxGb.toFixed(2)),
    totalRxGb: Number(entry.totalRxGb.toFixed(2)),
  }));
}

function numericNetworkSeries(values) {
  if (!Array.isArray(values)) return [];
  return values
    .map((value) => Number(value))
    .filter((value) => Number.isFinite(value) && value >= 0);
}

function normalizeNetworkHistory(primary, fallback) {
  const source = numericNetworkSeries(primary);
  const alternate = numericNetworkSeries(fallback);
  const values = (source.length ? source : alternate).slice(-60);
  if (!values.length) return [0, 0];
  if (values.length === 1) return [values[0], values[0]];
  return values;
}

function lastNetworkValue(values, fallback = 0) {
  const series = numericNetworkSeries(values);
  if (series.length) return series[series.length - 1];
  const value = Number(fallback);
  return Number.isFinite(value) ? value : 0;
}

function syncNetworkInterfaceSelect(interfaces) {
  if (!networkInterfaceSelect) return;
  const selectedStillExists = interfaces.some((item) => item.id === selectedNetworkInterface);
  if (!selectedStillExists) {
    selectedNetworkInterface = interfaces[0]?.id || "";
  }
  networkInterfaceSelect.replaceChildren();
  if (!interfaces.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No NIC";
    networkInterfaceSelect.appendChild(option);
    networkInterfaceSelect.value = "";
    networkInterfaceSelect.disabled = true;
    return;
  }
  networkInterfaceSelect.disabled = false;
  interfaces.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.label;
    networkInterfaceSelect.appendChild(option);
  });
  networkInterfaceSelect.value = selectedNetworkInterface || interfaces[0].id;
}

function renderNetworkInterfaceStrip(interfaces, selected) {
  if (!networkMiniChartStrip) return;
  const list = interfaces.length ? interfaces.slice(0, 3) : [];
  networkMiniChartStrip.replaceChildren();
  if (!list.length) {
    const empty = document.createElement("div");
    empty.className = "network-mini-chart-empty";
    empty.textContent = "NIC 데이터가 없습니다.";
    networkMiniChartStrip.appendChild(empty);
    return;
  }
  list.forEach((item) => {
    const card = document.createElement("article");
    card.className = `network-mini-chart-card${item.id === selected?.id ? " active" : ""}`;
    const isSelected = item.id === selected?.id;
    card.innerHTML = `
        <div class="network-mini-chart-head">
          <strong>${escapeHtml(item.label)}</strong>
          <span>${escapeHtml(isSelected ? (uiSettings.language === "ko" ? "선택" : "Selected") : "NIC")}</span>
        </div>
        <svg class="network-mini-flow" viewBox="0 0 640 120" preserveAspectRatio="none" role="img" aria-label="${escapeHtml(item.label)} traffic chart">
          ${buildMiniSparkline(item.txHistory, isSelected ? "#0b5cad" : "#7aa2d6")}
          ${buildMiniSparkline(item.rxHistory, isSelected ? "#f28f16" : "#c8a36f")}
        </svg>
        <div class="network-mini-chart-foot">
          <span>TX ${formatCompactRate(item.txHistory)} / ${item.totalTxGb.toFixed(1)} GB</span>
        <span>RX ${formatCompactRate(item.rxHistory)} / ${item.totalRxGb.toFixed(1)} GB</span>
      </div>
    `;
    card.addEventListener("click", () => {
      selectedNetworkInterface = item.id;
      if (latestNetworkStatusData) renderNetworkStatus(latestNetworkStatusData);
    });
    networkMiniChartStrip.appendChild(card);
  });
}

function threatTone(result = "") {
  const value = String(result).toUpperCase();
  if (value.includes("위험") || value.includes("RISK") || value.includes("DANGER")) return "danger";
  if (value.includes("주의") || value.includes("WARN")) return "warn";
  return "normal";
}

function renderThreatDetection(data = {}) {
  if (!threatSummaryCards || !threatResultTable) return;
  const summary = data.summary || {};
  const results = Array.isArray(data.results) ? data.results : [];
  const policy = data.policy || {};
  const veeamMalwareApi = data.veeam_malware_api || {};
  renderThreatManualProof(data.manual_scan || {});
  const cards = [
    { label: "최근 검사 상태", value: summary.status || "-", meta: summary.status_detail || "정상 / 주의 / 위험", tone: threatTone(summary.status) },
    { label: "위험 점수", value: String(summary.score ?? "-"), meta: "0~30 정상 · 31~70 주의 · 71~100 위험", tone: threatTone(summary.status) },
    { label: "탐지된 의심 항목", value: `${summary.suspicious_count ?? 0}건`, meta: "악성코드·랜섬웨어·비정상 변경", tone: Number(summary.suspicious_count || 0) > 0 ? "warn" : "normal" },
    { label: "마지막 검사 시간", value: summary.last_scan_at || "-", meta: summary.engine || "Windows Defender + YARA + Hash", tone: "normal" },
  ];
  threatSummaryCards.innerHTML = cards.map((card) => `
    <article class="threat-summary-card threat-${card.tone}">
      <span>${escapeHtml(card.label)}</span>
      <strong>${escapeHtml(card.value)}</strong>
      <em>${escapeHtml(card.meta)}</em>
    </article>
  `).join("");
  if (threatPolicyBadge) {
    threatPolicyBadge.textContent = policy.risk_action || "Air-gap 강제 유지 + 재연결 차단";
  }
  if (threatVeeamApiPanel) {
    const apiStatus = veeamMalwareApi.connected ? "연동 준비" : "연동 대기";
    const apiStatusClass = veeamMalwareApi.connected ? "ready" : "pending";
    threatVeeamApiPanel.innerHTML = `
      <div>
        <span class="threat-veeam-api-badge">VEEAM MALWARE REST API</span>
        <h2><strong>Veeam Malware Detection</strong> 연동 상태</h2>
        <p>Veeam 백업 세션의 Malware Detection 결과를 LOCK-FIX 위협 점수와 Air-gap 정책에 연결합니다.</p>
      </div>
      <div class="threat-veeam-api-grid">
        <article><span>API 상태</span><strong class="threat-api-status threat-api-${apiStatusClass}">${escapeHtml(apiStatus)}</strong></article>
        <article><span>Endpoint</span><strong>${escapeHtml(veeamMalwareApi.endpoint || "-")}</strong></article>
        <article><span>최근 Malware 결과</span><strong class="threat-${threatTone(veeamMalwareApi.last_result || "정상")}">${escapeHtml(veeamMalwareApi.last_result || "-")}</strong></article>
      </div>
    `;
  }
  threatResultTable.innerHTML = results.map((item) => `
    <tr>
      <td>${escapeHtml(item.scan_time || "-")}</td>
      <td>${escapeHtml(item.repository || "-")}</td>
      <td>${escapeHtml(item.backup_job || "-")}</td>
      <td><span class="threat-result-pill threat-${threatTone(item.result)}">${escapeHtml(item.result || "-")}</span></td>
      <td><strong class="threat-score threat-${threatTone(item.result)}">${escapeHtml(String(item.score ?? "-"))}</strong></td>
      <td>${escapeHtml(String(item.detection_count ?? 0))}건</td>
      <td>${escapeHtml(item.action_status || "-")}</td>
      <td><button type="button" class="threat-detail-button" data-threat-id="${escapeHtml(item.id || "")}">상세</button></td>
    </tr>
  `).join("") || `<tr><td colspan="8">위협 탐지 이력이 없습니다.</td></tr>`;
  renderThreatDetail(results[0] || null);
}

function renderThreatManualProof(scan = {}) {
  if (!threatManualProofPanel) return;
  if (!scan || !scan.scan_id) {
    threatManualProofPanel.hidden = true;
    threatManualProofPanel.innerHTML = "";
    return;
  }
  const evidence = Array.isArray(scan.evidence) ? scan.evidence : [];
  const sampleHashes = Array.isArray(scan.sample_hashes) ? scan.sample_hashes : [];
  const statusTone = threatTone(scan.result || "");
  threatManualProofPanel.hidden = false;
  threatManualProofPanel.innerHTML = `
    <div class="threat-manual-proof-head">
      <div>
        <span>MANUAL SCAN PROOF</span>
        <h2>수동 검사 실행 증적</h2>
        <p>검사 ID, 대상 저장소, 실행 시간, 샘플 해시와 점검 결과를 확인합니다.</p>
      </div>
      <strong class="threat-result-pill threat-${statusTone}">${escapeHtml(scan.result || "-")}</strong>
    </div>
    <div class="threat-manual-proof-grid">
      <article><span>검사 ID</span><strong>${escapeHtml(scan.scan_id || "-")}</strong></article>
      <article><span>실행 사용자</span><strong>${escapeHtml(scan.actor || "-")}</strong></article>
      <article><span>검사 시작</span><strong>${escapeHtml(scan.started_at || "-")}</strong></article>
      <article><span>검사 종료</span><strong>${escapeHtml(scan.completed_at || "-")}</strong></article>
      <article><span>대상 Repository</span><strong>${escapeHtml(scan.repository_path || "-")}</strong></article>
      <article><span>검사 파일</span><strong>${escapeHtml(String(scan.scanned_files ?? 0))}개</strong></article>
    </div>
    <div class="threat-manual-proof-evidence">
      ${evidence.map((item) => `
        <article class="threat-proof-${String(item.status || "").toLowerCase()}">
          <span>${escapeHtml(item.status || "-")}</span>
          <strong>${escapeHtml(item.name || "-")}</strong>
          <p>${escapeHtml(item.detail || "-")}</p>
        </article>
      `).join("")}
    </div>
    ${sampleHashes.length ? `
      <div class="threat-manual-hash-list">
        <strong>샘플 SHA-256 증적</strong>
        ${sampleHashes.slice(0, 5).map((item) => `
          <p><span>${escapeHtml(item.path || "-")}</span><code>${escapeHtml(item.sha256_64k || "-")}</code></p>
        `).join("")}
      </div>
    ` : ""}
  `;
}

function renderThreatDetail(item) {
  if (!threatDetailPanel) return;
  if (!item) {
    threatDetailPanel.hidden = true;
    return;
  }
  threatDetailPanel.hidden = false;
  const detections = Array.isArray(item.detections) ? item.detections : [];
  const memoText = item.admin_note || "정책 기준에 따라 감사로그와 승인 워크플로우에 연결됩니다.";
  threatDetailPanel.innerHTML = `
    <div class="threat-detail-head">
      <div>
        <span>SCAN DETAIL</span>
        <h2>${escapeHtml(item.repository || "-")} · ${escapeHtml(item.backup_job || "-")}</h2>
        <p>${escapeHtml(item.backup_file_path || "-")}</p>
      </div>
      <strong class="threat-${threatTone(item.result)}">${escapeHtml(item.result || "-")} · ${escapeHtml(String(item.score ?? "-"))}</strong>
    </div>
    <div class="threat-detail-grid">
      <div><span>백업 완료 시간</span><strong>${escapeHtml(item.backup_completed_at || "-")}</strong></div>
      <div><span>검사 시작</span><strong>${escapeHtml(item.scan_started_at || item.scan_time || "-")}</strong></div>
      <div><span>검사 종료</span><strong>${escapeHtml(item.scan_ended_at || "-")}</strong></div>
      <div><span>검사 엔진</span><strong>${escapeHtml(item.engine || "-")}</strong></div>
      <div><span>LOCK-FIX 조치</span><strong>${escapeHtml(item.lockfix_action || item.action_status || "-")}</strong></div>
      <div><span>감사로그</span><strong>${escapeHtml(item.audit_log_id || "-")}</strong></div>
    </div>
    <div class="threat-detection-list">
      <h3>탐지된 의심 항목</h3>
      <table class="threat-table">
        <thead><tr><th>탐지 유형</th><th>파일 경로</th><th>탐지 근거</th><th>심각도</th><th>처리 상태</th></tr></thead>
        <tbody>
          ${detections.map((detection) => `
            <tr>
              <td>${escapeHtml(detection.type || "-")}</td>
              <td>${escapeHtml(detection.file_path || "-")}</td>
              <td>${escapeHtml(detection.evidence || "-")}</td>
              <td>${escapeHtml(detection.severity || "-")}</td>
              <td>${escapeHtml(detection.status || "-")}</td>
            </tr>
          `).join("") || `<tr><td colspan="5">탐지된 의심 항목이 없습니다.</td></tr>`}
        </tbody>
      </table>
    </div>
    <section class="threat-admin-note" data-threat-memo-target="${escapeHtml(item.id || "")}">
      <div class="threat-admin-note-head">
        <span>${escapeHtml(t("threat.adminMemo"))}</span>
        <div>
          <button type="button" class="subtle-show-button" data-threat-memo-more="${escapeHtml(item.id || "")}">${escapeHtml(t("threat.memoMore"))}</button>
          <button type="button" class="primary-mini-button" data-threat-memo-save="${escapeHtml(item.id || "")}">${escapeHtml(t("threat.memoSave"))}</button>
        </div>
      </div>
      <textarea data-threat-memo-input="${escapeHtml(item.id || "")}">${escapeHtml(memoText)}</textarea>
      <p class="threat-admin-note-meta">${escapeHtml(item.admin_note_updated_at ? `${item.admin_note_updated_at} · ${item.admin_note_actor || "-"}` : "")}</p>
      <div class="threat-admin-note-history" data-threat-memo-history="${escapeHtml(item.id || "")}" hidden></div>
    </section>
  `;
}

async function saveThreatAdminMemo(targetId) {
  const input = threatDetailPanel?.querySelector(`[data-threat-memo-input="${CSS.escape(targetId)}"]`);
  if (!input) return;
  const button = threatDetailPanel?.querySelector(`[data-threat-memo-save="${CSS.escape(targetId)}"]`);
  if (button) button.disabled = true;
  try {
    const result = await requestJson("/api/threat-detection/admin-note", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ targetId, note: input.value }),
    });
    renderThreatMemoHistory(targetId, result.items || []);
    const meta = threatDetailPanel?.querySelector(".threat-admin-note-meta");
    if (meta && result.item) meta.textContent = `${result.item.created_at} · ${result.item.actor || "-"}`;
  } catch (error) {
    alert(error.message || "memo save failed");
  } finally {
    if (button) button.disabled = false;
  }
}

function renderThreatMemoHistory(targetId, items = []) {
  const history = threatDetailPanel?.querySelector(`[data-threat-memo-history="${CSS.escape(targetId)}"]`);
  if (!history) return;
  history.hidden = false;
  history.innerHTML = `
    <strong>${escapeHtml(t("threat.memoHistory"))}</strong>
    ${items.length ? `
      <ul>
        ${items.map((item) => `
          <li>
            <span>${escapeHtml(item.created_at || "-")} · ${escapeHtml(item.actor || "-")}</span>
            <p>${escapeHtml(item.note || "")}</p>
          </li>
        `).join("")}
      </ul>
    ` : `<p>${escapeHtml(t("threat.memoEmpty"))}</p>`}
  `;
}

async function loadThreatMemoHistory(targetId) {
  const history = threatDetailPanel?.querySelector(`[data-threat-memo-history="${CSS.escape(targetId)}"]`);
  if (!history) return;
  if (!history.hidden) {
    history.hidden = true;
    return;
  }
  const data = await requestJson(`/api/threat-detection/admin-notes?targetId=${encodeURIComponent(targetId)}`);
  renderThreatMemoHistory(targetId, Array.isArray(data.items) ? data.items : []);
}

async function reloadThreatDetection() {
  const data = await requestJson("/api/threat-detection");
  renderThreatDetection(data);
  return data;
}

async function runThreatManualScan() {
  if (!threatManualScanButton) return;
  const originalText = threatManualScanButton.textContent;
  threatManualScanButton.disabled = true;
  threatManualScanButton.textContent = "검사 중...";
  if (threatManualProofPanel) {
    threatManualProofPanel.hidden = false;
    threatManualProofPanel.innerHTML = `
      <div class="threat-manual-proof-head">
        <div>
          <span>MANUAL SCAN PROOF</span>
          <h2>수동 검사가 실행 중입니다.</h2>
          <p>저장소 경로, 샘플 해시, 의심 확장자, Air-Gap 정책을 확인하고 있습니다.</p>
        </div>
        <strong class="threat-result-pill threat-warn">RUNNING</strong>
      </div>
    `;
  }
  try {
    const result = await requestJson("/api/threat-detection/manual-scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requestedAt: new Date().toISOString() }),
      timeoutMs: 30000,
    });
    renderThreatDetection(result.summary || {});
    renderThreatManualProof(result.manual_scan || {});
  } catch (error) {
    if (threatManualProofPanel) {
      threatManualProofPanel.hidden = false;
      threatManualProofPanel.innerHTML = `
        <div class="threat-manual-proof-head">
          <div>
            <span>MANUAL SCAN PROOF</span>
            <h2>수동 검사 실행 실패</h2>
            <p>${escapeHtml(error.message || "manual scan failed")}</p>
          </div>
          <strong class="threat-result-pill threat-danger">FAILED</strong>
        </div>
      `;
    }
    console.warn("Unable to run manual threat scan", error);
  } finally {
    threatManualScanButton.disabled = false;
    threatManualScanButton.textContent = originalText || t("threat.manualScan");
  }
}

function formatCompactRate(values) {
  const max = Math.max(0, ...values.map((value) => Number(value) || 0));
  if (max >= 1) return `${max.toFixed(1)} Mbps`;
  return `${(max * 1000).toFixed(0)} Kbps`;
}

function formatNetworkRate(value) {
  const rate = Number(value) || 0;
  if (rate >= 1000) return `${(rate / 1000).toFixed(2)} Gbps`;
  if (rate >= 1) return `${rate.toFixed(1)} Mbps`;
  return `${(rate * 1000).toFixed(1)} Kbps`;
}

function buildMiniSparkline(values, stroke) {
  const series = Array.isArray(values) ? values : [];
  if (!series.length) {
    return `<path d="M 4 108 L 636 108" fill="none" stroke="${stroke}" stroke-width="2.1" stroke-linecap="round" />`;
  }
  const max = Math.max(1, ...series.map((value) => Number(value) || 0));
  const width = 640;
  const height = 120;
  const padX = 4;
  const padY = 8;
  const plotWidth = width - padX * 2;
  const plotHeight = height - padY * 2;
  const step = plotWidth / Math.max(1, series.length - 1);
  const points = series.map((value, index) => [
    padX + index * step,
    padY + plotHeight - ((Number(value) || 0) / max) * plotHeight,
  ]);
  const path = smoothPath(points, 0.2);
  const area = `${path} L ${points[points.length - 1][0].toFixed(1)} ${padY + plotHeight} L ${points[0][0].toFixed(1)} ${padY + plotHeight} Z`;
  return `
    <path d="${area}" fill="${stroke}" fill-opacity="0.11" />
    <path d="${path}" fill="none" stroke="${stroke}" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round" />
  `;
}

function smoothPath(points, tension = 0.18) {
  if (!points.length) return "";
  if (points.length === 1) {
    const [x, y] = points[0];
    return `M ${x.toFixed(1)} ${y.toFixed(1)}`;
  }
  const commands = [`M ${points[0][0].toFixed(1)} ${points[0][1].toFixed(1)}`];
  for (let index = 0; index < points.length - 1; index += 1) {
    const current = points[index];
    const next = points[index + 1];
    const prev = points[index - 1] || current;
    const after = points[index + 2] || next;
    const cp1x = current[0] + (next[0] - prev[0]) * tension;
    const cp1y = current[1] + (next[1] - prev[1]) * tension;
    const cp2x = next[0] - (after[0] - current[0]) * tension;
    const cp2y = next[1] - (after[1] - current[1]) * tension;
    commands.push(
      `C ${cp1x.toFixed(1)} ${cp1y.toFixed(1)}, ${cp2x.toFixed(1)} ${cp2y.toFixed(1)}, ${next[0].toFixed(1)} ${next[1].toFixed(1)}`
    );
  }
  return commands.join(" ");
}

function linearPath(points) {
  if (!points.length) return "";
  return points.map(([x, y], index) => `${index ? "L" : "M"} ${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
}

function renderNetworkIpSummary(target, items, type) {
  if (!target) return;
  const key = type === "tx" ? "tx_gb" : "rx_gb";
  const label = type === "tx"
    ? (uiSettings.language === "ko" ? "Top 송신 IP" : "Top TX IP")
    : (uiSettings.language === "ko" ? "Top 수신 IP" : "Top RX IP");
  const rows = (Array.isArray(items) ? items : [])
    .filter((item) => item && item.target)
    .sort((left, right) => Number(right[key] || 0) - Number(left[key] || 0))
    .slice(0, 3);
  if (!rows.length) {
    target.innerHTML = `<span>${escapeHtml(label)}</span><em>-</em>`;
    return;
  }
  const primary = rows[0];
  const secondaryRows = rows.slice(1);
  const total = rows.reduce((sum, item) => sum + Number(item[key] || 0), 0);
  const primaryValue = Number(primary[key] || 0);
  const primaryShare = total > 0 ? Math.max(8, Math.min(100, (primaryValue / total) * 100)) : 0;
  target.innerHTML = `
    <div class="network-ip-main">
      <span>${escapeHtml(label)}</span>
      <div class="network-ip-primary-rank">
        <i>1</i>
        <strong>${escapeHtml(primary.target)}</strong>
      </div>
      <em>${primaryValue.toFixed(2)} GB</em>
      <div class="network-ip-share" aria-hidden="true"><b style="width: ${primaryShare.toFixed(1)}%"></b></div>
    </div>
    <div class="network-ip-list">
      ${secondaryRows.map((item, index) => `
        <span><i>${index + 2}</i><code>${escapeHtml(item.target)}</code><b>${Number(item[key] || 0).toFixed(2)} GB</b></span>
      `).join("")}
      ${!secondaryRows.length ? `<span><i>2</i><code>-</code><b>-</b></span>` : ""}
    </div>
  `;
}

function networkDisplayState(value) {
  const state = String(value || "-").toUpperCase();
  if (uiSettings.language !== "ko") return value || "-";
  return {
    ALLOW: "허용",
    BLOCK: "정책 차단",
    BLOCKED: "정책 차단",
    PROTECTED: "보호",
    REACHABLE: "정상",
    MANAGED: "관리",
    CHECK: "확인 필요",
  }[state] || value || "-";
}

function networkDisplayRisk(value) {
  const risk = String(value || "-");
  if (uiSettings.language !== "ko") return risk;
  return {
    Required: "필수",
    Managed: "관리 대상",
    "Not configured": "미구성",
    "Recovery only": "복구 시 승인",
    "Admin approval": "관리자 승인",
  }[risk] || risk;
}

function networkDisplayInsightTitle(value) {
  const title = String(value || "-");
  if (uiSettings.language !== "ko") return title;
  return {
    "Packet Loss": "패킷 손실",
    Latency: "지연 시간",
    "Port Exposure": "포트 노출 정책",
  }[title] || title;
}

function networkDisplayInsightDetail(value) {
  const text = String(value || "-");
  if (uiSettings.language !== "ko") return text;
  return text
    .replace(/Current loss is ([0-9.]+)%\. Keep under 1\.00% for backup traffic quality\./, "현재 손실률은 $1%입니다. 백업 트래픽 품질 기준 1.00% 이하로 유지됩니다.")
    .replace(/Average response time is ([0-9.]+) ms\. No path bottleneck is detected\./, "평균 응답 시간은 $1 ms이며 경로 병목은 감지되지 않았습니다.")
    .replace("Only Veeam REST and managed WinRM are allowed. Recovery ports remain blocked until approval.", "Veeam REST와 관리형 WinRM만 허용됩니다. 복구 포트는 승인 전까지 보호 상태로 유지됩니다.");
}

function networkDisplayEvent(value) {
  const text = String(value || "-");
  if (uiSettings.language !== "ko") {
    return text
      .replace("Veeam REST API 9419 path is reachable.", "Veeam REST OK")
      .replace("WinRM 5985 is allowed only for managed operation.", "WinRM Managed")
      .replace("SMB and RDP recovery ports remain protected until approval.", "Recovery Ports Protected")
      .replace(/Packet loss is ([0-9.]+)% and remains under the 1\.00% operating threshold\./, "Packet loss $1%, normal");
  }
  return text
    .replace("Veeam REST API 9419 path is reachable.", "Veeam REST 정상")
    .replace("WinRM 5985 is allowed only for managed operation.", "WinRM 관리")
    .replace("SMB and RDP recovery ports remain protected until approval.", "복구 포트 보호")
    .replace(/Packet loss is ([0-9.]+)% and remains under the 1\.00% operating threshold\./, "패킷 손실 $1%, 정상");
}

function networkPathTone(value) {
  const state = String(value || "").toLowerCase().replace(/\s+/g, "-");
  if (state === "blocked") return "protected";
  return state || "ready";
}

function networkLossLabel(loss) {
  if (loss >= 1) return uiSettings.language === "ko" ? "위험" : "Critical";
  if (loss >= 0.3) return uiSettings.language === "ko" ? "주의" : "Warning";
  return uiSettings.language === "ko" ? "정상" : "Normal";
}

function networkLossTone(loss) {
  if (loss >= 1) return "critical";
  if (loss >= 0.3) return "warning";
  return "good";
}

function networkLossTrendInfo(values) {
  const samples = numericNetworkSeries(values);
  if (samples.length < 3) {
    return {
      label: uiSettings.language === "ko" ? "실시간 추세" : "Live trend",
      direction: "steady",
    };
  }
  const recent = samples.slice(-6);
  const first = recent[0];
  const last = recent[recent.length - 1];
  const delta = last - first;
  const threshold = Math.max(0.03, Math.max(...recent) * 0.08);
  if (delta > threshold) {
    return {
      label: uiSettings.language === "ko" ? "상승 감지" : "Rising",
      direction: "rising",
    };
  }
  if (delta < -threshold) {
    return {
      label: uiSettings.language === "ko" ? "개선 중" : "Improving",
      direction: "improving",
    };
  }
  return {
    label: uiSettings.language === "ko" ? "안정 흐름" : "Stable",
    direction: "steady",
  };
}

function networkLossHistory(quality, analysis, loss) {
  const supplied = numericNetworkSeries(
    quality.packet_loss_history
    || quality.loss_history
    || analysis.packet_loss_history
    || analysis.loss_history
    || []
  ).slice(-28);
  if (supplied.length >= 2) {
    networkLossSamples = supplied;
  } else {
    networkLossSamples = [...networkLossSamples, loss].slice(-28);
  }
  if (networkLossSamples.length < 2) {
    networkLossSamples = [loss, loss];
  }
  return networkLossSamples;
}

function renderNetworkLossSparkline(target, values) {
  if (!target) return;
  const samples = numericNetworkSeries(values).slice(-28);
  if (!samples.length) {
    target.innerHTML = "";
    return;
  }
  const width = 220;
  const height = 44;
  const pad = { left: 4, right: 4, top: 6, bottom: 8 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const maxValue = Math.max(0.1, ...samples) * 1.18;
  const points = samples.map((value, index) => [
    pad.left + (plotWidth * index) / Math.max(1, samples.length - 1),
    pad.top + plotHeight - (plotHeight * Math.min(maxValue, Number(value) || 0)) / maxValue,
  ]);
  const path = linearPath(points);
  const area = `${path} L ${points[points.length - 1][0].toFixed(1)} ${height - pad.bottom} L ${points[0][0].toFixed(1)} ${height - pad.bottom} Z`;
  target.innerHTML = `
    <path class="network-loss-spark-area" d="${area}"></path>
    <path class="network-loss-spark-line" d="${path}"></path>
    <circle class="network-loss-spark-dot" cx="${points[points.length - 1][0].toFixed(1)}" cy="${points[points.length - 1][1].toFixed(1)}" r="3.2"></circle>
  `;
}

function setNetworkQualityChipTone(node, tone) {
  const chip = node?.closest(".network-quality-chip");
  if (!chip) return;
  chip.classList.remove("quality-good", "quality-warning", "quality-critical", "quality-info");
  chip.classList.add(`quality-${tone}`);
}

function setNetworkQualityValue(node, value, unit = "") {
  if (!node) return;
  node.style.setProperty("display", "flex", "important");
  node.style.setProperty("align-items", "baseline", "important");
  node.style.setProperty("gap", "4px", "important");
  node.style.setProperty("font-size", "50px", "important");
  node.style.setProperty("font-weight", "950", "important");
  node.style.setProperty("line-height", "0.92", "important");
  node.innerHTML = `<span class="network-quality-value" style="font-size:50px!important;font-weight:950!important;line-height:.92!important;">${escapeHtml(String(value))}</span>${unit ? `<span class="network-quality-unit" style="font-size:18px!important;font-weight:850!important;line-height:1!important;">${escapeHtml(unit)}</span>` : ""}`;
}

function updateNetworkPortToggle() {
  if (!networkPortToggle || !networkPortTable) return;
  networkPortToggle.textContent = networkPortsCollapsed ? t("network.portBadgeCollapsed") : t("network.portBadge");
  networkPortToggle.setAttribute("aria-expanded", String(!networkPortsCollapsed));
  networkPortTable.setAttribute("aria-hidden", String(networkPortsCollapsed));
  networkPortTable.classList.toggle("network-port-list-collapsed", networkPortsCollapsed);
  if (networkPortsCollapsed) {
    networkPortTable.style.setProperty("display", "none", "important");
  } else {
    networkPortTable.style.removeProperty("display");
  }
}

function updateNetworkPathToggle() {
  if (!networkPathToggle || !networkPathStatus) return;
  networkPathToggle.textContent = networkPathCollapsed ? t("network.pathBadgeCollapsed") : t("network.pathBadge");
  networkPathToggle.setAttribute("aria-expanded", String(!networkPathCollapsed));
  networkPathStatus.setAttribute("aria-hidden", String(networkPathCollapsed));
  networkPathStatus.classList.toggle("network-path-list-collapsed", networkPathCollapsed);
  if (networkPathCollapsed) {
    networkPathStatus.style.setProperty("display", "none", "important");
  } else {
    networkPathStatus.style.removeProperty("display");
  }
}

function updateNetworkInsightToggle() {
  if (!networkInsightToggle || !networkInsights) return;
  networkInsightToggle.textContent = networkInsightsCollapsed ? t("network.insightBadgeCollapsed") : t("network.insightBadgeExpanded");
  networkInsightToggle.setAttribute("aria-expanded", String(!networkInsightsCollapsed));
  networkInsights.setAttribute("aria-hidden", String(networkInsightsCollapsed));
  networkInsights.classList.toggle("network-insight-list-collapsed", networkInsightsCollapsed);
  if (networkInsightsCollapsed) {
    networkInsights.style.setProperty("display", "none", "important");
  } else {
    networkInsights.style.removeProperty("display");
  }
}

function networkScaleCeil(maxValue) {
  const value = Math.max(0.1, Number(maxValue) || 0);
  const exponent = Math.pow(10, Math.floor(Math.log10(value)));
  const normalized = value / exponent;
  const step = normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10;
  return step * exponent;
}

function alignNetworkHistory(values, count) {
  const source = normalizeNetworkHistory(values, []);
  if (source.length >= count) return source.slice(source.length - count);
  return Array(count - source.length).fill(source[0] || 0).concat(source);
}

function updateNetworkFlowModeControls() {
  networkFlowModeButtons.forEach((button) => {
    const mode = button.dataset.networkFlowMode;
    const active = activeNetworkFlowMode === "both" || activeNetworkFlowMode === mode;
    button.classList.toggle("active", active);
    button.classList.toggle("muted", activeNetworkFlowMode !== "both" && !active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
}

function setNetworkFlowMode(mode) {
  const nextMode = activeNetworkFlowMode === mode ? "both" : mode;
  activeNetworkFlowMode = ["tx", "rx"].includes(nextMode) ? nextMode : "both";
  updateNetworkFlowModeControls();
  if (latestNetworkStatusData) renderNetworkStatus(latestNetworkStatusData);
}

function drawCombinedNetworkFlow(target, txValues, rxValues, displayMode = "both") {
  if (!target) return 0;
  const txSource = normalizeNetworkHistory(txValues, []);
  const rxSource = normalizeNetworkHistory(rxValues, []);
  const sampleCount = Math.max(2, Math.min(60, Math.max(txSource.length, rxSource.length)));
  const tx = alignNetworkHistory(txSource, sampleCount);
  const rx = alignNetworkHistory(rxSource, sampleCount);
  const mode = ["tx", "rx"].includes(displayMode) ? displayMode : "both";
  const showTx = mode !== "rx";
  const showRx = mode !== "tx";
  const visibleValues = [
    ...(showTx ? tx : []),
    ...(showRx ? rx : []),
  ];
  const width = 1280;
  const height = 320;
  const pad = { left: 2, right: 10, top: 28, bottom: 46 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const maxValue = networkScaleCeil(Math.max(0.1, ...visibleValues) * 1.12);
  const x = (index) => pad.left + (plotWidth * index) / Math.max(1, sampleCount - 1);
  const y = (value) => pad.top + plotHeight - (plotHeight * Math.min(maxValue, Number(value) || 0)) / maxValue;
  const txPoints = tx.map((value, index) => [x(index), y(value)]);
  const rxPoints = rx.map((value, index) => [x(index), y(value)]);
  const txPath = linearPath(txPoints);
  const rxPath = linearPath(rxPoints);
  const areaPath = (points) => `${linearPath(points)} L ${points[points.length - 1][0].toFixed(1)} ${pad.top + plotHeight} L ${points[0][0].toFixed(1)} ${pad.top + plotHeight} Z`;
  const rowCount = 6;
  const gridRows = Array.from({ length: rowCount + 1 }, (_, index) => {
    const value = maxValue - (maxValue * index) / rowCount;
    const gridY = y(value);
    const major = index === 0 || index === rowCount || index === Math.round(rowCount * 0.3);
    return `<line x1="${pad.left}" y1="${gridY.toFixed(1)}" x2="${(width - pad.right).toFixed(1)}" y2="${gridY.toFixed(1)}" class="network-task-grid${major ? " grid-major" : ""}"></line>`;
  }).join("");
  const gridColumns = Array.from({ length: 11 }, (_, index) => {
    const gridX = pad.left + (plotWidth * index) / 10;
    return `<line x1="${gridX.toFixed(1)}" y1="${pad.top}" x2="${gridX.toFixed(1)}" y2="${(height - pad.bottom).toFixed(1)}" class="network-task-grid network-task-grid-vertical"></line>`;
  }).join("");
  target.setAttribute("viewBox", `0 0 ${width} ${height}`);
  target.setAttribute("preserveAspectRatio", "none");
  target.innerHTML = `
    <defs>
      <linearGradient id="combinedTxFill" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0%" stop-color="#f97316" stop-opacity="0.13"></stop>
        <stop offset="100%" stop-color="#f97316" stop-opacity="0.01"></stop>
      </linearGradient>
      <linearGradient id="combinedRxFill" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0%" stop-color="#0ea5a3" stop-opacity="0.12"></stop>
        <stop offset="100%" stop-color="#0ea5a3" stop-opacity="0.01"></stop>
      </linearGradient>
      <filter id="combinedLineGlow" x="-12%" y="-12%" width="124%" height="124%">
        <feGaussianBlur stdDeviation="0.75" result="blur"></feGaussianBlur>
        <feMerge>
          <feMergeNode in="blur"></feMergeNode>
          <feMergeNode in="SourceGraphic"></feMergeNode>
        </feMerge>
      </filter>
    </defs>
    <rect x="${pad.left}" y="${pad.top}" width="${plotWidth}" height="${plotHeight}" class="network-task-plot"></rect>
    ${gridRows}
    ${gridColumns}
    ${showRx ? `<path d="${areaPath(rxPoints)}" fill="url(#combinedRxFill)"></path>` : ""}
    ${showTx ? `<path d="${areaPath(txPoints)}" fill="url(#combinedTxFill)"></path>` : ""}
    ${showRx ? `<path d="${rxPath}" fill="none" stroke="#0ea5a3" stroke-width="1.95" stroke-linecap="round" stroke-linejoin="round" filter="url(#combinedLineGlow)"></path>` : ""}
    ${showTx ? `<path d="${txPath}" fill="none" stroke="#f97316" stroke-width="2.15" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="4 2"></path>` : ""}
    ${showTx ? `<circle cx="${txPoints[txPoints.length - 1][0].toFixed(1)}" cy="${txPoints[txPoints.length - 1][1].toFixed(1)}" r="4.2" fill="#f97316"></circle>` : ""}
    ${showRx ? `<circle cx="${rxPoints[rxPoints.length - 1][0].toFixed(1)}" cy="${rxPoints[rxPoints.length - 1][1].toFixed(1)}" r="4.8" fill="#0ea5a3" class="network-chart-pulse"></circle>` : ""}
  `;
  return maxValue;
}

function networkPathDisplay(item) {
  const rawName = String(item?.name || "-");
  const target = String(item?.target || "-");
  const service = rawName
    .replace(/^LOCK-FIX\s*->\s*/i, "")
    .replace("Recovery Ports", uiSettings.language === "ko" ? "복구 포트" : "Recovery Ports")
    .replace("Gateway", uiSettings.language === "ko" ? "스토리지 게이트웨이" : "Storage Gateway");
  const arrow = "→";
  return {
    title: service || rawName,
    target: `LOCK-FIX ${arrow} ${target}`,
  };
}

function renderNetworkAnalysis(analysis) {
  const quality = analysis.quality || {};
  const ports = Array.isArray(analysis.ports) ? analysis.ports : [];
  const insights = Array.isArray(analysis.insights) ? analysis.insights : [];
  const pathStatus = Array.isArray(analysis.path_status) ? analysis.path_status : [];
  const events = Array.isArray(analysis.events) ? analysis.events : [];
  const loss = Number(quality.packet_loss_percent || 0);
  const lossTone = networkLossTone(loss);
  const lossHistory = networkLossHistory(quality, analysis, loss);
  const lossTrend = networkLossTrendInfo(lossHistory);
  if (networkLossCard) {
    networkLossCard.dataset.lossTone = lossTone;
    networkLossCard.dataset.lossTrend = lossTrend.direction;
  }
  if (networkLossScore) {
    networkLossScore.textContent = `${loss.toFixed(2)}%`;
    networkLossScore.className = `network-loss-${lossTone}`;
  }
  if (networkLossState) {
    networkLossState.textContent = `${networkLossLabel(loss)} · ${lossTrend.label}`;
    networkLossState.className = `loss-state-${lossTone}`;
  }
  if (networkLossTrend) networkLossTrend.textContent = lossTrend.label;
  renderNetworkLossSparkline(networkLossSparkline, lossHistory);
  const latency = Number(quality.latency_ms || 0);
  const jitter = Number(quality.jitter_ms || 0);
  const allowedCount = ports.filter((item) => String(item.state || "").toUpperCase().startsWith("ALLOW")).length;
  const blockedCount = ports.filter((item) => ["BLOCK", "PROTECTED"].includes(String(item.state || "").toUpperCase())).length;
  if (networkLatency) {
    setNetworkQualityValue(networkLatency, latency.toFixed(0), "ms");
    setNetworkQualityChipTone(networkLatency, latency >= 80 ? "critical" : (latency >= 35 ? "warning" : "good"));
  }
  if (networkJitter) {
    setNetworkQualityValue(networkJitter, jitter.toFixed(0), "ms");
    setNetworkQualityChipTone(networkJitter, jitter >= 25 ? "critical" : (jitter >= 10 ? "warning" : "good"));
  }
  if (networkAllowedPorts) {
    setNetworkQualityValue(networkAllowedPorts, allowedCount);
    setNetworkQualityChipTone(networkAllowedPorts, allowedCount ? "good" : "warning");
  }
  if (networkBlockedPorts) {
    setNetworkQualityValue(networkBlockedPorts, blockedCount);
    setNetworkQualityChipTone(networkBlockedPorts, blockedCount ? "info" : "warning");
  }
  if (networkOpsSummary) {
    const protectedCount = ports.filter((item) => ["BLOCK", "PROTECTED"].includes(String(item.state || "").toUpperCase())).length;
    const veeamRestPort = ports.find((item) => Number(item.port) === 9419);
    const veeamCurrentIpMatch = veeamRestPort?.veeam_config?.current_ip_match !== false && String(veeamRestPort?.state || "").toUpperCase() === "ALLOW";
    const summaryItems = [
      { label: "Veeam REST", value: veeamCurrentIpMatch ? (uiSettings.language === "ko" ? "현재 IP" : "Current IP") : (uiSettings.language === "ko" ? "IP 확인" : "Check IP"), tone: veeamCurrentIpMatch ? "ok" : "risk" },
      { label: "WinRM", value: ports.some((item) => Number(item.port) === 5985 && String(item.state).toUpperCase() === "ALLOW") ? (uiSettings.language === "ko" ? "관리" : "Managed") : (uiSettings.language === "ko" ? "차단" : "Blocked"), tone: "info" },
      { label: uiSettings.language === "ko" ? "복구 포트" : "Recovery Ports", value: uiSettings.language === "ko" ? `${protectedCount}개 보호` : `${protectedCount} Protected`, tone: "protected" },
      { label: uiSettings.language === "ko" ? "패킷 손실" : "Packet Loss", value: `${loss.toFixed(2)}%`, tone: loss >= 1 ? "risk" : (loss >= 0.3 ? "warn" : "ok") },
    ];
    networkOpsSummary.innerHTML = summaryItems.map((item) => `
      <article class="network-ops-summary-item summary-${escapeHtml(item.tone)}">
        <span>${escapeHtml(item.label)}</span>
        <strong>${escapeHtml(item.value)}</strong>
      </article>
    `).join("");
  }
  if (networkPortTable) {
    networkPortTable.innerHTML = ports.map((item) => {
      const state = String(item.state || "").toUpperCase();
      const veeamConfig = item.veeam_config || {};
      const isVeeamRest = Number(item.port) === 9419;
      const isStaleAllow = isVeeamRest && (state === "ALLOW_STALE" || veeamConfig.current_ip_match === false);
      const stateClass = isStaleAllow
        ? "allow-stale"
        : (state.toLowerCase() === "block" || state.toLowerCase() === "blocked" ? "protected" : state.toLowerCase());
      const stateLabel = isStaleAllow
        ? (uiSettings.language === "ko" ? "허용" : "Allow")
        : networkDisplayState(item.state);
      const riskLabel = isStaleAllow
        ? (uiSettings.language === "ko" ? "과거 IP" : "Past IP")
        : (isVeeamRest ? (uiSettings.language === "ko" ? "현재 IP" : "Current IP") : networkDisplayRisk(item.risk));
      const targetLine = item.target
        ? `<small>${escapeHtml(uiSettings.language === "ko" ? "대상" : "Target")} ${escapeHtml(item.target)}</small>`
        : "";
      const stateControl = isVeeamRest
        ? `<button type="button" class="network-port-state-button" data-veeam-sync title="${escapeHtml(uiSettings.language === "ko" ? "현재 agent 설치 IP 기준으로 실행 설정을 갱신합니다." : "Sync execution settings to the current agent install IP.")}">${escapeHtml(stateLabel)}</button>`
        : `<b>${escapeHtml(stateLabel)}</b>`;
      return `
        <article class="network-port-row port-${escapeHtml(stateClass)}">
          <div>
            <strong>${escapeHtml(item.port || "-")}</strong>
            <span>${escapeHtml(item.service || "-")} · ${escapeHtml(item.protocol || "TCP")}</span>
            ${targetLine}
          </div>
          <div class="network-port-metrics">
            ${stateControl}
            <em>${escapeHtml(riskLabel)}</em>
          </div>
        </article>
      `;
    }).join("") || `<article class="network-empty-row">No port policy data</article>`;
    updateNetworkPortToggle();
  }
  if (networkInsights) {
    networkInsights.innerHTML = insights.map((item) => `
      <article class="network-insight-row insight-${escapeHtml(String(item.level || "info").toLowerCase())}">
        <b>${escapeHtml(networkDisplayInsightTitle(item.title))}</b>
        <span>${escapeHtml(networkDisplayInsightDetail(item.detail))}</span>
      </article>
    `).join("") || `<article class="network-empty-row">No analysis data</article>`;
    updateNetworkInsightToggle();
  }
  if (networkPathStatus) {
    networkPathStatus.innerHTML = pathStatus.map((item) => {
      const state = networkPathTone(item.state || "Ready");
      const latency = item.latency_ms === null || item.latency_ms === undefined ? "-" : `${Number(item.latency_ms || 0).toFixed(0)} ms`;
      const display = networkPathDisplay(item);
      return `
        <article class="network-path-row path-${escapeHtml(state)}">
          <div>
            <strong>${escapeHtml(display.title)}</strong>
            <span>${escapeHtml(display.target)}</span>
          </div>
          <div class="network-path-metrics">
            <b>${escapeHtml(networkDisplayState(item.state))}</b>
            <em>${escapeHtml(latency)}</em>
          </div>
        </article>
      `;
    }).join("") || `<article class="network-empty-row">No path status data</article>`;
    updateNetworkPathToggle();
  }
  if (networkEventList) {
    networkEventList.innerHTML = events.map((item) => `
      <article class="network-event-row event-${escapeHtml(String(item.level || "info").toLowerCase())}">
        <time>${escapeHtml(item.time || "-")}</time>
        <span>${escapeHtml(networkDisplayEvent(item.message))}</span>
      </article>
    `).join("") || `<article class="network-empty-row">No recent network events</article>`;
  }
}

function drawFlowChart(target, values, type) {
  const width = 640;
  const height = 204;
  const pad = { left: 22, right: 22, top: 18, bottom: 24 };
  const chartWidth = width - pad.left - pad.right;
  const chartHeight = height - pad.top - pad.bottom;
  const maxValue = Math.max(...values, 1);
  const x = (index) => pad.left + (chartWidth * index) / Math.max(1, values.length - 1);
  const y = (value) => pad.top + chartHeight - (chartHeight * value) / maxValue;
  const points = values.map((value, index) => [x(index), y(value)]);
  const path = smoothPath(points, 0.16);
  const area = `${path} L ${x(values.length - 1).toFixed(1)} ${pad.top + chartHeight} L ${pad.left.toFixed(1)} ${pad.top + chartHeight} Z`;
  const color = type === "tx" ? "#2388ff" : "#37dca0";
  const gridRows = [0.25, 0.5, 0.75].map((ratio) => {
    const gridY = pad.top + chartHeight * ratio;
    return `<line x1="${pad.left}" y1="${gridY.toFixed(1)}" x2="${(width - pad.right).toFixed(1)}" y2="${gridY.toFixed(1)}" class="network-chart-grid"></line>`;
  }).join("");
  const gridColumns = Array.from({ length: 7 }, (_, index) => {
    const gridX = pad.left + (chartWidth * index) / 6;
    return `<line x1="${gridX.toFixed(1)}" y1="${pad.top}" x2="${gridX.toFixed(1)}" y2="${(height - pad.bottom).toFixed(1)}" class="network-chart-grid network-chart-grid-vertical"></line>`;
  }).join("");
  target.innerHTML = `
      <defs>
        <linearGradient id="flowFill-${type}" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="${color}" stop-opacity="0.24"></stop>
          <stop offset="62%" stop-color="${color}" stop-opacity="0.1"></stop>
          <stop offset="100%" stop-color="${color}" stop-opacity="0.03"></stop>
        </linearGradient>
        <filter id="flowGlow-${type}" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="2.4" result="blur"></feGaussianBlur>
          <feMerge>
            <feMergeNode in="blur"></feMergeNode>
            <feMergeNode in="SourceGraphic"></feMergeNode>
        </feMerge>
      </filter>
    </defs>
    <rect x="${pad.left}" y="${pad.top}" width="${chartWidth}" height="${chartHeight}" class="network-chart-plot"></rect>
    ${gridRows}
    ${gridColumns}
    <path d="${area}" fill="url(#flowFill-${type})"></path>
    <path d="${path}" fill="none" stroke="${color}" stroke-width="8" stroke-opacity="0.16" stroke-linecap="round" stroke-linejoin="round"></path>
    <path d="${path}" fill="none" stroke="${color}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#flowGlow-${type})"></path>
    <circle cx="${x(values.length - 1).toFixed(1)}" cy="${y(values[values.length - 1]).toFixed(1)}" r="8" fill="${color}" class="network-chart-pulse"></circle>
  `;
}

function renderMonitoring(data) {
  latestMonitoringData = data;
  monitoringTitle.textContent = uiSettings.language === "ko" ? "OAM - 하드웨어 사용량 모니터링" : data.title;
  const startDate = data.range.start.slice(0, 10).replaceAll(".", "-");
  const endDate = data.range.end.slice(0, 10).replaceAll(".", "-");
  if (!monitoringRange.start) {
    monitoringRange.start = startDate;
  }
  if (!monitoringRange.end) {
    monitoringRange.end = endDate;
  }
  monitoringStart.value = monitoringRange.start;
  monitoringEnd.value = monitoringRange.end;
  latestMonitoringSeries = data.series;
  renderMonitoringSummary(data);
  drawLineChart(latestMonitoringSeries);
  renderGauge(cpuGauge, "CPU", data.current.cpu, "#2c90ff");
  renderGauge(memoryGauge, "Memory", data.current.memory, "#46b865");
  renderGauge(diskGauge, "Disk", data.current.disk, "#ffa52b");
  renderGauge(networkGauge, "Network", data.current.network, "#8b5cf6");
  renderGauge(interfaceGauge, "Interface", data.current.interface, "#5a2f16");
  updateMemoryThresholdButton(data.current.memory);
  renderOperationsOverview();
}

function monitoringMetricName(metric) {
  const labels = {
    cpu: "CPU",
    memory: "Memory",
    disk: "Disk",
    network: "Network",
    interface: "Interface",
  };
  return labels[metric] || metric;
}

function monitoringMetricStats(data) {
  const thresholds = { cpu: 80, memory: 80, disk: 85, network: 75, interface: 70 };
  const metric = activeMonitoringMetric || "cpu";
  const values = (data.series || []).map((item) => Number(item[metric] || 0));
  const current = Number((data.current || {})[metric] || values[values.length - 1] || 0);
  const average = values.length ? values.reduce((sum, item) => sum + item, 0) / values.length : current;
  const peak = values.length ? Math.max(...values) : current;
  const threshold = thresholds[metric] || 80;
  return { metric, current, average, peak, threshold, warning: peak >= threshold || current >= threshold };
}

function renderMonitoringSummary(data) {
  if (!monitoringSummaryStrip) return;
  const stats = monitoringMetricStats(data);
  const items = [
    ["항목", monitoringMetricName(stats.metric)],
    ["현재", `${stats.current.toFixed(stats.current % 1 ? 1 : 0)}%`],
    ["평균", `${stats.average.toFixed(1)}%`],
    ["최대", `${stats.peak.toFixed(1)}%`],
    ["임계치", `${stats.threshold}%`],
  ];
  monitoringSummaryStrip.classList.toggle("summary-warning", stats.warning);
  monitoringSummaryStrip.innerHTML = items
    .map(([label, value]) => `<article><span>${label}</span><strong>${value}</strong></article>`)
    .join("");
}

function updateOpsClock() {
  if (!opsClock) return;
  opsClock.textContent = new Date().toLocaleString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function opsToneFromText(value, fallback = "neutral") {
  const text = String(value || "").toUpperCase();
  if (/(ERROR|FAIL|FAILED|UNREGISTERED|DENIED|WARNING_FOR_MOUNT|MISMATCH)/.test(text)) return "danger";
  if (/(WAIT|RUNNING|PENDING|START|WARN|UNKNOWN)/.test(text)) return "warn";
  if (/(OK|VALID|CONNECTED|SUCCESS|DONE|OFFLINE|ONLINE_VERIFIED|COMPLETED)/.test(text)) return "ok";
  return fallback;
}

function formatOpsLatency(veeam) {
  const value = veeam?.rest_latency_ms ?? veeam?.latency_ms;
  const numeric = Number(value);
  return Number.isFinite(numeric) && numeric >= 0 ? `${numeric}ms` : opsText("응답 시간 확인 중", "latency checking");
}

function formatOpsStatus(value) {
  const text = String(value || "-");
  if (/^ERROR$/i.test(text)) return "Check Required";
  if (/^UNKNOWN$/i.test(text)) return "Checking";
  return text;
}

function normalizeOpsEventText(text) {
  const value = String(text || "").trim();
  const lower = value.toLowerCase();
  if (lower.includes("disk.io_quiet.tick")) return "I/O quiet verification sample collected.";
  if (lower.includes("disk.io_quiet.start")) return "I/O quiet verification started.";
  if (lower.includes("disk.io_quiet.error")) return "I/O quiet verification requires attention.";
  if (lower.includes("disk.io_quiet")) return "I/O quiet verification completed.";
  if (lower.includes("disk.offline")) return "Disk Offline isolation event recorded.";
  if (lower.includes("veeam")) return value;
  return value || "LOCK-FIX event updated.";
}

function uniqueOpsEvents(items) {
  const seen = new Set();
  return items.filter((item) => {
    const key = `${item.tone}:${item.text}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, 3);
}

function latestOpsEvents(airGap, veeam) {
  const dashboardLogs = Array.isArray(latestDashboardData?.logs) ? latestDashboardData.logs : [];
  if (dashboardLogs.length) {
    const events = dashboardLogs.map((item) => ({
      time: formatLogDate(item.date),
      tone: opsToneFromText(item.type || item.content),
      text: normalizeOpsEventText(item.content || item.type),
    }));
    return uniqueOpsEvents(events);
  }
  const session = Array.isArray(airGap?.session_logs) ? airGap.session_logs[0] : null;
  const actions = Array.isArray(session?.actions) ? session.actions : [];
  if (actions.length) {
    const events = actions.map((text) => ({
      time: veeam?.last_checked || "-",
      tone: opsToneFromText(text),
      text: normalizeOpsEventText(text),
    }));
    return uniqueOpsEvents(events);
  }
  const logItems = Array.isArray(latestLogsData?.items) ? latestLogsData.items : [];
  if (logItems.length) {
    const events = logItems.map((item) => ({
      time: formatLogDate(item.date),
      tone: opsToneFromText(item.severity),
      text: normalizeOpsEventText(item.message || `${item.source || "system"} event`),
    }));
    return uniqueOpsEvents(events);
  }
  return [{
    time: "-",
    tone: "neutral",
    text: "최근 경고 또는 이벤트가 없습니다.",
  }];
}

function renderOperationsOverview() {
  if (!opsSummaryGrid || !opsEventList) return;
  const airGap = latestSourcesData?.air_gap || {};
  const veeam = airGap.veeam || {};
  const emergencySlot = airGap.emergency_access?.slot || {};
  const apiSynced = isVeeamSynced(veeam);
  const progress = Math.max(0, Math.min(100, Number(veeam.progress_percent || 0)));
  const dashboardDiskKpi = (Array.isArray(latestDashboardData?.security_kpis) ? latestDashboardData.security_kpis : [])
    .find((item) => /disk offline/i.test(String(item.label || "")));
  const diskState = emergencySlot.state || airGap.disk_state || airGap.offline_state || dashboardDiskKpi?.value || "-";
  const timeline = Array.isArray(airGap.timeline) ? airGap.timeline : [];
  const activeStep = timeline.find((item) => /ACTIVE|RUNNING|WORKING/i.test(String(item.state || "")));
  const lastStep = timeline.filter((item) => /DONE|COMPLETED|SUCCESS/i.test(String(item.state || ""))).pop();
  const liveProblem = ["stale", "error"].includes(String(opsOverviewLiveState.status || "")) && !apiSynced;
  const cards = [
    {
      label: "Veeam REST",
      value: liveProblem ? opsText("지연", "Stale") : apiSynced ? opsText("연동 정상", "Connected") : opsText("대기", "Waiting"),
      meta: `${veeam.server || "127.0.0.1"}:${veeam.port || 9419} · ${formatOpsLatency(veeam)} · ${liveStateMeta(opsOverviewLiveState)}`,
      tone: liveProblem ? "danger" : apiSynced ? "ok" : "warn",
    },
    {
      label: opsText("백업", "Backup"),
      value: `${progress}%`,
      meta: veeam.job || veeam.job_name || "Veeam session",
      tone: progress >= 100 ? "ok" : progress > 0 ? "run" : "warn",
    },
    {
      label: "Air-Gap",
      value: activeStep ? `Step ${activeStep.step}` : lastStep ? `Step ${lastStep.step} ${opsText("완료", "Done")}` : opsText("대기", "Standby"),
      meta: activeStep ? activeStep.label || activeStep.title || opsText("작동 중", "Working") : lastStep?.label || lastStep?.title || opsText("준비", "Ready"),
      tone: activeStep ? "run" : lastStep ? "ok" : "neutral",
    },
    {
      label: "Disk",
      value: formatOpsStatus(diskState),
      meta: `${emergencySlot.volume || airGap.volume || "D:\\"} · ${emergencySlot.slot_id || "BAY-01"}${opsToneFromText(diskState) === "danger" ? " · 상세 로그 확인" : ""}`,
      tone: opsToneFromText(diskState, "neutral"),
    },
  ];
  opsSummaryGrid.innerHTML = cards.map((card) => `
    <article class="ops-card ops-card-${card.tone}">
      <span>${escapeHtml(card.label)}</span>
      <strong>${escapeHtml(card.value)}</strong>
      <em>${escapeHtml(card.meta)}</em>
    </article>
  `).join("");
  opsEventList.innerHTML = latestOpsEvents(airGap, veeam).map((event) => `
    <article class="ops-event ops-event-${event.tone}">
      <span>${escapeHtml(event.time)}</span>
      <p>${escapeHtml(event.text)}</p>
    </article>
  `).join("");
  updateOpsEventsVisibility();
}

function monitoringUrl() {
  const params = new URLSearchParams();
  if (monitoringRange.start) params.set("start", monitoringRange.start);
  if (monitoringRange.end) params.set("end", monitoringRange.end);
  const query = params.toString();
  return query ? `/api/monitoring?${query}` : "/api/monitoring";
}

function monitoringCsvUrl() {
  const params = new URLSearchParams();
  if (monitoringRange.start) params.set("start", monitoringRange.start);
  if (monitoringRange.end) params.set("end", monitoringRange.end);
  const query = params.toString();
  return query ? `/api/monitoring.csv?${query}` : "/api/monitoring.csv";
}

function logsUrl() {
  const params = new URLSearchParams();
  if (logsRange.start) params.set("start", logsRange.start);
  if (logsRange.end) params.set("end", logsRange.end);
  if (logsRange.type) params.set("type", logsRange.type);
  if (logsRange.severity) params.set("severity", logsRange.severity);
  if (logsRange.source) params.set("source", logsRange.source);
  if (logsRange.q) params.set("q", logsRange.q);
  params.set("page", logsRange.page);
  params.set("retention", logsRange.retention);
  const query = params.toString();
  return query ? `/api/logs?${query}` : "/api/logs";
}

function logsCsvUrl() {
  const params = new URLSearchParams();
  if (logsRange.start) params.set("start", logsRange.start);
  if (logsRange.end) params.set("end", logsRange.end);
  if (logsRange.type) params.set("type", logsRange.type);
  if (logsRange.severity) params.set("severity", logsRange.severity);
  if (logsRange.source) params.set("source", logsRange.source);
  if (logsRange.q) params.set("q", logsRange.q);
  params.set("retention", logsRange.retention);
  const query = params.toString();
  return query ? `/api/logs.csv?${query}` : "/api/logs.csv";
}

async function reloadMonitoring() {
  const monitoring = await requestJson(monitoringUrl());
  renderMonitoring(monitoring);
}

async function reloadDashboard(options = {}) {
  if (dashboardReloadInFlight) return dashboardReloadInFlight;
  const live = Boolean(options.live);
  dashboardReloadInFlight = (async () => {
    try {
      if (live) markLiveRequest(dashboardLiveState);
      const dashboard = await requestJson(live ? "/api/dashboard?live=1" : "/api/dashboard", { timeoutMs: 30000, live });
      if (live) markLiveSuccess(dashboardLiveState);
      const renderedDashboard = live ? dashboardDataWithLiveState(dashboard, dashboardLiveState) : dashboard;
      renderDashboard(renderedDashboard);
      return dashboard;
    } catch (error) {
      console.warn("Unable to reload Dashboard view", error);
      if (live) markLiveFailure(dashboardLiveState, error);
      if (latestDashboardData) {
        renderDashboard(live ? dashboardDataWithLiveState(latestDashboardData, dashboardLiveState) : latestDashboardData);
      } else {
        renderDashboardFallback(error?.message || "");
      }
      return null;
    } finally {
      dashboardReloadInFlight = null;
    }
  })();
  return dashboardReloadInFlight;
}

async function reloadDetect(attempt = 0) {
  if (detectReloadInFlight) return detectReloadInFlight;
  detectReloadInFlight = requestJson("/api/detect?live=1", { live: true, timeoutMs: 2500 })
    .then((data) => {
      renderDetect(data);
      return data;
    })
    .catch((error) => {
      console.warn("Unable to reload Detect view", error);
      if (activeViewId() === "detect2View") {
        renderDetectFallback(
          "실시간 탐지 상태를 다시 확인 중입니다.",
          "서버 응답이 늦어도 화면은 유지하고 다음 갱신에서 자동으로 반영합니다."
        );
        if (attempt < 2) {
          window.setTimeout(() => {
            if (activeViewId() === "detect2View") reloadDetect(attempt + 1);
          }, 1000);
        }
      }
      return null;
    })
    .finally(() => {
      detectReloadInFlight = null;
    });
  return detectReloadInFlight;
}

async function reloadLogs() {
  const logs = await requestJson(logsUrl());
  renderLogs(logs);
}

function updateMemoryThresholdButton(value) {
  const memoryButton = document.querySelector('.metric-filter-button[data-metric="memory"]');
  if (!memoryButton) return;
  const memoryValue = Number(value || 0);
  if (memoryValue > 80) {
    memoryThresholdAlertActive = true;
  } else if (memoryValue <= 70) {
    memoryThresholdAlertActive = false;
  }
  memoryButton.classList.toggle("memory-threshold-alert", memoryThresholdAlertActive);
  memoryButton.classList.toggle("memory-threshold-normal", !memoryThresholdAlertActive);
}

function renderLoadedData(key, value) {
  if (key === "summary") renderSlots(value);
  if (key === "audit") {
    latestAuditData = Array.isArray(value.items) ? value.items : [];
    renderAudit(latestAuditData);
    renderSecurityAudit(latestAuditData);
  }
  if (key === "integrated") renderIntegrated(value);
  if (key === "monitoring") renderMonitoring(value);
  if (key === "sources") renderSources(value);
  if (key === "dashboard") renderDashboard(value);
  if (key === "report") renderReport(value);
  if (key === "notification") renderNotification(value);
  if (key === "detect") renderDetect(value);
  if (key === "threat") renderThreatDetection(value);
  if (key === "networkStatus") renderNetworkStatus(value);
  if (key === "logs") renderLogs(value);
  if (key === "license") {
    renderLicenseStatus(value);
    updateLicenseGate(value);
  }
}

function approvalDecisionsFor(request, decisions = latestApprovalsData.decisions) {
  return (Array.isArray(decisions) ? decisions : []).filter((decision) => decision.approvalRequestId === request.id);
}

function departmentReviewsFor(request, reviews = latestApprovalsData.departmentReviews) {
  const comments = Array.isArray(latestApprovalsData.reviewComments) ? latestApprovalsData.reviewComments : [];
  return (Array.isArray(reviews) ? reviews : [])
    .filter((review) => review.approvalRequestId === request.id)
    .map((review) => ({
      ...review,
      comments: comments.filter((comment) => comment.departmentReviewId === review.id),
    }));
}

function approvalDecisionSummary(request, decisions = latestApprovalsData.decisions) {
  const approved = approvalDecisionsFor(request, decisions).filter((decision) => decision.decision === "APPROVED").length;
  const required = Number(request?.requiredApprovals || 1);
  return `${approved} / ${required} approved`;
}

function repositoryOnlineWorkflowSummary(request, decisions = latestApprovalsData.decisions) {
  const metadata = request?.metadata || {};
  const reviews = metadata.reviews || {};
  const reviewCount = ["SECURITY_LOG_REVIEW", "HARDWARE_STATE_REVIEW", "MANAGER_REVIEW"].filter((key) => reviews[key]).length;
  const status = metadata.workflowStatus || (request?.requestType === "DISK_ONLINE" ? "AWAITING_SECURITY_HARDWARE_REVIEW" : "");
  const approvals = approvalDecisionSummary(request, decisions);
  const department = departmentReviewSummary(request);
  return request?.requestType === "DISK_ONLINE" ? `${status} · ${department} · reviews ${reviewCount} / 3 · ${approvals}` : `${department} · ${approvals}`;
}

function reviewTypeForRole(role) {
  return {
    SECURITY_ADMIN: "SECURITY_LOG_REVIEW",
    HARDWARE_ADMIN: "HARDWARE_STATE_REVIEW",
    SUPER_ADMIN: "MANAGER_REVIEW",
  }[role] || "";
}

function canShowReviewButton(request, session = currentSession) {
  if (!request || request.status !== "PENDING" || request.requestType !== "DISK_ONLINE") return false;
  if (String(request.requesterUserId || "") === String(session.user || "")) return false;
  const reviewType = reviewTypeForRole(session.role);
  if (!reviewType) return false;
  const reviews = request.metadata?.reviews || {};
  return !reviews[reviewType];
}

function workflowReviews(request) {
  const reviews = request?.metadata?.reviews || {};
  return typeof reviews === "object" && !Array.isArray(reviews) ? reviews : {};
}

function departmentReviewStatus(request) {
  const reviews = departmentReviewsFor(request);
  if (!reviews.length) return "NOT_REQUIRED";
  const statuses = new Set(reviews.map((review) => String(review.status || "PENDING").toUpperCase()));
  if (statuses.has("BLOCKED")) return "BLOCKED";
  if (statuses.has("NEEDS_CHANGES")) return "NEEDS_CHANGES";
  if (statuses.size === 1 && statuses.has("REVIEWED")) return "REVIEWED";
  if (statuses.has("IN_REVIEW")) return "IN_REVIEW";
  return "PENDING";
}

function departmentReviewSummary(request) {
  const reviews = departmentReviewsFor(request);
  if (!reviews.length) return "department reviews not required";
  const reviewed = reviews.filter((review) => String(review.status || "").toUpperCase() === "REVIEWED").length;
  return `department review ${reviewed} / ${reviews.length} ${departmentReviewStatus(request)}`;
}

function departmentDisplayName(departmentId) {
  const id = String(departmentId || "").trim();
  if (!id) return "-";
  const key = {
    management: "department.management",
    security: "department.security",
    "backup-operation": "department.backupOperation",
    "hardware-control": "department.hardwareControl",
    audit: "department.audit",
    development: "department.development",
    "web-design": "department.webDesign",
  }[id];
  return key ? t(key) : id;
}

function departmentReviewDisplayStatus(status) {
  return {
    PENDING: "검토 대기",
    IN_REVIEW: "검토 중",
    REVIEWED: "검토 완료",
    NEEDS_CHANGES: "보완 요청",
    BLOCKED: "차단",
  }[String(status || "PENDING").toUpperCase()] || "검토 대기";
}

function departmentWorkflowDisplayStatus(request) {
  return {
    NOT_REQUIRED: "부서 검토 불필요",
    PENDING: "부서 검토 진행 중",
    IN_REVIEW: "부서 검토 진행 중",
    REVIEWED: "부서 검토 완료",
    NEEDS_CHANGES: "보완 요청 상태",
    BLOCKED: "차단 상태",
  }[departmentReviewStatus(request)] || "부서 검토 진행 중";
}

function renderRepositoryOnlineRequestPanel(request) {
  if (request?.requestType !== "DISK_ONLINE") return "";
  const reason = request.metadata?.reason || "백업 검증을 위해 Repository Online 필요";
  const reviews = departmentReviewsFor(request);
  const requiredReviews = reviews.length ? reviews : [
    { departmentId: "security", status: "PENDING" },
    { departmentId: "hardware-control", status: "PENDING" },
  ];
  return `
    <div class="repository-online-request-card">
      <strong>[Repository Online 요청]</strong>
      <dl>
        <dt>요청 사유:</dt>
        <dd>${escapeHtml(reason)}</dd>
        <dt>관련 부서:</dt>
        <dd>
          ${requiredReviews.map((review) => {
            const checked = String(review.status || "").toUpperCase() === "REVIEWED" ? "☑" : "□";
            return `<span>${checked} ${escapeHtml(departmentDisplayName(review.departmentId))} ${escapeHtml(departmentReviewDisplayStatus(review.status))}</span>`;
          }).join("")}
        </dd>
        <dt>상태:</dt>
        <dd>${escapeHtml(departmentWorkflowDisplayStatus(request))}</dd>
      </dl>
    </div>
  `;
}

function renderFinalApprovalPanel(request, decisions = latestApprovalsData.decisions) {
  if (!request || departmentReviewStatus(request) !== "REVIEWED" || request.status !== "PENDING") return "";
  const reviews = departmentReviewsFor(request);
  const approved = approvalDecisionsFor(request, decisions).filter((decision) => decision.decision === "APPROVED").length;
  const required = Number(request.requiredApprovals || 1);
  const reviewLines = reviews.length
    ? reviews.map((review) => `<span>${escapeHtml(departmentDisplayName(review.departmentId))}: ${escapeHtml(departmentReviewDisplayStatus(review.status))}</span>`).join("")
    : `<span>부서 검토: 검토 완료</span>`;
  return `
    <div class="final-approval-wait-card">
      <strong>[최종 승인 대기]</strong>
      <div class="final-approval-review-lines">${reviewLines}</div>
      <dl>
        <dt>승인 상태:</dt>
        <dd>${approved} / ${required} 승인 완료</dd>
      </dl>
    </div>
  `;
}

function roleDepartmentIds(role) {
  return {
    SECURITY_ADMIN: ["security"],
    BACKUP_OPERATOR: ["backup-operation"],
    HARDWARE_ADMIN: ["hardware-control"],
    AUDITOR: ["audit"],
    SUPER_ADMIN: ["management", "security", "backup-operation", "hardware-control", "audit"],
  }[role] || [];
}

function canReviewDepartment(review, session = currentSession) {
  if (!review) return false;
  if (String(review.status || "").toUpperCase() === "REVIEWED") return false;
  if (String(review.status || "").toUpperCase() === "BLOCKED" && session.role !== "SUPER_ADMIN") return false;
  return roleDepartmentIds(session.role).includes(String(review.departmentId || ""));
}

function isNoPendingDepartmentReviewError(error) {
  return /no pending department review is available/i.test(String(error?.message || error || ""));
}

function showNoPendingDepartmentReviewNotice() {
  if (!approvalFormStatus) return;
  approvalFormStatus.textContent = "확인할 부서 검토가 없습니다. 이미 처리되었거나 현재 계정 권한의 검토 대상이 아니므로 승인 요청함 또는 내 승인 대기에서 다음 단계를 확인하세요.";
  approvalFormStatus.className = "approval-form-status status-warning";
}

function pendingDepartmentReviewsForSession(request, session = currentSession) {
  return departmentReviewsFor(request).filter((review) => canReviewDepartment(review, session));
}

function isDepartmentReviewPending(request) {
  if (!request || request.status !== "PENDING") return false;
  return ["PENDING", "IN_REVIEW", "NEEDS_CHANGES", "BLOCKED"].includes(departmentReviewStatus(request));
}

function isApprovalPendingRequest(request, decisions = latestApprovalsData.decisions) {
  if (!request || request.status !== "PENDING") return false;
  if (request.requestType !== "DISK_ONLINE") return true;
  if (isDepartmentReviewPending(request)) return false;
  return approvalDecisionsFor(request, decisions).filter((decision) => decision.decision === "APPROVED").length < Number(request.requiredApprovals || 1);
}

function canShowApprovalButton(request, session = currentSession, decisions = latestApprovalsData.decisions) {
  if (!request || request.status !== "PENDING") return false;
  if (!hasPermission("DISK_ONLINE_APPROVE", session)) return false;
  if (Array.isArray(request.allowedApproverRoles) && request.allowedApproverRoles.length && !request.allowedApproverRoles.includes(session.role)) return false;
  if (String(request.requesterUserId || "") === String(session.user || "")) return false;
  if (!["NOT_REQUIRED", "REVIEWED"].includes(departmentReviewStatus(request))) return false;
  if (request.requestType === "DISK_ONLINE") {
    const reviews = request.metadata?.reviews || {};
    if (!["SECURITY_LOG_REVIEW", "HARDWARE_STATE_REVIEW", "MANAGER_REVIEW"].every((key) => reviews[key])) return false;
    const approved = approvalDecisionsFor(request, decisions).filter((decision) => decision.decision === "APPROVED").length;
    if (approved === 0 && session.role !== "SECURITY_ADMIN") return false;
    if (approved === 1 && session.role !== "SUPER_ADMIN") return false;
  }
  return !approvalDecisionsFor(request, decisions).some((decision) => String(decision.approverUserId || "") === String(session.user || ""));
}

function filterApprovalRequests(requests) {
  const items = Array.isArray(requests) ? requests : [];
  if (activeApprovalTab === "approvalRequestBox") return items.filter((request) => String(request.requesterUserId || "") === String(currentSession.user || ""));
  if (activeApprovalTab === "departmentReviewBox") return items.filter((request) => isDepartmentReviewPending(request));
  if (activeApprovalTab === "myApprovalPending") return items.filter((request) => canShowApprovalButton(request));
  if (activeApprovalTab === "consultationOpinion") return items.filter((request) => workflowHistoryItems(request).length > 1 || departmentReviewsFor(request).length > 0);
  if (activeApprovalTab === "reworkRequest") return items.filter((request) => ["REJECTED", "EXPIRED"].includes(String(request.status || "")) || departmentReviewStatus(request) === "NEEDS_CHANGES");
  if (activeApprovalTab === "completedHistory") return items.filter((request) => request.status === "APPROVED");
  if (activeApprovalTab === "auditRecord") return items;
  return items;
}

function workflowHistoryItems(request, decisions = latestApprovalsData.decisions) {
  const items = [];
  if (!request) return items;
  items.push({ type: "request", actor: request.requesterUserId || "-", text: request.metadata?.reason || "request created", createdAt: request.createdAt || "" });
  Object.values(workflowReviews(request)).forEach((review) => {
    items.push({
      type: review.reviewType || "review",
      actor: review.reviewerUserId || "-",
      text: review.comment || "",
      createdAt: review.createdAt || "",
    });
  });
  departmentReviewsFor(request).forEach((review) => {
    (Array.isArray(review.comments) ? review.comments : []).forEach((comment) => {
      items.push({
        type: `${review.departmentId || "department"} ${comment.status || review.status || "review"}`,
        actor: comment.reviewerUserId || review.reviewerUserId || "-",
        text: comment.comment || review.comment || "",
        createdAt: comment.createdAt || review.updatedAt || "",
      });
    });
    if (review.comment && !(Array.isArray(review.comments) && review.comments.length)) {
      items.push({
        type: `${review.departmentId || "department"} ${review.status || "review"}`,
        actor: review.reviewerUserId || "-",
        text: review.comment || "",
        createdAt: review.updatedAt || review.createdAt || "",
      });
    }
  });
  approvalDecisionsFor(request, decisions).forEach((decision) => {
    items.push({
      type: decision.decision || "decision",
      actor: decision.approverUserId || "-",
      text: decision.comment || "",
      createdAt: decision.createdAt || "",
    });
  });
  return items.sort((left, right) => String(left.createdAt || "").localeCompare(String(right.createdAt || "")));
}

function renderWorkflowHistory(request, decisions = latestApprovalsData.decisions) {
  const items = workflowHistoryItems(request, decisions);
  if (!items.length) return "";
  return `<ol class="workflow-history-list">${items.map((item) => `
    <li>
      <strong>${escapeHtml(item.type)}</strong>
      <span>${escapeHtml(item.actor)}</span>
      <em>${escapeHtml(formatLogDate(item.createdAt))}</em>
      <p>${escapeHtml(item.text || "-")}</p>
    </li>
  `).join("")}</ol>`;
}

function renderApprovalWorkflowSummary() {
  if (!approvalWorkflowSummary) return;
  const requests = latestApprovalsData.requests || [];
  const decisions = latestApprovalsData.decisions || [];
  const pending = requests.filter((request) => String(request.status || "") === "PENDING").length;
  const reviewPending = requests.filter((request) => isDepartmentReviewPending(request)).length;
  const approvalPending = requests.filter((request) => isApprovalPendingRequest(request)).length;
  const executionAllowed = requests.filter((request) => isExecutionAllowedRequest(request)).length;
  const completed = requests.filter((request) => ["APPROVED", "EXECUTED"].includes(String(request.status || ""))).length;
  const approvedDecisions = decisions.filter((decision) => String(decision.decision || "") === "APPROVED").length;
  const cards = [
    ["요청 대기", pending, "새 요청 또는 승인 대기 상태"],
    ["부서 검토 필요", reviewPending, "보안/백업/하드웨어/감사 검토"],
    ["승인 대기", approvalPending, "2인 승인 조건 확인"],
    ["실행 허용됨", executionAllowed, "에어갭 실행 가능 상태"],
    ["완료·감사", completed, `${approvedDecisions}건 승인 기록 보존`],
  ];
  approvalWorkflowSummary.innerHTML = cards.map(([label, value, detail]) => `
    <article>
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <em>${escapeHtml(detail)}</em>
    </article>
  `).join("");
  renderApprovalExecutionProof();
}

function approvalProgress(request, decisions = latestApprovalsData.decisions) {
  const approved = approvalDecisionsFor(request, decisions).filter((decision) => decision.decision === "APPROVED").length;
  const required = Number(request?.requiredApprovals || 1);
  return { approved, required };
}

function isExecutionAllowedRequest(request, decisions = latestApprovalsData.decisions) {
  if (!request) return false;
  const requestStatus = String(request.status || "").toUpperCase();
  if (["APPROVED", "EXECUTED"].includes(requestStatus)) return true;
  const reviewOk = ["NOT_REQUIRED", "REVIEWED"].includes(departmentReviewStatus(request));
  const progress = approvalProgress(request, decisions);
  return requestStatus === "PENDING" && reviewOk && progress.approved >= progress.required;
}

function latestApprovalProofRequest(requests = latestApprovalsData.requests) {
  const items = Array.isArray(requests) ? requests.slice() : [];
  const relevant = items.filter((request) => ["DISK_ONLINE", "EMERGENCY_UNLOCK"].includes(String(request.requestType || "").toUpperCase()));
  return (relevant.length ? relevant : items).sort((left, right) => {
    const leftTime = String(left.updatedAt || left.createdAt || left.expiresAt || "");
    const rightTime = String(right.updatedAt || right.createdAt || right.expiresAt || "");
    return rightTime.localeCompare(leftTime);
  })[0];
}

function renderProofStep(label, value, detail, state = "pending") {
  return `
    <article class="approval-proof-step approval-proof-${escapeHtml(state)}">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <em>${escapeHtml(detail)}</em>
    </article>
  `;
}

function renderApprovalExecutionProof() {
  if (!approvalExecutionProof) return;
  const request = latestApprovalProofRequest();
  if (!request) {
    approvalExecutionProof.innerHTML = `
      <div class="approval-proof-empty">
        <strong>실행 허용 증명 대기</strong>
        <span>승인 요청을 등록하면 부서 검토, 2인 승인, 실행 허용, 감사 기록 상태가 이 카드에 자동으로 표시됩니다.</span>
      </div>
    `;
    return;
  }
  const reviews = departmentReviewsFor(request);
  const reviewed = reviews.filter((review) => String(review.status || "").toUpperCase() === "REVIEWED").length;
  const reviewRequired = reviews.length;
  const reviewOk = ["NOT_REQUIRED", "REVIEWED"].includes(departmentReviewStatus(request));
  const progress = approvalProgress(request);
  const allowed = isExecutionAllowedRequest(request);
  const historyCount = workflowHistoryItems(request).length;
  const repositoryPath = request.metadata?.repositoryPath || "-";
  const proofTitle = allowed ? "실행 허용이 완료되었습니다." : "실행 허용까지 남은 절차가 있습니다.";
  const proofDetail = allowed
    ? "부서 검토와 승인 조건을 충족했습니다. 에어갭 화면에서 바로 재접속 실행 상태를 확인할 수 있습니다."
    : "아래 카드에서 부족한 검토 또는 승인 단계를 확인한 뒤 한 번의 확인 버튼으로 다음 절차를 진행합니다.";
  approvalExecutionProof.innerHTML = `
    <div class="approval-proof-head">
      <div>
        <span>실행 허용 증명</span>
        <h2>${escapeHtml(proofTitle)}</h2>
        <p>${escapeHtml(proofDetail)}</p>
      </div>
      <button type="button" class="approval-airgap-shortcut" data-approval-airgap-shortcut>
        에어갭 화면에서 확인
      </button>
    </div>
    <div class="approval-proof-meta">
      <span>요청 유형 <strong>${escapeHtml(request.requestType || "-")}</strong></span>
      <span>대상 <strong>${escapeHtml(request.targetId || "-")}</strong></span>
      <span>저장소 <strong>${escapeHtml(repositoryPath)}</strong></span>
      <span>상태 <strong>${escapeHtml(allowed ? "실행 허용됨" : departmentWorkflowDisplayStatus(request))}</strong></span>
    </div>
    <div class="approval-proof-grid">
      ${renderProofStep("부서 검토", reviewRequired ? `${reviewed} / ${reviewRequired} 완료` : "불필요", reviewOk ? "검토 조건 충족" : "부서 검토가 남아 있습니다.", reviewOk ? "done" : "pending")}
      ${renderProofStep("2인 승인", `${progress.approved} / ${progress.required} 승인`, progress.approved >= progress.required ? "승인 조건 충족" : "서로 다른 관리자 승인이 필요합니다.", progress.approved >= progress.required ? "done" : "pending")}
      ${renderProofStep("실행 허용", allowed ? "허용됨" : "대기", allowed ? "에어갭 실행 가능" : "검토와 승인 완료 후 허용됩니다.", allowed ? "allowed" : "pending")}
      ${renderProofStep("감사 기록", `${historyCount}건`, "요청, 검토, 승인 이력 보존", historyCount ? "done" : "pending")}
    </div>
  `;
}

function approvalRequestMetadata(requestType, reason, repositoryPath) {
  const type = String(requestType || "").trim().toUpperCase();
  const metadata = {
    reason: String(reason || "").trim(),
    requestedFrom: "LOCK-FIX WebUI",
    workflowGuide: "작업 요청 > 부서 검토 > 승인 > 실행 > 감사 기록",
  };
  const path = String(repositoryPath || "").trim();
  if (path) metadata.repositoryPath = path;
  if (type === "DISK_ONLINE") {
    metadata.workflowType = "REPOSITORY_ONLINE";
    metadata.targetResourceType = "REPOSITORY";
    metadata.workflowStatus = "AWAITING_SECURITY_HARDWARE_REVIEW";
    metadata.reviews = {};
  }
  return metadata;
}

function renderApprovals(data, errorMessage = "") {
  latestApprovalsData = {
    policies: Array.isArray(data?.policies) ? data.policies : [],
    requests: Array.isArray(data?.requests) ? data.requests : [],
    decisions: Array.isArray(data?.decisions) ? data.decisions : [],
    departmentReviews: Array.isArray(data?.departmentReviews) ? data.departmentReviews : [],
    reviewComments: Array.isArray(data?.reviewComments) ? data.reviewComments : [],
    notifications: Array.isArray(data?.notifications) ? data.notifications : [],
  };
  renderApprovalWorkflowSummary();
  const tab = approvalTabDefinitions.find((item) => item.id === activeApprovalTab) || approvalTabDefinitions[0];
  if (approvalTabTitle) approvalTabTitle.textContent = tab.label;
  approvalTabs?.querySelectorAll("[data-approval-tab]").forEach((button) => {
    button.classList.toggle("active", button.dataset.approvalTab === activeApprovalTab);
  });
  const rows = filterApprovalRequests(latestApprovalsData.requests);
  if (approvalCount) approvalCount.textContent = `${rows.length} requests`;
  if (!approvalRequestsTable) return;
  approvalRequestsTable.replaceChildren();
  if (errorMessage || !rows.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="7">${escapeHtml(errorMessage || "No approval requests in this tab.")}</td>`;
    approvalRequestsTable.appendChild(row);
    return;
  }
  rows.forEach((request) => {
    const row = document.createElement("tr");
    const requestStatus = String(request.status || "").toUpperCase();
    const reviewType = reviewTypeForRole(currentSession.role);
    const pendingDepartmentReviews = pendingDepartmentReviewsForSession(request);
    const departmentButtons = pendingDepartmentReviews.length
      ? `<button type="button" class="rbac-action-button rbac-confirm-action" data-department-confirm-request-id="${escapeHtml(request.id)}" data-department-confirm-review-ids="${escapeHtml(pendingDepartmentReviews.map((review) => review.id).join(","))}" data-review-action="mark-reviewed">확인</button>`
      : "";
    const reviewButton = !departmentButtons && canShowReviewButton(request)
      ? `<button type="button" class="rbac-action-button rbac-confirm-action" data-review-id="${escapeHtml(request.id)}" data-review-type="${escapeHtml(reviewType)}">확인</button>`
      : "";
    const approveButton = canShowApprovalButton(request)
      ? `<button type="button" class="rbac-action-button rbac-confirm-action" data-approval-id="${escapeHtml(request.id)}">확인</button>`
      : "";
    const deleteExpiredButton = requestStatus === "EXPIRED"
      ? `<button type="button" class="rbac-action-button rbac-danger-action" data-delete-expired-id="${escapeHtml(request.id)}">만료 삭제</button>`
      : "";
    const history = ["consultationOpinion", "completedHistory", "auditRecord"].includes(activeApprovalTab) ? renderWorkflowHistory(request) : "";
    row.innerHTML = `
      <td>${escapeHtml(request.requestType)}</td>
      <td>${escapeHtml(request.requesterUserId)}</td>
      <td>${escapeHtml(request.targetId || "-")}</td>
      <td><span class="rbac-status rbac-status-${escapeHtml(String(request.status || "").toLowerCase())}">${escapeHtml(request.status)}</span></td>
      <td>${renderRepositoryOnlineRequestPanel(request)}${renderFinalApprovalPanel(request)}${escapeHtml(repositoryOnlineWorkflowSummary(request))}<br><span class="approval-review-state">최종 승인 가능 여부: ${canShowApprovalButton(request) ? "가능" : "불가"} · 검토 완료 상태: ${escapeHtml(departmentReviewStatus(request))}</span>${history}</td>
      <td>${escapeHtml(formatLogDate(request.expiresAt))}</td>
      <td>${departmentButtons}${reviewButton}${approveButton}${deleteExpiredButton}</td>
    `;
    approvalRequestsTable.appendChild(row);
  });
}

async function reloadApprovals() {
  if (!currentSession.authenticated) {
    renderApprovals(
      { requests: [], decisions: [], policies: [], departmentReviews: [], reviewComments: [], notifications: [] },
      "로그인 후 승인 요청을 확인할 수 있습니다."
    );
    return;
  }
  const data = await requestJson("/api/approvals");
  renderApprovals(data);
}

function renderVeeamIntegration(data, errorMessage = "") {
  const monitor = data?.air_gap?.copy_job_monitor || {};
  if (veeamIntegrationStatus) veeamIntegrationStatus.textContent = errorMessage || monitor.detail_status || monitor.status || "-";
  if (!veeamIntegrationSummary) return;
  const rows = [
    ["Server", monitor.server || monitor.server_ip || "-"],
    ["Job", monitor.detail_name || monitor.name || "-"],
    ["Progress", monitor.progress || "-"],
    ["Last Checked", monitor.last_checked || monitor.generated_at || "-"],
  ];
  veeamIntegrationSummary.innerHTML = rows.map(([label, value]) => `
    <article class="rbac-summary-card">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `).join("");
}

async function reloadVeeamIntegration() {
  const data = await requestJson("/api/sources");
  renderVeeamIntegration(data);
}

function templateText(key, values = {}) {
  let text = t(key);
  Object.entries(values).forEach(([name, value]) => {
    text = text.replaceAll(`{${name}}`, String(value));
  });
  return text;
}

function renderUserManagementOptions(departments = []) {
  const options = departments.length ? departments : USER_MANAGEMENT_DEFAULT_DEPARTMENTS;
  if (userManagementDepartment) {
    userManagementDepartment.innerHTML = options.map((department) => (
      `<option value="${escapeHtml(department.id || "")}">${escapeHtml(departmentDisplayName(department.id) || department.name || department.id || "")}</option>`
    )).join("");
  }
  if (userManagementRole) {
    userManagementRole.innerHTML = USER_MANAGEMENT_ROLES.map((role) => (
      `<option value="${escapeHtml(role)}">${escapeHtml(role)}</option>`
    )).join("");
  }
}

function resetUserManagementForm() {
  if (!userManagementForm) return;
  userManagementForm.reset();
  if (userManagementUserId) userManagementUserId.value = "";
  if (userManagementFormTitle) userManagementFormTitle.textContent = t("userManagement.newUser");
  if (userManagementSubmitButton) userManagementSubmitButton.textContent = t("userManagement.create");
  setUserManagementStatus();
}

function userManagementStatusText(user) {
  if (user.disabled) return t("userManagement.disabled");
  if (user.passwordChangeRequired) return t("userManagement.passwordRequired");
  return t("userManagement.active");
}

function userManagementErrorMessage(error) {
  const message = String(error?.message || "");
  if (/user email already exists/i.test(message)) return t("userManagement.errorDuplicateEmail");
  if (/departmentId is required/i.test(message)) return t("userManagement.errorDepartmentRequired");
  if (/department not found/i.test(message)) return t("userManagement.errorDepartmentRequired");
  return message || t("userManagement.errorGeneric");
}

function setUserManagementStatus(message = "", tone = "") {
  if (!userManagementStatus) return;
  userManagementStatus.textContent = message;
  userManagementStatus.className = `user-management-status${tone ? ` status-${tone}` : ""}`;
}

function hasUserManagementDuplicateEmail(email, currentUserId = "") {
  const normalizedEmail = String(email || "").trim().toLowerCase();
  if (!normalizedEmail) return false;
  return latestUserManagementData.users.some((user) => (
    String(user.email || "").trim().toLowerCase() === normalizedEmail
    && String(user.id || "") !== String(currentUserId || "")
  ));
}

function renderWindowsAdminStatus(status) {
  if (!userManagementWindowsStatus) return;
  if (status?.error) {
    userManagementWindowsStatus.innerHTML = `
      <strong class="status-neutral">${escapeHtml(t("userManagement.windowsUnavailable"))}</strong>
      <span>${escapeHtml(t("userManagement.windowsUnavailableDesc"))}</span>
      <em>${escapeHtml(t("userManagement.windowsStatusDesc"))}</em>
    `;
    return;
  }
  const checkedAt = status?.checkedAt ? formatLogDate(status.checkedAt) : "-";
  const stateLabel = status?.isAdministrator ? t("userManagement.windowsAdmin") : t("userManagement.windowsStandard");
  const stateClass = status?.isAdministrator ? "status-success" : "status-warning";
  userManagementWindowsStatus.innerHTML = `
    <strong class="${stateClass}">${escapeHtml(stateLabel)}</strong>
    <span>${escapeHtml(templateText("userManagement.windowsAudit", { time: checkedAt }))}</span>
    <em>${escapeHtml(t("userManagement.windowsStatusDesc"))}</em>
  `;
}

function renderUserManagement(data, errorMessage = "") {
  const loadedDepartments = Array.isArray(data?.departments) ? data.departments : [];
  const departments = loadedDepartments.length ? loadedDepartments : USER_MANAGEMENT_DEFAULT_DEPARTMENTS;
  const users = Array.isArray(data?.users) ? data.users : [];
  const usersError = errorMessage || data?.usersError || "";
  const departmentError = data?.departmentError || "";
  latestUserManagementData = {
    users,
    departments,
    windowsAdminStatus: data?.windowsAdminStatus || latestUserManagementData.windowsAdminStatus,
  };
  renderUserManagementOptions(departments);
  renderWindowsAdminStatus(latestUserManagementData.windowsAdminStatus);
  if (userManagementDepartmentCount) {
    userManagementDepartmentCount.textContent = templateText("userManagement.departmentCount", { count: departments.length });
  }
  if (userManagementDepartments) {
    userManagementDepartments.innerHTML = departments.length
      ? departments.map((department) => `<span>${escapeHtml(departmentDisplayName(department.id) || department.name || department.id)}</span>`).join("")
      : `<em>${escapeHtml(departmentError || t("userManagement.noDepartments"))}</em>`;
  }
  if (userManagementCount) userManagementCount.textContent = templateText("userManagement.count", { count: users.length });
  if (!userManagementTable) return;
  userManagementTable.replaceChildren();
  if (usersError || !users.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="5">${escapeHtml(usersError || t("userManagement.noUsers"))}</td>`;
    userManagementTable.appendChild(row);
    return;
  }
  users.forEach((user) => {
    const department = departments.find((item) => item.id === user.departmentId);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>${escapeHtml(user.name || user.email || user.id)}</strong><span class="rbac-table-muted">${escapeHtml(user.email || "-")}</span></td>
      <td>${escapeHtml(department?.name || user.departmentId || "-")}</td>
      <td>${escapeHtml(user.role || "-")}</td>
      <td>${escapeHtml(userManagementStatusText(user))}</td>
      <td class="rbac-action-cell">
        <button type="button" class="rbac-mini-button" data-user-edit="${escapeHtml(user.id || "")}">${escapeHtml(t("userManagement.edit"))}</button>
        <button type="button" class="rbac-mini-button" data-user-temp="${escapeHtml(user.id || "")}">${escapeHtml(t("userManagement.issueTemp"))}</button>
        <button type="button" class="rbac-mini-button rbac-danger-button" data-user-archive="${escapeHtml(user.id || "")}">${escapeHtml(t("userManagement.delete"))}</button>
      </td>
    `;
    userManagementTable.appendChild(row);
  });
}

async function reloadUserManagement() {
  const [usersResult, departmentsResult, windowsResult] = await Promise.allSettled([
    requestJson("/api/admin/users", { timeoutMs: 30000 }),
    requestJson("/api/admin/departments", { timeoutMs: 30000 }),
    requestJson("/api/admin/windows-admin-status", { timeoutMs: 30000 }),
  ]);
  const users = usersResult.status === "fulfilled" ? usersResult.value.items || [] : latestUserManagementData.users;
  const departments = departmentsResult.status === "fulfilled"
    ? departmentsResult.value.items || []
    : (latestUserManagementData.departments.length ? latestUserManagementData.departments : USER_MANAGEMENT_DEFAULT_DEPARTMENTS);
  const windowsAdminStatus = windowsResult.status === "fulfilled"
    ? windowsResult.value
    : {
      ...(latestUserManagementData.windowsAdminStatus || {}),
      error: windowsResult.reason?.message || "Windows administrator status check failed.",
    };
  renderUserManagement({
    users,
    departments,
    windowsAdminStatus,
    usersError: usersResult.status === "rejected" ? usersResult.reason?.message || "User list load failed." : "",
    departmentError: departmentsResult.status === "rejected" ? departmentsResult.reason?.message || "Department list load failed." : "",
  });
}

async function submitUserManagementForm(event) {
  event.preventDefault();
  if (!userManagementForm) return;
  const userId = userManagementUserId?.value || "";
  const payload = {
    email: userManagementEmail?.value.trim() || "",
    name: userManagementName?.value.trim() || "",
    departmentId: userManagementDepartment?.value || "",
    role: userManagementRole?.value || "AUDITOR",
    disabled: Boolean(userManagementDisabled?.checked),
  };
  if (hasUserManagementDuplicateEmail(payload.email, userId)) {
    setUserManagementStatus(t("userManagement.errorDuplicateEmail"), "error");
    userManagementEmail?.focus();
    return;
  }
  if (userManagementSubmitButton) userManagementSubmitButton.disabled = true;
  setUserManagementStatus(userId ? t("userManagement.save") : t("userManagement.create"), "pending");
  try {
    const response = await requestJson(userId ? `/api/admin/users/${encodeURIComponent(userId)}` : "/api/admin/users", {
      method: userId ? "PATCH" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      timeoutMs: 60000,
    });
    const message = userId
      ? t("userManagement.updated")
      : templateText("userManagement.created", {
        password: response.temporaryPassword || "-",
        expires: response.temporaryPasswordExpiresAt || "-",
    });
    resetUserManagementForm();
    setUserManagementStatus(message, "success");
    await reloadUserManagement();
  } catch (error) {
    if (!userId && error?.code === "REQUEST_TIMEOUT") {
      await reloadUserManagement();
      if (latestUserManagementData.users.some((user) => String(user.email || "").trim().toLowerCase() === payload.email.toLowerCase())) {
        resetUserManagementForm();
        setUserManagementStatus(templateText("userManagement.createdAfterTimeout", { email: payload.email }), "warning");
        return;
      }
    }
    setUserManagementStatus(userManagementErrorMessage(error), "error");
  } finally {
    if (userManagementSubmitButton) userManagementSubmitButton.disabled = false;
  }
}

function editUserManagementUser(userId) {
  const user = latestUserManagementData.users.find((item) => String(item.id || "") === String(userId || ""));
  if (!user) return;
  if (userManagementUserId) userManagementUserId.value = user.id || "";
  if (userManagementEmail) userManagementEmail.value = user.email || "";
  if (userManagementName) userManagementName.value = user.name || "";
  if (userManagementDepartment) userManagementDepartment.value = user.departmentId || "";
  if (userManagementRole) userManagementRole.value = user.role || "AUDITOR";
  if (userManagementDisabled) userManagementDisabled.checked = Boolean(user.disabled);
  if (userManagementFormTitle) userManagementFormTitle.textContent = t("userManagement.editUser");
  if (userManagementSubmitButton) userManagementSubmitButton.textContent = t("userManagement.save");
  setUserManagementStatus();
  userManagementEmail?.focus();
}

async function archiveUserManagementUser(userId) {
  if (!window.confirm(t("userManagement.confirmArchive"))) return;
  const response = await requestJson(`/api/admin/users/${encodeURIComponent(userId)}/archive`, { method: "POST" });
  setUserManagementStatus(response.ok ? t("userManagement.archived") : t("userManagement.errorGeneric"), response.ok ? "success" : "error");
  await reloadUserManagement();
}

async function issueUserManagementTemporaryPassword(userId) {
  const response = await requestJson(`/api/admin/users/${encodeURIComponent(userId)}/temporary-password`, { method: "POST" });
  setUserManagementStatus(templateText("userManagement.tempIssued", {
    password: response.temporaryPassword || "-",
    expires: response.temporaryPasswordExpiresAt || "-",
  }), "success");
  await reloadUserManagement();
}

async function handleUserManagementTableClick(event) {
  const editButton = event.target.closest("[data-user-edit]");
  const archiveButton = event.target.closest("[data-user-archive]");
  const tempButton = event.target.closest("[data-user-temp]");
  try {
    if (editButton) {
      editUserManagementUser(editButton.dataset.userEdit);
      return;
    }
    if (archiveButton) {
      await archiveUserManagementUser(archiveButton.dataset.userArchive);
      return;
    }
    if (tempButton) {
      await issueUserManagementTemporaryPassword(tempButton.dataset.userTemp);
    }
  } catch (error) {
    setUserManagementStatus(userManagementErrorMessage(error), "error");
  }
}

function renderAuditLogs(data, errorMessage = "") {
  const items = Array.isArray(data?.items) ? data.items : [];
  if (auditLogsCount) auditLogsCount.textContent = `${items.length} events`;
  if (auditLogsSummary) {
    const recentItems = items.slice(-200);
    const failed = recentItems.filter((item) => String(item.result || "").toUpperCase().includes("FAIL")).length;
    const blocked = recentItems.filter((item) => /403|forbidden|blocked|unauthorized/i.test(`${item.action || item.event || ""} ${item.message || ""}`)).length;
    const policy = recentItems.filter((item) => String(item.action || item.event || "").startsWith("policy.guard")).length;
    const latest = recentItems.length ? formatLogDate(recentItems[recentItems.length - 1].createdAt || recentItems[recentItems.length - 1].ts || recentItems[recentItems.length - 1].time) : "-";
    const cards = [
      ["Total Events", items.length, "Append-only audit records", "audit-summary-total"],
      ["Failures", failed, "Execution or permission failures", failed ? "audit-summary-risk" : "audit-summary-ok"],
      ["Blocked", blocked, "Unauthorized or guarded attempts", blocked ? "audit-summary-risk" : "audit-summary-ok"],
      ["Policy Guard", policy, "Automatic protection responses", policy ? "audit-summary-info" : "audit-summary-total"],
      ["Latest", latest, "Most recent audit event", "audit-summary-total"],
    ];
    auditLogsSummary.innerHTML = cards.map(([label, value, detail, className]) => `
      <article class="audit-summary-card ${className}">
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(String(value))}</strong>
        <em>${escapeHtml(detail)}</em>
      </article>
    `).join("");
  }
  if (!auditLogsTable) return;
  auditLogsTable.replaceChildren();
  if (errorMessage || !items.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="5"><div class="audit-empty-state"><strong>${escapeHtml(errorMessage || "No audit events loaded.")}</strong><span>로그가 생성되면 시간, 사용자, 작업, 대상, 결과가 이 영역에 표시됩니다.</span></div></td>`;
    auditLogsTable.appendChild(row);
    return;
  }
  items.slice(-200).reverse().forEach((item) => {
    const row = document.createElement("tr");
    const result = String(item.result || "-");
    const resultClass = result.toLowerCase().includes("fail") || result.toLowerCase().includes("error")
      ? "audit-result-failed"
      : (result.toLowerCase().includes("success") ? "audit-result-success" : "audit-result-info");
    row.innerHTML = `
      <td>${escapeHtml(formatLogDate(item.createdAt || item.ts || item.time))}</td>
      <td>${escapeHtml(item.actorUserId || item.user || "-")}</td>
      <td>${escapeHtml(item.action || item.event || "-")}</td>
      <td>${escapeHtml([item.resourceType, item.resourceId].filter(Boolean).join(" / ") || "-")}</td>
      <td><span class="audit-result-pill ${resultClass}">${escapeHtml(result)}</span></td>
    `;
    auditLogsTable.appendChild(row);
  });
}

async function reloadAuditLogs() {
  const data = await requestJson("/api/audit-logs");
  renderAuditLogs(data);
}

window.lockfixUiAuth = {
  menuDefinitions,
  approvalTabDefinitions,
  visibleMenuDefinitions,
  canAccessView,
  approvalDecisionSummary,
  repositoryOnlineWorkflowSummary,
  departmentReviewsFor,
  departmentReviewStatus,
  departmentReviewSummary,
  approvalWorkflowStages,
  renderApprovalWorkflowPipeline,
  renderRepositoryOnlineRequestPanel,
  renderFinalApprovalPanel,
  workflowHistoryItems,
  renderWorkflowHistory,
  canShowReviewButton,
  canReviewDepartment,
  canShowApprovalButton,
};

async function reloadReport() {
  reportAnalysis.textContent = t("report.loading");
  const report = await requestJson("/api/report");
  renderReport(report);
}

async function reloadConsoleStatus() {
  if (!consoleStatusText || !consoleStatusDetail) return;
  consoleStatusText.textContent = "Checking Web UI console status...";
  const status = await requestJson("/api/console/status");
  consoleStatusText.textContent = status.message;
  consoleStatusDetail.textContent = [
    `Mode: ${status.mode}`,
    `CMD execution from browser: ${status.cmd_execution}`,
    `URL: ${status.url}`,
    `Root: ${status.root}`,
    `Config: ${status.config_path}`,
    `Entrypoint: ${status.server.entrypoint}`,
  ].join("\n");
}

function renderServiceControlStatus(status) {
  if (!serviceControlStatus) return;
  const name = status.service_name || "LOCKFIXWebUI";
  const state = status.state || "UNKNOWN";
  serviceControlStatus.textContent = `${name} : ${state}`;
  if (serviceStartButton) serviceStartButton.disabled = !status.can_start;
  if (serviceStopButton) serviceStopButton.disabled = !status.can_stop;
}

function preflightStatusLabel(status) {
  const text = String(status || "").toUpperCase();
  if (text === "OK" || text === "정상") return uiSettings.language === "ko" ? "정상" : "OK";
  if (text.includes("서비스")) return uiSettings.language === "ko" ? "서비스 미실행" : "Service stopped";
  if (text.includes("권한")) return uiSettings.language === "ko" ? "권한 부족" : "Insufficient permission";
  return uiSettings.language === "ko" ? "고객사 정책 확인 필요" : "Customer policy review";
}

function preflightDisplayLabel(row = {}) {
  const key = row.key || "";
  const labels = {
    veeam_rest_connection: ["Veeam REST connection", "Veeam REST 연결"],
    veeam_job_detection: ["Veeam Job detection", "Veeam Job 감지"],
    repository_path: ["Repository path", "Repository 경로"],
    target_volume: ["Target volume", "대상 볼륨"],
    disk_offline_permission: ["Disk Offline permission", "디스크 Offline 권한"],
  };
  if (labels[key]) return uiSettings.language === "ko" ? labels[key][1] : labels[key][0];
  return row.label || key || "Preflight";
}

function renderServicePreflight(data = {}) {
  if (!servicePreflightStatus) return;
  const restricted = Array.isArray(data.restricted_features) ? data.restricted_features : [];
  const service = data.service || {};
  servicePreflightStatus.textContent = preflightStatusLabel(data.status);
  servicePreflightStatus.className = `settings-preflight-status ${data.ok ? "is-ok" : "is-warning"}`;
  if (servicePreflightMode) servicePreflightMode.textContent = data.mode_label || data.operation_mode || "-";
  if (servicePreflightAccount) {
    const account = service.account || "-";
    const admin = service.local_admin ? "Admin" : (uiSettings.language === "ko" ? "권한 부족" : "Limited");
    servicePreflightAccount.textContent = `${account} · ${admin}`;
  }
  if (servicePreflightRestricted) servicePreflightRestricted.textContent = restricted.length ? `${restricted.length}` : "0";
  if (servicePreflightChecks) {
    const diskChecks = Array.isArray(data.disk_commands) ? data.disk_commands : [];
    const installChecks = Array.isArray(data.preflight_checks) ? data.preflight_checks : [];
    const rows = installChecks.length
      ? installChecks
      : [
        { label: "Service", ok: Boolean(service.running), detail: data.service_status?.state || "" },
        { label: "Local Admin", ok: Boolean(service.local_admin), detail: service.account || "" },
        ...diskChecks.map((item) => ({ label: item.name || item.command || "PowerShell", ok: Boolean(item.ok), detail: item.error || item.output || "" })),
        { label: "Veeam REST", ok: Boolean(data.veeam_api?.ok), detail: data.veeam_api?.diagnostics?.error || "" },
        { label: "UAC", ok: Boolean(data.uac?.ok), detail: data.uac?.detail || "" },
        { label: "ExecutionPolicy", ok: Boolean(data.execution_policy?.ok), detail: data.execution_policy?.detail || "" },
        { label: "Firewall", ok: Boolean(data.firewall?.ok), detail: data.firewall?.detail || "" },
        { label: "WinRM", ok: Boolean(data.winrm?.ok), detail: data.winrm?.detail || "" },
      ];
    servicePreflightChecks.innerHTML = rows.map((row) => `
      <li class="${row.ok ? "is-ok" : "is-warning"}" title="${escapeHtml(row.detail || row.resolution || "")}">
        <span>${escapeHtml(preflightDisplayLabel(row))}</span>
        <strong>${row.ok ? "OK" : "CHECK"}</strong>
      </li>
    `).join("");
  }
}

async function reloadServicePreflight() {
  if (!servicePreflightStatus) return;
  servicePreflightStatus.textContent = uiSettings.language === "ko" ? "권한 진단 중..." : "Checking permissions...";
  try {
    const data = await requestJson("/api/service/preflight");
    renderServicePreflight(data);
  } catch (error) {
    renderServicePreflight({
      status: "서비스 미실행",
      ok: false,
      service: { running: false, account: "-", local_admin: false },
      restricted_features: [error.message],
      disk_commands: [],
      veeam_api: { ok: false, diagnostics: { error: error.message } },
      preflight_checks: [
        { key: "veeam_rest_connection", ok: false, detail: error.message },
        { key: "veeam_job_detection", ok: false, detail: error.message },
        { key: "repository_path", ok: false, detail: error.message },
        { key: "target_volume", ok: false, detail: error.message },
        { key: "disk_offline_permission", ok: false, detail: error.message },
      ],
    });
  }
}

function setSettingsShortcutStatus(target, key, replacements = {}) {
  if (!target) return;
  let text = t(key);
  Object.entries(replacements).forEach(([name, value]) => {
    text = text.replaceAll(`{${name}}`, String(value));
  });
  target.textContent = text;
}

function sourcesHardwareConnected(data) {
  const airGap = data?.air_gap || {};
  const slot = airGap?.emergency_access?.slot || {};
  const bays = Array.isArray(airGap?.bays) ? airGap.bays : [];
  const state = String(slot.state || "").toUpperCase();
  if (["ERROR", "FAILED", "UNREGISTERED"].includes(state)) return false;
  return Boolean(slot.slot_id || slot.device || slot.mount_point || bays.length);
}

async function reloadSettingsShortcutStatus() {
  setSettingsShortcutStatus(settingsHardwareStatus, "settings.statusChecking");
  setSettingsShortcutStatus(settingsServiceStatus, "settings.statusChecking");
  setSettingsShortcutStatus(settingsAuditStatus, "settings.statusChecking");

  const update = (promise, onSuccess, target) => promise.then(onSuccess).catch(() => {
    setSettingsShortcutStatus(target, "settings.statusUnavailable");
  });

  await Promise.allSettled([
    update(requestJson("/api/sources"), (data) => {
      setSettingsShortcutStatus(settingsHardwareStatus, sourcesHardwareConnected(data) ? "settings.hardwareConnected" : "settings.hardwareCheckNeeded");
    }, settingsHardwareStatus),
    update(requestJson("/api/service/status"), (status) => {
      const state = String(status?.state || "").toUpperCase();
      setSettingsShortcutStatus(settingsServiceStatus, state === "RUNNING" ? "settings.serviceNormal" : "settings.serviceStopped");
    }, settingsServiceStatus),
    update(requestJson("/api/audit-logs"), (data) => {
      const count = Array.isArray(data?.items) ? data.items.length : 0;
      setSettingsShortcutStatus(settingsAuditStatus, "settings.auditEvents", { count });
    }, settingsAuditStatus),
  ]);
}

async function reloadServiceControlStatus() {
  if (!serviceControlStatus) return;
  serviceControlStatus.textContent = uiSettings.language === "ko" ? "서비스 상태 확인 중..." : "Checking service status...";
  try {
    const status = await requestJson("/api/service/status");
    renderServiceControlStatus(status);
  } catch (error) {
    serviceControlStatus.textContent = error.message;
    if (serviceStartButton) serviceStartButton.disabled = true;
    if (serviceStopButton) serviceStopButton.disabled = true;
  }
}

async function controlLockfixService(action) {
  if (!serviceControlStatus) return;
  if (serviceStartButton) serviceStartButton.disabled = true;
  if (serviceStopButton) serviceStopButton.disabled = true;
  serviceControlStatus.textContent = action === "start"
    ? (uiSettings.language === "ko" ? "서비스 시작 요청 중..." : "Requesting service start...")
    : (uiSettings.language === "ko" ? "서비스 중지 요청 중..." : "Requesting service stop...");
  try {
    const status = await requestJson("/api/service/control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action }),
    });
    renderServiceControlStatus(status);
    if (status.message) serviceControlStatus.textContent = status.message;
    if (action === "start") {
      setTimeout(reloadServiceControlStatus, 1400);
    }
  } catch (error) {
    serviceControlStatus.textContent = error.message;
    await reloadServiceControlStatus();
  }
}

async function reloadSources() {
  renderSources({ air_gap: fallbackAirGapSummary(true) });
  const sources = await requestJson("/api/sources", { timeoutMs: 8000 });
  renderSources(sources);
}

async function pollSourcesLive() {
  if (!currentSession.authenticated || appRoot.classList.contains("app-locked")) return;
  if (activeViewId() !== "sourcesView") return;
  if (sourcesLiveInFlight) return sourcesLiveInFlight;
  sourcesLiveInFlight = (async () => {
    try {
      const sources = await requestJson("/api/sources?live=1", { live: true, timeoutMs: 6000 });
      renderSources(sources);
      finalizeEmergencyReconnectFromSources(sources);
    } catch (error) {
      console.warn("Unable to poll Air-Gap live status", error);
    } finally {
      sourcesLiveInFlight = null;
    }
  })();
  return sourcesLiveInFlight;
}

async function syncVeeamExecutionConfig(button) {
  const originalText = button?.textContent || "";
  if (button) {
    button.disabled = true;
    button.textContent = uiSettings.language === "ko" ? "갱신 중" : "Syncing";
  }
  try {
    const result = await requestJson("/api/veeam-config/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: "network_port_card" }),
    });
    if (button) button.textContent = uiSettings.language === "ko" ? "완료" : "Done";
    await pollSourcesLive();
    return result;
  } catch (error) {
    if (button) button.textContent = uiSettings.language === "ko" ? "실패" : "Failed";
    console.warn("Unable to sync Veeam execution config", error);
    setTimeout(() => {
      if (button) {
        button.disabled = false;
        button.textContent = originalText;
      }
    }, 1200);
    return null;
  }
}

function setAirGapLivePolling(enabled) {
  if (enabled && !airgapPollTimer) {
    airgapPollTimer = setInterval(pollSourcesLive, REALTIME_POLL_INTERVAL_MS);
    pollSourcesLive();
  }
  if (!enabled && airgapPollTimer) {
    clearInterval(airgapPollTimer);
    airgapPollTimer = null;
  }
}

async function pollDashboardLive() {
  if (!currentSession.authenticated || appRoot.classList.contains("app-locked")) return;
  if (activeViewId() !== "dashboardView") return;
  await reloadDashboard({ live: true });
}

function setDashboardLivePolling(enabled) {
  if (enabled && !dashboardPollTimer) {
    dashboardPollTimer = setInterval(pollDashboardLive, REALTIME_POLL_INTERVAL_MS);
    pollDashboardLive();
  }
  if (!enabled && dashboardPollTimer) {
    clearInterval(dashboardPollTimer);
    dashboardPollTimer = null;
  }
}

async function pollOpsOverviewLive() {
  if (!currentSession.authenticated || appRoot.classList.contains("app-locked")) return;
  if (activeViewId() !== "monitoringView") return;
  if (opsOverviewLiveInFlight) return opsOverviewLiveInFlight;
  markLiveRequest(opsOverviewLiveState);
  opsOverviewLiveInFlight = (async () => {
    try {
      const [sourcesResult, dashboardResult] = await Promise.allSettled([
        requestJson("/api/sources?live=1", { live: true, timeoutMs: 6000 }),
        requestJson("/api/dashboard?live=1", { live: true, timeoutMs: 6000 }),
      ]);
      if (sourcesResult.status === "fulfilled") latestSourcesData = sourcesResult.value;
      if (dashboardResult.status === "fulfilled") latestDashboardData = dashboardResult.value;
      const failures = [sourcesResult, dashboardResult].filter((result) => result.status === "rejected");
      if (sourcesResult.status === "fulfilled") {
        markLiveSuccess(opsOverviewLiveState);
      } else if (failures.length) {
        markLiveFailure(opsOverviewLiveState, failures[0].reason);
      }
      renderOperationsOverview();
    } catch (error) {
      markLiveFailure(opsOverviewLiveState, error);
      console.warn("Unable to poll operations overview", error);
    } finally {
      opsOverviewLiveInFlight = null;
    }
  })();
  return opsOverviewLiveInFlight;
}

function setOpsOverviewLivePolling(enabled) {
  if (enabled && !opsOverviewPollTimer) {
    opsOverviewPollTimer = setInterval(pollOpsOverviewLive, REALTIME_POLL_INTERVAL_MS);
    pollOpsOverviewLive();
  }
  if (!enabled && opsOverviewPollTimer) {
    clearInterval(opsOverviewPollTimer);
    opsOverviewPollTimer = null;
  }
}

function setEmergencyReconnectLivePolling(enabled) {
  if (enabled && !emergencyReconnectPollTimer) {
    emergencyReconnectPollTimer = setInterval(pollSourcesLive, REALTIME_POLL_INTERVAL_MS);
    pollSourcesLive();
  }
  if (!enabled && emergencyReconnectPollTimer) {
    clearInterval(emergencyReconnectPollTimer);
    emergencyReconnectPollTimer = null;
  }
}

function emergencyReconnectTimestamp() {
  const now = new Date();
  const pad = (value) => String(value).padStart(2, "0");
  return [
    now.getFullYear(),
    pad(now.getMonth() + 1),
    pad(now.getDate()),
  ].join("-") + " " + [
    pad(now.getHours()),
    pad(now.getMinutes()),
    pad(now.getSeconds()),
  ].join(":");
}

function sanitizeEmergencyReconnectMessage(message) {
  const text = String(message || "").trim();
  if (!text) return "";
  if (text.includes("1초 단위로 재접속 단계 진행 상태와 백그라운드 작업 결과가 이 영역에 유지됩니다.")) return "";
  if (text.includes("백그라운드 상에서만 이력을 남깁니다.")) return "";
  return text;
}

function appendEmergencyReconnectDetail(message) {
  const clean = sanitizeEmergencyReconnectMessage(message);
  if (!clean) return;
  const slot = emergencyReconnectDetailSlot || "-";
  const suffix = `, ${clean}`;
  if (emergencyReconnectDetailLogs.slice(-8).some((line) => String(line || "").endsWith(suffix))) return;
  emergencyReconnectDetailLogs.push(`${emergencyReconnectTimestamp()} - LOCK-FIX Reconnect DETAIL - slot ${slot}, ${clean}`);
  emergencyReconnectDetailLogs = emergencyReconnectDetailLogs.slice(-120);
}

function mergeEmergencyReconnectDetails(lines) {
  if (!Array.isArray(lines) || !lines.length) return;
  const next = [...emergencyReconnectDetailLogs];
  lines.forEach((line) => {
    const text = sanitizeEmergencyReconnectMessage(line);
    if (text && !next.includes(text)) next.push(text);
  });
  emergencyReconnectDetailLogs = next.slice(-120);
}

function applyEmergencyReconnectFlowState(state) {
  const value = String(state || "").trim();
  if (!value || !latestSourcesData?.air_gap?.emergency_access?.slot) return;
  latestSourcesData.air_gap.emergency_access.slot.state = value;
}

function isEmergencyReconnectCompleteState(state) {
  return ["ONLINE_VERIFIED_RW", "ONLINE_VERIFIED", "MOUNTED_RW", "COMPLETE", "COMPLETED"].includes(String(state || "").toUpperCase());
}

function appendEmergencyReconnectCompletion(state = "ONLINE_VERIFIED_RW") {
  const completionText = `긴급 접속이 완료되었다 - state ${state || "ONLINE_VERIFIED_RW"}`;
  const historyText = "완료 이력 저장됨 - Reconnect Detail Logs 및 Logs 메뉴에서 확인 가능";
  const alreadyLogged = emergencyReconnectDetailLogs.some((line) => line.includes("긴급 접속이 완료되었다") || line.includes("긴급 접속 완료") || line.includes("Reconnect COMPLETE"));
  if (!alreadyLogged) {
    appendEmergencyReconnectDetail(completionText);
    appendEmergencyReconnectDetail(historyText);
  }
}

function completeEmergencyReconnectWatch(state = "ONLINE_VERIFIED_RW") {
  appendEmergencyReconnectCompletion(state);
  stopEmergencyReconnectWatch("긴급 볼륨 접속 작업이 완료되었습니다.");
  renderSources(latestSourcesData || { air_gap: fallbackAirGapSummary(true) });
}

function finalizeEmergencyReconnectFromSources(sources) {
  if (!emergencyReconnectRunning) return false;
  const slot = sources?.air_gap?.emergency_access?.slot || {};
  const state = String(slot.state || "");
  const history = Array.isArray(slot.reconnect_history) ? slot.reconnect_history : [];
  const historyComplete = history.some((line) => /Reconnect COMPLETE|BACKGROUND COMPLETE|background\.complete|emergency\.reconnect\.complete|ONLINE_VERIFIED_RW|긴급 접속 완료|긴급 접속이 완료되었다/i.test(String(line || "")));
  if (isEmergencyReconnectCompleteState(state) || historyComplete) {
    mergeEmergencyReconnectDetails(history);
    completeEmergencyReconnectWatch(state || "ONLINE_VERIFIED_RW");
    return true;
  }
  return false;
}

function setEmergencyReconnectDetailLogging(enabled) {
  if (enabled && !emergencyReconnectDetailTimer) {
    emergencyReconnectDetailTimer = setInterval(() => {
      renderSources(latestSourcesData || { air_gap: fallbackAirGapSummary(true) });
    }, 1000);
  }
  if (!enabled && emergencyReconnectDetailTimer) {
    clearInterval(emergencyReconnectDetailTimer);
    emergencyReconnectDetailTimer = null;
  }
}

function stopEmergencyReconnectWatch(message = "") {
  emergencyReconnectRunning = false;
  setEmergencyReconnectLivePolling(false);
  setEmergencyReconnectDetailLogging(false);
  setEmergencyReconnectStatusPolling(false);
  if (message) emergencyActionStatus = message;
}

function emergencyReconnectResolutionText(result) {
  if (Array.isArray(result?.resolution) && result.resolution.length) {
    return result.resolution.join(" / ");
  }
  if (result?.resolution) return String(result.resolution);
  return "LOCK-FIX 관리자 권한 재시작 / WebUI 서비스 최신 소스 재시작 / Windows 디스크 API 권한 확인";
}

function setEmergencyReconnectStatusPolling(enabled) {
  if (enabled && !emergencyReconnectStatusTimer) {
    emergencyReconnectStatusTimer = setInterval(async () => {
      if (!emergencyReconnectRunning || !emergencyReconnectDetailSlot || !emergencyReconnectJobId) return;
      try {
        const result = await requestJson(`/api/emergency-reconnect/status?slot=${encodeURIComponent(emergencyReconnectDetailSlot)}&job_id=${encodeURIComponent(emergencyReconnectJobId)}`);
        const status = String(result.status || "").toLowerCase();
        mergeEmergencyReconnectDetails(result.detail_logs);
        applyEmergencyReconnectFlowState(result.flow_state);
        if (status === "idle" || status === "stale") {
          const message = status === "stale"
            ? "다른 긴급 재접속 작업이 등록되어 현재 작업 상태를 확인할 수 없습니다."
            : "재접속 작업이 현재 서비스에 등록되어 있지 않습니다. 버튼 요청이 서비스까지 도달했는지 확인 필요";
          appendEmergencyReconnectDetail(message);
          appendEmergencyReconnectDetail("해결 안내: WebUI 로그인 세션, 서비스 상태, 관리자 권한을 확인한 뒤 다시 데이터 무결성 확인 후 긴급 접속을 실행하세요.");
          stopEmergencyReconnectWatch(message);
          renderSources(latestSourcesData || { air_gap: fallbackAirGapSummary(true) });
        } else if (status === "not_started") {
          const message = result.message || "재접속 작업이 시작되지 않았습니다. 관리자 권한/서비스 상태 확인 필요";
          appendEmergencyReconnectDetail(message);
          appendEmergencyReconnectDetail(`해결 안내: ${emergencyReconnectResolutionText(result)}`);
          stopEmergencyReconnectWatch(message);
          renderSources(latestSourcesData || { air_gap: fallbackAirGapSummary(true) });
        } else if (status === "error") {
          const message = result.error || result.message || "긴급 볼륨 접속 작업이 오류로 종료되었습니다.";
          appendEmergencyReconnectDetail(`background job error: ${message}`);
          appendEmergencyReconnectDetail(`해결 안내: ${emergencyReconnectResolutionText(result)}`);
          stopEmergencyReconnectWatch("긴급 볼륨 접속 작업이 오류로 종료되었습니다. 상세 로그를 확인하세요.");
          renderSources(latestSourcesData || { air_gap: fallbackAirGapSummary(true) });
        } else if (status === "complete") {
          appendEmergencyReconnectDetail(`background job complete: ${result.state || "complete"}`);
          completeEmergencyReconnectWatch(result.state || result.flow_state || "ONLINE_VERIFIED_RW");
          await pollSourcesLive();
        } else if (status === "running") {
          const elapsed = Number(result.elapsed_seconds || 0);
          const message = result.background_started_at
            ? `background job running - ${elapsed}s elapsed`
            : `waiting for background worker start - ${elapsed}s elapsed`;
          if (!Array.isArray(result.detail_logs) || !result.detail_logs.length) {
            appendEmergencyReconnectDetail(message);
          }
        }
      } catch (error) {
        const latestState = latestSourcesData?.air_gap?.emergency_access?.slot?.state || "";
        const latestHistory = latestSourcesData?.air_gap?.emergency_access?.slot?.reconnect_history || [];
        if (isEmergencyReconnectCompleteState(latestState) || latestHistory.some((line) => /Reconnect COMPLETE|BACKGROUND COMPLETE|background\.complete|emergency\.reconnect\.complete|ONLINE_VERIFIED_RW|긴급 접속 완료|긴급 접속이 완료되었다/i.test(String(line || "")))) {
          mergeEmergencyReconnectDetails(latestHistory);
          completeEmergencyReconnectWatch(latestState || "ONLINE_VERIFIED_RW");
        } else {
          mergeEmergencyReconnectDetails(latestHistory);
          const message = Number(error.status || 0) === 401
            ? "status check failed: 로그인 세션이 만료되어 재접속 상태를 확인할 수 없습니다."
            : `status check failed: ${friendlyEmergencyError(error)}`;
          appendEmergencyReconnectDetail(message);
        }
      }
    }, 1000);
  }
  if (!enabled && emergencyReconnectStatusTimer) {
    clearInterval(emergencyReconnectStatusTimer);
    emergencyReconnectStatusTimer = null;
  }
}

async function reloadVeeamBackup() {
  const data = await requestJson("/api/veeam-backup");
  renderVeeamBackup(data);
}

async function pollVeeamBackupLive() {
  if (!currentSession.authenticated || appRoot.classList.contains("app-locked")) return;
  const activeView = document.querySelector(".view.view-active");
  if (!activeView || activeView.id !== "veeamView") return;
  try {
    await reloadVeeamBackup();
  } catch (error) {
    console.warn("Unable to poll Veeam backup status", error);
    if (veeamApiChip) veeamApiChip.textContent = error.message;
  }
}

function setVeeamLivePolling(enabled) {
  if (enabled && !veeamPollTimer) {
    veeamPollTimer = setInterval(pollVeeamBackupLive, 1000);
    pollVeeamBackupLive();
  }
  if (!enabled && veeamPollTimer) {
    clearInterval(veeamPollTimer);
    veeamPollTimer = null;
  }
}

function renderVeeamBackup(data) {
  if (!veeamApiChip) return;
  const api = data.api || {};
  const job = data.job || {};
  const steps = Array.isArray(data.steps) ? data.steps : [];
  const logs = Array.isArray(data.logs) ? data.logs : [];
  const result = String(job.result || "WAITING").toUpperCase();
  const apiSynced = isVeeamSynced(api);
  const progress = apiSynced ? Math.max(0, Math.min(100, Number(job.progress_percent || 0))) : 0;

  veeamApiChip.className = `veeam-api-chip veeam-api-${apiSynced ? "connected" : "waiting"}`;
  veeamApiChip.textContent = `${apiSynced ? "API CONNECTED" : "API WAITING"} · ${api.server}:${api.port} · ${api.poll_interval_seconds || 1}s`;
  veeamJobName.textContent = job.name || "-";
  veeamSessionState.textContent = job.session_state || "-";
  veeamResult.className = `veeam-result veeam-result-${result.toLowerCase()}`;
  veeamResult.textContent = result;
  veeamLastChecked.textContent = api.last_checked || "-";
  veeamProgressValue.textContent = `${progress}%`;
  veeamProgressFill.style.width = `${progress}%`;

  veeamStepGrid.replaceChildren();
  steps.forEach((step) => {
    const item = document.createElement("article");
    item.className = `veeam-step-card veeam-step-${String(step.state || "PENDING").toLowerCase()}`;
    const stepLabel = Number(step.step) === 1 ? "UID 검증<br />백업 완료" : step.label || "-";
    item.innerHTML = `
      <b>${step.step}</b>
      <strong>${stepLabel}</strong>
      <span>${step.code || "-"}</span>
      <em>${step.time || "-"}</em>
    `;
    veeamStepGrid.appendChild(item);
  });

  veeamLogCount.textContent = `${logs.length} logs`;
  veeamLogTable.replaceChildren();
  logs.forEach((log) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${log.time || "-"}</td>
      <td><span class="veeam-log-level veeam-log-${String(log.level || "INFO").toLowerCase()}">${log.level || "-"}</span></td>
      <td>${log.step || "-"}</td>
      <td>${log.source || "-"}</td>
      <td>${log.message || "-"}</td>
    `;
    veeamLogTable.appendChild(row);
  });
}

function isVeeamSynced(value) {
  const stateSource = String(value?.state_source || value?.stateSource || "").toLowerCase();
  return Boolean(
    value?.api_synced ||
    value?.connected ||
    value?.port_open && stateSource.startsWith("veeam_rest_api") ||
    stateSource.startsWith("veeam_rest_api")
  );
}

function fallbackAirGapSummary(loading = false) {
  return {
    security_score: {
      score: loading ? "--" : 98,
      status: loading ? "Air-Gap status is loading" : "SAFE AIR-GAP",
      description: loading
        ? "The Air-Gap overview remains available while live source data is refreshed."
        : "Power cut-off, solenoid lock, and integrity verification are all operating normally.",
    },
    kpis: [
      {
        id: "power",
        title: "Disk Offline",
        value: "Offline Complete",
        detail: "Windows disk offline isolation after unmount.",
      },
      {
        id: "lock",
        title: "Solenoid Lock",
        value: "Locked",
        detail: "Mechanical lock is engaged on the drive bay.",
      },
      {
        id: "integrity",
        title: "Integrity Check",
        value: "Verified",
        detail: "UID match and SHA-256 hash validation passed.",
      },
    ],
    timeline: [
      { step: 1, title: "Backup completed", label: "백업 완료", state: "PENDING", code: "BACKUP_COMPLETED" },
      { step: 2, title: "Flush running", label: "Flush 실행", state: "PENDING", code: "FLUSHING" },
      { step: 3, title: "I/O checking", label: "I/O 종료 확인", state: "PENDING", code: "IO_CHECKING" },
      { step: 4, title: "Unmount", label: "Unmount", state: "PENDING", code: "UNMOUNTING" },
      { step: 5, title: "Offline", label: "오프라인", state: "PENDING", code: "DISK_OFFLINING" },
    ],
    veeam: {
      api_poll_interval_seconds: 1,
      server: "127.0.0.1",
      port: 9419,
      connected: false,
      last_checked: "-",
      job: "LOCK-FIX-AIRGAP-BACKUP",
      session_state: loading ? "LOADING" : "BACKUP_COMPLETED",
      current_step: 1,
      state_source: "waiting_for_veeam_api",
      api_synced: false,
      port_open: false,
      progress_percent: 0,
      api_verification_percent: 0,
      message: "Veeam REST API is not connected yet. Current step is held and colors will not advance automatically.",
    },
    step_logs: [
      { step: 1, label: "백업 완료", code: "BACKUP_COMPLETED", state: "PENDING", time: "-", source: "Veeam REST API 대기", detail: "실제 Veeam REST API 세션이 확인될 때까지 단계 색상을 회색으로 유지합니다.", transition_allowed: false },
      { step: 2, label: "Flush 실행", code: "FLUSHING", state: "PENDING", time: "-", source: "Veeam REST API 대기", detail: "아직 이전 단계 완료 신호가 확인되지 않았습니다.", transition_allowed: false },
      { step: 3, label: "I/O 종료 확인", code: "IO_CHECKING", state: "PENDING", time: "-", source: "Veeam REST API 대기", detail: "아직 이전 단계 완료 신호가 확인되지 않았습니다.", transition_allowed: false },
      { step: 4, label: "Unmount", code: "UNMOUNTING", state: "PENDING", time: "-", source: "Veeam REST API 대기", detail: "아직 이전 단계 완료 신호가 확인되지 않았습니다.", transition_allowed: false },
      { step: 5, label: "오프라인", code: "DISK_OFFLINING", state: "PENDING", time: "-", source: "Veeam REST API 대기", detail: "아직 이전 단계 완료 신호가 확인되지 않았습니다.", transition_allowed: false },
    ],
    policy_events: [],
    bays: [
      {
        slot: "LOCK-FIX BAY 01",
        power: { label: "Disk Offline Complete" },
        lock: { state: "LOCKED", label: "Locked", description: "External physical access is blocked." },
        integrity: { uid: "Drive #1 - Match", hash: "SHA-256 Hash - Valid" },
      },
    ],
    integrity_history: [
      { time: "-", target: "Backup Cycle #1042", uid: "MATCH", hash: "VALID" },
    ],
    emergency: {
      title: "Emergency Control Center",
      description: "Manual release is available after current-user password approval.",
      primary: "Waiting for Password Approval",
      secondary: "Data path activation remains protected",
    },
    emergency_access: {
      title: "Emergency Volume Access",
      description: "Unmount 이후 긴급 접속이 필요한 경우 인증 해시값을 확인한 뒤 UID와 SHA-256 검증을 다시 수행하고 볼륨을 즉시 접속합니다.",
      primary: "무결성 검증 후 재접속",
      secondary: "C:\\ OS 볼륨은 어떤 경우에도 작업 대상이 될 수 없습니다.",
      slot: {
        slot_id: "BAY-01",
        device: "D:\\",
        mount_point: "D:\\",
        state: "WAITING",
        eligible: false,
        authorization_hash_short: "-",
        authorization_hash_protected: true,
        current_uid_short: "-",
        hash_status: "WAITING_FOR_MOUNT",
        manifest_hash_short: "-",
        last_unmount: "-",
        last_power_off: "-",
      },
      slots: [],
    },
  };
}

function renderSources(data) {
  latestSourcesData = data;
  renderOperationsOverview();
  const restoreContentScroll = keepContentAreaScroll();
  const previousSessionScroll = new Map();
  sourceList.querySelectorAll(".veeam-session-scroll-row").forEach((row, index) => {
    previousSessionScroll.set(row.dataset.scrollKey || String(index), row.scrollTop);
    previousSessionScroll.set(String(index), row.scrollTop);
  });
  const airGap = data?.air_gap || fallbackAirGapSummary();
  const securityScore = airGap.security_score || fallbackAirGapSummary().security_score;
  const kpis = Array.isArray(airGap.kpis) && airGap.kpis.length ? airGap.kpis : fallbackAirGapSummary().kpis;
  const timelineItems = Array.isArray(airGap.timeline) && airGap.timeline.length ? airGap.timeline : fallbackAirGapSummary().timeline;
  const veeam = airGap.veeam || fallbackAirGapSummary().veeam;
  const stepLogs = Array.isArray(airGap.step_logs) && airGap.step_logs.length ? airGap.step_logs : fallbackAirGapSummary().step_logs;
  const policyEvents = Array.isArray(airGap.policy_events) ? airGap.policy_events : [];
  const apiSynced = isVeeamSynced(veeam);
  const backupProgress = apiSynced ? Math.max(0, Math.min(100, Number(veeam.progress_percent || 0))) : 0;
  const apiPercent = backupProgress;
  const veeamSessionLogs = Array.isArray(airGap.session_logs) && airGap.session_logs.length
    ? airGap.session_logs
    : [{
        name: "Veeam REST API",
        status: "Waiting",
        actions: [
          `Veeam REST API is not synced. Check ${veeam.server || "127.0.0.1"}:${veeam.port || 9419} host, port, credentials, or token.`,
          "Step colors and arrows stay fixed until a real Veeam REST API session is received.",
        ],
        duration: "-",
        progress_percent: 0,
      }];
  const bays = Array.isArray(airGap.bays) && airGap.bays.length ? airGap.bays : fallbackAirGapSummary().bays;
  const integrityHistory = Array.isArray(airGap.integrity_history) && airGap.integrity_history.length
    ? airGap.integrity_history
    : fallbackAirGapSummary().integrity_history;
  const emergency = airGap.emergency || fallbackAirGapSummary().emergency;
  const emergencyAccess = airGap.emergency_access || fallbackAirGapSummary().emergency_access;
  const emergencySlot = emergencyAccess.slot || {};
  const autoApproval = emergencySlot.auto_approval || airGap.auto_approval || {};
  const procedureLabels = {
    1: "Backup Done",
    2: "Flush",
    3: "I/O Check",
    4: "Unmount",
    5: "Offline",
  };
  const stepLabel = (item) => procedureLabels[Number(item.step)] || airgapText(item.label || item.title || "-");
  const isStepLive = (item) => {
    const state = String(item.state || "").toUpperCase();
    return ["ACTIVE", "RUNNING", "WORKING", "DONE", "COMPLETED", "SUCCESS"].includes(state);
  };
  const veeamActionText = veeamSessionLogs
    .flatMap((log) => Array.isArray(log.actions) ? log.actions : [log.action || log.message || ""])
    .map((item) => String(item || ""))
    .join("\n");
  if (apiSynced && Number(veeam.current_step || 1) <= 1 && apiPercent < 100) {
    airgapStepEvidenceCache = {};
  }
  const stepEvidencePatterns = {
    2: {
      start: [/LOCK-FIX Flush START/i, /LOCK-FIX Flush TICK/i, /LOCK-FIX Flush OK/i, /LOCK-FIX STEP 2 COMPLETE/i],
      complete: [/LOCK-FIX Flush OK/i, /LOCK-FIX STEP 2 COMPLETE/i],
    },
    3: {
      start: [/LOCK-FIX I\/O Check START/i, /LOCK-FIX I\/O Check TICK/i, /LOCK-FIX I\/O Check OK/i, /LOCK-FIX STEP 3 COMPLETE/i],
      complete: [/LOCK-FIX I\/O Check OK/i, /LOCK-FIX STEP 3 COMPLETE/i],
    },
    4: {
      start: [/LOCK-FIX Unmount START/i, /LOCK-FIX Unmount TICK/i, /LOCK-FIX Unmount OK/i, /LOCK-FIX STEP 4 COMPLETE/i],
      complete: [/LOCK-FIX Unmount OK/i, /LOCK-FIX STEP 4 COMPLETE/i],
    },
    5: {
      start: [/LOCK-FIX Offline START/i, /LOCK-FIX Offline TICK/i, /LOCK-FIX Offline VERIFY START/i],
      complete: [
        /LOCK-FIX Offline VERIFY CONFIRMED[^\n]*IsOffline=true[^\n]*PathReachable=false/i,
        /LOCK-FIX Offline PROOF[^\n]*IsOffline=true/i,
        /LOCK-FIX STEP 5 COMPLETE[^\n]*IsOffline=true/i,
        /OFFLINE_COMPLETE[^\n]*IsOffline=true/i,
        /is_offline["']?\s*:\s*true/i,
      ],
    },
  };
  const hasStepEvidence = (step, type) => {
    const patterns = stepEvidencePatterns[step]?.[type] || [];
    return patterns.some((pattern) => pattern.test(veeamActionText));
  };
  const stepHasAdvanced = (item) => (
    apiSynced &&
    Number(item.step) < Number(veeam.current_step || 1) &&
    isStepLive(item) &&
    hasStepEvidence(Number(item.step) + 1, "start")
  );
  const stepIsPreparingTransfer = (item) => {
    const step = Number(item?.step);
    if (!apiSynced || step >= 5) return false;
    const currentStep = Number(veeam.current_step || 1);
    if (step !== currentStep) return false;
    const state = String(item?.state || "").toUpperCase();
    return ["DONE", "COMPLETED", "SUCCESS"].includes(state) || (step === 1 && apiPercent >= 100);
  };
  const stepTransferClass = (item) => {
    const step = Number(item.step);
    if (step >= 5) return "";
    const nextStep = step + 1;
    const currentStep = Number(veeam.current_step || 1);
    const canTransfer = apiSynced && currentStep > step;
    const complete = canTransfer && hasStepEvidence(nextStep, "complete");
    const running = stepIsPreparingTransfer(item) || (canTransfer && !complete && hasStepEvidence(nextStep, "start"));
    if (complete) return "veeam-step-transfer-arrow veeam-step-transfer-complete";
    if (running) return "veeam-step-transfer-arrow veeam-step-transfer-running";
    return "veeam-step-transfer-arrow";
  };
  const stepIncomingClass = (item) => {
    const step = Number(item.step);
    const previous = timelineItems.find((candidate) => Number(candidate.step) === step - 1);
    return previous && stepIsPreparingTransfer(previous) ? "veeam-step-visual-incoming" : "";
  };
  const stepVisualClass = (item) => {
    const step = Number(item.step);
    const currentStep = Number(veeam.current_step || 1);
    if (!apiSynced) return "veeam-step-visual-pending";
    if (step < currentStep) return "veeam-step-visual-complete";
    if (step === currentStep) return "veeam-step-visual-current";
    return "veeam-step-visual-pending";
  };
  const autoIsolate = veeam.auto_isolate || airGap.auto_isolate || {};
  const stepLiveState = (item) => {
    const step = Number(item.step);
    const currentStep = Number(veeam.current_step || 1);
    const state = String(item.state || "").toUpperCase();
    const autoState = String(autoIsolate.state || "").toUpperCase();
    if (!apiSynced) return "pending";
    if (step < currentStep || ["DONE", "COMPLETED", "SUCCESS"].includes(state)) return "complete";
    if (step > currentStep) return "pending";
    const isolationRunning = Boolean(autoIsolate.triggered) || ["IN_PROGRESS", "RUNNING", "WORKING"].includes(autoState);
    const activeRunning = ["ACTIVE", "RUNNING", "WORKING"].includes(state) && (
      isolationRunning ||
      (currentStep > 1 && currentStep < 5) ||
      (currentStep === 5 && autoState !== "ISOLATED")
    );
    return activeRunning ? "running" : "current";
  };
  const stepLiveClass = (item) => `veeam-step-live-${stepLiveState(item)}`;
  const airGapLiveStatus = () => {
    const autoState = String(autoIsolate.state || "").toUpperCase();
    if (!apiSynced) return "Waiting";
    if (["IN_PROGRESS", "RUNNING", "WORKING"].includes(autoState) || timelineItems.some((item) => stepLiveState(item) === "running")) {
      return "Running";
    }
    if (autoState === "ISOLATED" || timelineItems.every((item) => stepLiveState(item) === "complete")) return "Success";
    return "Monitoring";
  };
  const airGapStateVerb = (state) => ({
    running: "RUNNING",
    complete: "OK",
    current: "READY",
    pending: "WAIT",
  })[state] || "WAIT";
  const airGapLogTime = (item) => {
    const raw = item?.time || item?.timestamp || item?.at || item?.created_at || veeam.last_checked || "";
    return String(raw || "").trim() || "-";
  };
  const airGapLiveActions = () => {
    const currentStep = Number(veeam.current_step || 1);
    const actions = stepLogs.map((log, index) => {
      const step = Number(log.step || index + 1);
      const state = String(log.state || "").toLowerCase();
      const verb = airGapStateVerb(state === "done" ? "complete" : state === "active" ? "running" : state || "pending");
      const detail = log.detail || log.message || log.result || "Air-Gap 상태를 실시간 확인 중입니다.";
      return `${verb} - ${airGapLogTime(log)} · Step ${step} ${stepLabel({ step, label: log.label })}: ${detail}`;
    });
    actions.unshift(`${apiSynced ? "OK" : "WAIT"} - ${airGapLogTime(veeam)} · Air-Gap live feed ${apiSynced ? "receiving /api/sources?live=1 updates" : "waiting for Veeam REST API synchronization"}.`);
    actions.push(`${airGapLiveStatus().toUpperCase()} - ${airGapLogTime(veeam)} · Current Air-Gap step ${currentStep} / 5, Veeam progress ${apiPercent}%.`);
    if (autoIsolate.message) {
      const autoState = String(autoIsolate.state || airGapLiveStatus()).toUpperCase();
      actions.push(`${autoState === "ISOLATED" ? "OK" : autoState === "FAILED" ? "ERROR" : "RUNNING"} - ${airGapLogTime(autoIsolate)} · ${autoIsolate.message}`);
    }
    return actions.filter(Boolean).slice(-80);
  };
  const airGapLiveLog = {
    name: "LOCK-FIX Air-Gap",
    status: airGapLiveStatus(),
    actions: airGapLiveActions(),
    duration: "LIVE 1s",
    progress_percent: apiSynced ? Math.max(0, Math.min(100, Number(veeam.current_step || 1) * 20)) : 0,
  };
  const procedureSessionLogs = [airGapLiveLog, ...veeamSessionLogs];
  const progressCell = (log) => {
    const value = log.progress_percent;
    return value === "" || value === undefined || value === null ? "-" : `${value}%`;
  };
  const statusDisplay = (log) => progressCell(log);
  const statusVisualClass = (log) => {
    const key = String(log.status || "").toLowerCase();
    const progress = Number(log.progress_percent || 0);
    if (key.includes("fail") || key.includes("error")) return "failed";
    if (progress >= 100 || key.includes("success") || key.includes("succeed") || key.includes("completed")) return "success";
    return "running";
  };
  const transferMeta = (log) => {
    const values = [
      ["Progress", progressCell(log)],
      ["Size", log.backup_size || "-"],
      ["Transferred", log.transferred || "-"],
      ["Speed", log.speed || "-"],
      ["Start", log.started_at || "-"],
      ["End", log.ended_at || "-"],
      ["API", `${apiPercent}%`],
    ];
    if (log.last_known) values.unshift("Retained detail log");
    return values;
  };
  const statusClass = (status) => {
    const key = String(status || "").toLowerCase();
    if (key.includes("success") || key.includes("succeed") || key.includes("completed")) return "success";
    if (key.includes("fail") || key.includes("error")) return "failed";
    if (key.includes("running") || key.includes("working")) return "running";
    return "waiting";
  };
  const actionLevel = (text, status) => {
    const key = `${status || ""} ${text || ""}`.toLowerCase();
    if (key.includes("error") || key.includes("fail") || key.includes("cannot")) return "failed";
    if (key.includes("warn") || key.includes("wait")) return "waiting";
    if (key.includes("ok") || key.includes("success") || key.includes("complete")) return "success";
    if (key.includes("running") || key.includes("started") || key.includes("processing")) return "running";
    return statusClass(status);
  };
  const actionLabel = (text) => {
    const match = String(text || "").match(/^([A-Z][A-Z0-9 _-]{1,18})\s*-\s*/);
    return match ? match[1].trim() : "";
  };
  const actionBody = (text) => String(text || "").replace(/^([A-Z][A-Z0-9 _-]{1,18})\s*-\s*/, "");
  const transferMetaHtml = (log) => {
    const values = transferMeta(log);
    return `<div class="veeam-progress-summary">${values.map((item) => {
      if (Array.isArray(item)) {
        return `<span><b>${escapeHtml(item[0])}</b><strong>${escapeHtml(item[1])}</strong></span>`;
      }
      return `<span><strong>${escapeHtml(item)}</strong></span>`;
    }).join("")}</div>`;
  };
  const actionLines = (log) => {
    const actions = Array.isArray(log.actions) && log.actions.length ? log.actions : [log.action || log.message || "-"];
    return actions.map((action) => {
      const text = String(action ?? "-");
      const isSection = text.startsWith("LOCK-FIX STEP ");
      const level = actionLevel(text, log.status);
      const icon = isSection ? "" : `<i class="veeam-action-icon veeam-action-${level}"></i>`;
      return `<span class="${isSection ? "veeam-action-section" : `veeam-action-line veeam-action-line-${level}`}">${icon}<b>${escapeHtml(actionLabel(text))}</b><small>${escapeHtml(actionBody(text))}</small></span>`;
    }).join("");
  };
  const stepEvidenceLines = (step) => {
    const patterns = {
      2: [/LOCK-FIX STEP 2/i, /LOCK-FIX Flush/i, /disk\.flush/i, /disk\.cache\.flush/i],
      3: [/LOCK-FIX STEP 3/i, /LOCK-FIX I\/O/i, /io quiet/i, /disk\.io/i],
      4: [/LOCK-FIX STEP 4/i, /LOCK-FIX Unmount/i, /disk\.unmount/i],
      5: [/LOCK-FIX STEP 5/i, /LOCK-FIX Offline/i, /disk\.offline/i, /OFFLINE_COMPLETE/i],
    }[Number(step)] || [];
    if (!patterns.length) return [];
    const lines = veeamSessionLogs
      .flatMap((log) => Array.isArray(log.actions) ? log.actions : [log.action || log.message || ""])
      .map((item) => String(item || "").trim())
      .filter((item) => item && patterns.some((pattern) => pattern.test(item)));
    const unique = [...new Set(lines)];
    if (unique.length) {
      airgapStepEvidenceCache[String(step)] = [
        ...new Set([...(airgapStepEvidenceCache[String(step)] || []), ...unique]),
      ].slice(-40);
    }
    return (airgapStepEvidenceCache[String(step)] || unique).slice(-12);
  };
  const stepFallbackEvidence = (step) => {
    if (Number(step) === 2) {
      return [
        "LOCK-FIX STEP 2 DETAIL - Flush operation flow is monitored from audit records.",
        "LOCK-FIX Flush TARGET - configured backup volume only; C:\\ OS volume remains protected.",
        "LOCK-FIX Flush RESULT - waiting until disk.flush / disk.cache.flush audit result is recorded.",
      ];
    }
    if (Number(step) === 3) {
      return [
        "LOCK-FIX STEP 3 DETAIL - I/O quiet verification flow is monitored from audit records.",
        "LOCK-FIX I/O Check WINDOW - no-write quiet window must be satisfied before Unmount.",
        "LOCK-FIX I/O Check RESULT - waiting until disk.io_quiet audit result is recorded.",
      ];
    }
    return [];
  };
  sourceList.replaceChildren();

  sourceRoot.className = "source-root airgap-procedure-root";
  sourceRoot.innerHTML = `
    <div class="veeam-step-grid airgap-procedure-steps">
      ${timelineItems.map((item) => `
        <article class="veeam-step-card veeam-step-${String(item.state || "PENDING").toLowerCase()} ${stepVisualClass(item)} ${stepIncomingClass(item)} ${stepLiveClass(item)} ${stepHasAdvanced(item) ? "veeam-step-arrow-visible" : ""} ${stepTransferClass(item)}" data-step-state="${stepLiveState(item)}" aria-label="${stepLabel(item)} ${stepLiveState(item)}">
          <b>${item.step}</b>
          <div class="veeam-step-copy">
            <strong class="step-label-main">${stepLabel(item)}</strong>
          </div>
        </article>
      `).join("")}
    </div>
  `;

  const procedureLogs = document.createElement("section");
  procedureLogs.className = "veeam-panel veeam-monitoring-panel airgap-monitoring-panel";
  const sessionMetaParts = [
    `${procedureSessionLogs.length} sessions`,
    veeam.job,
    veeam.last_checked,
  ].map((item) => String(item || "").trim()).filter((item) => item && item !== "-");
  procedureLogs.innerHTML = `
    <div class="veeam-log-header">
      <h2>${t("veeam.logs")}</h2>
      <div class="veeam-log-meta">
        <span>${escapeHtml(sessionMetaParts.join(" · "))}</span>
      </div>
    </div>
    <div class="veeam-log-wrap">
      <table class="veeam-log-table">
        <colgroup>
          <col class="veeam-log-col-name" />
          <col class="veeam-log-col-action" />
          <col class="veeam-log-col-duration" />
        </colgroup>
        <thead>
          <tr>
            <th>Name</th>
            <th>Action</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          ${procedureSessionLogs.map((log, index) => `
            <tr>
              <td class="veeam-session-name">${escapeHtml(log.name || "-")}</td>
              <td colspan="2">
                <div class="veeam-session-scroll-row" data-scroll-key="${escapeHtml(`${index}:${log.name || "-"}`)}">
                  <div class="veeam-session-actions">${actionLines(log)}${transferMetaHtml(log)}</div>
                  <span class="veeam-session-duration">${escapeHtml(log.duration || "-")}</span>
                </div>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
  sourceList.appendChild(procedureLogs);
  procedureLogs.querySelectorAll(".veeam-session-scroll-row").forEach((row, index) => {
    const previousTop = previousSessionScroll.get(row.dataset.scrollKey || "") ?? previousSessionScroll.get(String(index));
    if (Number.isFinite(previousTop)) row.scrollTop = previousTop;
  });

  // Policy guard events continue to be generated and stored in audit/detail logs.
  // The customer-facing Air-Gap screen keeps those background decisions hidden.

  const emergencyPanel = document.createElement("section");
  const emergencyVolumePath = String(emergencySlot.mount_point || emergencySlot.device || "").trim();
  const emergencyVolumeNormalized = emergencyVolumePath.replaceAll("/", "\\").trim().toUpperCase();
  const emergencyStateText = [
    emergencySlot.state,
    emergencySlot.hash_status,
    emergencySlot.blocked_reason,
    emergencySlot.last_unmount,
    emergencySlot.last_power_off,
  ].map((item) => String(item || "")).join(" ").toUpperCase();
  const emergencyIsOsVolume = emergencyVolumeNormalized === "C:" || emergencyVolumeNormalized.startsWith("C:\\");
  const emergencyLooksDisconnected = /ISOLATED|OFFLINE|DISK_OFFLINE|OFFLINE_COMPLETE|UNMOUNT|DISMOUNT|WAITING_DISK|WAITING_FOR_MOUNT|MOUNT_ACCESS_ERROR|QUARANTINE|ERROR/.test(emergencyStateText);
  const emergencyAlreadyOnline = /ONLINE_VERIFIED_RW|ONLINE_VERIFIED|READY/.test(emergencyStateText) && !emergencyLooksDisconnected;
  const emergencyEligible = !emergencyIsOsVolume && !emergencyAlreadyOnline && (Boolean(emergencySlot.eligible) || emergencyLooksDisconnected);
  const emergencyHashOk = String(emergencySlot.hash_status || "").toUpperCase() === "VALID";
  const emergencyStateValue = String(emergencySlot.state || "-");
  const emergencyStateUpper = emergencyStateValue.toUpperCase();
  const emergencyStateClass = emergencyStateUpper === "ERROR"
    ? "emergency-state-error"
    : ((emergencyReconnectRunning || emergencyEligible) ? "emergency-state-ok" : "emergency-state-neutral");
  const reconnectRuntimeOrder = [
    "RECONNECT_REQUESTED",
    "DISK_ONLINING",
    "WAITING_DISK",
    "VERIFYING_UID",
    "MOUNTED_READONLY",
    "VERIFYING_HASH",
    "ONLINE_VERIFIED_RW",
  ];
  const reconnectDisplayOrder = [...reconnectRuntimeOrder].reverse();
  const reconnectReportedState = String(emergencySlot.state || "").toUpperCase();
  const reconnectIsComplete = isEmergencyReconnectCompleteState(reconnectReportedState);
  const reconnectFlowIsActive = emergencyReconnectRunning || emergencyReconnectDetailLogs.length > 0 || reconnectIsComplete;
  const reconnectCurrentState = reconnectFlowIsActive && reconnectRuntimeOrder.includes(reconnectReportedState)
    ? reconnectReportedState
    : (emergencyReconnectRunning ? "RECONNECT_REQUESTED" : "");
  const reconnectTerminalStates = ["ONLINE_VERIFIED_RW", "ERROR", "QUARANTINE"];
  const reconnectCurrentIndex = reconnectRuntimeOrder.indexOf(reconnectCurrentState);
  const reconnectOlderLogs = Array.isArray(emergencySlot.reconnect_history_more) ? emergencySlot.reconnect_history_more : [];
  const reconnectRecentLogs = Array.isArray(emergencySlot.reconnect_history) ? emergencySlot.reconnect_history : [];
  const reconnectMoreCount = Number(emergencySlot.reconnect_history_more_count || reconnectOlderLogs.length || 0);
  const hasReconnectMore = reconnectMoreCount > 0;
  const hasLiveReconnectLogs = emergencyReconnectRunning || emergencyReconnectDetailLogs.length > 0;
  const hasCurrentReconnectError = reconnectCurrentState === "ERROR" && reconnectRecentLogs.length > 0;
  const reconnectDetailLogs = [
    ...(hasLiveReconnectLogs ? emergencyReconnectDetailLogs : []),
    ...(hasCurrentReconnectError ? reconnectRecentLogs : []),
    ...(reconnectHistoryExpanded ? reconnectOlderLogs : []),
  ];
  const reconnectLiveLogLines = [
    ...(emergencyReconnectDetailLogs.length ? emergencyReconnectDetailLogs : []),
    ...reconnectRecentLogs,
  ].filter(Boolean).slice(-8);
  const showReconnectDetailLogs = hasLiveReconnectLogs || hasCurrentReconnectError || reconnectHistoryExpanded;
  const reconnectStepClass = (state) => {
    if (!reconnectFlowIsActive) return "pending";
    const index = reconnectRuntimeOrder.indexOf(state);
    if (reconnectIsComplete && reconnectCurrentIndex >= 0 && index >= 0 && index <= reconnectCurrentIndex) return "done";
    if (state === reconnectCurrentState) return "current";
    if (reconnectCurrentIndex >= 0 && index >= 0 && index < reconnectCurrentIndex) return "done";
    return "pending";
  };
  const reconnectFriendlyLabels = {
    ONLINE_VERIFIED_RW: "ONLINE VERIFIED",
    VERIFYING_HASH: "VERIFYING HASH",
    MOUNTED_READONLY: "MOUNTED",
    VERIFYING_UID: "VERIFYING UID",
    WAITING_DISK: "VOLUME DETECTING",
    DISK_ONLINING: "DISK ONLINE",
    RECONNECT_REQUESTED: "RECONNECT",
  };
  const reconnectStepLabel = (state) => reconnectFriendlyLabels[String(state || "").toUpperCase()]
    || String(state || "")
      .replace(/_RW$/, "")
      .replace(/_REQUESTED$/, "")
      .replace(/_READONLY$/, "")
      .replaceAll("_", " ");
  const reconnectFlowMarkup = reconnectDisplayOrder.map((state, index) => {
    const stepClass = reconnectStepClass(state);
    const nextState = reconnectDisplayOrder[index + 1] || "";
    const nextIndex = reconnectRuntimeOrder.indexOf(nextState);
    const isArrowRunning = reconnectFlowIsActive && reconnectCurrentIndex === nextIndex;
    const isArrowComplete = reconnectFlowIsActive && reconnectCurrentIndex > nextIndex && nextIndex >= 0;
    return `
      <article class="emergency-reconnect-step emergency-reconnect-${stepClass}">
        <strong>${escapeHtml(reconnectStepLabel(state))}</strong>
      </article>
      ${index < reconnectDisplayOrder.length - 1 ? `<i class="emergency-reconnect-arrow ${isArrowComplete ? "arrow-active" : ""} ${isArrowRunning ? "arrow-running" : ""}" aria-hidden="true"></i>` : ""}
    `;
  }).join("");
  emergencyPanel.className = `airgap-panel emergency-access-panel ${emergencyEligible ? "emergency-access-ready" : "emergency-access-wait"} ${emergencyReconnectRunning ? "emergency-reconnect-running" : ""}`;
  const emergencyCtaText = emergencyReconnectRunning ? "작업 시작됨" : (emergencyAccess.primary || "무결성 검증 후 재접속");
  const emergencyStatusText = emergencyReconnectRunning
    ? "RUNNING"
    : emergencyEligible
      ? "READY"
      : "WAITING";
  const emergencyLiveLogMarkup = reconnectLiveLogLines
    .map((line) => `<li>${escapeHtml(line)}</li>`)
    .join("");
  emergencyPanel.innerHTML = `
    <div class="emergency-access-card-head">
      <div class="emergency-access-copy">
        <h2>${escapeHtml(emergencyAccess.title || "Emergency Volume Access")}</h2>
        <p>${escapeHtml(emergencyAccess.description || "-")}</p>
      </div>
      <div class="emergency-access-control-card">
        <span>${escapeHtml(emergencyStatusText)}</span>
        <button class="emergency-access-button" type="button" data-slot="${escapeHtml(emergencySlot.slot_id || "")}" data-volume="${escapeHtml(emergencyVolumePath)}" data-lock-disabled="${emergencyEligible ? "false" : "true"}" ${emergencyEligible && !emergencyReconnectRunning ? "" : "disabled"}>
          ${escapeHtml(emergencyCtaText)}
        </button>
      </div>
    </div>
    <div class="emergency-reconnect-flow-wrap">
      <span>Reconnect State Flow</span>
      <div class="emergency-reconnect-flow" aria-label="Emergency reconnect state flow">
        ${reconnectFlowMarkup}
      </div>
    </div>
    <div class="emergency-live-log-card">
      <ul class="emergency-live-log-list" data-emergency-live-log>
        ${emergencyLiveLogMarkup}
      </ul>
    </div>
  `;
  sourceList.appendChild(emergencyPanel);
  const emergencyLiveLog = emergencyPanel.querySelector("[data-emergency-live-log]");
  if (emergencyLiveLog) emergencyLiveLog.scrollTop = emergencyLiveLog.scrollHeight;
  const emergencyHistory = emergencyPanel.querySelector(".emergency-history-log");
  if (emergencyHistory && hasLiveReconnectLogs) {
    emergencyHistory.scrollTop = emergencyHistory.scrollHeight;
  }
  emergencyPanel.querySelector("[data-reconnect-more]")?.addEventListener("click", () => {
    reconnectHistoryExpanded = !reconnectHistoryExpanded;
    renderSources(latestSourcesData || { air_gap: fallbackAirGapSummary(true) });
  });
  emergencyPanel.querySelector(".emergency-access-button")?.addEventListener("click", (event) => {
    const button = event.currentTarget;
    button.classList.add("emergency-access-button-pending");
    const slotId = button.dataset.slot || "";
    const volumePath = button.dataset.volume || "";
    runEmergencyReconnect(slotId, volumePath);
  });
  restoreContentScroll();
  return;

  sourceRoot.innerHTML = `
    <section class="airgap-hero">
      <div class="airgap-score">
        <span>${airgapText("Unified Security Score")}</span>
        <strong>${securityScore.score}</strong>
        <em>${airgapText(securityScore.status)}</em>
      </div>
      <p>${airgapText(securityScore.description)}</p>
    </section>
  `;

  const kpi = document.createElement("section");
  kpi.className = "airgap-kpi-grid";
  kpi.innerHTML = kpis.map((item) => `
    <article class="airgap-kpi airgap-kpi-${item.id}">
      <i aria-hidden="true"></i>
      <div>
        <span>${airgapText(item.title)}</span>
        <strong>${airgapText(item.value)}</strong>
        <p>${airgapText(item.detail)}</p>
      </div>
    </article>
  `).join("");
  sourceList.appendChild(kpi);

  const timeline = document.createElement("section");
  timeline.className = "airgap-panel airgap-interlock-panel";
  timeline.innerHTML = `
    <div class="airgap-panel-head">
      <h2>${airgapText("Real-time Interlock Process")}</h2>
      <span>${airgapText("Veeam REST API Polling")} · ${veeam.api_poll_interval_seconds || 1}s</span>
    </div>
    <div class="veeam-live-status">
      <strong>${veeam.connected ? "CONNECTED" : "CHECKING"}</strong>
      <span>Veeam ${veeam.server}:${veeam.port} · ${veeam.job} · ${veeam.last_checked}</span>
      <em>${airgapText(veeam.message)}</em>
    </div>
    <div class="airgap-interlock-flow">
      ${timelineItems.map((item) => `
        <article class="interlock-step interlock-${String(item.state || "PENDING").toLowerCase()}">
          <b>${item.step}</b>
          <strong>${airgapText(item.label || item.title)}</strong>
        </article>
      `).join("")}
    </div>
  `;
  sourceList.appendChild(timeline);

  const detailLogs = document.createElement("section");
  detailLogs.className = "airgap-panel airgap-step-log-panel";
  detailLogs.innerHTML = `
    <div class="airgap-panel-head">
      <h2>${airgapText("Step Detail Logs")}</h2>
      <span>${airgapText("Real-time transition evidence")}</span>
    </div>
    <div class="airgap-step-log-grid">
      ${stepLogs.map((log) => `
        <article class="step-log-card step-log-${String(log.state || "PENDING").toLowerCase()}">
          <div class="step-log-top">
            <b>${log.step}</b>
            <div>
              <strong>${airgapText(log.label)}</strong>
              <span>${log.code}</span>
            </div>
          </div>
          <dl>
            <div><dt>상태</dt><dd>${log.state || "PENDING"}</dd></div>
            <div><dt>확인 시간</dt><dd>${log.time || "-"}</dd></div>
            <div><dt>연동</dt><dd>${airgapText(log.source || "-")}</dd></div>
            <div><dt>색상 전환</dt><dd>${log.transition_allowed ? "허용" : "대기"}</dd></div>
          </dl>
          <p>${log.detail || "-"}</p>
          ${[2, 3].includes(Number(log.step)) || stepEvidenceLines(log.step).length ? `
            <div class="step-log-evidence">
              <strong>근거 로그</strong>
              ${(stepEvidenceLines(log.step).length ? stepEvidenceLines(log.step) : stepFallbackEvidence(log.step)).map((line) => `<span>${escapeHtml(line)}</span>`).join("")}
            </div>
          ` : ""}
        </article>
      `).join("")}
    </div>
  `;
  sourceList.appendChild(detailLogs);

  const bayMap = document.createElement("section");
  bayMap.className = "airgap-panel";
  bayMap.innerHTML = `
    <div class="airgap-panel-head">
      <h2>${airgapText("Drive Bay Map")}</h2>
      <span>${airgapText("Physical power and solenoid status by slot")}</span>
    </div>
    <div class="airgap-bay-grid">
      ${bays.map((bay) => `
        <article class="airgap-bay ${bay.lock?.state === "LOCKED" ? "bay-locked" : "bay-ready"}">
          <div class="bay-top">
            <strong>${bay.slot}</strong>
            <span>${airgapText(bay.lock?.label)}</span>
          </div>
          <div class="bay-visual">
            <i class="circuit-cut" aria-hidden="true"></i>
            <i class="bay-lock" aria-hidden="true"></i>
          </div>
          <dl>
            <div><dt>${airgapText("Power Cut-off")}</dt><dd>${airgapText(bay.power?.label)}</dd></div>
            <div><dt>${airgapText("Solenoid")}</dt><dd>${airgapText(bay.lock?.description)}</dd></div>
            <div><dt>UID</dt><dd>${airgapText(bay.integrity?.uid)}</dd></div>
            <div><dt>${airgapText("Hash")}</dt><dd>${airgapText(bay.integrity?.hash)}</dd></div>
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
        <h2>${airgapText("Integrity Check Report")}</h2>
        <span>${airgapText("UID and SHA-256 verification history")}</span>
      </div>
      <div class="integrity-summary">
        <div><span>${airgapText("UID Match")}</span><strong>${airgapText("Drive #1 - Match")}</strong></div>
        <div><span>${airgapText("Hash Validation")}</span><strong>${airgapText("SHA-256 Hash - Valid")}</strong></div>
        <div><span>${airgapText("Anomaly Detection")}</span><strong class="integrity-ok">${airgapText("None")}</strong></div>
      </div>
      <table class="airgap-history">
        <thead><tr><th>${airgapText("Time")}</th><th>${airgapText("Target")}</th><th>UID</th><th>${airgapText("Hash")}</th></tr></thead>
        <tbody>
          ${integrityHistory.map((item) => `
            <tr><td>${item.time}</td><td>${airgapText(item.target)}</td><td>${airgapText(item.uid)}</td><td>${airgapText(item.hash)}</td></tr>
          `).join("")}
        </tbody>
      </table>
    </article>
    <article class="airgap-panel emergency-panel">
      <div class="airgap-panel-head">
        <h2>${airgapText(emergency.title)}</h2>
        <span>${airgapText("Password re-authentication required")}</span>
      </div>
      <p>${airgapText(emergency.description)}</p>
      <button type="button">${airgapText(emergency.primary)}</button>
      <strong>${airgapText(emergency.secondary)}</strong>
    </article>
  `;
  sourceList.appendChild(integrity);
}

function drawLineChart(series) {
  const width = 920;
  const height = 210;
  const pad = { left: 90, right: 22, top: 6, bottom: 28 };
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
      return `<line x1="${pad.left}" y1="${yy}" x2="${width - pad.right}" y2="${yy}" class="grid-line"></line><text x="${pad.left - 14}" y="${Number(yy) + 3.5}" class="axis-label" text-anchor="end">${tick}.00%</text>`;
    })
    .join("");

  const labels = visibleSeries
    .filter((_, index) => index % Math.max(1, Math.ceil(visibleSeries.length / 6)) === 0 || index === visibleSeries.length - 1)
    .map((item) => {
      const realIndex = visibleSeries.indexOf(item);
      return `<text x="${x(realIndex)}" y="${height - 18}" class="axis-label" text-anchor="middle">${item.label.slice(0, 5)}</text>`;
    })
    .join("");

  const memoryPath = smoothPathFor("memory");
  const metricMeta = {
    cpu: { className: "line-cpu", path: smoothPathFor("cpu") },
    memory: { className: "line-memory", path: memoryPath },
    disk: { className: "line-disk", path: smoothPathFor("disk") },
    network: { className: "line-network", path: smoothPathFor("network") },
    interface: { className: "line-interface", path: smoothPathFor("interface") },
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
    <text x="24" y="${height / 2}" class="axis-title" transform="rotate(-90 24 ${height / 2})">하드웨어 사용량</text>
    ${fillPath}
    <path d="${activePath.path}" class="line ${activePath.className}"></path>
    ${labels}
  `;
}
function renderGauge(target, label, value, color) {
  const key = label.toLowerCase();
  const thresholds = { cpu: 80, memory: 80, disk: 85, network: 75, interface: 70 };
  const values = latestMonitoringSeries.map((item) => Number(item[key] || 0));
  const average = values.length ? values.reduce((sum, item) => sum + item, 0) / values.length : value;
  const peak = values.length ? Math.max(...values) : value;
  const status = peak >= (thresholds[key] || 80) ? "Warning" : "Normal";
  const statusClass = status === "Warning" ? "warning" : "normal";
  const valueColor = status === "Warning" ? "#e11d1d" : "#0b2e79";
  target.innerHTML = `
    <div class="gauge-card-body">
      <span>${escapeHtml(label)}</span>
      <strong style="color:${valueColor}">${Number(value).toFixed(value % 1 ? 1 : 0)}%</strong>
      <div class="gauge-meta">
        <em>Avg ${average.toFixed(1)}%</em>
        <em>Peak ${peak.toFixed(1)}%</em>
      </div>
      <b class="gauge-status-${statusClass}">${status}</b>
    </div>
  `;
}

function auditRecordText(record) {
  try {
    return JSON.stringify(record || {}, null, 0);
  } catch (error) {
    return String(record || "");
  }
}

function auditRecordTime(record) {
  return formatLogDate(record?.ts || record?.time || record?.date || record?.timestamp || "");
}

function auditDateValue(value) {
  const text = String(value || "").replace(" ", "T").slice(0, 19);
  const date = new Date(text);
  return Number.isNaN(date.getTime()) ? null : date;
}

function auditDateKey(value) {
  const date = auditDateValue(value);
  if (!date) return "";
  const pad = (item) => String(item).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

function auditEventLabel(record) {
  const event = String(record?.event || "").toLowerCase();
  const text = auditRecordText(record).toLowerCase();
  if (event.includes("auth.login.warning.threshold")) return "로그인 3회 실패 경고";
  if (event.includes("auth.login.locked")) return "관리자 승인 필요";
  if (event.includes("auth.temp_password.requested")) return "임시 비밀번호 승인 요청";
  if (event.includes("auth.temp_password.approved")) return "임시 비밀번호 승인";
  if (event.includes("auth.login.temp.success")) return "임시 비밀번호 로그인";
  if (event.includes("auth.login.failed")) return "로그인 실패";
  if (event.includes("auth.login.success")) return "로그인 성공";
  if (event.includes("auth.security_mail")) return "보안 메일 발송";
  if (event.includes("emergency.reconnect")) return "긴급 재접속";
  if (event.includes("disk.online.approval.cleared")) return "승인 해제";
  if (event.includes("disk.online") || event.includes("mount_rw")) return "승인 기반 온라인";
  if (event.includes("disk.offline") || event.includes("isolation") || event.includes("power.command.off")) return "격리/오프라인";
  if (event.includes("unauthorized") || text.includes("unauthorized") || text.includes("reblocked")) return "차단된 재연결";
  if (event.includes("verify.hash") || text.includes("hash")) return "무결성 검증";
  if (event.includes("verify.uid") || text.includes("uid")) return "UID 검증";
  if (event.includes("veeam")) return "Veeam 백업";
  if (event.includes("license")) return "라이선스";
  if (event.includes("state.transition")) return "상태 전환";
  return record?.event || "감사 이벤트";
}

function auditDevice(record) {
  const text = auditRecordText(record);
  const bay = text.match(/BAY-\d+/i)?.[0];
  const drive = text.match(/[A-Z]:\\/i)?.[0];
  return record?.slot_id || record?.device || record?.drive_letter || record?.target_device || bay || drive || "-";
}

function auditUser(record) {
  return record?.user || record?.actor || record?.account || record?.requested_by || "system";
}

function auditApprover(record) {
  const event = String(record?.event || "").toLowerCase();
  if (record?.approver || record?.approved_by) return record.approver || record.approved_by;
  if (event.includes("auth.temp_password") || event.includes("auth.login.locked")) return "administrator";
  if (record?.approved_until || event.includes("approved")) return "administrator";
  return "-";
}

function auditResult(record) {
  const event = String(record?.event || "").toLowerCase();
  const state = String(record?.state || "").toLowerCase();
  const text = auditRecordText(record).toLowerCase();
  if (event.includes("auth.login.locked") || event.includes("auth.temp_password.requested")) return "진행";
  if (event.includes("auth.login.failed")) return "실패";
  if (event.includes("auth.security_mail.skipped")) return "진행";
  if (event.includes("error") || event.includes("failed") || event.includes("denied") || state === "error" || text.includes("access denied") || text.includes("액세스 거부")) return "실패";
  if (event.includes(".start") || event.includes(".tick") || event.includes("heartbeat") || state === "running") return "진행";
  return "성공";
}

function auditRisk(record) {
  const event = String(record?.event || "").toLowerCase();
  const text = auditRecordText(record).toLowerCase();
  const failureCount = Number(record?.failure_count || 0);
  if (event.includes("auth.login.locked") || event.includes("auth.temp_password.requested") || failureCount >= 5) return "높음";
  if (event.includes("auth.login.warning") || event.includes("auth.login.failed") || failureCount >= 3) return "주의";
  if (event.includes("unauthorized") || event.includes("denied") || event.includes("quarantine") || text.includes("mismatch") || text.includes("불일치")) return "높음";
  if (event.includes("error") || event.includes("failed") || event.includes("timeout") || text.includes("access denied") || text.includes("액세스 거부")) return "주의";
  return "낮음";
}

function auditBackupJob(record) {
  const text = auditRecordText(record);
  return record?.job_name || record?.job || record?.backup_job || text.match(/Backup Copy Job [^\\"]+/i)?.[0] || "-";
}

function auditBeforeAfter(record) {
  const before = record?.before_state || record?.previous_state || record?.from_state || "-";
  const after = record?.after_state || record?.state || record?.to_state || "-";
  if (before === "-" && after === "-") return "-";
  return `${before} -> ${after}`;
}

function auditIntegrityResult(record) {
  const event = String(record?.event || "").toLowerCase();
  const text = auditRecordText(record).toLowerCase();
  if (record?.hash_status) return String(record.hash_status);
  if (record?.uid_status) return String(record.uid_status);
  if (text.includes("mismatch") || text.includes("불일치")) return "MISMATCH";
  if (event.includes("verify.hash") || text.includes("hash") || text.includes("valid")) return "VALID";
  return "-";
}

function auditLoginSecurity(record) {
  const event = String(record?.event || "").toLowerCase();
  const isAuth = event.includes("auth.login") || event.includes("auth.temp_password") || event.includes("auth.security_mail");
  return {
    visible: isAuth,
    failureCount: record?.failure_count ?? "-",
    lastFailedAt: formatLogDate(record?.last_failed_at || record?.ts || record?.time || ""),
    smtpStatus: record?.smtp_status || record?.mail_status || "-",
    adminEmail: record?.admin_email || "-",
    approvalStatus: record?.approval_status || (event.includes("approved") ? "APPROVED" : event.includes("requested") || event.includes("locked") ? "PENDING" : "-"),
    temporaryExpiresAt: formatLogDate(record?.temporary_expires_at || record?.expires_at || ""),
    temporaryDigest: record?.temporary_password_digest || "-",
    clientIp: record?.client_ip || "-",
    authMethod: record?.auth_method || (event.includes("temp") ? "temporary_password" : "-"),
  };
}

function normalizeSecurityAuditRecord(record, index) {
  const id = `${index}-${record?.ts || ""}-${record?.event || ""}`;
  const detail = record?.message || record?.resolution || record?.error || record?.output || auditRecordText(record);
  return {
    id,
    source: record || {},
    time: auditRecordTime(record),
    eventCode: record?.event || "audit.event",
    event: auditEventLabel(record),
    device: auditDevice(record),
    user: auditUser(record),
    approver: auditApprover(record),
    result: auditResult(record),
    risk: auditRisk(record),
    detail: detail || "-",
    backupJob: auditBackupJob(record),
    beforeAfter: auditBeforeAfter(record),
    approvalReason: record?.reason || record?.approval_reason || record?.message || "-",
    integrity: auditIntegrityResult(record),
    loginSecurity: auditLoginSecurity(record),
  };
}

function securityAuditMatchesFilters(item) {
  const dateKey = auditDateKey(item.time);
  if (securityAuditFilters.start && dateKey && dateKey < securityAuditFilters.start) return false;
  if (securityAuditFilters.end && dateKey && dateKey > securityAuditFilters.end) return false;
  if (securityAuditFilters.event && item.event !== securityAuditFilters.event) return false;
  if (securityAuditFilters.device && item.device !== securityAuditFilters.device) return false;
  if (securityAuditFilters.user && !String(item.user).toLowerCase().includes(securityAuditFilters.user.toLowerCase())) return false;
  if (securityAuditFilters.result && item.result !== securityAuditFilters.result) return false;
  if (securityAuditFilters.risk && item.risk !== securityAuditFilters.risk) return false;
  return true;
}

function renderSecurityAuditOptions(items) {
  const fillSelect = (select, values, current) => {
    if (!select) return;
    const unique = [...new Set(values.filter(Boolean))].sort((a, b) => String(a).localeCompare(String(b)));
    select.innerHTML = [`<option value="">전체</option>`]
      .concat(unique.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`))
      .join("");
    select.value = current || "";
  };
  fillSelect(securityAuditType, items.map((item) => item.event), securityAuditFilters.event);
  fillSelect(securityAuditDevice, items.map((item) => item.device).filter((item) => item !== "-"), securityAuditFilters.device);
}

function renderSecurityAuditSummary(items) {
  if (!securityAuditSummary) return;
  const now = new Date();
  const pad = (value) => String(value).padStart(2, "0");
  const todayKey = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  const todayItems = items.filter((item) => auditDateKey(item.time) === todayKey);
  const countBy = (matcher) => todayItems.filter(matcher).length;
  const cards = [
    {
      label: "오늘 격리 성공",
      value: countBy((item) => item.result === "성공" && /격리|오프라인|offline/i.test(`${item.event} ${item.eventCode}`)),
      tone: "success",
    },
    {
      label: "승인 해제",
      value: countBy((item) => /승인 해제|approval\.cleared/i.test(`${item.event} ${item.eventCode}`)),
      tone: "info",
    },
    {
      label: "차단된 재연결 시도",
      value: countBy((item) => /차단|unauthorized|reblocked/i.test(`${item.event} ${item.detail}`)),
      tone: "warning",
    },
    {
      label: "무단 탈거 감지",
      value: countBy((item) => /무단 탈거|unauthorized removal|removed|탈거/i.test(`${item.event} ${item.detail}`)),
      tone: "danger",
    },
  ];
  securityAuditSummary.innerHTML = cards.map((card) => `
    <article class="security-audit-card security-audit-card-${card.tone}">
      <span>${escapeHtml(card.label)}</span>
      <strong>${card.value}건</strong>
      <em>오늘 기준</em>
    </article>
  `).join("");
}

function renderSecurityAuditDetail(item) {
  if (!securityAuditDetail) return;
  if (!item) {
    securityAuditDetail.innerHTML = `<div class="security-audit-empty">감사 로그를 선택하면 상세 정보가 표시됩니다.</div>`;
    return;
  }
  const flow = item.loginSecurity?.visible
    ? ["로그인 시도", "실패 횟수 집계", "SMTP 알림", "관리자 승인", "감사 로그 저장"]
    : ["이벤트 접수", "정책 확인", "장치 상태 확인", "무결성 검증", "감사 로그 저장"];
  const loginSecurityHtml = item.loginSecurity?.visible ? `
      <div><dt>로그인 실패 횟수</dt><dd>${escapeHtml(item.loginSecurity.failureCount)}</dd></div>
      <div><dt>최근 실패 시간</dt><dd>${escapeHtml(item.loginSecurity.lastFailedAt || "-")}</dd></div>
      <div><dt>접속 위치</dt><dd>${escapeHtml(item.loginSecurity.clientIp)}</dd></div>
      <div><dt>SMTP 알림 상태</dt><dd>${escapeHtml(item.loginSecurity.smtpStatus)}</dd></div>
      <div><dt>관리자 메일</dt><dd>${escapeHtml(item.loginSecurity.adminEmail)}</dd></div>
      <div><dt>임시 비밀번호 승인</dt><dd>${escapeHtml(item.loginSecurity.approvalStatus)}</dd></div>
      <div><dt>임시 비밀번호 만료</dt><dd>${escapeHtml(item.loginSecurity.temporaryExpiresAt || "-")}</dd></div>
      <div><dt>임시 비밀번호 식별값</dt><dd>${escapeHtml(item.loginSecurity.temporaryDigest)}</dd></div>
    ` : "";
  securityAuditDetail.innerHTML = `
    <div class="security-audit-detail-head">
      <span class="security-audit-risk security-audit-risk-${item.risk}">${escapeHtml(item.risk)}</span>
      <strong>${escapeHtml(item.event)}</strong>
      <em>${escapeHtml(item.time || "-")}</em>
    </div>
    <div class="security-audit-flow">
      ${flow.map((step, index) => `<span class="${index < 2 || item.result !== "실패" ? "done" : "pending"}">${escapeHtml(step)}</span>`).join("")}
    </div>
    <dl class="security-audit-detail-list">
      ${loginSecurityHtml}
      <div><dt>백업 작업명</dt><dd>${escapeHtml(item.backupJob)}</dd></div>
      <div><dt>격리 전/후 상태</dt><dd>${escapeHtml(item.beforeAfter)}</dd></div>
      <div><dt>승인 사유</dt><dd>${escapeHtml(item.approvalReason)}</dd></div>
      <div><dt>무결성 검증 결과</dt><dd>${escapeHtml(item.integrity)}</dd></div>
      <div><dt>이벤트 원문</dt><dd>${escapeHtml(item.eventCode)}</dd></div>
      <div class="wide"><dt>상세 내용</dt><dd>${escapeHtml(item.detail)}</dd></div>
    </dl>
  `;
}

function renderSecurityAudit(items = []) {
  if (!securityAuditSummary || !securityAuditTable) return;
  const normalized = (Array.isArray(items) ? items : []).map(normalizeSecurityAuditRecord);
  renderSecurityAuditSummary(normalized);
  renderSecurityAuditOptions(normalized);
  if (securityAuditStart) securityAuditStart.value = securityAuditFilters.start;
  if (securityAuditEnd) securityAuditEnd.value = securityAuditFilters.end;
  if (securityAuditUser) securityAuditUser.value = securityAuditFilters.user;
  if (securityAuditResult) securityAuditResult.value = securityAuditFilters.result;
  if (securityAuditRisk) securityAuditRisk.value = securityAuditFilters.risk;

  const filtered = normalized.filter(securityAuditMatchesFilters);
  if (securityAuditCount) securityAuditCount.textContent = `${filtered.length}건`;
  if (!filtered.some((item) => item.id === securityAuditSelectedId)) {
    securityAuditSelectedId = filtered[0]?.id || "";
  }
  const selected = filtered.find((item) => item.id === securityAuditSelectedId) || filtered[0];

  securityAuditTable.replaceChildren();
  if (!filtered.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="7" class="security-audit-empty-row">조건에 맞는 보안 감사 로그가 없습니다.</td>`;
    securityAuditTable.appendChild(row);
    renderSecurityAuditDetail(null);
    return;
  }

  filtered.forEach((item) => {
    const row = document.createElement("tr");
    row.className = item.id === selected?.id ? "selected" : "";
    row.innerHTML = `
      <td>${escapeHtml(item.time || "-")}</td>
      <td><strong>${escapeHtml(item.event)}</strong><em>${escapeHtml(item.eventCode)}</em></td>
      <td>${escapeHtml(item.device)}</td>
      <td>${escapeHtml(item.user)}</td>
      <td>${escapeHtml(item.approver)}</td>
      <td><span class="security-audit-result security-audit-result-${item.result}">${escapeHtml(item.result)}</span></td>
      <td><button type="button" data-security-audit-id="${escapeHtml(item.id)}">보기</button></td>
    `;
    securityAuditTable.appendChild(row);
  });
  renderSecurityAuditDetail(selected);
}

function renderAudit(items) {
  auditTable.replaceChildren();
  if (!items.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="4">${uiSettings.language === "ko" ? "아직 감사 로그가 없습니다." : "No audit logs yet."}</td>`;
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
  const fastRequests = {
    summary: requestJson("/api/summary"),
    audit: requestJson("/api/audit"),
    integrated: requestJson("/api/integrated"),
    monitoring: requestJson(monitoringUrl()),
    dashboard: requestJson("/api/dashboard"),
    report: requestJson("/api/report"),
    notification: requestJson("/api/notification"),
    threat: requestJson("/api/threat-detection"),
    networkStatus: requestJson("/api/network-status"),
    logs: requestJson(logsUrl()),
    license: requestJson("/api/license"),
  };
  requestJson("/api/sources")
    .then((sources) => renderLoadedData("sources", sources))
    .catch((error) => console.warn("Unable to refresh Air-Gap sources", error));
  const entries = await Promise.allSettled(Object.entries(fastRequests).map(async ([key, promise]) => [key, await promise]));
  entries.forEach((entry) => {
    if (entry.status === "fulfilled") {
      renderLoadedData(entry.value[0], entry.value[1]);
      return;
    }
    console.warn("Unable to refresh data", entry.reason);
  });
  lastUpdated.textContent = new Date().toLocaleString();
}

function refreshAllInBackground(reason = "background refresh") {
  return loadAll().catch((error) => {
    console.warn(`Unable to refresh all data during ${reason}`, error);
  });
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

function requestEmergencyReconnectPassword() {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    overlay.className = "emergency-approval-modal emergency-reauth-modal";
    overlay.innerHTML = `
      <form class="emergency-approval-card emergency-reauth-card" role="dialog" aria-modal="true" aria-labelledby="emergencyReauthTitle">
        <span class="emergency-approval-kicker">Re-authentication</span>
        <h2 id="emergencyReauthTitle">비밀번호 재인증</h2>
        <p>현재 로그인한 LOCK-FIX 사용자 비밀번호를 다시 입력하고 승인하면 무결성 검증 후 재접속을 바로 실행합니다.</p>
        <label>
          현재 사용자 비밀번호
          <input type="password" name="reauthPassword" autocomplete="current-password" required />
        </label>
        <em class="emergency-approval-error" aria-live="polite"></em>
        <div class="emergency-approval-actions">
          <button type="button" data-reauth-cancel="true">취소</button>
          <button type="submit">비밀번호 승인 후 실행</button>
        </div>
      </form>
    `;
    const form = overlay.querySelector("form");
    const input = overlay.querySelector("input[name='reauthPassword']");
    const status = overlay.querySelector(".emergency-approval-error");
    const close = (value) => {
      document.removeEventListener("keydown", onKey);
      overlay.remove();
      resolve(value);
    };
    function onKey(event) {
      if (event.key === "Escape") close(null);
    }
    overlay.querySelector("[data-reauth-cancel]").addEventListener("click", () => close(null));
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) close(null);
    });
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const password = String(input.value || "");
      if (!password.trim()) {
        status.textContent = "현재 로그인한 사용자 비밀번호를 입력하세요.";
        input.focus();
        return;
      }
      close(password);
    });
    document.addEventListener("keydown", onKey);
    document.body.appendChild(overlay);
    setTimeout(() => input.focus(), 0);
  });
}

async function runEmergencyReconnect(slotId, volumePath = "") {
  const reauthPassword = await requestEmergencyReconnectPassword();
  if (reauthPassword === null) {
    return;
  }
  emergencyReconnectRunning = true;
  emergencyReconnectInitialState = String((latestSourcesData?.air_gap?.emergency_access?.slot?.state) || "").toUpperCase();
  emergencyReconnectDetailSlot = slotId || "-";
  emergencyReconnectDetailLogs = [];
  emergencyReconnectJobId = "";
  emergencyActionStatus = "";
  renderSources(latestSourcesData || { air_gap: fallbackAirGapSummary(true) });
  setEmergencyReconnectLivePolling(true);
  setEmergencyReconnectDetailLogging(true);
  try {
    const result = await requestJson(`/api/emergency-reconnect?slot=${encodeURIComponent(slotId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repository_path: volumePath, reauth_password: reauthPassword }),
    });
    emergencyActionStatus = result.message || "긴급 접속 작업이 백그라운드에서 진행 중입니다.";
    emergencyReconnectJobId = result.job_id || "";
    setEmergencyReconnectStatusPolling(true);
    await loadAll();
  } catch (error) {
    emergencyActionStatus = error?.payload?.error === "reauth_failed"
      ? "비밀번호 재인증에 실패했습니다. 현재 로그인한 사용자 비밀번호를 다시 확인하세요."
      : Number(error.status || 0) === 401
        ? "로그인 세션이 만료되어 긴급 재접속 요청이 서비스에 전달되지 않았습니다. 다시 로그인 후 실행하세요."
        : friendlyEmergencyError(error);
    appendEmergencyReconnectDetail(`reconnect request failed: ${emergencyActionStatus}`);
    stopEmergencyReconnectWatch();
    await loadAll();
  }
}

function setBusy(busy) {
  document.querySelectorAll("button").forEach((button) => {
    button.disabled = busy || button.dataset.lockDisabled === "true";
  });
}

refreshButton.addEventListener("click", loadAll);
loginForm.addEventListener("submit", login);
registerAccountButton?.addEventListener("click", openAccountGuide);
accountGuideClose?.addEventListener("click", closeAccountGuide);
accountGuideOk?.addEventListener("click", closeAccountGuide);
accountGuideModal?.addEventListener("click", (event) => {
  if (event.target === accountGuideModal) closeAccountGuide();
});
qrLoginButton.addEventListener("click", startQrLogin);
qrCodeBox.addEventListener("click", confirmQrLogin);
logoutButton.addEventListener("click", logout);
logoutSideButton.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  logout();
});
sidebarAccountSwitchButton?.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  switchAccount();
});
sidebarUserLogoutButton?.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  logout();
});
licenseForm.addEventListener("submit", registerLicense);
sidebarToggle?.addEventListener("click", toggleSidebar);
sidebarUserToggle?.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  if (!currentSession.authenticated) return;
  const expanded = sidebarUserToggle.getAttribute("aria-expanded") === "true";
  setSidebarUserPanel(!expanded);
});
document.addEventListener("click", (event) => {
  if (!sidebarUserMenu || sidebarUserPanel?.hidden) return;
  if (!sidebarUserMenu.contains(event.target)) setSidebarUserPanel(false);
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !sidebarUserPanel?.hidden) setSidebarUserPanel(false);
});
sideItems.forEach((item) => item.addEventListener("click", () => {
  if (item.classList.contains("logout-side")) return;
  showView(item.dataset.view);
}));
settingsShortcutItems.forEach((item) => item.addEventListener("click", () => showView(item.dataset.settingsView)));
approvalTabs?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-approval-tab]");
  if (!button) return;
  activeApprovalTab = button.dataset.approvalTab || "approvalRequestBox";
  renderApprovals(latestApprovalsData);
});
approvalRequestForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentSession.authenticated) {
    if (approvalFormStatus) {
      approvalFormStatus.textContent = "요청 등록 불가: 로그인 세션이 만료되었습니다. 다시 로그인 후 승인 요청을 등록하세요.";
      approvalFormStatus.className = "approval-form-status status-error";
    }
    setAuthenticated(false);
    return;
  }
  const requestType = String(approvalRequestType?.value || "DISK_ONLINE").trim().toUpperCase();
  const targetId = String(approvalTargetId?.value || "").trim() || "BAY-01";
  const repositoryPath = String(approvalRepositoryPath?.value || "").trim();
  const reason = String(approvalReason?.value || "").trim();
  if (!reason) {
    if (approvalFormStatus) {
      approvalFormStatus.textContent = "요청 등록 불가: 요청 사유를 입력해야 합니다.";
      approvalFormStatus.className = "approval-form-status status-error";
    }
    approvalReason?.focus();
    return;
  }
  const submitButton = approvalRequestForm.querySelector("button[type='submit']");
  if (submitButton) submitButton.disabled = true;
  if (approvalFormStatus) {
    approvalFormStatus.textContent = "승인 요청을 등록하는 중입니다.";
    approvalFormStatus.className = "approval-form-status status-pending";
  }
  try {
    await requestJson("/api/approvals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      timeoutMs: 30000,
      body: JSON.stringify({
        requestType,
        targetId,
        metadata: approvalRequestMetadata(requestType, reason, repositoryPath),
      }),
    });
    if (approvalFormStatus) {
      approvalFormStatus.textContent = "승인 요청이 등록되었습니다. 필요한 부서 검토와 승인 단계가 자동 생성되었습니다.";
      approvalFormStatus.className = "approval-form-status status-success";
    }
    if (approvalReason) approvalReason.value = "";
    activeApprovalTab = "approvalRequestBox";
    await reloadApprovals();
  } catch (error) {
    if (approvalFormStatus) {
      const rawDetail = error?.payload?.message || error?.payload?.error || error.message || "알 수 없는 오류입니다.";
      const detail = String(rawDetail).replace(/^요청 등록 불가:\s*/i, "");
      if (error?.code === "UNAUTHENTICATED" || error?.status === 401) {
        approvalFormStatus.textContent = `요청 등록 불가: ${detail}`;
        approvalFormStatus.className = "approval-form-status status-error";
        setAuthenticated(false);
      } else if (error?.code === "REQUEST_TIMEOUT") {
        approvalFormStatus.textContent = `등록 결과 확인 필요: ${detail} 요청이 서버에 저장되었을 수 있으니 승인 요청함을 새로고침해 확인하세요.`;
        approvalFormStatus.className = "approval-form-status status-warning";
      } else {
        approvalFormStatus.textContent = `요청 등록 불가: ${detail}`;
        approvalFormStatus.className = "approval-form-status status-error";
      }
    }
  } finally {
    if (submitButton) submitButton.disabled = false;
  }
});
approvalRequestsTable?.addEventListener("click", async (event) => {
  const deleteExpiredButton = event.target.closest("[data-delete-expired-id]");
  if (deleteExpiredButton) {
    const confirmed = window.confirm("만료된 승인 요청을 삭제하시겠습니까? 감사로그는 보존되며, 해당 요청/검토/승인 대기 레코드만 정리됩니다.");
    if (!confirmed) return;
    deleteExpiredButton.disabled = true;
    try {
      await requestJson(`/api/approvals/${encodeURIComponent(deleteExpiredButton.dataset.deleteExpiredId)}/expired-delete`, {
        method: "POST",
      });
      await reloadApprovals();
    } catch (error) {
      alert(error.message);
      deleteExpiredButton.disabled = false;
    }
    return;
  }
  const departmentConfirmButton = event.target.closest("[data-department-confirm-request-id]");
  if (departmentConfirmButton) {
    const requestId = departmentConfirmButton.dataset.departmentConfirmRequestId || "";
    if (!requestId) return;
    const request = latestApprovalsData.requests.find((item) => String(item.id || "") === String(requestId));
    if (!request || !pendingDepartmentReviewsForSession(request).length) {
      showNoPendingDepartmentReviewNotice();
      await reloadApprovals();
      return;
    }
    const originalText = departmentConfirmButton.textContent;
    approvalActionInProgress = true;
    departmentConfirmButton.disabled = true;
    departmentConfirmButton.textContent = "확인 중...";
    if (approvalFormStatus) {
      approvalFormStatus.textContent = "승인 검토를 확인하는 중입니다.";
      approvalFormStatus.className = "approval-form-status status-pending";
    }
    try {
      const result = await requestJson(`/api/approval-requests/${encodeURIComponent(requestId)}/reviews/confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        timeoutMs: 30000,
        body: JSON.stringify({ comment: "확인 완료" }),
      });
      if (approvalFormStatus) {
        approvalFormStatus.textContent = `확인 완료: ${Number(result.confirmed || 1)}건의 검토가 처리되었습니다.`;
        approvalFormStatus.className = "approval-form-status status-success";
      }
      await reloadApprovals();
    } catch (error) {
      if (approvalFormStatus) {
        if (isNoPendingDepartmentReviewError(error)) {
          showNoPendingDepartmentReviewNotice();
          await reloadApprovals();
        } else {
          approvalFormStatus.textContent = `확인 실패: ${error.message}`;
          approvalFormStatus.className = "approval-form-status status-error";
        }
      }
      departmentConfirmButton.disabled = false;
      departmentConfirmButton.textContent = originalText || "확인";
    } finally {
      approvalActionInProgress = false;
    }
    return;
  }
  const departmentReviewButton = event.target.closest("[data-department-review-id]");
  if (departmentReviewButton) {
    const action = departmentReviewButton.dataset.reviewAction || "comment";
    const promptLabel = action === "mark-reviewed" ? "검토 완료 의견을 입력하세요." : "부서 검토 의견을 입력하세요.";
    const comment = prompt(promptLabel, action === "mark-reviewed" ? "Department review completed." : "");
    if (comment === null) return;
    departmentReviewButton.disabled = true;
    try {
      await requestJson(`/api/approval-requests/${encodeURIComponent(departmentReviewButton.dataset.approvalRequestId)}/reviews/${encodeURIComponent(departmentReviewButton.dataset.departmentReviewId)}/${encodeURIComponent(action)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comment }),
      });
      await reloadApprovals();
    } catch (error) {
      alert(error.message);
      departmentReviewButton.disabled = false;
    }
    return;
  }
  const reviewButton = event.target.closest("[data-review-id]");
  if (reviewButton) {
    const originalText = reviewButton.textContent;
    approvalActionInProgress = true;
    reviewButton.disabled = true;
    reviewButton.textContent = "확인 중...";
    if (approvalFormStatus) {
      approvalFormStatus.textContent = "승인 검토를 확인하는 중입니다.";
      approvalFormStatus.className = "approval-form-status status-pending";
    }
    try {
      await requestJson(`/api/approvals/${encodeURIComponent(reviewButton.dataset.reviewId)}/reviews`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        timeoutMs: 30000,
        body: JSON.stringify({ reviewType: reviewButton.dataset.reviewType, comment: "확인 완료" }),
      });
      if (approvalFormStatus) {
        approvalFormStatus.textContent = "확인 완료: 검토가 처리되었습니다.";
        approvalFormStatus.className = "approval-form-status status-success";
      }
      await reloadApprovals();
    } catch (error) {
      if (approvalFormStatus) {
        if (isNoPendingDepartmentReviewError(error)) {
          showNoPendingDepartmentReviewNotice();
          await reloadApprovals();
        } else {
          approvalFormStatus.textContent = `확인 실패: ${error.message}`;
          approvalFormStatus.className = "approval-form-status status-error";
        }
      }
      reviewButton.disabled = false;
      reviewButton.textContent = originalText || "확인";
    } finally {
      approvalActionInProgress = false;
    }
    return;
  }
  const button = event.target.closest("[data-approval-id]");
  if (!button) return;
  const originalText = button.textContent;
  approvalActionInProgress = true;
  button.disabled = true;
  button.textContent = "확인 중...";
  if (approvalFormStatus) {
    approvalFormStatus.textContent = "승인을 확인하는 중입니다.";
    approvalFormStatus.className = "approval-form-status status-pending";
  }
    try {
      await requestJson(`/api/approvals/${encodeURIComponent(button.dataset.approvalId)}/decisions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        timeoutMs: 30000,
        body: JSON.stringify({ decision: "APPROVED", comment: "Approved from LOCK-FIX Web UI" }),
      });
      if (approvalFormStatus) {
        approvalFormStatus.textContent = "확인 완료: 승인 처리가 완료되었습니다.";
        approvalFormStatus.className = "approval-form-status status-success";
      }
      await reloadApprovals();
      maybeOpenAirgapConfirmation(button.dataset.approvalId);
    } catch (error) {
    if (/not pending:\s*EXPIRED|EXPIRED/i.test(error.message || "") && window.confirm("이미 만료된 승인 요청입니다. 이 요청을 삭제하시겠습니까?")) {
      try {
        await requestJson(`/api/approvals/${encodeURIComponent(button.dataset.approvalId)}/expired-delete`, { method: "POST" });
        await reloadApprovals();
        return;
      } catch (deleteError) {
        alert(deleteError.message);
      }
    } else {
      if (approvalFormStatus) {
        approvalFormStatus.textContent = `확인 실패: ${error.message}`;
        approvalFormStatus.className = "approval-form-status status-error";
      }
    }
    button.disabled = false;
    button.textContent = originalText || "확인";
  } finally {
    approvalActionInProgress = false;
  }
});

approvalExecutionProof?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-approval-airgap-shortcut]");
  if (!button) return;
  closeAirgapConfirmation();
  showView("sources");
});

airgapConfirmClose?.addEventListener("click", closeAirgapConfirmation);
airgapConfirmModal?.addEventListener("click", (event) => {
  if (event.target === airgapConfirmModal) closeAirgapConfirmation();
});
airgapConfirmOk?.addEventListener("click", () => {
  closeAirgapConfirmation();
  showView("sources");
});

approvalRequestsTable?.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-reject-id]");
  if (!button) return;
  const comment = prompt("반려 사유를 입력하세요.", "Rejected from LOCK-FIX Web UI");
  if (comment === null) return;
  button.disabled = true;
  try {
    await requestJson(`/api/approvals/${encodeURIComponent(button.dataset.rejectId)}/decisions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision: "REJECTED", comment }),
    });
    await reloadApprovals();
  } catch (error) {
    alert(error.message);
    button.disabled = false;
  }
});
window.addEventListener("hashchange", () => {
  if (currentSession.authenticated) showView(initialRouteView());
});
detectFingerprintRoot?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-detect-action]");
  if (!button) return;
  const action = button.dataset.detectAction;
  if (action === "logs") {
    const keyword = "disk.fingerprint";
    logsRange.highlight = keyword;
    showView("logs2");
  }
  if (action === "airgap") showView("sources");
  if (action === "settings") showView("settings");
});
threatResultTable?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-threat-id]");
  if (!button) return;
  requestJson("/api/threat-detection")
    .then((data) => {
      const item = (Array.isArray(data.results) ? data.results : []).find((entry) => entry.id === button.dataset.threatId);
      renderThreatDetail(item || null);
    })
    .catch((error) => {
      console.warn("Unable to open threat detail", error);
    });
});
threatDetailPanel?.addEventListener("click", (event) => {
  const saveButton = event.target.closest("[data-threat-memo-save]");
  if (saveButton) {
    saveThreatAdminMemo(saveButton.dataset.threatMemoSave || "");
    return;
  }
  const moreButton = event.target.closest("[data-threat-memo-more]");
  if (moreButton) {
    loadThreatMemoHistory(moreButton.dataset.threatMemoMore || "").catch((error) => {
      console.warn("Unable to load threat memo history", error);
    });
  }
});
threatManualScanButton?.addEventListener("click", () => {
  runThreatManualScan();
});
chartMenuButton.addEventListener("click", () => downloadMenu.classList.toggle("open"));
chartZoomInButton.addEventListener("click", () => {
  monitoringZoom = Math.min(3, monitoringZoom + 0.5);
  drawLineChart(latestMonitoringSeries);
});
chartZoomOutButton.addEventListener("click", () => {
  monitoringZoom = Math.max(1, monitoringZoom - 0.5);
  drawLineChart(latestMonitoringSeries);
});
monitoringRangeApply.addEventListener("click", async () => {
  let start = monitoringStart.value;
  let end = monitoringEnd.value;
  if (start && end && start > end) {
    end = start;
    monitoringEnd.value = end;
  }
  monitoringRange.start = start;
  monitoringRange.end = end;
  await reloadMonitoring();
});
  monitoringRangeDownload.addEventListener("click", () => {
    window.location.href = monitoringCsvUrl();
  });
  networkInterfaceSelect?.addEventListener("change", () => {
    selectedNetworkInterface = networkInterfaceSelect.value;
    if (latestNetworkStatusData) renderNetworkStatus(latestNetworkStatusData);
  });
networkPortTable?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-veeam-sync]");
  if (!button) return;
  syncVeeamExecutionConfig(button);
});
networkPortToggle?.addEventListener("click", () => {
  networkPortsCollapsed = !networkPortsCollapsed;
  updateNetworkPortToggle();
});
networkPathToggle?.addEventListener("click", () => {
  networkPathCollapsed = !networkPathCollapsed;
  updateNetworkPathToggle();
});
networkInsightToggle?.addEventListener("click", () => {
  networkInsightsCollapsed = !networkInsightsCollapsed;
  updateNetworkInsightToggle();
});
networkFlowModeButtons.forEach((button) => {
  button.addEventListener("click", () => setNetworkFlowMode(button.dataset.networkFlowMode));
});
logsRangeApply.addEventListener("click", async () => {
  let start = logsStart.value;
  let end = logsEnd.value;
  if (start && end && start > end) {
    end = start;
    logsEnd.value = end;
  }
  logsRange.start = start;
  logsRange.end = end;
  logsRange.type = logsTypeFilter?.value || "";
  logsRange.severity = logsSeverityFilter?.value || "";
  logsRange.source = logsSourceFilter?.value || "";
  logsRange.q = logsSearch?.value.trim() || "";
  logsRange.page = 1;
  await reloadLogs();
});
logsRangeDownload?.addEventListener("click", () => {
  window.location.href = logsCsvUrl();
});
logsSearch?.addEventListener("keydown", async (event) => {
  if (event.key !== "Enter") return;
  logsRange.q = logsSearch.value.trim();
  logsRange.type = logsTypeFilter?.value || "";
  logsRange.severity = logsSeverityFilter?.value || "";
  logsRange.source = logsSourceFilter?.value || "";
  logsRange.page = 1;
  await reloadLogs();
});
logsTypeFilter?.addEventListener("change", async () => {
  logsRange.type = logsTypeFilter.value || "";
  logsRange.page = 1;
  await reloadLogs();
});
logsSourceFilter?.addEventListener("change", async () => {
  logsRange.source = logsSourceFilter.value || "";
  logsRange.page = 1;
  await reloadLogs();
});
logsSeverityFilter?.addEventListener("change", async () => {
  logsRange.severity = logsSeverityFilter.value || "";
  logsRange.page = 1;
  await reloadLogs();
});
securityAuditApply?.addEventListener("click", () => {
  securityAuditFilters = {
    start: securityAuditStart?.value || "",
    end: securityAuditEnd?.value || "",
    event: securityAuditType?.value || "",
    device: securityAuditDevice?.value || "",
    user: securityAuditUser?.value.trim() || "",
    result: securityAuditResult?.value || "",
    risk: securityAuditRisk?.value || "",
  };
  securityAuditSelectedId = "";
  renderSecurityAudit(latestAuditData);
});
securityAuditReset?.addEventListener("click", () => {
  securityAuditFilters = { start: "", end: "", event: "", device: "", user: "", result: "", risk: "" };
  securityAuditSelectedId = "";
  renderSecurityAudit(latestAuditData);
});
securityAuditTable?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-security-audit-id]");
  if (!button) return;
  securityAuditSelectedId = button.dataset.securityAuditId || "";
  renderSecurityAudit(latestAuditData);
});
reportRefreshButton?.addEventListener("click", reloadReport);
metricFilterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeMonitoringMetric = button.dataset.metric;
    metricFilterButtons.forEach((item) => item.classList.toggle("active", item === button));
    if (latestMonitoringData) {
      renderMonitoringSummary(latestMonitoringData);
    }
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
logRetentionSelect?.addEventListener("change", () => {
  settingsApplyStatus.textContent = translations[pendingUiSettings.language]?.["settings.pending"] || translations.en["settings.pending"];
});
[
  notificationChannel,
  notificationTargetEmail,
  notificationSmtpHost,
  notificationSmtpPort,
  notificationSmtpFrom,
  notificationSmtpUser,
  notificationSmtpPassword,
  notificationUseTls,
  notificationUseSsl,
].forEach((field) => field?.addEventListener("input", () => {
  settingsApplyStatus.textContent = translations[pendingUiSettings.language]?.["settings.pending"] || translations.en["settings.pending"];
}));
settingsApplyButton.addEventListener("click", () => applyPendingUiSettings());
serviceStartButton?.addEventListener("click", () => controlLockfixService("start"));
serviceStopButton?.addEventListener("click", () => controlLockfixService("stop"));
servicePreflightButton?.addEventListener("click", () => reloadServicePreflight());
userManagementForm?.addEventListener("submit", submitUserManagementForm);
userManagementTable?.addEventListener("click", handleUserManagementTableClick);
userManagementCancelButton?.addEventListener("click", resetUserManagementForm);
userManagementBackButton?.addEventListener("click", () => showView("settings"));
[userManagementEmail, userManagementName].forEach((field) => field?.addEventListener("input", () => setUserManagementStatus()));
[userManagementDepartment, userManagementRole, userManagementDisabled].forEach((field) => field?.addEventListener("change", () => setUserManagementStatus()));
applySidebarState();
applyUiSettings();
setupNetworkCardDragDrop();
setupReportSignatures();
opsEventsToggle?.addEventListener("click", () => {
  const visible = !opsEventList?.closest(".ops-events")?.classList.contains("ops-events-visible");
  saveOpsEventsVisible(visible);
  updateOpsEventsVisibility(visible);
});
checkSession();
updateOpsClock();
renderOperationsOverview();
setInterval(updateOpsClock, 1000);
globalRefreshTimer = setInterval(() => {
  if (shouldRunGlobalRefresh()) {
    loadAll();
  }
}, GLOBAL_REFRESH_INTERVAL_MS);
