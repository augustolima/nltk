#! /bin/bash

# Installs the current version of NLTK to
# the current python virtual environment.
# Requires virtualenvwrapper. Run from within
# the desired virtual environment.


function doublecheck {
    echo "Install to virtual environment '$(basename ${VIRTUAL_ENV})'? (y/n)"
    read -n 1 ANS
    if [[ ${ANS} == "n" ]]
    then
        echo -e "\rInstallation aborted"
        exit 1
    fi
}


SAFE=true
while getopts ":f" opt
do
    case ${opt} in
        f)
            SAFE=false
            ;;
        \?)
            echo "Invalid option -${OPTARG}" >&2
            ;;
    esac
done


if [ ${SAFE} = true ]
then
    doublecheck
fi

echo -e "\rCreating required directories"
INSTALLDIR=${VIRTUAL_ENV}/lib/python2.7/site-packages/nltk
TEMPDIR=${HOME}/Software/nltk
mkdir -p ${INSTALLDIR}
mkdir -p ${TEMPDIR}

echo "Copying source to temp directory '${TEMPDIR}'"
cp -r * ${TEMPDIR}
cd ${TEMPDIR}

echo "Building NLTK"
sudo python setup.py install > /dev/null 2>&1 

echo "Installing NLTK"
cp -r ${TEMPDIR}/build/lib/nltk/* ${INSTALLDIR}

if [[ $(python -c 'import nltk') -eq 0 ]]
then
    echo "Installation successful"
else
    echo "Installation failed"
fi