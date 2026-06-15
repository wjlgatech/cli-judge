"""Template adapter. Copy to adapters/<tool>_adapter.py and implement invoke()."""
from __future__ import annotations
import subprocess, time, os
from atb.adapter import Adapter, Call, Result

class MyAdapter:
    name = "my-tool"
    def invoke(self, call: Call) -> Result:
        env = dict(os.environ); env.update(call.env)
        if call.replay_base_url:
            env["BASE_URL"] = call.replay_base_url  # route to replay server
        t0 = time.time()
        proc = subprocess.run(["my-tool", *call.argv], input=call.stdin,
                              capture_output=True, text=True, env=env)
        return Result(exit_code=proc.returncode, stdout=proc.stdout,
                      stderr=proc.stderr, duration_ms=(time.time()-t0)*1000)

ADAPTER: Adapter = MyAdapter()
