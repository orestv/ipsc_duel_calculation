

build: build_frontend build_backend

.PHONY: build_backend
build_backend:
	mkdir -p dist
	docker build --platform linux/amd64 -f backend/Dockerfile -t duels_backend:latest backend
	docker tag duels_backend europe-central2-docker.pkg.dev/duelscalculator/duels-all/backend:latest
	docker push europe-central2-docker.pkg.dev/duelscalculator/duels-all/backend:latest
	#docker save duels_backend:latest | xz > dist/backend.tar.xz


.PHONY: build_frontend
build_frontend:
	mkdir -p dist
	cd ui && npm run build
	cd ui/dist && tar -cJf ../../dist/ui.tar.xz .

.PHONY: deploy
deploy: build
	ansible-playbook -i ops/inventory.yml ops/playbook.yml
