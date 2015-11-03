#! /bin/bash

# Installs the current version of NLTK to
# the current python virtual environment.
# Requires virtualenvwrapper. Run from within
# the desired virtual environment.


echo "Install to virtual environment '$(basename ${VIRTUAL_ENV})'? (y/n)"
ANS=$(read -n 1)
if [[ ${ANS} -ne "y" ]]
then
    echo -e "\nInstallation aborted"
    exit 1
fi

echo -e "\nCreating required directories"
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
