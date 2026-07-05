# EPenguinOJ Judge

Judge worker lấy submission từ backend, chấm với testcase trong thư mục problem chung `/data/problems`, chạy chương trình thí sinh trong `isolate` sandbox bên trong Docker, rồi gửi kết quả về backend.

## Config

Copy `config.example.yml` thành `config.yml`:

```yml
name: local-judge
key: change-me
server_url: http://127.0.0.1:8000
problems_dir: /data/problems
work_dir: ./tmp
poll_interval: 3
box_id: 0
use_cgroups: true
compile_time_limit: 20
wall_time_extra: 1.0
```

`problems_dir` mặc định là `/data/problems`. Backend cũng tạo/đọc problem package ở `/data/problems` (có thể override bằng biến môi trường `PROBLEMS_DIR`).

## Problem folder

Mỗi bài nằm trong `/data/problems/<problem_id>/problem.yml`. Test có thể khai báo theo example package:

```yml
id: apio24_a
name: Sequence
time_limit: 2000
memory_limit: 512
testcases:
  - tests/1.in tests/1.out
  - tests/2.in tests/2.out
```

Nếu không khai báo `testcases`, judge sẽ tự lấy các cặp `tests/*.in` và `tests/*.out` cùng tên.

## Chạy judge bằng Docker

`isolate` cần quyền tạo sandbox/cgroup, vì vậy container judge nên chạy privileged và mount thư mục problem chung:

```bash
docker build -t epenguinoj-judge ./judge
docker run --rm --privileged \
  -v /data/problems:/data/problems \
  -v "$(pwd)/judge/config.yml:/app/config.yml:ro" \
  epenguinoj-judge
```

Chạy một vòng để debug:

```bash
docker run --rm --privileged \
  -v /data/problems:/data/problems \
  -v "$(pwd)/judge/config.yml:/app/config.yml:ro" \
  epenguinoj-judge python judge.py --config config.yml --once
```

## Judge API trên backend

- `POST /api/judge/get-task`: Judge gửi `name` và `key` để nhận một submission `Pending`. Backend đổi trạng thái thành `Judging`.
- `POST /api/judge/update-result`: Judge gửi kết quả sau khi chấm xong. Backend lưu verdict, score, time, memory và raw result.
