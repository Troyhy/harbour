#!/bin/bash

docker run  --link harbour_elasticsearch_1:es  -t sherzberg/elasticdump \
    --input=http://es:9200/.kibana \
    --output=$ \
    --type=data \
    --searchBody='{"filter": { "or": [ {"type": {"value": "search"}}, {"type": {"value": "dashboard"}}, {"type" : {"value":"visualization"}}] }}' \
    > kibana-exported.json