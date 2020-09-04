curl -X POST -H 'Content-Type: application/json' \
     -H 'Authorization: Bearer '8ffbdbbea4f55db712d1bda1e927b8f238a1bda4008cb4197149f8ca1f05ffb1'' -d \
    '{"name":"coffeeserver","region":"fra1","size":"1gb","image":"docker-18-04", "ssh_key_name": [26836309]}' \
    "https://api.digitalocean.com/v2/droplets"