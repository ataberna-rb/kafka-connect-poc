################################# ---- VARIABLES ---- #################################

CONNECT_URL="http://localhost:8088"

################################# ---- FUNCIONES ---- #################################

delete_connector(){
    connector_name="$1"
    curl -X DELETE $CONNECT_URL/connectors/$connector_name
}

infer_connector_name(){
    connector_file="$1"

    connector_name=$(cat $connector_file | jq .name)
    connector_name=$(echo $connector_name | sed -r "s#\"##g")
    connector_name=$(echo $connector_name | sed -r "s#\"##g")

    echo $connector_name
}

create_connector(){
    connector_file="$1"

    connector_name=$(infer_connector_name $connector_file)

    delete_connector $connector_name

    curl -s -X POST -H 'Content-Type: application/json' --data @$connector_file $CONNECT_URL/connectors
}

################################# ---- EJECUCION ---- #################################

create_connector redis-sink-config.json
create_connector mysql-sink-config.json
