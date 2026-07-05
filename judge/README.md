# EPenguinOJ Judge

Judge worker lấy submission đang `Pending` từ backend, chấm bằng testcase trong thư mục problem, rồi gửi kết quả về backend.

## Config

Copy `config.example.yml` thành `config.yml`:

```yml
name: local-judge
key: change-me
server_url: http://127.0.0.1:8000
problems_dir: ./problems
work_dir: ./tmp
poll_interval: 3
box_id: 0
```

Backend cũng cần đặt cùng key qua biến môi trường `JUDGE_KEY`.

## Problem folder

Mỗi bài nằm trong `problems_dir/<problem_id>/problem.yml`. Test có thể khai báo theo example package:

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

## Chạy judge

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python judge.py --config config.yml
```

Chạy một vòng để debug:

```bash
python judge.py --config config.yml --once
```

## Judge API trên backend

- `POST /api/judge/get-task`: Judge gửi `name` và `key` để nhận một submission `Pending`. Backend đổi trạng thái thành `Judging`.
- `POST /api/judge/update-result`: Judge gửi kết quả sau khi chấm xong. Backend lưu verdict, score, time, memory và raw result.
