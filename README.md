# minimal-footprint

## Deployment
- ```Add public key to server```
- ```pip install ansible```
- ```ansible-playbook -i ansible_inventory.yml -u {username} -k ansible_playbook.yml --ask-become-pass```

## HTTPS / SSL
- ```sudo apt-get install certbot```
- ```sudo certbot certonly --manual --preferred-challenges dns```

## Build / push Docker containers

### Backend
- ```cd backend```
- ```docker build --tag registry.fovodohovi.nl/minimal-footprint:backend-latest .```
- ```docker push registry.fovodohovi.nl/minimal-footprint:backend-latest```

### Frontend
- ```cd frontend```
- ```npm run build```
- ```docker build --tag registry.fovodohovi.nl/minimal-footprint:frontend-latest .```
- ```docker push registry.fovodohovi.nl/minimal-footprint:frontend-latest```

## Technologies used
- Ansible
- Kubernetes
- Docker
- OAuth2 (Authorization Code Grant)
- Container Registry (self-hosted)
- Python
- nginx (as reverse proxy)
- PostgreSQL
- ETL
- DNS