# EPenguinOJ Judge
Judge worker receives and judges submission from backend (EpenguinOJ-example-packages) using `isolate` sandbox.

## Config
```yml
name: local-judge
key: change-me
```

## Problem folder sync
- Same host: just volume into it.
- Remote server judge: (idk)

## By Docker
Build
```bash
docker build -t epenguinoj-judge ./judge
```

- `--privileged` permission for sandbox/cgroup
- `--network="host"` connect to vps network
Run
```bash
docker run --rm \
  --privileged \
  --name <ga> \
  --network="host" \
  -v <file_problems_dir>:/app/problems \
  -v <file_config_yml>:/app/config.yml:ro \
  -d \
  epenguinoj-judge \
  --key <key>
  --server_url <url> \
  --poll_interval <seconds>
```

