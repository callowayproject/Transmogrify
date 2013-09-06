sudo mkdir /etc/transmogrify
sudo mkdir /etc/transmogrify/originals
sudo mkdir /etc/transmogrify/modified
sudo curl https://raw.github.com/callowayproject/Transmogrify/master/bootstrap.py | sudo python
sudo /etc/transmogrify/virtualenv/bin/configure_transmogrify -o /etc/transmogrify/originals -d /etc/transmogrify/modified -s "I am not an animal! I am a smelly human being." -f /etc/transmogrify/settings.py
