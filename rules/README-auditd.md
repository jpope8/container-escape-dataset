The auditd tool is configured using a sequence of rule files.

The sequence is necessary because for a given event, multiple rules may apply.
The first rule encountered is used to the sequence provides a course way to specify which one is preferred.

The auditd installation comes with example rule files in /usr/share/doc/auditd/examples.
The following shows the example rule files from a Raspian Buster installation.

    -rw-r--r-- 1 root root  240 Jun 19  2018 10-base-config.rules
    -rw-r--r-- 1 root root  284 May 21  2018 10-no-audit.rules
    -rw-r--r-- 1 root root   93 May 21  2018 11-loginuid.rules
    -rw-r--r-- 1 root root  329 May 21  2018 12-cont-fail.rules
    -rw-r--r-- 1 root root  323 May 21  2018 12-ignore-error.rules
    -rw-r--r-- 1 root root  516 May 21  2018 20-dont-audit.rules
    -rw-r--r-- 1 root root  273 May 21  2018 21-no32bit.rules
    -rw-r--r-- 1 root root  252 May 21  2018 22-ignore-chrony.rules
    -rw-r--r-- 1 root root  506 May 21  2018 23-ignore-filesystems.rules
    -rw-r--r-- 1 root root 1368 May 21  2018 30-nispom.rules.gz
    -rw-r--r-- 1 root root 2105 May 21  2018 30-pci-dss-v31.rules.gz
    -rw-r--r-- 1 root root 2171 May 21  2018 30-stig.rules.gz
    -rw-r--r-- 1 root root 1498 May 21  2018 31-privileged.rules
    -rw-r--r-- 1 root root  218 May 21  2018 32-power-abuse.rules
    -rw-r--r-- 1 root root  156 May 21  2018 40-local.rules
    -rw-r--r-- 1 root root  439 May 21  2018 41-containers.rules
    -rw-r--r-- 1 root root  672 May 21  2018 42-injection.rules
    -rw-r--r-- 1 root root  454 May 21  2018 43-module-load.rules
    -rw-r--r-- 1 root root  326 May 21  2018 70-einval.rules
    -rw-r--r-- 1 root root  151 May 21  2018 71-networking.rules
    -rw-r--r-- 1 root root   86 May 21  2018 99-finalize.rules
    -rw-r--r-- 1 root root 1202 May 21  2018 README-rules

The intended number groupings are defined as follows:

    10 - Kernel and auditctl configuration
    20 - Rules that could match general rules but we want a different match
    30 - Main rules
    40 - Optional rules
    50 - Server Specific rules
    70 - System local rules
    90 - Finalize (immutable)

There is one set of rules, 31-privileged.rules, that should be regenerated.
There is a script in the comments of that file. You can uncomment the commands
and run the script and then rename the resulting file.
see https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/security_guide/sec-defining_audit_rules_and_controls

These are just examples.
The auditd daemon reads and uses the rules specified in the audit.rules file in /etc/audit/audit.rules.
It is recommended to generate this file from the rule files and the augenrules utulity is provided for this purpose.

Copy all the desired rule files into the /etc/audit/rules.d directory.

    pi@raspberry:~ $ sudo ls -la /etc/audit/rules.d/
    drwxr-x--- 2 root root 4096 Jul 22 13:43 .
    drwxr-x--- 3 root root 4096 Jul  1 13:56 ..
    -rw-r--r-- 1 root root  240 Jul 22 13:43 10-base-config.rules
    -rw-r--r-- 1 root root   98 Jul 22 13:43 10-procmon.rules
    -rw-r--r-- 1 root root 5559 Jul 22 13:43 30-stig.rules
    -rw-r--r-- 1 root root 1187 Jul 22 13:43 31-privileged.rules
    -rw-r--r-- 1 root root 1502 Jul 22 13:43 33-docker.rules
    -rw-r--r-- 1 root root 1258 Jul 22 13:43 41-containers.rules
    -rw-r--r-- 1 root root  458 Jul 22 13:43 43-module-load.rules
    -rw-r--r-- 1 root root  950 Jul 22 13:43 71-networking.rules
    -rw-r--r-- 1 root root   86 Jul 22 13:43 99-finalize.rules

Now run the augenrules utility.  This concatenates the rule file contents
into the /etc/audit/audit.rules file in the correct order.

    augenrules --load

Once this is done the auditd daemon must be started or restarted.

    sudo service auditd start
    sudo service auditd restart

Some useful commands

    scp -p pi@192.168.1.102:/storage/logs/audit/audit.log .
    ssh -i id_rsa pi@192.168.1.102
