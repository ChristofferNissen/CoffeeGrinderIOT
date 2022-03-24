IP=$1
curl -X POST -H "Content-Type: application/json" -H "" -d '{"type":"A","name":"@","data":"'$IP'","priority":null,"port":null,"ttl":3600,"weight":null,"flags":null,"tag":null}' "https://api.digitalocean.com/v2/domains/iotcoffee.online/records"
