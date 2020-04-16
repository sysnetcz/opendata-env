#!/bin/bash
echo "Upload OpenData to CKAN"


API_KEY="0753e953-a26a-4c1a-8805-84b12f655ebf"
AUTHORIZATION="Authorization: "$API_KEY
END_POINT="https://opendata.mzp.cz/api/3/action/resource_update"
LICENSE="license_link=https://portal.gov.cz/portal/ostatni/volny-pristup-k-ds.html"
FAKURA="describedBy=https://opendata.mzp.cz/schema/schema_faktura.json"
OBJEDNAVKA="describedBy=https://opendata.mzp.cz/schema/schema_objednavka.json"
SMLOUVA="describedBy=https://opendata.mzp.cz/schema/schema_smlouva.json"
JSON="describedByType=application/json"

echo "$AUTHORIZATION"


# MZP
# faktury 2019:
curl -H $AUTHORIZATION $END_POINT -F "id=8221caa9-3df6-4c09-880b-3b18386c330a" -F $LICENSE -F $FAKURA -F $JSON -F "upload=@/cesta_k_datove_sade/datova_sada.csv"

# objednavky 2019:
curl -H $AUTHORIZATION $END_POINT -F "id=5dab30ac-dba4-4c8c-b9b9-da394133bdad" -F $LICENSE -F $OBJEDNAVKA -F $JSON -F "upload=@/cesta_k_datove_sade/datova_sada.csv"

# faktury 2020:
curl -H $AUTHORIZATION $END_POINT -F "id=233ff4c8-2baa-4670-bcc1-ae9a105d3c2e" -F $LICENSE -F $FAKURA -F $JSON -F "upload=@/cesta_k_datove_sade/datova_sada.csv"

# objednavky 2020:
curl -H $AUTHORIZATION $END_POINT -F "id=349f2667-e690-4680-8a2d-dd3fff9ba08e" -F $LICENSE -F $OBJEDNAVKA -F $JSON -F "upload=@/cesta_k_datove_sade/datova_sada.csv"



