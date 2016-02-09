#! /bin/bash

# Installs the current version of NLTK to
# the current python virtual environment.
# Requires virtualenvwrapper. Run from within
# the desired virtual environment.


function usage {
    bold=$(tput bold)
    normal=$(tput sgr0)
    echo 'Usage: install.sh [-f] [-h] [NLTK_BASE_DIR ${PWD}]'
    echo -e "  ${bold}-f${normal}\tForce. Automatically install to current venv."
    echo -e "  ${bold}-h${normal}\tHelp. Print this message."
    echo -e "  ${bold}NLTK_BASE_DIR${normal}\tNLTK directory containing setup.py."
    echo -e "    If setup.py is not found, installation will abort. Default: cwd."
    echo
    exit 1
}

function doublecheck {
    echo "Install to virtual environment '$(basename ${VIRTUAL_ENV})'? (y/n)"
    read -n 1 ANS
    if [[ ${ANS} == "n" ]]
    then
        echo -e "\rInstallation aborted"
        exit 1
    fi
}

if [ $(uname) == 'Darwin' ]
then
    if which gstat > /dev/null 2>&1
    then
        STAT=gstat
    else
        echo "I need GNU stat (gstat). Please install it."
        exit 1
    fi
else
    STAT=stat
fi

HELP=false
SAFE=true
while getopts ":fh" opt
do
    case ${opt} in
        f)
            SAFE=false
            ;;
        h)
            HELP=true
            ;;
        \?)
            echo "Invalid option -${OPTARG}" >&2
            ;;
    esac
done
shift $((OPTIND - 1))

if [ ${HELP} = true ]
then
    usage
fi

if [ $# -gt 1 ]
then
    usage
fi

if [ $# -eq 1 ]
then
    NLTK_BASE_DIR=$1
else
    NLTK_BASE_DIR=${PWD}
fi

if [ ! -x ${NLTK_BASE_DIR}/setup.py ]
then
    echo "Can't find an executable ${NLTK_BASE_DIR}/setup.py. Aborting..."
    exit 1
fi

if [ ${SAFE} = true ]
then
    doublecheck
fi

echo -e "\rCreating required directories"
INSTALLDIR=${VIRTUAL_ENV}/lib/python2.7/site-packages
TEMPDIR=${HOME}/Software/nltk
mkdir -p ${INSTALLDIR}/nltk
mkdir -p ${TEMPDIR}

if [ -e ${INSTALLDIR}/nltk*.egg ]
then
    OLDCTIME=$(${STAT} -c %Y ${INSTALLDIR}/nltk*.egg)
else
    OLDCTIME=0
fi

echo "Copying source to temp directory '${TEMPDIR}'"
cp -r ${NLTK_BASE_DIR}/* ${TEMPDIR}
cd ${TEMPDIR}

echo "Building NLTK"
sudo python setup.py install > /dev/null 2>&1 

echo "Installing NLTK"
cp -r ${TEMPDIR}/build/lib/nltk/* ${INSTALLDIR}/nltk
NEWCTIME=$(${STAT} -c %Y ${INSTALLDIR}/nltk*.egg)

SUCCESS=false
if $(python -c 'import nltk')
then
    if [ ${OLDCTIME} -ne ${NEWCTIME} ]
    then
        SUCCESS=true
    fi
fi
echo "Installed: ${SUCCESS}"
