# HWOJ Judge
Judge worker receives and judges submission from backend (HWOJ-example-packages) using `isolate` sandbox.

## Problem folder sync
- Same host: just volume into it.
- Remote server judge: (idk)

## By supervisord

## By Docker
Build
```bash
docker build -t hwoj-judge ./judge
```

- `--privileged` permission for sandbox/cgroup
- `--network="host"` connect to vps network
Run
```bash
docker run --rm \
  --privileged \
  --name <ga> \
  --network="host" \
  -v <file_problems_dir>:/app/problems:ro \
  -d \
  HWoj-judge \
  --name <ga>
  --server_url <url> \
  --poll_interval <seconds>
```

