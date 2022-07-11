cd /opt
sudo systemctl stop helena.service &&  sudo systemctl stop influxshake.service && \
        tar xvf beddot.tar.gz && crontab < /opt/helena/cronjobs && \
        echo "updated at $(date)" > update.log && \
        sudo reboot
