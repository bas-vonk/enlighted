# enlighted

## Deployment
- ```Add public key to server```
- ```pip install ansible```
- ```ansible-playbook -i ansible_inventory.yml -u {username} -k ansible_playbook.yml --ask-become-pass```

## HTTPS / SSL

### Relevant URLs
- registry.fovodohovi.nl (services1)
- pgadmin.fovodohovi.nl (services)
- redisinsight.fovodohovi.nl (services1)
- homeassistant.fovodohovi.nl (public IP)

### Commands (then follow on-screen instructions)
- ```sudo apt-get install certbot```
- ```sudo certbot certonly --manual --preferred-challenges dns```

## Build / push Docker containers

### Backend
- ```cd backend```
- ```docker build --tag registry.fovodohovi.nl/enlighted-backend:latest .```
- ```docker push registry.fovodohovi.nl/enlighted-backend:latest```

### Frontend
- ```cd frontend```
- ```npm run build```
- ```docker build --tag registry.fovodohovi.nl/enlighted-frontend:latest .```
- ```docker push registry.fovodohovi.nl/enlighted-frontend:latest```

## Technologies used
- Ansible
- Kubernetes
- Docker
- OAuth2 (Client Credentials Grant)
- Container Registry (self-hosted)
- Python
- nginx (as reverse proxy)
- PostgreSQL
- ETL
- DNS
- HTML / CSS / Javascript (VueJS)