#!/bin/bash
set -e  # Optional: stop on first error


exec > /var/log/user-data.log 2>&1
set -xe

# Get DC info from instance metadata tag (example)
DC_NAME=$(curl -s http://169.254.169.254/latest/meta-data/tags/instance/Name)



run_container() {
  local service=$1
  local dockerfile=$2
  local port=$3
  local volume=$4
  local container_name=$5

  docker build -f "$dockerfile" -t "$service" .
  docker run -d --rm \
    --name "$container_name" \
    -p "$port" \
    -v "$volume" \
    "$service"
}

case $DC_NAME in

  "DC1")
    # Gateway-Nginx
    run_container "gateway-nginx" "dockerfiles/Dockerfile.gateway-nginx" "80:80" "./Configs/nginx/:/usr/share/nginx/html" "gateway-nginx"

    # User-Nginx
    run_container "user-nginx" "dockerfiles/Dockerfile.user-nginx" "8080:8080" "./data/service-responses/user-nginx/:/usr/share/nginx/html" "user-nginx"

    # Order-Nginx
    run_container "order-nginx" "dockerfiles/Dockerfile.order-nginx" "8082:8082" "./data/service-responses/order-nginx/:/usr/share/nginx/html" "order-nginx"

    # Catalog-Nginx
    run_container "catalog-nginx" "dockerfiles/Dockerfile.catalog-nginx" "8081:8081" "./data/service-responses/catalog-nginx/:/usr/share/nginx/html" "catalog-nginx"
    ;;

  "DC2")
    # Gateway-Nginx (backup)
    run_container "gateway-nginx-backup" "dockerfiles/Dockerfile.gateway-nginx" "80:80" "./Configs/nginx/:/usr/share/nginx/html" "gateway-nginx-backup"

    # Payment-Nginx
    run_container "payment-nginx" "dockerfiles/Dockerfile.payment-nginx" "8083:8083" "./data/service-responses/payment-nginx/:/usr/share/nginx/html" "payment-nginx"

    # Notify-Nginx
    run_container "notify-nginx" "dockerfiles/Dockerfile.notify-nginx" "8084:8084" "./data/service-responses/notify-nginx/:/usr/share/nginx/html" "notify-nginx"

    # Order-Nginx (replica)
    run_container "order-nginx-replica" "dockerfiles/Dockerfile.order-nginx" "8082:8082" "./data/service-responses/order-nginx/:/usr/share/nginx/html" "order-nginx-replica"
    ;;

  "DC3")
    # All services (standby)
    for svc in gateway user order catalog payment notify analytics discovery; do
      run_container "$svc-standby" "dockerfiles/Dockerfile.$svc-nginx" "8500:8500" "./data/service-responses/$svc-nginx/:/usr/share/nginx/html" "$svc-standby"
    done

    # Discovery-Nginx explicitly
    run_container "discovery-nginx" "dockerfiles/Dockerfile.discovery-nginx" "8500:8500" "./data/service-responses/discovery-nginx/:/usr/share/nginx/html" "discovery-nginx"
    ;;

  *)
    echo "Unknown DataCenter: $DC_NAME"
    exit 1
    ;;
esac
