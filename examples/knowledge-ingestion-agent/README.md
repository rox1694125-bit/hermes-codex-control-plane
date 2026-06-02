# Knowledge Ingestion Agent Example

This example shows the Hermes-Codex 3+3 standard on a local-only knowledge ingestion workflow.

Run the demo:

```bash
python3 examples/knowledge-ingestion-agent/scripts/run_demo.py --json
```

The demo reads `fixtures/sample-article.txt` and writes generated artifacts under `demo-output/`:

- `notes/local-knowledge-ingestion-smoke-test.md`
- `raw/408958dbf08d.txt`
- `index.json`
- `reports/latest-run.json`

The script uses only the Python standard library. It does not fetch URLs, call external APIs, send messages, edit credentials, or start the Hermes gateway.

For tests:

```bash
python3 tests/test_runnable_demo.py
```
