#!/bin/bash
for type in `curl 'localhost:5601/api/saved_objects/_find?search_fields=title^3&search_fields=description&per_page=999`| jq -r .saved_objects[].type|sort -u`; do
    echo $type
    curl "localhost:5601/api/saved_objects/find?type=$type&title^3&search_fields=description&per_page=999" | jq . > $type.json
done
