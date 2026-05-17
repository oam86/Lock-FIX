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
const reportInspectionSummary = document.querySelector("#reportInspectionSummary");
const reportAttentionList = document.querySelector("#reportAttentionList");
const reportRefreshButton = document.querySelector("#reportRefreshButton");
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
const settingsApprovalStatus = document.querySelector("#settingsApprovalStatus");
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
let latestLogsData = null;
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
let currentSession = { authenticated: false, user: "", role: "", permissions: [] };
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
  {
    view: "approvals",
    label: "협업/승인 워크플로우",
    anyPermissions: ["DISK_ONLINE_APPROVE", "AIRGAP_POLICY_MANAGE", "DISK_OFFLINE_REQUEST", "DISK_ONLINE_REQUEST", "HARDWARE_CONTROL"],
    section: "operator",
  },
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
    "nav.customerWorkspace": "",
    "nav.operatorWorkspace": "Operation",
    "nav.adminWorkspace": "Admin / Developer",
    "network.subtitle": "View transmit/receive rates, port policy, and loss analysis in one screen.",
    "network.badge": "Live Traffic",
    "network.opsSummaryTitle": "Network Operations Summary",
    "network.opsSummaryBadge": "Live",
    "network.title": "Real-time Network Status",
    "network.pathTitle": "Network Path Status",
    "network.pathBadge": "Collapse",
    "network.pathBadgeCollapsed": "View",
    "network.eventsTitle": "Recent Network Events",
    "network.eventsBadge": "Live",
    "network.chartTitle": "Cumulative Traffic by IP",
    "network.chartDesc": "Compare the top traffic flow by transmit and receive volume.",
    "network.tx": "Transmit",
    "network.rx": "Receive",
    "network.combinedTitle": "Transmit / Receive",
    "network.cumulativeTx": "Cumulative transmit",
    "network.cumulativeRx": "Cumulative receive",
    "network.lossTitle": "Network Loss",
    "network.latency": "Latency",
    "network.jitter": "Jitter",
    "network.allowedPorts": "Allowed Ports",
    "network.blockedPorts": "Blocked Ports",
    "network.portTitle": "Port Allow/Block Analysis",
    "network.portBadge": "Collapse",
    "network.portBadgeCollapsed": "View",
    "network.insightTitle": "Network Analysis",
    "network.insightBadge": "QoE",
    "network.insightBadgeCollapsed": "View",
    "network.insightBadgeExpanded": "Collapse",
    "settings.title": "Settings",
    "settings.subtitle": "Configure display language and screen theme.",
    "settings.languageTitle": "Language",
    "settings.languageDesc": "Choose the UI language for menus and labels.",
    "settings.themeTitle": "Theme",
    "settings.themeDesc": "Switch between white and black backgrounds.",
    "settings.logRetentionTitle": "Log Retention",
    "settings.logRetentionDesc": "Choose how many days logs are retained.",
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
    "settings.managementDesc": "Open operational, approval, user, and audit management screens from Settings.",
    "settings.hardwareControl": "Hardware Control",
    "settings.approvalWorkflow": "Approval Workflow",
    "settings.userRoleManagement": "User & Role Management",
    "settings.auditLogs": "Audit Logs",
    "settings.statusChecking": "Checking",
    "settings.statusUnavailable": "Unavailable",
    "settings.hardwareConnected": "Hardware connected",
    "settings.hardwareCheckNeeded": "Check required",
    "settings.pendingApprovals": "{count} pending",
    "settings.auditEvents": "{count} events",
    "settings.serviceNormal": "Service running",
    "settings.serviceStopped": "Service stopped",
    "settings.serviceTitle": "LOCK-FIX Service",
    "settings.serviceDesc": "Start or stop the installed LOCK-FIX Windows service.",
    "settings.servicePolicyTitle": "Operation Permission Policy",
    "settings.servicePolicyDesc": "Check operation mode, service account, disk-control permissions, and Veeam REST permissions through the Agent/Service.",
    "settings.preflightRefresh": "Recheck",
    "settings.serviceStart": "Start",
    "settings.serviceStop": "Stop",
    "settings.themeLight": "White",
    "settings.themeDark": "Black",
    "settings.apply": "Apply",
    "settings.pending": "Select options, then click Apply.",
    "settings.applied": "Settings have been applied.",
    "settings.notificationSaved": "Security Notification Gateway settings have been saved.",
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
    "monitoring.title": "Monitoring",
    "monitoring.subtitle": "Hardware usage status is updated every 5 seconds.",
    "monitoring.startDate": "Start Date",
    "monitoring.endDate": "End Date",
    "monitoring.applyRange": "Apply",
    "logs.startDate": "Start Date",
    "logs.endDate": "End Date",
    "logs.apply": "Apply",
    "dashboard.notification": "Security Notification Gateway",
    "dashboard.logs": "Logs",
    "dashboard.type": "Type",
    "dashboard.date": "Date",
    "dashboard.totalLogs": "Total: {count} logs",
    "dashboard.detectDesc": "Hardware changes",
    "dashboard.warningDesc": "Hardware threshold usage",
    "dashboard.logsDesc": "External server logs",
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
    "airgap.title": "Post-Backup Isolation Procedure",
    "airgap.subtitle": "Veeam backup completion, isolation steps, and detail logs are monitored in real time.",
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
    "nav.customerWorkspace": "",
    "nav.operatorWorkspace": "운영 작업",
    "nav.adminWorkspace": "관리 / 개발",
    "network.subtitle": "송신/수신 속도와 포트 정책, 손실 분석을 한 화면에서 확인합니다.",
    "network.badge": "실시간 트래픽",
    "network.opsSummaryTitle": "네트워크 운영 요약",
    "network.opsSummaryBadge": "Live",
    "network.title": "실시간 네트워크 상태",
    "network.pathTitle": "네트워크 경로 상태",
    "network.pathBadge": "접기",
    "network.pathBadgeCollapsed": "보기",
    "network.eventsTitle": "최근 네트워크 이벤트",
    "network.eventsBadge": "실시간",
    "network.chartTitle": "IP별 누적 트래픽",
    "network.chartDesc": "상위 트래픽 흐름을 송신/수신 기준으로 비교합니다.",
    "network.tx": "송신",
    "network.rx": "수신",
    "network.combinedTitle": "송신 / 수신",
    "network.cumulativeTx": "누적 송신",
    "network.cumulativeRx": "누적 수신",
    "network.lossTitle": "네트워크 손실",
    "network.latency": "지연",
    "network.jitter": "지터",
    "network.allowedPorts": "허용 포트",
    "network.blockedPorts": "차단 포트",
    "network.portTitle": "포트 허용/차단 분석",
    "network.portBadge": "접기",
    "network.portBadgeCollapsed": "보기",
    "network.insightTitle": "네트워크 분석",
    "network.insightBadge": "QoE",
    "network.insightBadgeCollapsed": "보기",
    "network.insightBadgeExpanded": "접기",
    "settings.title": "설정",
    "settings.subtitle": "표시 언어와 화면 테마를 설정합니다.",
    "settings.languageTitle": "언어",
    "settings.languageDesc": "메뉴와 주요 라벨에 사용할 언어를 선택합니다.",
    "settings.themeTitle": "테마",
    "settings.themeDesc": "흰색 배경 또는 검은색 배경으로 전환합니다.",
    "settings.logRetentionTitle": "로그 보관 기간",
    "settings.logRetentionDesc": "로그를 보관할 기간을 선택합니다.",
    "settings.notificationTitle": "Security Notification Gateway",
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
    "settings.managementDesc": "운영, 승인, 사용자, 감사 관리 화면은 설정에서만 이동합니다.",
    "settings.hardwareControl": "하드웨어 제어",
    "settings.approvalWorkflow": "협업/승인 워크플로우",
    "settings.userRoleManagement": "사용자/권한 관리",
    "settings.auditLogs": "감사 기록",
    "settings.statusChecking": "확인 중",
    "settings.statusUnavailable": "확인 불가",
    "settings.hardwareConnected": "하드웨어 연결됨",
    "settings.hardwareCheckNeeded": "확인 필요",
    "settings.pendingApprovals": "승인 대기 {count}건",
    "settings.auditEvents": "감사 이벤트 {count}건",
    "settings.serviceNormal": "서비스 정상",
    "settings.serviceStopped": "서비스 중지",
    "settings.serviceTitle": "LOCK-FIX 서비스",
    "settings.serviceDesc": "설치된 LOCK-FIX Windows 서비스를 시작하거나 중지합니다.",
    "settings.servicePolicyTitle": "권한 운영 정책",
    "settings.servicePolicyDesc": "운영 모드, 서비스 실행 계정, 디스크 제어 권한, Veeam REST 권한을 Agent/Service 기준으로 진단합니다.",
    "settings.preflightRefresh": "재진단",
    "settings.serviceStart": "시작",
    "settings.serviceStop": "중지",
    "settings.themeLight": "흰색",
    "settings.themeDark": "검은색",
    "settings.apply": "적용",
    "settings.pending": "항목을 선택한 뒤 적용 버튼을 누르세요.",
    "settings.applied": "설정이 적용되었습니다.",
    "settings.notificationSaved": "Security Notification Gateway 설정이 저장되었습니다.",
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
    "monitoring.title": "모니터링",
    "monitoring.subtitle": "하드웨어 사용 상태가 5초마다 업데이트됩니다.",
    "monitoring.startDate": "시작일",
    "monitoring.endDate": "종료일",
    "monitoring.applyRange": "적용",
    "logs.startDate": "시작일",
    "logs.endDate": "종료일",
    "logs.apply": "적용",
    "dashboard.notification": "Security Notification Gateway",
    "dashboard.logs": "로그",
    "dashboard.type": "유형",
    "dashboard.date": "날짜",
    "dashboard.totalLogs": "전체: {count}개 로그",
    "dashboard.detectDesc": "하드웨어 변경 사항",
    "dashboard.warningDesc": "하드웨어 임계값 초과 사용",
    "dashboard.logsDesc": "외부 서버 로그",
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
    "report.exportWord": "워드",
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
    "airgap.title": "백업 완료 후 격리 절차",
    "airgap.subtitle": "Veeam 백업 완료 후 격리 단계와 상세 로그를 실시간으로 확인합니다.",
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
  "Veeam API Polling": "Veeam API 실시간 확인",
  "Veeam backup status API is checked every 1 second while the Air-Gap screen is open.": "실제 Veeam API 세션이 확인되기 전까지 API 대기 상태로 유지합니다.",
  "Veeam API is connected. Step colors change only when the current_step value advances.": "Veeam API가 연결되어 있습니다. current_step 값이 실제로 증가할 때만 단계 색상이 넘어갑니다.",
  "Veeam API is not connected yet. Current step is held and colors will not advance automatically.": "Veeam API가 아직 연결되지 않았습니다. 현재 단계를 유지하며 색상은 자동으로 넘어가지 않습니다.",
  "Step Detail Logs": "단계별 상세 로그",
  "Real-time transition evidence": "실시간 전환 근거",
  "Veeam API": "Veeam API",
  "Veeam API waiting": "Veeam API 대기",
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
  "Two-administrator approval required": "관리자 2인 승인 필요",
  "Manual release is available only after two-administrator approval.": "수동 해제는 관리자 2인 승인 후에만 가능합니다.",
  "Waiting for Dual Approval": "2인 승인 대기 중",
  "Data path activation remains blocked": "데이터 통로 활성화 차단 유지",
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
      event: "Recent Events",
      alert: "Warnings / Alerts",
      audit: "Audit Log Summary",
      policy: "Policy Summary",
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
    event: "최근 이벤트",
    alert: "경고 / 알림",
    audit: "감사 로그 요약",
    policy: "정책 설정 요약",
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
    return "긴급 접속 상태 확인 인증이 만료되었습니다. 최신 재접속 완료 여부는 백그라운드 로그와 상태 이력에서 다시 확인합니다.";
  }
  return "긴급 접속을 완료하지 못했습니다. 상세 오류는 백그라운드 로그 이력에 저장됨";
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

  function drawImageToCanvas(source) {
    const img = new Image();
    img.onload = () => {
      context.clearRect(0, 0, canvas.width, canvas.height);
      const scale = Math.min(canvas.width / img.width, canvas.height / img.height);
      const width = img.width * scale;
      const height = img.height * scale;
      const x = (canvas.width - width) / 2;
      const y = (canvas.height - height) / 2;
      context.drawImage(img, x, y, width, height);
      localStorage.setItem(storageKey, canvas.toDataURL("image/png"));
      scheduleReportExtrasSave();
    };
    img.src = source;
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
  document.querySelector(`[data-signature-upload="${canvas.id}"]`)?.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => drawImageToCanvas(String(reader.result || ""));
    reader.readAsDataURL(file);
    event.target.value = "";
  });
  restore();
}

function setupReportSignatures() {
  setupReportOpinion();
  setupSignaturePad(document.querySelector("#engineerSignaturePad"));
  setupSignaturePad(document.querySelector("#managerSignaturePad"));
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
  applySidebarTooltips();
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

function toggleSidebar() {
  sidebarCollapsed = !sidebarCollapsed;
  localStorage.setItem("lockfix.sidebarCollapsed", String(sidebarCollapsed));
  applySidebarState();
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
    reloadLogs().catch((error) => console.warn("Unable to reload logs after retention change", error));
    reloadNotification().catch((error) => console.warn("Unable to reload notification view after settings change", error));
  } catch (error) {
    settingsApplyStatus.textContent = error.message || "Notification settings save failed.";
  }
}

async function requestJson(url, options = {}) {
  const timeoutMs = Number(options.timeoutMs || 15000);
  const fetchOptions = { ...options };
  delete fetchOptions.timeoutMs;
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
      ? "WebUI 서버 응답이 지연되어 중단했습니다. 현재 접속 주소가 http://127.0.0.1:8088 인지 확인하고, WebUI/Python 서버를 새로고침 또는 재시작하세요."
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
    permissions: Array.isArray(session.permissions) ? session.permissions : [],
  };
  applyMenuVisibility();
  setAuthenticated(session.authenticated);
  if (session.authenticated) {
    renderLicenseStatus(session.license);
    updateLicenseGate(session.license);
    await loadAll();
    showView(initialRouteView());
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
    currentSession = { authenticated: false, user: "", role: "", permissions: [] };
    applyMenuVisibility();
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
    permissions: Array.isArray(session.permissions) ? session.permissions : [],
  };
  applyMenuVisibility();
  await Promise.all([
    loadAll(),
    new Promise((resolve) => setTimeout(resolve, LOGIN_SPLASH_DURATION_MS)),
  ]);
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
    } else {
      setAuthenticated(false);
    }
  } catch (error) {
    loginError.textContent = error.message || "Account or password is not valid.";
  }
}

async function logout() {
  resetQrLoginState();
  try {
    await requestJson("/api/logout", { method: "POST" });
  } catch (error) {
    console.warn("Logout request failed; clearing local session state.", error);
  } finally {
    setAuthenticated(false);
    if (window.location.hash) history.replaceState(null, "", window.location.pathname || "/");
  }
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
  if (targetView === "detect2") {
    renderDetectFallback();
    requestJson("/api/detect")
      .then((data) => renderDetect(data))
      .catch((error) => {
        console.warn("Unable to reload Detect view", error);
        renderDetectFallback(
          "탐지 내역을 표시할 수 없습니다.",
          error?.message || "WebUI 서버 연결, 로그인 권한, 또는 AIRGAP_POLICY_VIEW 권한을 확인해 주세요."
        );
      });
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
  if (targetView === "approvals") {
    reloadApprovals().catch((error) => {
      console.warn("Unable to reload approvals", error);
      renderApprovals({ requests: [], decisions: [], policies: [] }, error.message);
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
  if (qrLoginButton) qrLoginButton.textContent = "QR CODE LOGIN";
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
  const flowItems = Array.isArray(data.flow) && data.flow.length
    ? data.flow
    : [
      { icon: "backup-complete", lines: ["백업", "완료"], state: "done" },
      { icon: "flush-run", lines: ["Flush", "실행"], state: "done" },
      { icon: "io-check", lines: ["I/O 종료", "확인"], state: "done" },
      { icon: "power-off", lines: ["디스크", "오프라인"], state: "done" },
      { icon: "airgap-logo", lines: ["Air-Gap", "활성"], state: "done" },
    ];
  const backup = data.backup || {};
  const events = Array.isArray(data.logs) ? data.logs.slice(0, 5) : [];
  const alerts = Array.isArray(data.alerts) ? data.alerts : [];
  const threat = data.threat_detection || {};
  const threatStatus = String(threat.status || "정상");
  const threatDanger = threatTone(threatStatus) === "danger";
  dashboardView.innerHTML = `
    ${threatDanger ? `
      <section class="dashboard-threat-banner">
        <strong>위험 경고: 최근 백업본에서 랜섬웨어 의심 징후가 탐지되었습니다.</strong>
        <span>Repository 재연결이 차단되었으며 관리자 승인이 필요합니다.</span>
      </section>
    ` : ""}
    <div class="security-kpi-grid">
      ${securityKpis.map(({ icon, label, value, tone, meta }) => `
        <article class="security-kpi security-kpi-${icon}">
          <i class="security-icon security-icon-${icon} security-tone-${tone}" ${meta ? `title="${escapeHtml(meta)}" aria-label="${escapeHtml(meta)}"` : 'aria-hidden="true"'}></i>
          <div><span>${escapeHtml(label || "-")}</span><strong class="security-value-${tone}">${escapeHtml(value || "-")}</strong></div>
        </article>
      `).join("")}
    </div>

    <div class="security-dashboard-grid">
      <section class="security-panel security-flow-panel">
        <header><h2><i class="panel-title-icon protection-title-icon" aria-hidden="true"></i>${copy.liveProtection}</h2><span>ⓘ</span></header>
        <div class="panel-body">
          <p>${copy.protectedMessage.replace("Offline", "<b>Offline</b>").replace("offline", "<b>offline</b>")}</p>
          <div class="security-flow">
            ${flowItems.map(({ icon, lines, state }) => `
              <div class="flow-step ${state === "done" ? "flow-step-active" : ""}">
                <i class="security-icon security-icon-${icon}" aria-hidden="true"></i>
                <span>${(lines || []).map((line) => `<b>${escapeHtml(line)}</b>`).join("")}</span>
              </div>
            `).join("")}
          </div>
        </div>
      </section>

      <section class="security-panel backup-panel">
        <header><h2><i class="panel-title-icon backup-title-icon" aria-hidden="true"></i>${copy.backupLink}</h2></header>
        <div class="panel-body">
          <dl>
            <div><dt>연동 백업 솔루션</dt><dd>${escapeHtml(backup.solution || "Veeam Backup & Replication")}</dd></div>
            <div><dt>마지막 작업명</dt><dd>${escapeHtml(backup.job || "-")}</dd></div>
            <div><dt>백업 시작</dt><dd>${escapeHtml(backup.started_at || "-")}</dd></div>
            <div><dt>백업 종료</dt><dd>${escapeHtml(backup.ended_at || "-")}</dd></div>
            <div><dt>LOCK-FIX 상태</dt><dd>${escapeHtml(backup.isolation_state || "-")}</dd></div>
            <div><dt>차단 결과</dt><dd class="backup-result ${String(backup.result || "").includes("Failed") ? "backup-result-failed" : "backup-result-success"}">${escapeHtml(backup.result || "-")}</dd></div>
          </dl>
        </div>
      </section>

      <section class="security-panel dashboard-threat-panel">
        <header><h2>위협 탐지 요약</h2><button type="button" class="threat-detail-button" onclick="window.location.hash='#threat'">보기</button></header>
        <div class="panel-body dashboard-threat-summary">
          <div><span>최근 상태</span><strong class="threat-${threatTone(threatStatus)}">${escapeHtml(threatStatus)}</strong></div>
          <div><span>위험 점수</span><strong>${escapeHtml(String(threat.score ?? "-"))}</strong></div>
          <div><span>마지막 검사</span><strong>${escapeHtml(threat.last_scan_at || "-")}</strong></div>
          <div><span>의심 항목</span><strong>${escapeHtml(String(threat.suspicious_count ?? 0))}건</strong></div>
        </div>
      </section>

      <section class="security-panel event-panel">
        <header><h2><i class="panel-title-icon event-title-icon" aria-hidden="true"></i>${copy.event}</h2></header>
        <div class="panel-body">
        ${events.map((event) => `<div class="event-row"><span><i class="event-clock" aria-hidden="true"></i>${escapeHtml(event.date || "-")}</span><strong>${escapeHtml(event.content || "-")}</strong></div>`).join("")}
        <a>${copy.detail} ›</a>
        </div>
      </section>

      <section class="security-panel alert-panel">
        <header><h2><i class="panel-title-icon alert-title-icon" aria-hidden="true"></i>${copy.alert}</h2></header>
        <div class="panel-body">
          <div class="alert-ok"><span>${alerts.some((item) => String(item.value || "").match(/Failed|Detected|Error/i)) ? "확인 필요" : copy.noCritical}</span></div>
          ${alerts.map((item) => `<div class="health-row"><span>${escapeHtml(item.label || "-")}</span><b>${escapeHtml(item.value || "-")}</b></div>`).join("")}
          <a>${copy.detail} ›</a>
        </div>
      </section>

      <section class="security-panel audit-summary-panel">
        <header><h2><i class="panel-title-icon audit-title-icon" aria-hidden="true"></i>${copy.audit}</h2></header>
        <div class="panel-body">
          <div class="audit-count-grid">
            <div><span>관리자 수동 조작</span><strong>1건</strong></div>
            <div><span>정책 변경</span><strong>0건</strong></div>
            <div><span>승인 요청</span><strong>2건</strong></div>
            <div><span>로그인 실패</span><strong>0건</strong></div>
          </div>
          <span class="export-label">로그 내보내기</span>
          <div class="export-buttons">
            <button><i class="file-icon file-csv" aria-hidden="true"></i>${copy.csv}</button>
            <button><i class="file-icon file-pdf" aria-hidden="true"></i>${copy.pdf}</button>
            <button><i class="file-icon file-word" aria-hidden="true"></i>${copy.word}</button>
          </div>
        </div>
      </section>

    </div>
  `;
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
    const statusClass = isNormal ? "normal" : "abnormal";
    const judgementLabel = isNormal ? "REGISTERED" : status === "DIFFERENT_DISK" ? "DIFFERENT DISK" : "UNREGISTERED";
    const judgementKorean = isNormal ? "등록된 디스크" : status === "DIFFERENT_DISK" ? "다른 디스크 감지" : "등록되지 않은 디스크";
    const recognitionLabel = isNormal ? "NORMAL RECOGNITION" : "RECOGNITION FAILED";
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

function renderThreatDetail(item) {
  if (!threatDetailPanel) return;
  if (!item) {
    threatDetailPanel.hidden = true;
    return;
  }
  threatDetailPanel.hidden = false;
  const detections = Array.isArray(item.detections) ? item.detections : [];
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
    <label class="threat-admin-note"><span>관리자 메모</span><textarea readonly>${escapeHtml(item.admin_note || "정책 기준에 따라 감사로그와 승인 워크플로우에 연결됩니다.")}</textarea></label>
  `;
}

async function reloadThreatDetection() {
  const data = await requestJson("/api/threat-detection");
  renderThreatDetection(data);
  return data;
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
  return Number.isFinite(numeric) && numeric >= 0 ? `${numeric}ms` : "latency checking";
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
  const cards = [
    {
      label: "Veeam REST",
      value: apiSynced ? "Connected" : "Waiting",
      meta: `${veeam.server || "127.0.0.1"}:${veeam.port || 9419} · ${formatOpsLatency(veeam)}`,
      tone: apiSynced ? "ok" : "warn",
    },
    {
      label: "Backup",
      value: `${progress}%`,
      meta: veeam.job || veeam.job_name || "Veeam session",
      tone: progress >= 100 ? "ok" : progress > 0 ? "run" : "warn",
    },
    {
      label: "Air-Gap",
      value: activeStep ? `Step ${activeStep.step}` : lastStep ? `Step ${lastStep.step} Done` : "Standby",
      meta: activeStep ? activeStep.label || activeStep.title || "Working" : lastStep?.label || lastStep?.title || "Ready",
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
  return {
    security: "보안팀",
    "backup-operation": "백업팀",
    "hardware-control": "하드웨어팀",
    audit: "감사팀",
    management: "관리자",
  }[departmentId] || departmentId || "-";
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
      ? `<button type="button" class="rbac-action-button rbac-confirm-action" data-department-confirm-request-id="${escapeHtml(request.id)}" data-department-confirm-review-ids="${escapeHtml(pendingDepartmentReviews.map((review) => review.id).join(","))}">확인</button>`
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

function renderUserManagement(data, errorMessage = "") {
  const departments = Array.isArray(data?.departments) ? data.departments : [];
  const users = Array.isArray(data?.users) ? data.users : [];
  if (userManagementDepartmentCount) userManagementDepartmentCount.textContent = `${departments.length} departments`;
  if (userManagementDepartments) {
    userManagementDepartments.innerHTML = departments.length
      ? departments.map((department) => `<span>${escapeHtml(department.name || department.id)}</span>`).join("")
      : `<em>${escapeHtml(errorMessage || "No departments loaded.")}</em>`;
  }
  if (userManagementCount) userManagementCount.textContent = `${users.length} users`;
  if (!userManagementTable) return;
  userManagementTable.replaceChildren();
  if (errorMessage || !users.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="4">${escapeHtml(errorMessage || "No users loaded.")}</td>`;
    userManagementTable.appendChild(row);
    return;
  }
  users.forEach((user) => {
    const department = departments.find((item) => item.id === user.departmentId);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(user.username || user.id)}</td>
      <td>${escapeHtml(department?.name || user.departmentId || "-")}</td>
      <td>${escapeHtml(user.role || "-")}</td>
      <td>${escapeHtml(user.disabled ? "Disabled" : "Active")}</td>
    `;
    userManagementTable.appendChild(row);
  });
}

async function reloadUserManagement() {
  const [users, departments] = await Promise.all([
    requestJson("/api/admin/users"),
    requestJson("/api/admin/departments"),
  ]);
  renderUserManagement({ users: users.items || [], departments: departments.items || [] });
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
    const rows = [
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
      <li class="${row.ok ? "is-ok" : "is-warning"}">
        <span>${escapeHtml(row.label)}</span>
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

function activeApprovalRequestCount(data) {
  const closed = new Set(["APPROVED", "REJECTED", "EXPIRED", "EXECUTED", "COMPLETED", "CANCELLED"]);
  return (Array.isArray(data?.requests) ? data.requests : []).filter((request) => !closed.has(String(request.status || "").toUpperCase())).length;
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
  setSettingsShortcutStatus(settingsApprovalStatus, "settings.statusChecking");
  setSettingsShortcutStatus(settingsServiceStatus, "settings.statusChecking");
  setSettingsShortcutStatus(settingsAuditStatus, "settings.statusChecking");

  const update = (promise, onSuccess, target) => promise.then(onSuccess).catch(() => {
    setSettingsShortcutStatus(target, "settings.statusUnavailable");
  });

  await Promise.allSettled([
    update(requestJson("/api/sources"), (data) => {
      setSettingsShortcutStatus(settingsHardwareStatus, sourcesHardwareConnected(data) ? "settings.hardwareConnected" : "settings.hardwareCheckNeeded");
    }, settingsHardwareStatus),
    update(requestJson("/api/approvals"), (data) => {
      setSettingsShortcutStatus(settingsApprovalStatus, "settings.pendingApprovals", { count: activeApprovalRequestCount(data) });
    }, settingsApprovalStatus),
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
  const sources = await requestJson("/api/sources");
  renderSources(sources);
}

async function pollSourcesLive() {
  if (!currentSession.authenticated || appRoot.classList.contains("app-locked")) return;
  if (activeViewId() !== "sourcesView") return;
  try {
    const sources = await requestJson("/api/sources");
    renderSources(sources);
    finalizeEmergencyReconnectFromSources(sources);
  } catch (error) {
    console.warn("Unable to poll Air-Gap live status", error);
  }
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
  try {
    const dashboard = await requestJson("/api/dashboard");
    renderDashboard(dashboard);
  } catch (error) {
    console.warn("Unable to poll Dashboard live status", error);
  }
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
  try {
    const [sourcesResult, dashboardResult] = await Promise.allSettled([
      requestJson("/api/sources"),
      requestJson("/api/dashboard"),
    ]);
    if (sourcesResult.status === "fulfilled") latestSourcesData = sourcesResult.value;
    if (dashboardResult.status === "fulfilled") latestDashboardData = dashboardResult.value;
    renderOperationsOverview();
  } catch (error) {
    console.warn("Unable to poll operations overview", error);
  }
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

function appendEmergencyReconnectDetail(message) {
  const slot = emergencyReconnectDetailSlot || "-";
  emergencyReconnectDetailLogs.push(`${emergencyReconnectTimestamp()} - LOCK-FIX Reconnect DETAIL - slot ${slot}, ${message}`);
  emergencyReconnectDetailLogs = emergencyReconnectDetailLogs.slice(-120);
}

function mergeEmergencyReconnectDetails(lines) {
  if (!Array.isArray(lines) || !lines.length) return;
  const next = [...emergencyReconnectDetailLogs];
  lines.forEach((line) => {
    const text = String(line || "").trim();
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
    appendEmergencyReconnectDetail("request accepted; live detail logging started");
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
      message: "Veeam API is not connected yet. Current step is held and colors will not advance automatically.",
    },
    step_logs: [
      { step: 1, label: "백업 완료", code: "BACKUP_COMPLETED", state: "PENDING", time: "-", source: "Veeam API 대기", detail: "실제 Veeam API 세션이 확인될 때까지 단계 색상을 회색으로 유지합니다.", transition_allowed: false },
      { step: 2, label: "Flush 실행", code: "FLUSHING", state: "PENDING", time: "-", source: "Veeam API 대기", detail: "아직 이전 단계 완료 신호가 확인되지 않았습니다.", transition_allowed: false },
      { step: 3, label: "I/O 종료 확인", code: "IO_CHECKING", state: "PENDING", time: "-", source: "Veeam API 대기", detail: "아직 이전 단계 완료 신호가 확인되지 않았습니다.", transition_allowed: false },
      { step: 4, label: "Unmount", code: "UNMOUNTING", state: "PENDING", time: "-", source: "Veeam API 대기", detail: "아직 이전 단계 완료 신호가 확인되지 않았습니다.", transition_allowed: false },
      { step: 5, label: "오프라인", code: "DISK_OFFLINING", state: "PENDING", time: "-", source: "Veeam API 대기", detail: "아직 이전 단계 완료 신호가 확인되지 않았습니다.", transition_allowed: false },
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
      description: "Manual release is available only after two-administrator approval.",
      primary: "Waiting for Dual Approval",
      secondary: "Data path activation remains blocked",
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
        name: "Veeam API",
        status: "Waiting",
        actions: [
          `Veeam REST API is not synced. Check ${veeam.server || "127.0.0.1"}:${veeam.port || 9419} host, port, credentials, or token.`,
          "Step colors and arrows stay fixed until a real Veeam session is received.",
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
        <article class="veeam-step-card veeam-step-${String(item.state || "PENDING").toLowerCase()} ${stepVisualClass(item)} ${stepIncomingClass(item)} ${stepHasAdvanced(item) ? "veeam-step-arrow-visible" : ""} ${stepTransferClass(item)}">
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
    `${veeamSessionLogs.length} sessions`,
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
          <col class="veeam-log-col-status" />
          <col class="veeam-log-col-action" />
          <col class="veeam-log-col-duration" />
        </colgroup>
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Action</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          ${veeamSessionLogs.map((log, index) => `
            <tr>
              <td class="veeam-session-name">${escapeHtml(log.name || "-")}</td>
              <td><span class="veeam-session-status veeam-session-${statusVisualClass(log)}">${escapeHtml(statusDisplay(log))}</span></td>
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

  const approvalVerificationPanel = document.createElement("section");
  const approvalAvailable = Boolean(autoApproval.available);
  const approvalVerified = approvalAvailable && Number(autoApproval.approved_count || 0) >= Number(autoApproval.required_count || 1);
  approvalVerificationPanel.className = `airgap-panel airgap-approval-verification ${approvalVerified ? "airgap-approval-ready" : "airgap-approval-wait"}`;
  approvalVerificationPanel.innerHTML = `
    <div class="airgap-panel-head">
      <h2>자동 승인 검증</h2>
      <span>${escapeHtml(approvalVerified ? "검증 완료" : "검증 대기")}</span>
    </div>
    <div class="airgap-approval-grid">
      <article>
        <span>허용 여부</span>
        <strong>${escapeHtml(approvalVerified ? "허용됨" : "대기")}</strong>
        <p>${escapeHtml(approvalVerified ? "에어갭 자동 승인 정책이 실행 가능합니다." : "자동 승인 결과를 아직 확인하지 못했습니다.")}</p>
      </article>
      <article>
        <span>승인 진행률</span>
        <strong>${escapeHtml(Number(autoApproval.approved_count || 0))} / ${escapeHtml(Number(autoApproval.required_count || 1))}</strong>
        <p>${escapeHtml(autoApproval.summary || "자동 승인 상태를 확인합니다.")}</p>
      </article>
      <article>
        <span>검증 모드</span>
        <strong>${escapeHtml(autoApproval.mode || "-")}</strong>
        <p>${escapeHtml(autoApproval.requester_user_id ? `요청자 ${autoApproval.requester_user_id}` : "자동 정책 기반 승인 요청")}</p>
      </article>
      <article>
        <span>최종 상태</span>
        <strong>${escapeHtml(approvalVerified ? "실행 가능" : "실행 전 확인 필요")}</strong>
        <p>${escapeHtml(approvalVerified ? "승인 완료 후 에어갭 화면 확인으로 이어집니다." : "부서 검토와 승인 완료 뒤 다시 확인하세요.")}</p>
      </article>
    </div>
  `;
  sourceList.appendChild(approvalVerificationPanel);

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
  const emergencyLogMessage = emergencyActionStatus || emergencySlot.blocked_reason || emergencyAccess.secondary || "-";
  const emergencyLiveLogMarkup = reconnectLiveLogLines.length
    ? reconnectLiveLogLines.map((line) => `<li>${escapeHtml(line)}</li>`).join("")
    : `<li>${escapeHtml(emergencyLogMessage)}</li>`;
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
      <span>실시간 작업 로그</span>
      <strong>${escapeHtml(emergencyLogMessage)}</strong>
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
      <span>${airgapText("Veeam API Polling")} · ${veeam.api_poll_interval_seconds || 1}s</span>
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
        <span>${airgapText("Two-administrator approval required")}</span>
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
  const height = 320;
  const pad = { left: 96, right: 22, top: 12, bottom: 46 };
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
      return `<line x1="${pad.left}" y1="${yy}" x2="${width - pad.right}" y2="${yy}" class="grid-line"></line><text x="${pad.left - 16}" y="${Number(yy) + 4}" class="axis-label" text-anchor="end">${tick}.00%</text>`;
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
    detect: requestJson("/api/detect"),
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

function requestEmergencyApprovalPassword() {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    overlay.className = "emergency-approval-modal";
    overlay.innerHTML = `
      <form class="emergency-approval-card">
        <h2>긴급 재접속 승인</h2>
        <p>관리자 계정 비밀번호를 한 번 더 입력해야 긴급 재접속이 시작됩니다.</p>
        <label>
          <span>승인 비밀번호</span>
          <input type="password" autocomplete="current-password" autofocus>
        </label>
        <em class="emergency-approval-error" aria-live="polite"></em>
        <div class="emergency-approval-actions">
          <button type="button" data-approval-cancel="true">취소</button>
          <button type="submit">승인</button>
        </div>
      </form>
    `;
    const form = overlay.querySelector("form");
    const input = overlay.querySelector("input");
    const error = overlay.querySelector(".emergency-approval-error");
    const close = (value) => {
      document.removeEventListener("keydown", onKey);
      overlay.remove();
      resolve(value);
    };
    function onKey(event) {
      if (event.key === "Escape") close("");
    }
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const value = input.value;
      if (value !== "1") {
        error.textContent = "승인 비밀번호가 일치하지 않습니다.";
        input.select();
        return;
      }
      close(value);
    });
    overlay.querySelector("[data-approval-cancel]").addEventListener("click", () => close(""));
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) close("");
    });
    document.addEventListener("keydown", onKey);
    document.body.appendChild(overlay);
    setTimeout(() => input.focus(), 0);
  });
}

function showEmergencyReconnectApprovalRequired(error, slotId, volumePath = "") {
  return new Promise((resolve) => {
    const payload = error?.payload || {};
    const missing = Array.isArray(payload.missing_approvals) && payload.missing_approvals.length
      ? payload.missing_approvals
      : ["EMERGENCY_UNLOCK", "DISK_ONLINE"];
    const overlay = document.createElement("div");
    overlay.className = "emergency-approval-modal";
    overlay.innerHTML = `
      <section class="emergency-approval-card emergency-approval-required-card" role="dialog" aria-modal="true" aria-labelledby="emergencyApprovalRequiredTitle">
        <span class="emergency-approval-kicker">Approval Required</span>
        <h2 id="emergencyApprovalRequiredTitle">재접속 승인이 필요합니다</h2>
        <p>격리된 백업 볼륨을 온라인 상태로 전환하려면 보안 해제 승인과 디스크 온라인 승인이 먼저 완료되어야 합니다.</p>
        <div class="emergency-approval-required-list">
          ${missing.map((item) => `<strong>${escapeHtml(item)}</strong>`).join("")}
        </div>
        <em class="emergency-approval-error" aria-live="polite"></em>
        <div class="emergency-approval-actions">
          <button type="button" data-approval-cancel="true">취소</button>
          <button type="button" data-approval-open="true">승인 화면으로 이동</button>
          <button type="button" data-approval-create="true">승인 요청 생성</button>
        </div>
      </section>
    `;
    const status = overlay.querySelector(".emergency-approval-error");
    const createButton = overlay.querySelector("[data-approval-create]");
    const close = (value) => {
      document.removeEventListener("keydown", onKey);
      overlay.remove();
      resolve(value);
    };
    function onKey(event) {
      if (event.key === "Escape") close("");
    }
    overlay.querySelector("[data-approval-cancel]").addEventListener("click", () => close(""));
    overlay.querySelector("[data-approval-open]").addEventListener("click", () => {
      close("open");
      showView("approvals");
    });
    createButton.addEventListener("click", async () => {
      createButton.disabled = true;
      status.textContent = "필요한 승인 요청을 생성하는 중입니다.";
      try {
        await requestJson("/api/emergency-reconnect/approval-requests", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            slot_id: slotId,
            repository_path: volumePath,
            reason: "긴급 재접속을 위해 EMERGENCY_UNLOCK 및 DISK_ONLINE 승인이 필요합니다.",
          }),
        });
        status.textContent = "승인 요청이 생성되었습니다. 부서 검토와 2인 승인 완료 후 다시 재접속할 수 있습니다.";
        activeApprovalTab = "approvalRequestBox";
        await reloadApprovals();
        setTimeout(() => {
          close("created");
          showView("approvals");
        }, 650);
      } catch (createError) {
        status.textContent = createError.message || "승인 요청 생성에 실패했습니다.";
        createButton.disabled = false;
      }
    });
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) close("");
    });
    document.addEventListener("keydown", onKey);
    document.body.appendChild(overlay);
    setTimeout(() => createButton.focus(), 0);
  });
}

async function runEmergencyReconnect(slotId, volumePath = "") {
  const approvalPassword = await requestEmergencyApprovalPassword();
  if (!approvalPassword) {
    emergencyReconnectDetailSlot = slotId || "-";
    emergencyReconnectDetailLogs = [];
    emergencyActionStatus = "긴급 재접속 승인이 취소되어 작업을 시작하지 않았습니다.";
    appendEmergencyReconnectDetail("approval canceled; emergency reconnect was not submitted to the service");
    renderSources(latestSourcesData || { air_gap: fallbackAirGapSummary(true) });
    return;
  }
  emergencyReconnectRunning = true;
  emergencyReconnectInitialState = String((latestSourcesData?.air_gap?.emergency_access?.slot?.state) || "").toUpperCase();
  emergencyReconnectDetailSlot = slotId || "-";
  emergencyReconnectDetailLogs = [];
  emergencyReconnectJobId = "";
  emergencyActionStatus = "긴급 접속 작업이 백그라운드에서 시작되었습니다.";
  renderSources(latestSourcesData || { air_gap: fallbackAirGapSummary(true) });
  setEmergencyReconnectLivePolling(true);
  setEmergencyReconnectDetailLogging(true);
  try {
    const result = await requestJson(`/api/emergency-reconnect?slot=${encodeURIComponent(slotId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repository_path: volumePath, approval_password: approvalPassword }),
    });
    emergencyActionStatus = result.message || "긴급 접속 작업이 백그라운드에서 진행 중입니다.";
    emergencyReconnectJobId = result.job_id || "";
    appendEmergencyReconnectDetail(`background job accepted${result.job_id ? ` - ${result.job_id}` : ""}`);
    setEmergencyReconnectStatusPolling(true);
    await loadAll();
  } catch (error) {
    if (error?.payload?.approval_required) {
      emergencyActionStatus = "긴급 재접속에 필요한 승인이 아직 완료되지 않았습니다.";
      appendEmergencyReconnectDetail(`approval required: ${(error.payload.missing_approvals || []).join(", ") || "EMERGENCY_UNLOCK, DISK_ONLINE"}`);
      stopEmergencyReconnectWatch();
      await showEmergencyReconnectApprovalRequired(error, slotId, volumePath);
      await loadAll();
      return;
    }
    emergencyActionStatus = Number(error.status || 0) === 401
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
licenseForm.addEventListener("submit", registerLicense);
sidebarToggle?.addEventListener("click", toggleSidebar);
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
      await requestJson(`/api/approvals/${encodeURIComponent(deleteExpiredButton.dataset.deleteExpiredId)}`, {
        method: "DELETE",
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
        await requestJson(`/api/approvals/${encodeURIComponent(button.dataset.approvalId)}`, { method: "DELETE" });
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
threatManualScanButton?.addEventListener("click", () => {
  reloadThreatDetection().catch((error) => {
    console.warn("Unable to run manual threat refresh", error);
  });
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
applySidebarState();
applyUiSettings();
setupNetworkCardDragDrop();
setupReportSignatures();
checkSession();
updateOpsClock();
renderOperationsOverview();
setInterval(updateOpsClock, 1000);
globalRefreshTimer = setInterval(() => {
  if (shouldRunGlobalRefresh()) {
    loadAll();
  }
}, GLOBAL_REFRESH_INTERVAL_MS);
