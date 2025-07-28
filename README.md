# 在 Kubernetes 上部署 PostgreSQL 及 Python Web 應用程式

本專案旨在示範如何在 Kubernetes 叢集中部署一個具備持久化儲存的 PostgreSQL 資料庫，並建立一個簡單的 Python Flask Web 應用程式來與之互動。

整個過程涵蓋了建立設定檔、容器化應用程式、部署到 Kubernetes，以及驗證資料持久性的完整流程。

## 專案結構

```
.
├── app.py                   # Python Flask 應用程式原始碼
├── Dockerfile               # 用於建立 Web 應用程式映像檔的 Dockerfile
├── postgres-deployment.yaml # PostgreSQL 的 Deployment 設定
├── postgres-pvc.yaml        # PostgreSQL 的 PersistentVolumeClaim (PVC) 設定
├── postgres-service.yaml    # PostgreSQL 的 Service 設定
├── README.md                # 本說明檔案
├── requirements.txt         # Python 應用程式的依賴套件
├── web-app-deployment.yaml  # Web 應用程式的 Deployment 設定
└── web-app-service.yaml     # Web 應用程式的 Service 設定
```

## 部署步驟

### 1. 部署 PostgreSQL

首先，部署 PostgreSQL 資料庫。這會建立一個 PVC 來儲存資料、一個 Deployment 來運行 Pod，以及一個 Service 來讓叢集內部可以連線。

```bash
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml
```

### 2. 建置 Web 應用程式的 Docker 映像檔

在部署 Web 應用程式之前，需要先在本機使用 Docker 建置它的映像檔。`web-app-deployment.yaml` 已設定為使用本地映像檔 (`imagePullPolicy: Never`)。

```bash
docker build -t python-web-app:latest .
```

### 3. 部署 Web 應用程式

現在，部署 Web 應用程式。這會建立一個 Deployment 來運行應用程式 Pod，以及一個 `NodePort` 類型的 Service 來從外部存取它。

```bash
kubectl apply -f web-app-deployment.yaml
kubectl apply -f web-app-service.yaml
```

## 如何存取應用程式

1.  首先，取得 `web-app-service` 分配到的 `NodePort`。

    ```bash
    kubectl get service web-app-service
    ```

2.  在輸出中找到類似 `80:3XXXX/TCP` 的埠號對應。`3XXXX` 就是您可以使用的埠號。

3.  打開瀏覽器，訪問 `http://<您的節點IP>:<NodePort>` (如果使用 Docker Desktop 或 Minikube，節點 IP 通常是 `localhost`)。

## 驗證資料持久性 (PVC 測試)

這個測試旨在證明即使 Pod 被銷毀重建，資料仍然會因為 PVC 的存在而保留下來。

1.  **取得目前 Pod 名稱**
    ```bash
    kubectl get pods -l app=postgres
    ```

2.  **刪除 Pod** (將 `<pod-name>` 替換為上一步取得的名稱)
    ```bash
    kubectl delete pod <pod-name>
    ```

3.  **等待新 Pod 啟動**
    Kubernetes 會自動建立一個新的 Pod。使用 `kubectl get pods -l app=postgres` 確認新 Pod 進入 `Running` 狀態。

4.  **驗證資料**
    多次訪問 Web 應用程式，或使用以下指令進入新 Pod 查詢資料筆數，會發現資料依然存在。
    ```bash
    # 取得新 Pod 的名稱
    NEW_POD_NAME=$(kubectl get pods -l app=postgres -o jsonpath="{.items[0].metadata.name}")

    # 查詢資料筆數
    kubectl exec -it $NEW_POD_NAME -- psql -U postgres -d postgres -c "SELECT COUNT(*) FROM visits;"
    ```

## 實用指令

*   **查看所有 Pod 狀態**:
    ```bash
    kubectl get pods -o wide
    ```

*   **查看特定 Pod 的日誌** (用於排查應用程式錯誤):
    ```bash
    kubectl logs <pod-name>
    ```

*   **進入 Pod 內部的互動式 Shell**:
    ```bash
    kubectl exec -it <pod-name> -- /bin/bash
    ```

*   **進入 PostgreSQL 資料庫**:
    ```bash
    # 取得 Pod 名稱
    PG_POD_NAME=$(kubectl get pods -l app=postgres -o jsonpath="{.items[0].metadata.name}")
    
    # 執行 psql
    kubectl exec -it $PG_POD_NAME -- psql -U postgres -d postgres
    ```
    進入後，可使用 `\dt` (顯示資料表) 或 `SELECT * FROM visits;` (查詢資料) 等指令。
