import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error executing command: {e}"

# 1. CPU 정보
def get_cpu_info():
    cpu_model = run_command("lscpu | grep 'Model name' | awk -F: '{print $2}'").strip()
    cpu_model = cpu_model if cpu_model else "N/A"
    return {"Type": "CPU", "Model": cpu_model, "Serial": None}

# 2. 메모리 정보
def get_memory_info():
    memory_raw = run_command("sudo dmidecode --type memory | grep -i -E 'Size:|Part Number:|Serial Number:' | grep -v -E 'Not Specified|No Module Installed'")
    memory_info_list = []
    if memory_raw:
        memory_lines = memory_raw.splitlines()
        for i in range(0, len(memory_lines), 3):  # 3줄씩 묶음 (Size, Serial, Part Number)
            size = memory_lines[i].split(":")[1].strip() if ":" in memory_lines[i] else "N/A"
            serial = memory_lines[i + 1].split(":")[1].strip() if (i + 1) < len(memory_lines) and ":" in memory_lines[i + 1] else "N/A"
            part_number = memory_lines[i + 2].split(":")[1].strip() if (i + 2) < len(memory_lines) and ":" in memory_lines[i + 2] else "N/A"
            memory_info_list.append({"Type": "MEMORY", "Model": part_number, "Serial": serial})
    return memory_info_list

# 3. 디스크 정보
def get_disk_info():
    disk_info_list = []
    disks = run_command("lsblk -dno NAME").splitlines()
    for disk in disks:
        model = run_command(f"lsblk -dn -o MODEL /dev/{disk}").strip() or "N/A"
        serial = run_command(f"udevadm info --query=all --name=/dev/{disk} | grep 'ID_SERIAL=' | cut -d'=' -f2").strip() or "N/A"
        disk_info_list.append({"Type": "DISK", "Model": model, "Serial": serial})
    return disk_info_list

# 4. HBA 정보
def get_hba_info():
    hba_raw = run_command("lspci | grep -i 'Fibre Channel'")
    hba_info_list = []
    if hba_raw:
        for line in hba_raw.splitlines():
            model = line.split(":")[2].strip() if len(line.split(":")) > 2 else "N/A"
            hba_info_list.append({"Type": "HBA", "Model": model, "Serial": None})
    return hba_info_list

# 5. NIC 정보
def get_nic_info():
    nic_raw = run_command("sudo lshw -class network | grep -i -E 'product|serial'")
    nic_info_list = []
    if nic_raw:
        lines = nic_raw.splitlines()
        for i in range(0, len(lines), 2):  # product와 serial이 한쌍으로 존재
            product = lines[i].split(":")[1].strip() if ":" in lines[i] else "N/A"
            serial = lines[i + 1].split(":")[1].strip() if (i + 1) < len(lines) and ":" in lines[i + 1] else "N/A"
            nic_info_list.append({"Type": "NIC", "Model": product, "Serial": serial})
    return nic_info_list

# 6. SAS 카드 정보
def get_sas_card_info():
    sas_raw = run_command("lspci | grep -i 'SAS'")
    sas_info_list = []
    if sas_raw:
        for line in sas_raw.splitlines():
            model = line.split(":")[2].strip() if len(line.split(":")) > 2 else "N/A"
            sas_info_list.append({"Type": "SAS_CARD", "Model": model, "Serial": None})
    return sas_info_list

# 전체 하드웨어 정보 수집
# 전체 하드웨어 정보 수집
def get_all_hardware_info():
    hardware_info = []

    # Helper function to filter out invalid entries
    def add_hardware(hardware):
        if hardware["Model"] != "N/A" or hardware["Serial"] != "N/A":
            hardware_info.append(hardware)

    add_hardware(get_cpu_info())

    for memory in get_memory_info():
        add_hardware(memory)

    for disk in get_disk_info():
        add_hardware(disk)

    for hba in get_hba_info():
        add_hardware(hba)

    for nic in get_nic_info():
        add_hardware(nic)

    for sas_card in get_sas_card_info():
        add_hardware(sas_card)

    return hardware_info