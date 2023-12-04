minikube start --cpus=4
kubectl apply -f monitoring/prometheus-operator/namespace.yaml
kubectl create -f monitoring/prometheus-operator/crds 
kubectl apply -f monitoring/prometheus-operator/rbac
kubectl apply -f monitoring/prometheus-operator/deployment
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled
kubectl apply -f monitoring/prometheus/
kubectl apply -f monitoring/grafana.yaml
kubectl apply -f monitoring/cadvisor/
kubectl apply -f monitoring/istio-monitors.yaml
kubectl apply -f httpbin/httpbin.yaml
kubectl apply -f httpbin/httpbin-gateway.yaml
kubectl apply -f httpbin/sample-client/fortio-deploy.yaml
# kubectl create namespace monitoring
# helm install prom-operator prometheus-community/kube-prometheus-stack --namespace monitoring