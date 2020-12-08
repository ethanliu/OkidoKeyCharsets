#!/usr/bin/env bash
#
# shortcut for buidning jyut6pin3
# php ./bin/make.php -c jyut6ping3 src/rime-cantonese/jyut6ping3.dict.yaml > table/jyut6ping3.cin
# php ./bin/make.php -c jyut6ping3-toneless src/rime-cantonese/jyut6ping3.dict.yaml > table/jyut6ping3-toneless.cin
# php ./bin/make.php -c jyut6ping3-phrase src/rime-cantonese/jyut6ping3.dict.yaml > lexicon/Rime-cantonese.csv
#


BINDIR=$(dirname $0)
BASEDIR=`(cd "${BINDIR}/../" && pwd)`
# BINDIR="${BASEDIR}/bin"
# SRCDIR="${BASEDIR}/src/rime-cantonese"
# SRCDIR="src/rime-cantonese"
SRCPATH="_repos/rime-cantonese/jyut6ping3.dict.yaml"

# echo "${BINDIR}"
# echo "${BASEDIR}"

cd "${BASEDIR}"

/usr/bin/env php ./bin/make.php -c jyut6ping3 "${SRCPATH}" > ./table/jyut6ping3.cin
/usr/bin/env php ./bin/make.php -c jyut6ping3-toneless "${SRCPATH}" > ./table/jyut6ping3-toneless.cin
/usr/bin/env php ./bin/make.php -c jyut6ping3-phrase "${SRCPATH}" > ./lexicon/Rime-cantonese.csv

rm db/jyut6ping3.cin.db
rm db/jyut6ping3-toneless.cin.db
rm db/lexicon-Rime-cantonese.csv.db

/usr/bin/env php ./bin/make.php -dm

