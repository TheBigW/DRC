#!/bin/bash

SCRIPT_NAME=`basename "$0"`
SCRIPT_PATH=${0%`basename "$0"`}
PLUGIN_PATH="${HOME}/.local/share/rhythmbox/plugins/DRC/"

function uninstall {
    rm -rf "${PLUGIN_PATH}"
    echo "plugin uninstalled"
    exit
}


################################ USAGE #######################################

usage=$(
cat <<EOF
Usage:
$0 [OPTION]
-h, --help      show this message.
-u, --uninstall uninstall the plugin

EOF
)

########################### OPTIONS PARSING #################################

#parse options
TMP=`getopt --name=$0 -a --longoptions=help,uninstall -o u,h -- $@`

if [[ $? == 1 ]]
then
    echo
    echo "$usage"
    exit
fi

eval set -- $TMP

until [[ $1 == -- ]]; do
    case $1 in
        -h|--help)
            echo "$usage"
            exit
            ;;
        -u|--uninstall)
            uninstall
            exit
            ;;
    esac
    shift # move the arg list to the next option or '--'
done
shift # remove the '--', now $1 positioned at first argument if any


########################## START INSTALLATION ################################

#build the dirs
mkdir -p $PLUGIN_PATH

#copy the files
cp -r "${SCRIPT_PATH}"* "$PLUGIN_PATH"

#remove the install script from the dir (not needed)
rm "${PLUGIN_PATH}${SCRIPT_NAME}"

exit
