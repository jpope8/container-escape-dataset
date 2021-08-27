sudo rm /etc/audit/rules.d/10-base-config.rules
sudo rm /etc/audit/rules.d/10-procmon.rules
sudo rm /etc/audit/rules.d/30-stig.rules
sudo rm /etc/audit/rules.d/31-privileged.rules
sudo rm /etc/audit/rules.d/33-docker.rules
sudo rm /etc/audit/rules.d/41-containers.rules
sudo rm /etc/audit/rules.d/43-module-load.rules
sudo rm /etc/audit/rules.d/71-networking.rules
sudo rm /etc/audit/rules.d/99-finalize.rules
sudo rm /etc/audit/rules.d/audit.rules

sudo cp 10-base-config.rules /etc/audit/rules.d/.
sudo cp 10-procmon.rules /etc/audit/rules.d/.
sudo cp 30-stig.rules /etc/audit/rules.d/.
sudo cp 31-privileged.rules /etc/audit/rules.d/.
sudo cp 33-docker.rules /etc/audit/rules.d/.
sudo cp 41-containers.rules /etc/audit/rules.d/.
sudo cp 43-module-load.rules /etc/audit/rules.d/.
sudo cp 71-networking.rules /etc/audit/rules.d/.
sudo cp 99-finalize.rules /etc/audit/rules.d/.

sudo ls -la /etc/audit/rules.d/
