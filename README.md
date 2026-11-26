# Môi trường Neo4j và PostgreSQL cho đồ án Hệ quản trị cơ sở dữ liệu

## 1. Giới thiệu

Repository này dùng để tái lập môi trường triển khai Neo4j và PostgreSQL cho đồ án phát hiện gian lận giao dịch. Hai cấu hình demo phục vụ cài đặt và kết nối. Cấu hình benchmark cung cấp giới hạn tài nguyên có thể điều chỉnh và hai script kiểm tra kết nối Python. Việc đo hiệu năng cần được thực hiện trong một đợt benchmark riêng.

| Thư mục | Image | Container | Cổng trên máy chạy Docker | Giới hạn CPU | Giới hạn RAM |
| --- | --- | --- | --- | --- | --- |
| `demo/` | `neo4j:5.26.34-community` | `hqt-neo4j-demo` | `127.0.0.1:7474` (HTTP), `127.0.0.1:7687` (Bolt) | 2 CPU logic | 2 GiB |
| `postgres-demo/` | `postgres:17.12` | `hqt-postgres-demo` | `127.0.0.1:5432` | 2 CPU logic | 2 GiB |
| `benchmark/`, profile `neo4j` | `neo4j:5.26.34-community` | `hqt-neo4j-benchmark` | `127.0.0.1:7475` (HTTP), `127.0.0.1:7688` (Bolt) | 2 CPU logic mặc định | 2 GiB mặc định |
| `benchmark/`, profile `postgres` | `postgres:17.12` | `hqt-postgres-benchmark` | `127.0.0.1:5433` | 2 CPU logic mặc định | 2 GiB mặc định |

Hai service demo đều giới hạn năng lực xử lý tương đương 2 CPU logic và 2 GiB RAM mỗi container. Đây là hạn mức CPU, không phải cấp riêng hai lõi vật lý. Các container dùng named volume cho dữ liệu. Neo4j có thêm named volume cho `/logs`.

## 2. Yêu cầu và chuẩn bị

- **Windows** dùng Docker Desktop với WSL 2 và Linux containers. Có thể chạy các lệnh dưới đây trong PowerShell.
- **Linux** dùng Docker Engine và Docker Compose plugin. Có thể chạy các lệnh dưới đây trong Bash.
- **Python 3.12** cùng `venv` và `pip` để chạy các script kiểm tra. Trên một số bản phân phối Linux, cần cài thêm gói `venv` tương ứng. Hai môi trường demo chỉ cần Docker. [Tài liệu venv của Python 3.12](https://docs.python.org/3.12/library/venv.html)
- **Git** để clone repository. Tài khoản GitHub cần quyền đọc vì repository ở chế độ private.

```text
docker version
docker compose version
git --version
git clone https://github.com/HaiLong2152/neo4j-postgresql-benchmark.git
cd neo4j-postgresql-benchmark
```

Nếu đã triển khai đồ án gốc trên máy, hãy kiểm tra Docker context, container và volume trước khi khởi động bản sao. Cùng một Docker daemon sẽ nhận diện các tài nguyên Compose theo tên. Repository này giữ nguyên tên project, container và volume của đồ án gốc. Dùng một Docker daemon riêng nếu cần triển khai bản sao độc lập với bản gốc và chạy các lệnh kết nối trên máy đang giữ cổng localhost.

```text
docker context show
docker ps -a --format "table {{.Names}}\t{{.Ports}}"
docker volume ls
```

Mỗi thư mục Compose có mẫu `.env.example`. Tạo `.env` trong đúng thư mục, nhập mật khẩu bằng trình soạn thảo và lưu UTF-8. Neo4j yêu cầu mật khẩu ban đầu tối thiểu 8 ký tự theo mặc định. Trong mẫu `.env`, dùng dấu nháy đơn để các ký tự như `$` được giữ nguyên. Giữ `.env` trên máy chạy Docker. Dùng `config --quiet` khi kiểm tra cấu hình để tránh in các giá trị đã nội suy. [Docker Compose config](https://docs.docker.com/reference/cli/docker/compose/config/), [Cú pháp tệp .env của Compose](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/), [Cấu hình xác thực Neo4j trong Docker](https://neo4j.com/docs/operations-manual/current/docker/introduction/)

## 3. Neo4j demo

1. Từ thư mục gốc, vào `demo/` và tạo `.env`.

   **Windows PowerShell**

   ```powershell
   cd demo
   Copy-Item .env.example .env
   ```

   **Linux Bash**

   ```bash
   cd demo
   cp .env.example .env
   ```

2. Thay giá trị minh họa của `NEO4J_PASSWORD` bằng mật khẩu tự đặt. Heap khởi tạo là 256 MiB, heap tối đa 512 MiB và page cache 256 MiB. Docker quản lý các volume tại `/data` và `/logs`.
3. Kiểm tra cấu hình, tải image và khởi động từ thư mục `demo/`.

   ```text
   docker compose config --quiet
   docker compose pull neo4j
   docker compose up -d neo4j
   docker compose ps
   docker compose logs --tail 30 neo4j
   ```

4. Mở Neo4j Browser tại `http://127.0.0.1:7474/`. Khi được hỏi, dùng địa chỉ `bolt://127.0.0.1:7687`, người dùng `neo4j`, mật khẩu đã đặt và database `neo4j`.
5. Để kết nối bằng Cypher Shell, chạy lệnh sau và nhập mật khẩu khi được hỏi. Thoát bằng `:exit`. Khi cần dừng môi trường, chạy `docker compose stop neo4j` trong thư mục `demo/`. [Hướng dẫn Neo4j trong Docker](https://neo4j.com/docs/operations-manual/current/docker/introduction/)

   ```text
   docker compose exec neo4j cypher-shell -a bolt://127.0.0.1:7687 -u neo4j -d neo4j
   ```

## 4. PostgreSQL demo

1. Từ thư mục gốc, vào `postgres-demo/` và tạo `.env`.

   **Windows PowerShell**

   ```powershell
   cd postgres-demo
   Copy-Item .env.example .env
   ```

   **Linux Bash**

   ```bash
   cd postgres-demo
   cp .env.example .env
   ```

2. Điền `POSTGRES_DEMO_PASSWORD` trong `.env`. Image khởi tạo người dùng `postgres` và database `fraud_demo` trên volume mới gắn tại `/var/lib/postgresql/data`.

   | Tham số | Giá trị demo |
   | --- | --- |
   | `shared_buffers` | `256MB` |
   | `work_mem` | `4MB` |
   | `maintenance_work_mem` | `64MB` |
   | `max_connections` | `100` |

3. Kiểm tra cấu hình, khởi động và kiểm tra PostgreSQL đã sẵn sàng nhận kết nối.

   ```text
   docker compose config --quiet
   docker compose pull postgres
   docker compose up -d postgres
   docker compose ps
   docker compose exec postgres pg_isready -h 127.0.0.1 -p 5432 -U postgres -d fraud_demo
   ```

4. Kết nối bằng `psql` trong container và nhập mật khẩu khi được hỏi. Có thể bỏ phần `docker compose exec postgres` nếu đã cài `psql` trên máy. Thoát bằng `\q`. [Tài liệu psql 17](https://www.postgresql.org/docs/17/app-psql.html)

   ```text
   docker compose exec postgres psql -X -h 127.0.0.1 -p 5432 -U postgres -d fraud_demo -W
   ```

5. Với **pgAdmin 4 bản Desktop**, mở **Servers → Register → Server**. Đặt tên hiển thị ở tab **General**, sau đó nhập các thông số trong tab **Connection**. Khi cần dừng PostgreSQL, chạy `docker compose stop postgres` trong thư mục `postgres-demo/`. [Tài liệu đăng ký server của pgAdmin](https://www.pgadmin.org/docs/pgadmin4/latest/server_dialog.html)

   | Trường | Giá trị |
   | --- | --- |
   | Host name/address | `127.0.0.1` |
   | Port | `5432` |
   | Maintenance database | `fraud_demo` |
   | Username | `postgres` |
   | Password | Giá trị `POSTGRES_DEMO_PASSWORD` trong `.env` |
   | Save password | Tắt nếu chỉ dùng để kiểm tra kết nối |

## 5. Môi trường benchmark

1. Từ thư mục gốc, vào `benchmark/`, tạo `.env` và môi trường ảo. Các lệnh gọi trực tiếp Python trong `.venv` nên không cần kích hoạt môi trường ảo.

   **Windows PowerShell**

   ```powershell
   cd benchmark
   Copy-Item .env.example .env
   py -0p
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m pip check
   ```

   **Linux Bash**

   ```bash
   cd benchmark
   cp .env.example .env
   python3.12 --version
   python3.12 -m venv .venv
   ./.venv/bin/python -m pip install -r requirements.txt
   ./.venv/bin/python -m pip check
   ```

2. Điền cả `BENCHMARK_NEO4J_PASSWORD` và `BENCHMARK_POSTGRES_PASSWORD` trong `.env`. Compose nội suy biến ở cả hai service, kể cả khi lệnh chỉ bật một profile. Hai script dùng các phiên bản đã cố định trong [requirements.txt](benchmark/requirements.txt).

   | Gói Python | Phiên bản |
   | --- | --- |
   | `neo4j` | `6.4.1` |
   | `psycopg[binary]` | `3.3.9` |
   | `python-dotenv` | `1.2.4` |

3. Chọn thông số phù hợp với máy. Các giá trị dưới đây dùng để tái lập cấu hình kiểm tra ban đầu. Hãy ghi lại giá trị thực tế trước khi đo hiệu năng.

   | Cấu hình | Neo4j | PostgreSQL |
   | --- | --- | --- |
   | Giới hạn CPU | `BENCHMARK_NEO4J_CPUS=2.0` | `BENCHMARK_POSTGRES_CPUS=2.0` |
   | Giới hạn RAM | `BENCHMARK_NEO4J_MEMORY_LIMIT=2g` | `BENCHMARK_POSTGRES_MEMORY_LIMIT=2g` |
   | Cổng host | HTTP `7475`, Bolt `7688` | `5433` |
   | Bộ nhớ DBMS | Heap initial, heap max và page cache đều `512m` | `shared_buffers=256MB`, `work_mem=4MB`, `maintenance_work_mem=64MB` |
   | Database và người dùng | `neo4j` / `neo4j` | `fraud_benchmark` / `postgres` |

   Xem [benchmark/.env.example](benchmark/.env.example) để biết tên biến điều chỉnh cổng và bộ nhớ DBMS. Khởi động một hệ quản trị mỗi lần nếu ngân sách bộ nhớ của Docker hạn chế.

4. Trong `benchmark/`, chọn một trong hai khối lệnh dưới đây. Khi chuyển hệ quản trị, có thể dừng profile đang dùng bằng `docker compose --profile neo4j stop neo4j` hoặc `docker compose --profile postgres stop postgres`. [Tài liệu Docker Compose profiles](https://docs.docker.com/compose/how-tos/profiles/)

   **Neo4j**

   ```text
   docker compose --profile neo4j config --quiet
   docker compose --profile neo4j pull neo4j
   docker compose --profile neo4j up -d neo4j
   docker compose --profile neo4j ps
   ```

   **PostgreSQL**

   ```text
   docker compose --profile postgres config --quiet
   docker compose --profile postgres pull postgres
   docker compose --profile postgres up -d postgres
   docker compose --profile postgres ps
   ```

## 6. Kiểm tra kết nối Python và giới hạn tài nguyên

Chạy script tương ứng trong `benchmark/` sau khi DBMS sẵn sàng. Script đọc cấu hình kết nối từ `benchmark/.env` và các biến môi trường của tiến trình. Kết quả kỳ vọng gồm phiên bản Python, phiên bản driver, kết quả truy vấn bằng `1`, phiên bản server khớp với image và trạng thái kết nối thành công. Exit code khác 0 báo lỗi. Đây là kiểm tra kết nối và phiên bản.

**Windows PowerShell**

```powershell
.\.venv\Scripts\python.exe scripts/check_neo4j.py
.\.venv\Scripts\python.exe scripts/check_postgres.py
```

**Linux Bash**

```bash
./.venv/bin/python scripts/check_neo4j.py
./.venv/bin/python scripts/check_postgres.py
```

Dùng lệnh tương ứng với container đã tạo. Các trường được chọn chỉ hiển thị giới hạn tài nguyên. `Memory` là số byte. `NanoCpus` là số CPU logic nhân với một tỷ.

```text
docker inspect --format '{{.Name}} CPU={{.HostConfig.NanoCpus}} RAM={{.HostConfig.Memory}}' hqt-neo4j-demo
docker inspect --format '{{.Name}} CPU={{.HostConfig.NanoCpus}} RAM={{.HostConfig.Memory}}' hqt-postgres-demo
docker inspect --format '{{.Name}} CPU={{.HostConfig.NanoCpus}} RAM={{.HostConfig.Memory}}' hqt-neo4j-benchmark
docker inspect --format '{{.Name}} CPU={{.HostConfig.NanoCpus}} RAM={{.HostConfig.Memory}}' hqt-postgres-benchmark
```

Với cấu hình trong repository, cả hai service demo có `CPU=2000000000` và `RAM=2147483648`. Hai service benchmark mặc định có cùng giới hạn; nếu thay đổi `.env`, đối chiếu với giá trị thực tế đã chọn. Số liệu sử dụng tức thời không phải kết quả benchmark. Có thể xem mức sử dụng tại thời điểm kiểm tra bằng `docker stats --no-stream hqt-neo4j-benchmark` hoặc lệnh tương tự với tên container PostgreSQL.

## 7. Xung đột cổng và lỗi thường gặp

| Triệu chứng | Cách kiểm tra và xử lý |
| --- | --- |
| Cổng host đã được sử dụng | Liệt kê cổng đang lắng nghe bằng lệnh bên dưới và đối chiếu với `docker ps`. Với benchmark có thể đổi cổng trong `.env` và dùng cổng mới ở client. Nếu cần giữ đúng cổng demo, chọn máy có cổng tương ứng còn trống. |
| Container cùng tên hoặc volume trùng tên | Đối chiếu `docker context show`, `docker ps -a` và `docker volume ls`. Chọn Docker daemon riêng cho bản sao, giữ nguyên tài nguyên của đồ án gốc. |
| Compose báo thiếu biến | Kiểm tra thư mục lệnh và tên tệp `.env`, nhất là phần mở rộng ẩn trên Windows. Điền cả hai mật khẩu cho cấu hình benchmark. |
| Docker daemon chưa sẵn sàng | Mở Docker Desktop hoặc kiểm tra dịch vụ Docker trên Linux, rồi chạy lại `docker version`. |
| Kết nối bị từ chối hoặc bị ngắt | Kiểm tra `docker compose ps` và `docker compose logs --tail 30 <service>` với `neo4j` hoặc `postgres`. Đợi server hoàn tất khởi tạo, kiểm tra địa chỉ và cổng, rồi kết nối lại. |
| Xác thực thất bại sau khi đổi `.env` | Mật khẩu khởi tạo chỉ áp dụng với volume mới. Với volume đã được khởi tạo, dùng mật khẩu hiện hành hoặc quy trình đổi mật khẩu của DBMS. |
| Python thiếu driver hoặc kiểm tra sai phiên bản server | Chạy `pip check` bằng Python trong `.venv`. Xác minh cổng benchmark, biến môi trường đang ghi đè và image của container bằng `docker compose --profile <profile> images`. |

**Windows PowerShell**

```powershell
Get-NetTCPConnection -State Listen -LocalPort 7474,7687,5432,7475,7688,5433 -ErrorAction SilentlyContinue
```

**Linux Bash**

```bash
ss -ltn
```
