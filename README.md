# minimal-footprint

## Deployment
- ```Add public key to server```
- ```pip install ansible```
- ```ansible-playbook -i ansible_inventory.yml -u {username} -k ansible_playbook.yml --ask-become-pass```

## HTTPS / SSL
- ```sudo apt-get install certbot```
- ```sudo certbot certonly --manual --preferred-challenges dns```