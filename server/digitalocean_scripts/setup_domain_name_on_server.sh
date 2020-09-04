IP=$1
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer 8ffbdbbea4f55db712d1bda1e927b8f238a1bda4008cb4197149f8ca1f05ffb1" -d '{"type":"A","name":"@","data":"'$IP'","priority":null,"port":null,"ttl":3600,"weight":null,"flags":null,"tag":null}' "https://api.digitalocean.com/v2/domains/iotcoffee.online/records"
