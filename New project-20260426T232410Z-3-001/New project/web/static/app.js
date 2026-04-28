const slotList = document.querySelector("#slotList");
const loginScreen = document.querySelector("#loginScreen");
const loginSplash = document.querySelector("#loginSplash");
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
const monitoringRangeApply = document.querySelector("#monitoringRangeApply");
const monitoringRangeDownload = document.querySelector("#monitoringRangeDownload");
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
const notificationTable = document.querySelector("#notificationTable");
const detectStart = document.querySelector("#detectStart");
const detectEnd = document.querySelector("#detectEnd");
const detectCards = document.querySelector("#detectCards");
const detectDetectTable = document.querySelector("#detectDetectTable");
const detectWarningTable = document.querySelector("#detectWarningTable");
const detectLogsTable = document.querySelector("#detectLogsTable");
const logsStart = document.querySelector("#logsStart");
const logsEnd = document.querySelector("#logsEnd");
const logsRangeApply = document.querySelector("#logsRangeApply");
const logsRangeDownload = document.querySelector("#logsRangeDownload");
const logsTotal = document.querySelector("#logsTotal");
const logsHistoryTable = document.querySelector("#logsHistoryTable");
const logsPagination = document.querySelector("#logsPagination");
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
const logRetentionSelect = document.querySelector("#logRetentionSelect");
const settingsApplyButton = document.querySelector("#settingsApplyButton");
const settingsApplyStatus = document.querySelector("#settingsApplyStatus");
let qrToken = "";
let qrExpiresAt = 0;
let qrPollTimer = null;
let qrClockTimer = null;
let monitoringZoom = 1;
let latestMonitoringSeries = [];
let latestMonitoringData = null;
let latestReportData = null;
let latestSourcesData = null;
let latestDashboardData = null;
let latestLicenseData = null;
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
};
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
    "license.statusTitle": "License Status",
    "license.customerInfo": "Customer Information",
    "license.supportCode": "License Key (Support Code)",
    "license.status": "License Status",
    "license.firstUsedAt": "First Used At",
    "license.expiresAt": "Expiration Date",
    "license.daysLeft": "Days Left",
    "license.updatedAt": "Updated At",
    "license.contact": "License Contact",
    "license.permanent": "Permanent License",
    "license.daysUnit": "{count} days",
    "license.reason.notRegistered": "A license key must be registered to use the Web UI.",
    "license.reason.expired": "The 365-day license period has expired. Please enter a new license key.",
    "license.reason.invalidKey": "The stored license key needs to be checked.",
    "license.reason.invalidExpiry": "The license expiration date needs to be checked.",
    "license.reason.default": "License verification is required.",
    "license.deviceBasis": "Customer + Support Code",
    "license.hardwareChange": "No impact from IP/MAC changes",
    "license.registerFailed": "License registration failed.",
    "settings.title": "Settings",
    "settings.subtitle": "Configure display language and screen theme.",
    "settings.languageTitle": "Language",
    "settings.languageDesc": "Choose the UI language for menus and labels.",
    "settings.themeTitle": "Theme",
    "settings.themeDesc": "Switch between white and black backgrounds.",
    "settings.logRetentionTitle": "Log Retention",
    "settings.logRetentionDesc": "Choose how many days logs are retained.",
    "settings.themeLight": "White",
    "settings.themeDark": "Black",
    "settings.apply": "Apply",
    "settings.pending": "Select options, then click Apply.",
    "settings.applied": "Settings have been applied.",
    "monitoring.title": "Monitoring",
    "monitoring.subtitle": "Hardware usage status is updated every 5 seconds.",
    "monitoring.startDate": "Start Date",
    "monitoring.endDate": "End Date",
    "monitoring.applyRange": "Apply",
    "dashboard.notification": "Notification",
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
    "report.exportWord": "Word",
    "report.exportExcel": "Excel",
    "report.avg": "Avg",
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
    "report.engineerOpinion": "Engineer Opinion",
    "report.engineerOpinionDesc": "Inspection comments and electronic signatures",
    "report.opinionContent": "Opinion Content",
    "report.engineerSignature": "Engineer Inspection Signature",
    "report.managerSignature": "Manager Signature",
    "report.attachSignature": "Attach",
    "report.clearSignature": "Clear",
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
    "license.statusTitle": "라이선스 상태",
    "license.customerInfo": "고객사 정보",
    "license.supportCode": "라이선스 키(Support Code)",
    "license.status": "라이선스 상태",
    "license.firstUsedAt": "최초 사용 일자",
    "license.expiresAt": "만료 일자",
    "license.daysLeft": "남은 일자",
    "license.updatedAt": "갱신 일자",
    "license.contact": "라이선스 문의",
    "license.permanent": "Permanent License",
    "license.daysUnit": "{count}일",
    "license.reason.notRegistered": "라이선스 키를 등록해야 Web UI를 사용할 수 있습니다.",
    "license.reason.expired": "라이선스 사용 기간 365일이 만료되었습니다. 새 라이선스 키를 입력해 주세요.",
    "license.reason.invalidKey": "저장된 라이선스 키 확인이 필요합니다.",
    "license.reason.invalidExpiry": "라이선스 만료 일자 확인이 필요합니다.",
    "license.reason.default": "라이선스 확인이 필요합니다.",
    "license.deviceBasis": "고객사 + Support Code",
    "license.hardwareChange": "IP/MAC 변경 영향 없음",
    "license.registerFailed": "라이선스 등록에 실패했습니다.",
    "settings.title": "설정",
    "settings.subtitle": "표시 언어와 화면 테마를 설정합니다.",
    "settings.languageTitle": "언어",
    "settings.languageDesc": "메뉴와 주요 라벨에 사용할 언어를 선택합니다.",
    "settings.themeTitle": "테마",
    "settings.themeDesc": "흰색 배경 또는 검은색 배경으로 전환합니다.",
    "settings.logRetentionTitle": "로그 보관 기간",
    "settings.logRetentionDesc": "로그를 보관할 기간을 선택합니다.",
    "settings.themeLight": "흰색",
    "settings.themeDark": "검은색",
    "settings.apply": "적용",
    "settings.pending": "항목을 선택한 뒤 적용 버튼을 누르세요.",
    "settings.applied": "설정이 적용되었습니다.",
    "monitoring.title": "모니터링",
    "monitoring.subtitle": "하드웨어 사용 상태가 5초마다 업데이트됩니다.",
    "monitoring.startDate": "Start Date",
    "monitoring.endDate": "End Date",
    "monitoring.applyRange": "적용",
    "dashboard.notification": "알림",
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
    "report.exportWord": "워드",
    "report.exportExcel": "엑셀",
    "report.avg": "평균",
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
    "report.engineerOpinion": "엔지니어 의견",
    "report.engineerOpinionDesc": "점검 의견 및 전자 서명",
    "report.opinionContent": "내용",
    "report.engineerSignature": "엔지니어 점검 담당자 서명",
    "report.managerSignature": "담당자 서명",
    "report.attachSignature": "첨부",
    "report.clearSignature": "지우기",
    "airgap.title": "에어갭",
    "airgap.subtitle": "물리적 전원 차단, 솔레노이드 잠금, 무결성 검증 상태를 실시간으로 확인합니다.",
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
  "Power cut-off, solenoid lock, and integrity verification are all operating normally.": "전원 차단, 솔레노이드 잠금, 무결성 검증이 모두 정상 동작 중입니다.",
  "Power Cut-off": "전원 차단",
  "Physical Cut-off Complete": "물리적 전원 차단 완료",
  "Hard power isolation, not a software-only unmount.": "소프트웨어 언마운트가 아닌 하드웨어 전원 격리 상태입니다.",
  "Solenoid Lock": "솔레노이드 잠금",
  Locked: "잠금",
  "Mechanical lock is engaged on the drive bay.": "드라이브 베이에 기구적 잠금이 체결되어 있습니다.",
  "Integrity Check": "무결성 검증",
  Verified: "검증 완료",
  "UID match and SHA-256 hash validation passed.": "UID 일치 및 SHA-256 해시 검증이 통과되었습니다.",
  "Real-time Interlock Process": "실시간 인터록 프로세스",
  "Power cut-off and lock sequence": "전원 차단 및 잠금 연동 순서",
  "Veeam backup completion signal received": "Veeam 백업 종료 신호 수신",
  "Permission Required": "권한 필요",
  Waiting: "대기",
  Running: "진행 중",
  Failed: "실패",
  "Veeam API Integration": "Veeam API 연동",
  "Backup completion signal and session status from VBR REST API": "VBR REST API 백업 종료 신호 및 세션 상태",
  "Backup Completion Monitor": "백업 완료 모니터",
  "Progress and isolation readiness are refreshed every 5 seconds.": "진행률과 격리 준비 상태가 5초마다 갱신됩니다.",
  "Connection": "연결",
  "Endpoint": "엔드포인트",
  "API Version": "API 버전",
  "Server Time": "서버 시간",
  "Last Backup Session": "마지막 백업 세션",
  "Backup Progress": "백업 진행률",
  "Started": "시작",
  "Ended": "종료",
  "Backup Completed": "백업 완료",
  "Backup Not Completed": "백업 미완료",
  "Live Veeam credentials required": "실시간 Veeam 계정 정보 필요",
  "Backup Policy Status": "백업 정책 상태",
  "Veeam Job States compatible policy result view": "Veeam Job States 호환 정책 결과 화면",
  "Policies": "정책",
  "Success": "성공",
  "Warning": "경고",
  "Failed": "실패",
  "Running": "실행 중",
  "Policy Name": "정책명",
  "Last Result": "마지막 결과",
  "Last Run": "마지막 실행",
  "Next Run": "다음 실행",
  "Enabled": "활성",
  "Disabled": "비활성",
  "No backup policy data": "백업 정책 데이터 없음",
  "No session data": "세션 데이터 없음",
  "Backup Result History": "백업 성공/실패 이력",
  "Last 24 hours compatible Veeam session result view": "최근 24시간 Veeam 세션 결과 호환 화면",
  "Latest Veeam REST sessions ordered by poll result": "Veeam REST 조회 기준 최신 세션 목록",
  "Job Name": "작업명",
  "Session Type": "세션 유형",
  "Start Time": "시작 시간",
  "End Time": "종료 시간",
  "LOCK-FIX Interlock": "LOCK-FIX 인터록",
  "Isolation Ready": "격리 준비 완료",
  "Hold Isolation": "격리 보류",
  "Recent Veeam Sessions": "최근 Veeam 세션",
  "Repository Capacity": "Repository 용량",
  "Backup Repositories": "백업 Repository",
  Repository: "Repository",
  "Repository capacity and free space from VBR REST API": "VBR REST API 기반 Repository 용량 및 여유 공간",
  "Scale-out Repositories": "Scale-out Repository",
  "Object Storage": "오브젝트 스토리지",
  "Repositories": "Repository",
  "Online": "온라인",
  "Status": "상태",
  "Total Capacity": "총 용량",
  "Used Space": "사용 용량",
  "Free Space": "여유 공간",
  "Usage": "사용률",
  "Capacity": "용량",
  "Used": "사용",
  "Free": "여유",
  "Host": "호스트",
  "Path": "경로",
  "Type": "유형",
  "State": "상태",
  "No repository data": "Repository 데이터 없음",
  "Session": "세션",
  "State": "상태",
  "Result": "결과",
  "Progress": "진행률",
  Name: "이름",
  "Drive hard power-off executed": "드라이브 물리 전원 차단 실행",
  "Solenoid lock engaged": "솔레노이드 잠금 체결 완료",
  "Air-Gap isolation active": "에어갭 격리 활성화",
  "Safe state active": "안전 상태 활성화",
  Complete: "완료",
  "Drive Bay Map": "드라이브 베이 맵",
  "Physical power and solenoid status by slot": "슬롯별 물리 전원 및 솔레노이드 상태",
  "Ready to Unlock": "해제 가능",
  "Physical Power Cut-off Complete": "물리적 전원 차단 완료",
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

function veeamStatusClass(status) {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "connected" || normalized === "live" || normalized === "success") return "veeam-status-live";
  if (normalized === "warning") return "veeam-status-wait";
  if (normalized === "failed") return "veeam-status-error";
  if (normalized === "disabled" || normalized === "waiting_for_credentials" || normalized === "not_configured") {
    return "veeam-status-wait";
  }
  if (normalized === "error") return "veeam-status-error";
  return "veeam-status-mock";
}

function veeamMonitorClass(monitor) {
  const state = String(monitor?.state || "").toLowerCase();
  if (state === "completed") return "veeam-status-live";
  if (state === "running" || state === "completed_waiting") return "veeam-status-wait";
  if (state === "attention") return "veeam-status-error";
  return "veeam-status-mock";
}

function airgapStepClass(state) {
  const normalized = String(state || "").toLowerCase();
  if (normalized === "active") return "airgap-step-active";
  if (normalized === "done") return "airgap-step-done";
  if (normalized === "running") return "airgap-step-running";
  if (normalized === "error") return "airgap-step-error";
  return "airgap-step-waiting";
}

function formatGb(value) {
  const number = Number(value || 0);
  if (number >= 1024) return `${(number / 1024).toFixed(2)} TB`;
  return `${number.toFixed(1)} GB`;
}

function dashboardCopy() {
  if (uiSettings.language !== "ko") {
    return {
      protection: "Protection Status",
      normal: "Normal",
      airgap: "Air-Gap Status",
      active: "Active",
      storagePower: "Storage Power",
      off: "OFF",
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
      protectedMessage: "Current backup storage power is cut off and external access is unavailable.",
      backupStart: "Backup completed detected",
      powerOn: "Storage power ON",
      backupRunning: "Backup running",
      backupEnd: "Backup completed",
      flush: "Flush verified",
      flowBackupComplete: ["Backup", "complete"],
      flowFlushRun: ["Flush", "run"],
      flowIoCheck: ["I/O closed", "verified"],
      flowPowerOff: ["Power", "OFF"],
      flowAirgapActive: ["Air-Gap", "active"],
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
    storagePower: "저장장치 전원",
    off: "OFF",
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
    protectedMessage: "현재 백업 저장소는 전원이 차단되어 외부 접근이 불가능한 상태입니다.",
    backupStart: "백업 완료 감지",
    powerOn: "저장장치 전원 ON",
    backupRunning: "백업 진행",
    backupEnd: "백업 종료",
    flush: "Flush 확인",
    flowBackupComplete: ["백업", "완료"],
    flowFlushRun: ["Flush", "실행"],
    flowIoCheck: ["I/O 종료", "확인"],
    flowPowerOff: ["전원", "OFF"],
    flowAirgapActive: ["Air-Gap", "활성"],
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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
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
}

function applyPendingUiSettings() {
  uiSettings = { ...pendingUiSettings };
  localStorage.setItem("lockfix.language", uiSettings.language);
  localStorage.setItem("lockfix.theme", uiSettings.theme);
  logsRange.retention = Number(logRetentionSelect?.value || logsRange.retention || 30);
  logsRange.page = 1;
  localStorage.setItem("lockfix.logRetentionDays", String(logsRange.retention));
  applyUiSettings();
  settingsApplyStatus.textContent = t("settings.applied");
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
  if (latestLicenseData) {
    updateLicenseGate(latestLicenseData);
  }
  reloadLogs().catch((error) => console.warn("Unable to reload logs after retention change", error));
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
  loginSplash.classList.add("hidden");
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

async function showLoginSplashThenEnter() {
  loginScreen.classList.add("login-hidden");
  appRoot.classList.add("app-locked");
  loginSplash.classList.remove("hidden");
  stopQrTimers();
  await loadAll();
  await new Promise((resolve) => setTimeout(resolve, 3000));
  setAuthenticated(true);
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
  dashboardView.innerHTML = `
    <div class="security-kpi-grid">
      ${[
        ["data-protection-logo", copy.protection, copy.normal, "green", ""],
        ["airgap-logo", copy.airgap, copy.active, "blue", ""],
        ["storage-power", copy.storagePower, copy.off, "dark", ""],
        ["veeam-backup-completed", copy.lastBackup, copy.success, "green", "2026-04-25 18:25"],
        ["integrity-logo", copy.integrity, copy.normal, "green", `${copy.latest} 2026-04-25 17:40`],
      ].map(([icon, label, value, tone, meta]) => `
        <article class="security-kpi security-kpi-${icon}">
          <i class="security-icon security-icon-${icon} security-tone-${tone}" ${meta ? `title="${meta}" aria-label="${meta}"` : 'aria-hidden="true"'}></i>
          <div><span>${label}</span><strong class="security-value-${tone}">${value}</strong></div>
        </article>
      `).join("")}
    </div>

    <div class="security-dashboard-grid">
      <section class="security-panel security-flow-panel">
        <header><h2><i class="panel-title-icon protection-title-icon" aria-hidden="true"></i>${copy.liveProtection}</h2><span>ⓘ</span></header>
        <div class="panel-body">
          <p>${copy.protectedMessage.replace("전원이 차단", "<b>전원이 차단</b>").replace("Power is cut off", "<b>power is cut off</b>")}</p>
          <div class="security-flow">
            ${[
              ["backup-complete", copy.flowBackupComplete],
              ["flush-run", copy.flowFlushRun],
              ["io-check", copy.flowIoCheck],
              ["power-off", copy.flowPowerOff],
              ["airgap-logo", copy.flowAirgapActive],
            ].map(([icon, lines], index, arr) => `
              <div class="flow-step ${index === arr.length - 1 ? "flow-step-active" : ""}">
                <i class="security-icon security-icon-${icon}" aria-hidden="true"></i>
                <span>${lines.map((line) => `<b>${line}</b>`).join("")}</span>
              </div>
            `).join("")}
          </div>
        </div>
      </section>

      <section class="security-panel backup-panel">
        <header><h2><i class="panel-title-icon backup-title-icon" aria-hidden="true"></i>${copy.backupLink}</h2></header>
        <div class="panel-body">
          <dl>
            <div><dt>연동 백업 솔루션</dt><dd>Veeam Backup & Replication</dd></div>
            <div><dt>마지막 작업명</dt><dd>Daily_Backup_VM_01</dd></div>
            <div><dt>백업 시작</dt><dd>2026-04-25 17:00</dd></div>
            <div><dt>백업 종료</dt><dd>2026-04-25 18:25</dd></div>
            <div><dt>LOCK-FIX 차단 수행</dt><dd>2026-04-25 18:32</dd></div>
            <div><dt>차단 결과</dt><dd class="backup-result backup-result-success">${copy.success}</dd></div>
          </dl>
        </div>
      </section>

      <section class="security-panel event-panel">
        <header><h2><i class="panel-title-icon event-title-icon" aria-hidden="true"></i>${copy.event}</h2></header>
        <div class="panel-body">
        ${[
          ["18:32", "백업 종료 후 전원 차단 성공"],
          ["18:30", "백업 작업 완료"],
          ["17:58", "백업 시작 전 전원 ON"],
          ["17:55", "정책 검증 완료"],
          ["17:40", "무결성 검사 정상"],
        ].map((event) => `<div class="event-row"><span><i class="event-clock" aria-hidden="true"></i>${event[0]}</span><strong>${event[1]}</strong></div>`).join("")}
        <a>${copy.detail} ›</a>
        </div>
      </section>

      <section class="security-panel alert-panel">
        <header><h2><i class="panel-title-icon alert-title-icon" aria-hidden="true"></i>${copy.alert}</h2></header>
        <div class="panel-body">
          <div class="alert-ok"><span>${copy.noCritical}</span></div>
          ${[
            "전원 차단 실패",
            "통신 끊김",
            "비인가 전원 ON 시도",
            "디스크 탈거 감지",
          ].map((item) => `<div class="health-row"><span>${item}</span><b>${copy.normal}</b></div>`).join("")}
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
  data.inspection_items.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${reportInspectionText(item.category)}</td>
      <td>${reportInspectionText(item.item)}</td>
      <td>${reportInspectionText(item.detail)}</td>
      <td>${reportInspectionText(item.criteria)}</td>
      <td>${reportInspectionText(item.metric)}</td>
      <td><span class="${item.result === "Warning" ? "status-bad" : "status-good"}">${reportStatusLabel(item.result)}</span></td>
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
  if (!logsRange.start) logsRange.start = data.range.start;
  if (!logsRange.end) logsRange.end = data.range.end;
  logsRange.page = data.page || 1;
  logsRange.retention = data.retention_days || logsRange.retention;
  logsStart.value = logsRange.start;
  logsEnd.value = logsRange.end;
  if (logRetentionSelect) logRetentionSelect.value = String(logsRange.retention);
  logsTotal.textContent = `Total: ${data.total_logs} logs / ${data.retention_days}일 보관`;
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
  renderLogsPagination(data);
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

function renderLicenseStatus(license) {
  if (!licenseStatusTable) return;
  latestLicenseData = license;
  const state = license.valid ? t("license.permanent") : licenseReasonText(license.reason);
  const daysLeft = license.valid ? t("license.daysUnit").replace("{count}", license.days_left) : "-";
  licenseStatusTable.innerHTML = `
    <tr><th>${t("license.customerInfo")}</th><td>${license.customer || "-"}</td></tr>
    <tr><th>${t("license.supportCode")}</th><td>${license.support_code || "-"}</td></tr>
    <tr><th>${t("license.status")}</th><td class="${license.valid ? "license-ok" : "license-bad"}">${state}</td></tr>
    <tr><th>${t("license.firstUsedAt")}</th><td>${license.issued_at || "-"}</td></tr>
    <tr><th>${t("license.expiresAt")}</th><td class="${license.days_left <= 30 ? "license-bad" : ""}">${license.expires_at || "-"}</td></tr>
    <tr><th>${t("license.daysLeft")}</th><td>${daysLeft}</td></tr>
    <tr><th>${t("license.updatedAt")}</th><td>${license.updated_at || "-"}</td></tr>
    <tr class="license-contact-row"><th>${t("license.contact")}</th><td><a href="https://www.oam.co.kr" target="_blank" rel="noreferrer">www.oam.co.kr</a><strong>| 1666 - 3736</strong></td></tr>
  `;
}

function licenseReasonText(reason) {
  const reasonKeys = {
    not_registered: "license.reason.notRegistered",
    expired: "license.reason.expired",
    invalid_key: "license.reason.invalidKey",
    invalid_expiry: "license.reason.invalidExpiry",
  };
  return reasonKeys[reason] ? t(reasonKeys[reason]) : t("license.reason.default");
}

function updateLicenseGate(license) {
  renderLicenseStatus(license);
  const locked = !license.valid;
  licenseModal.classList.toggle("hidden", !locked);
  if (!locked) return;
  licenseModalReason.textContent = licenseReasonText(license.reason);
  licenseIp.textContent = t("license.deviceBasis");
  licenseMac.textContent = t("license.hardwareChange");
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
    licenseError.textContent = payload.error || t("license.registerFailed");
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
    <text x="22" y="${height / 2}" class="network-axis-title" transform="rotate(-90 22 ${height / 2})">${uiSettings.language === "ko" ? "누적 트래픽" : "Cumulative Traffic"} (${unit})</text>
    ${bars}
    <text x="${pad.left + chartWidth / 2}" y="${height - 6}" class="network-axis-title" text-anchor="middle">${uiSettings.language === "ko" ? "IP 주소" : "IP Address"}</text>
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
  drawLineChart(latestMonitoringSeries);
  renderGauge(cpuGauge, "CPU", data.current.cpu, "#2c90ff");
  renderGauge(memoryGauge, "Memory", data.current.memory, "#46b865");
  renderGauge(diskGauge, "Disk", data.current.disk, "#ffa52b");
  renderGauge(networkGauge, "Network", data.current.network, "#8b5cf6");
  renderGauge(interfaceGauge, "Interface", data.current.interface, "#5a2f16");
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
  params.set("page", logsRange.page);
  params.set("retention", logsRange.retention);
  const query = params.toString();
  return query ? `/api/logs?${query}` : "/api/logs";
}

function logsCsvUrl() {
  const params = new URLSearchParams();
  if (logsRange.start) params.set("start", logsRange.start);
  if (logsRange.end) params.set("end", logsRange.end);
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
function renderSources(data) {
  latestSourcesData = data;
  const airGap = data.air_gap;
  sourceList.replaceChildren();
  if (!airGap) {
    sourceRoot.textContent = data.root;
    return;
  }

  sourceRoot.innerHTML = `
    <section class="airgap-hero">
      <div class="airgap-score">
        <span>${airgapText("Unified Security Score")}</span>
        <strong>${airGap.security_score.score}</strong>
        <em>${airgapText(airGap.security_score.status)}</em>
      </div>
      <p>${airgapText(airGap.security_score.description)}</p>
    </section>
  `;

  const kpi = document.createElement("section");
  kpi.className = "airgap-kpi-grid";
  kpi.innerHTML = airGap.kpis.map((item) => `
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
  timeline.className = "airgap-panel";
  timeline.innerHTML = `
    <div class="airgap-panel-head">
      <h2>${airgapText("Real-time Interlock Process")}</h2>
      <span>${airgapText("Power cut-off and lock sequence")}</span>
    </div>
    <div class="airgap-timeline">
      ${airGap.timeline.map((item) => `
        <article class="airgap-step ${airgapStepClass(item.state)}">
          <b>${item.step}</b>
          <strong>${airgapText(item.title)}</strong>
          <span>${airgapText(item.status || (item.state === "ACTIVE" ? "Safe state active" : "Complete"))}</span>
        </article>
      `).join("")}
    </div>
  `;
  sourceList.appendChild(timeline);

  if (airGap.veeam) {
    const veeam = airGap.veeam;
    const lastBackup = veeam.last_backup || {};
    const monitor = veeam.backup_monitor || {};
    const sessionResultMonitor = veeam.session_result_monitor || {};
    const policyMonitor = veeam.policy_monitor || {};
    const policies = policyMonitor.policies || [];
    const repositoryMonitor = veeam.repository_monitor || {};
    const repositories = repositoryMonitor.repositories || [];
    const progress = Math.max(0, Math.min(100, Number(monitor.progress || lastBackup.progress || 0)));
    const veeamPanel = document.createElement("section");
    veeamPanel.className = "airgap-panel veeam-panel";
    veeamPanel.innerHTML = `
      <div class="airgap-panel-head">
        <h2>${airgapText("Backup Completion Monitor")}</h2>
        <span>${airgapText("Progress and isolation readiness are refreshed every 5 seconds.")}</span>
      </div>
      <div class="veeam-monitor-hero">
        <article class="veeam-monitor-primary">
          <span>${airgapText("Last Backup Session")}</span>
          <strong>${escapeHtml(lastBackup.name || "-")}</strong>
          <em class="${veeamMonitorClass(monitor)}">${airgapText(monitor.completed ? "Backup Completed" : "Backup Not Completed")}</em>
          <div class="veeam-progress" aria-label="${airgapText("Backup Progress")}">
            <i style="width: ${progress}%"></i>
          </div>
          <p><b>${airgapText("Backup Progress")}</b><strong>${progress}%</strong></p>
        </article>
        <article class="veeam-monitor-gate">
          <span>${airgapText("LOCK-FIX Interlock")}</span>
          <strong class="${veeam.interlock_ready ? "veeam-status-live" : "veeam-status-wait"}">${airgapText(veeam.interlock_ready ? "Isolation Ready" : "Hold Isolation")}</strong>
          <p>${escapeHtml(veeam.interlock_policy || "-")}</p>
        </article>
        <article class="veeam-monitor-time">
          <span>${airgapText("Started")}</span>
          <strong>${escapeHtml(monitor.started_at || lastBackup.creation_time || "-")}</strong>
          <span>${airgapText("Ended")}</span>
          <strong>${escapeHtml(monitor.ended_at || lastBackup.end_time || "-")}</strong>
        </article>
        <article class="veeam-monitor-results">
          <span>${airgapText("Backup Result History")}</span>
          <div>
            <strong class="veeam-status-live">${sessionResultMonitor.success_count || 0}</strong><small>${airgapText("Success")}</small>
            <strong class="veeam-status-error">${sessionResultMonitor.failed_count || 0}</strong><small>${airgapText("Failed")}</small>
            <strong class="veeam-status-wait">${sessionResultMonitor.running_count || 0}</strong><small>${airgapText("Running")}</small>
          </div>
        </article>
      </div>
      <div class="veeam-summary-grid">
        <article>
          <span>${airgapText("Connection")}</span>
          <strong class="${veeamStatusClass(veeam.status)}">${escapeHtml(veeam.status || "-")}</strong>
          <p>${escapeHtml(veeam.message || "-")}</p>
        </article>
        <article>
          <span>${airgapText("Endpoint")}</span>
          <strong>${escapeHtml(veeam.endpoint || "-")}</strong>
          <p>${airgapText("API Version")}: ${escapeHtml(veeam.api_version || "-")}</p>
        </article>
        <article>
          <span>${airgapText("Result")}</span>
          <strong class="${veeamMonitorClass(monitor)}">${escapeHtml(monitor.result || lastBackup.result || "-")}</strong>
          <p>${escapeHtml(airgapText(monitor.title || "-"))}</p>
        </article>
      </div>
      <div class="veeam-session-table-wrap">
        <h3>${airgapText("Backup Policy Status")}</h3>
        <p class="veeam-section-note">${airgapText("Veeam Job States compatible policy result view")}</p>
        <div class="veeam-policy-summary">
          <article><span>${airgapText("Policies")}</span><strong>${policyMonitor.policy_count || 0}</strong><p>${airgapText("Running")}: ${policyMonitor.running_count || 0}</p></article>
          <article><span>${airgapText("Success")}</span><strong class="veeam-status-live">${policyMonitor.success_count || 0}</strong><p>${airgapText("Warning")}: ${policyMonitor.warning_count || 0}</p></article>
          <article><span>${airgapText("Failed")}</span><strong class="veeam-status-error">${policyMonitor.failed_count || 0}</strong><p>${escapeHtml(policyMonitor.message || "-")}</p></article>
        </div>
        <table class="veeam-session-table veeam-policy-table">
          <thead>
            <tr><th>${airgapText("Policy Name")}</th><th>${airgapText("Type")}</th><th>${airgapText("State")}</th><th>${airgapText("Last Result")}</th><th>${airgapText("Last Run")}</th><th>${airgapText("Next Run")}</th><th>${airgapText("Enabled")}</th></tr>
          </thead>
          <tbody>
            ${policies.length ? policies.map((item) => `
              <tr>
                <td>${escapeHtml(item.name || "-")}</td>
                <td>${escapeHtml(item.type || "-")}</td>
                <td>${escapeHtml(item.status || "-")}</td>
                <td><strong class="${veeamStatusClass(item.last_result)}">${escapeHtml(item.last_result || "-")}</strong></td>
                <td>${escapeHtml(item.last_run || "-")}</td>
                <td>${escapeHtml(item.next_run || "-")}</td>
                <td>${airgapText(item.is_enabled ? "Enabled" : "Disabled")}</td>
              </tr>
            `).join("") : `<tr><td colspan="7">${airgapText("No backup policy data")}</td></tr>`}
          </tbody>
        </table>
        <h3>${airgapText("Repository Capacity")}</h3>
        <p class="veeam-section-note">${airgapText("Repository capacity and free space from VBR REST API")}</p>
        <div class="veeam-repository-console">
          <aside class="veeam-repository-tree" aria-label="${airgapText("Backup Repositories")}">
            <strong>${airgapText("Backup Infrastructure")}</strong>
            <button type="button" class="active"><span></span>${airgapText("Backup Repositories")} <b>${repositoryMonitor.repository_count || 0}</b></button>
            <button type="button"><span></span>${airgapText("Scale-out Repositories")} <b>0</b></button>
            <button type="button"><span></span>${airgapText("Object Storage")} <b>0</b></button>
          </aside>
          <section class="veeam-repository-grid">
            <div class="veeam-repository-toolbar">
              <div>
                <strong>${airgapText("Backup Repositories")}</strong>
                <span>${airgapText("Online")}: ${repositoryMonitor.online_count || 0} / ${repositoryMonitor.repository_count || 0}</span>
              </div>
              <div class="repository-total-meter">
                <span>${airgapText("Total Capacity")}</span>
                <b>${formatGb(repositoryMonitor.total_capacity_gb)}</b>
                <i><em style="width: ${Math.max(0, Math.min(100, Number(repositoryMonitor.usage_percent || 0)))}%"></em></i>
              </div>
            </div>
            <table class="veeam-session-table veeam-repository-table">
              <thead>
                <tr>
                  <th>${airgapText("Name")}</th>
                  <th>${airgapText("Status")}</th>
                  <th>${airgapText("Type")}</th>
                  <th>${airgapText("Host")}</th>
                  <th>${airgapText("Path")}</th>
                  <th>${airgapText("Capacity")}</th>
                  <th>${airgapText("Free")}</th>
                  <th>${airgapText("Used")}</th>
                </tr>
              </thead>
              <tbody>
                ${repositories.length ? repositories.map((item) => `
                  <tr>
                    <td><span class="repository-name-cell"><i></i>${escapeHtml(item.name || "-")}</span></td>
                    <td><span class="repository-status ${item.is_online ? "repository-online" : "repository-offline"}">${escapeHtml(item.is_online ? "Online" : "Offline")}</span></td>
                    <td>${escapeHtml(item.type || "-")}</td>
                    <td>${escapeHtml(item.host || "-")}</td>
                    <td>${escapeHtml(item.path || "-")}</td>
                    <td>${formatGb(item.capacity_gb)}</td>
                    <td>${formatGb(item.free_gb)}</td>
                    <td>
                      <div class="repository-usage">
                        <span><i style="width: ${Math.max(0, Math.min(100, Number(item.usage_percent || 0)))}%"></i></span>
                        <b>${escapeHtml(String(item.usage_percent ?? 0))}%</b>
                      </div>
                    </td>
                  </tr>
                `).join("") : `<tr><td colspan="8">${airgapText("No repository data")}</td></tr>`}
              </tbody>
            </table>
            <div class="veeam-repository-footer">
              <span>${airgapText("Used Space")}: <b>${formatGb(repositoryMonitor.total_used_gb)}</b></span>
              <span>${airgapText("Free Space")}: <b>${formatGb(repositoryMonitor.total_free_gb)}</b></span>
              <span>${airgapText("Usage")}: <b>${repositoryMonitor.usage_percent || 0}%</b></span>
            </div>
          </section>
        </div>
        <h3>${airgapText("Backup Result History")}</h3>
        <p class="veeam-section-note">${airgapText("Last 24 hours compatible Veeam session result view")}</p>
        <table class="veeam-session-table">
          <thead>
            <tr><th>${airgapText("Job Name")}</th><th>${airgapText("Session Type")}</th><th>${airgapText("Status")}</th><th>${airgapText("Start Time")}</th><th>${airgapText("End Time")}</th></tr>
          </thead>
          <tbody>
            ${(veeam.sessions || []).length ? (veeam.sessions || []).map((item) => `
              <tr>
                <td>${escapeHtml(item.name || "-")}</td>
                <td>${escapeHtml(item.session_type || "-")}</td>
                <td><strong class="${veeamStatusClass(item.result)}">${escapeHtml(item.result || item.state || "-")}</strong></td>
                <td>${escapeHtml(item.creation_time || "-")}</td>
                <td>${escapeHtml(item.end_time || "-")}</td>
              </tr>
            `).join("") : `<tr><td colspan="5">${airgapText("No session data")}</td></tr>`}
          </tbody>
        </table>
        <h3>${airgapText("Recent Veeam Sessions")}</h3>
        <p class="veeam-section-note">${airgapText("Latest Veeam REST sessions ordered by poll result")}</p>
        <table class="veeam-session-table veeam-recent-session-table">
          <thead>
            <tr><th>${airgapText("Session")}</th><th>${airgapText("Session Type")}</th><th>${airgapText("State")}</th><th>${airgapText("Result")}</th><th>${airgapText("Progress")}</th></tr>
          </thead>
          <tbody>
            ${(veeam.sessions || []).length ? (veeam.sessions || []).map((item) => `
              <tr>
                <td>${escapeHtml(item.name || "-")}</td>
                <td>${escapeHtml(item.session_type || "-")}</td>
                <td>${escapeHtml(item.state || "-")}</td>
                <td><strong class="${veeamStatusClass(item.result)}">${escapeHtml(item.result || "-")}</strong></td>
                <td>
                  <div class="repository-usage">
                    <span><i style="width: ${Math.max(0, Math.min(100, Number(item.progress || 0)))}%"></i></span>
                    <b>${escapeHtml(String(item.progress ?? "-"))}${item.progress === undefined ? "" : "%"}</b>
                  </div>
                </td>
              </tr>
            `).join("") : `<tr><td colspan="5">${airgapText("No session data")}</td></tr>`}
          </tbody>
        </table>
      </div>
    `;
    sourceList.appendChild(veeamPanel);
  }

  const bayMap = document.createElement("section");
  bayMap.className = "airgap-panel";
  bayMap.innerHTML = `
    <div class="airgap-panel-head">
      <h2>${airgapText("Drive Bay Map")}</h2>
      <span>${airgapText("Physical power and solenoid status by slot")}</span>
    </div>
    <div class="airgap-bay-grid">
      ${airGap.bays.map((bay) => `
        <article class="airgap-bay ${bay.lock.state === "LOCKED" ? "bay-locked" : "bay-ready"}">
          <div class="bay-top">
            <strong>${bay.slot}</strong>
            <span>${airgapText(bay.lock.label)}</span>
          </div>
          <div class="bay-visual">
            <i class="circuit-cut" aria-hidden="true"></i>
            <i class="bay-lock" aria-hidden="true"></i>
          </div>
          <dl>
            <div><dt>${airgapText("Power Cut-off")}</dt><dd>${airgapText(bay.power.label)}</dd></div>
            <div><dt>${airgapText("Solenoid")}</dt><dd>${airgapText(bay.lock.description)}</dd></div>
            <div><dt>UID</dt><dd>${airgapText(bay.integrity.uid)}</dd></div>
            <div><dt>${airgapText("Hash")}</dt><dd>${airgapText(bay.integrity.hash)}</dd></div>
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
          ${airGap.integrity_history.map((item) => `
            <tr><td>${item.time}</td><td>${airgapText(item.target)}</td><td>${airgapText(item.uid)}</td><td>${airgapText(item.hash)}</td></tr>
          `).join("")}
        </tbody>
      </table>
    </article>
    <article class="airgap-panel emergency-panel">
      <div class="airgap-panel-head">
        <h2>${airgapText(airGap.emergency.title)}</h2>
        <span>${airgapText("Two-administrator approval required")}</span>
      </div>
      <p>${airgapText(airGap.emergency.description)}</p>
      <button type="button">${airgapText(airGap.emergency.primary)}</button>
      <strong>${airgapText(airGap.emergency.secondary)}</strong>
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
  const [summary, audit, integrated, monitoring, sources, dashboard, report, notification, detect, networkStatus, logs, license] = await Promise.all([
    requestJson("/api/summary"),
    requestJson("/api/audit"),
    requestJson("/api/integrated"),
    requestJson(monitoringUrl()),
    requestJson("/api/sources"),
    requestJson("/api/dashboard"),
    requestJson("/api/report"),
    requestJson("/api/notification"),
    requestJson("/api/detect"),
    requestJson("/api/network-status"),
    requestJson(logsUrl()),
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
logsRangeApply.addEventListener("click", async () => {
  let start = logsStart.value;
  let end = logsEnd.value;
  if (start && end && start > end) {
    end = start;
    logsEnd.value = end;
  }
  logsRange.start = start;
  logsRange.end = end;
  logsRange.page = 1;
  await reloadLogs();
});
logsRangeDownload?.addEventListener("click", () => {
  window.location.href = logsCsvUrl();
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
logRetentionSelect?.addEventListener("change", () => {
  settingsApplyStatus.textContent = translations[pendingUiSettings.language]?.["settings.pending"] || translations.en["settings.pending"];
});
settingsApplyButton.addEventListener("click", applyPendingUiSettings);
applyUiSettings();
setupReportSignatures();
checkSession();
setInterval(() => {
  if (!appRoot.classList.contains("app-locked")) {
    loadAll();
  }
}, 5000);

