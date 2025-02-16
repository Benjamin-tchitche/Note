# install buildozer

## install cython
* sudo apt-get install git libssl-dev cython3

### problem with cython

* cd /bin/ && sudo gedit cython
* Write 'cython3 $@' and save

* sudo chmod 755 cython

## install buildozer

git clone https://github.com/kivy/buildozer.git

## buildozer depencies 

* sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev

* cd buildozer/
sudo python3 setup.py install

## build
* buildozer init

* make changes in spec file 
    (internet enable, orientation etc )

* buildozer android debug