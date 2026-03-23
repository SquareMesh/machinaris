#!/bin/bash
set -eo pipefail
#
# Due to complaints about JS CDNs, this pulls all JS libs into web/static/3rd_party folder
#

# Bootstrap and Icons
BSI_VERSION=1.13.1
BOOTSTRAP_VERSION=5.3.8
BASEPATH=${JS_LIBS_BASEPATH:-/machinaris/web/static/3rd_party}

# Mapping library
LEAFLET_VERSION=1.9.4

# List of other css/js links
LIST="
https://cdn.datatables.net/2.3.5/css/dataTables.bootstrap5.css
https://cdn.datatables.net/2.3.5/js/dataTables.bootstrap5.js
https://cdn.datatables.net/2.3.5/js/dataTables.min.js
https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.js.map
https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js
https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.3.1/dist/chartjs-adapter-luxon.umd.min.js
https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js
https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js
https://cdn.jsdelivr.net/npm/luxon@3.7.2/build/global/luxon.min.js"

mkdir -p $BASEPATH
for url in $LIST ; do
  wget -nv -O ${BASEPATH}/$(basename $url) "$url"
done

# Bootstrap Icons (font CSS + woff2 from npm, not the SVG-only GitHub zip)
mkdir -p ${BASEPATH}/icons/fonts
wget -nv -O ${BASEPATH}/icons/bootstrap-icons.css "https://cdn.jsdelivr.net/npm/bootstrap-icons@${BSI_VERSION}/font/bootstrap-icons.css"
wget -nv -O ${BASEPATH}/icons/bootstrap-icons.min.css "https://cdn.jsdelivr.net/npm/bootstrap-icons@${BSI_VERSION}/font/bootstrap-icons.min.css"
wget -nv -O ${BASEPATH}/icons/fonts/bootstrap-icons.woff2 "https://cdn.jsdelivr.net/npm/bootstrap-icons@${BSI_VERSION}/font/fonts/bootstrap-icons.woff2"
wget -nv -O ${BASEPATH}/icons/fonts/bootstrap-icons.woff "https://cdn.jsdelivr.net/npm/bootstrap-icons@${BSI_VERSION}/font/fonts/bootstrap-icons.woff"

# Bootstrap
wget -O ${BASEPATH}/bs.zip -nv "https://github.com/twbs/bootstrap/releases/download/v${BOOTSTRAP_VERSION}/bootstrap-${BOOTSTRAP_VERSION}-dist.zip" && \
unzip -q -o -j ${BASEPATH}/bs.zip -d $BASEPATH/ bootstrap-${BOOTSTRAP_VERSION}*/css/bootstrap.min.css* bootstrap-${BOOTSTRAP_VERSION}*/js/bootstrap.bundle.min.js*  && \
rm -f ${BASEPATH}/bs.zip

# Leaflet and plugins
wget -O ${BASEPATH}/leaflet.zip -nv "https://leafletjs-cdn.s3.amazonaws.com/content/leaflet/v${LEAFLET_VERSION}/leaflet.zip" && \
unzip -q -o ${BASEPATH}/leaflet.zip -d $BASEPATH/ && \
rm -f ${BASEPATH}/leaflet.zip
wget -O ${BASEPATH}/leaflet-layervisibility.js -nv "https://unpkg.com/leaflet-layervisibility/dist/leaflet-layervisibility.js"
sed -i 's/\/\/# sourceMapping.*//g' ${BASEPATH}/leaflet-layervisibility.js

# Pull localization files for DataTables.js
mkdir -p $BASEPATH/i18n/
LANGS=$(grep -oP "LANGUAGES = \[\K(.*)\]" $BASEPATH/../../default_settings.py | cut -d ']' -f 1 | tr -d \'\" | tr -d ' ')
IFS=',';
for lang in $LANGS; 
do
  if [[ "$lang" == 'en' ]]; then
      continue  # No separate translation files for default locale
  fi

  lang_hyphen=${lang/_/-}
  if wget -nv -O ${BASEPATH}/i18n/datatables.${lang}.json https://raw.githubusercontent.com/DataTables/Plugins/master/i18n/${lang_hyphen}.json; then
    echo "Successfully downloaded DataTables language translations for ${lang}."
  else
    echo "ERROR: Failed to download DataTables language translations for ${lang}."
  fi
done
