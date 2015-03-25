#!/bin/bash
set -x
docker run --link harbour_elasticsearch_1:es -v `pwd`:/tmp -t sherzberg/elasticdump \
    --input=/tmp/kibana-exported.json \
    --output=http://es:9200/.kibana \
    --type=data