##- Use of privileged commands (unsuccessful and successful)
## You can run the following commands to generate the rules:
find /bin -type f -perm -04000 2>/dev/null | awk '{ printf "-a always,exit -F path=%s -F perm=x -F auid>=1000 -F auid!=4294967295 -F key=privileged\n", $1 }' > 31-privileged.rules
find /sbin -type f -perm -04000 2>/dev/null | awk '{ printf "-a always,exit -F path=%s -F perm=x -F auid>=1000 -F auid!=4294967295 -F key=privileged\n", $1 }' >> 31-privileged.rules
find /usr/bin -type f -perm -04000 2>/dev/null | awk '{ printf "-a always,exit -F path=%s -F perm=x -F auid>=1000 -F auid!=4294967295 -F key=privileged\n", $1 }' >> 31-privileged.rules
find /usr/sbin -type f -perm -04000 2>/dev/null | awk '{ printf "-a always,exit -F path=%s -F perm=x -F auid>=1000 -F auid!=4294967295 -F key=privileged\n", $1 }' >> 31-privileged.rules
filecap /bin 2>/dev/null | sed '1d' | awk '{ printf "-a always,exit -F path=%s -F perm=x -F auid>=1000 -F auid!=4294967295 -F key=privileged\n", $1 }' >> 31-privileged.rules
filecap /sbin 2>/dev/null | sed '1d' | awk '{ printf "-a always,exit -F path=%s -F perm=x -F auid>=1000 -F auid!=4294967295 -F key=privileged\n", $1 }' >> 31-privileged.rules
filecap /usr/bin 2>/dev/null | sed '1d' | awk '{ printf "-a always,exit -F path=%s -F perm=x -F auid>=1000 -F auid!=4294967295 -F key=privileged\n", $1 }' >> 31-privileged.rules
filecap /usr/sbin 2>/dev/null | sed '1d' | awk '{ printf "-a always,exit -F path=%s -F perm=x -F auid>=1000 -F auid!=4294967295 -F key=privileged\n", $1 }' >> 31-privileged.rules

