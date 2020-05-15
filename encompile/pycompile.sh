# $1: the path containing the python files to compile
# $2: the entry point python module
# $3: the key to encrypt

# check the compiling env is raspberry pi
ID=`cat /etc/*-release | egrep ^ID= | cut -f2 -d'='`
if [ $ID != "raspbian" ] 
then
    echo "Please compile in raspberry pi!"
    exit
fi

# if pyinstaller is not installed
if [ -z "`pip list 2>/dev/null | grep PyInstaller`" ]
then
    pip install --user pyinstaller
fi

if [ $# -lt 1 ]
then
    echo "the path of storing files to compile is required!"
    exit
fi

pypath=$1

cp auth.py "$pypath"

# compile the python files

if [ $# -lt 2 ]
then
    echo 'entry point module name (.py) is required!'
    exit
fi

entryfile=$2
cd "$pypath"

if [ ! -e "$entryfile" ]
then
    echo "the file $pypath/$entryfile does not exist."
    exit
fi

# set auth.py as the entry point of programs
# _main.py is entry point what user specified

mv "$entryfile" _main.py
mv auth.py "$entryfile"

# key should be 16 characters
pyinstaller --onefile "$entryfile" --log-level DEBUG --key=@@@SensorWeb0987 # this key is for encrypting the bytecode

mv "$entryfile" auth.py
mv _main.py "$entryfile"

# generate a key file for preventing copy
if [ $# -lt 3 ]
then
    echo "key not specified.-> set to default: sensorweb987"
    key=sensorweb987
else
    key="$3"
fi

cat /proc/cpuinfo | grep Serial | awk '{print($3)}' > temp
echo "--------" >> temp

openssl enc -a -e -salt -aes-256-cbc -pass pass:$key -in temp -out temp.enc

mv temp.enc key
rm temp

echo "key generated successful!"
mv key dist/

rm -rf auth.py *.spec build/

echo "build completed in $pypath/dist/."
