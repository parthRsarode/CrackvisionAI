---
phase: "03"
slug: "yolov8-segmentation-pipeline-integration"
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-09-28"
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio |
| **Config file** | `backend/pytest.ini` (Wave 0 creates) |
| **Quick run command** | `pytest backend/tests/test_api.py -v` |
| **Full suite command** | `pytest backend/tests/ -v --junitxml=test-reports/results.xml` |
| **Estimated runtime** | ~8 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest backend/tests/test_api.py -v`
- **After every plan wave:** Run `pytest backend/tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---|---|---|---|---|---|---|---|---|---|
| 03-01-01 | 01 | 0 | REQ-2.1 | — | N/A | setup | `pytest backend/tests/test_env.py` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | REQ-2.1 | T-03-01 | Graceful fallback on corrupt/missing weights without unhandled 500 error | unit | `pytest backend/tests/test_yolo_service.py` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | REQ-2.2 | T-03-02 | Validation of polygon boundary geometry and coordinates | unit | `pytest backend/tests/test_morphometry.py` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | REQ-2.2 | T-03-03 | Offload inference to worker thread; non-blocking API endpoint | integration | `pytest backend/tests/test_api.py` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 2 | REQ-2.3 | — | N/A | e2e | `npm run build --prefix frontend` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/pytest.ini` — pytest configuration with asyncio mode
- [ ] `backend/tests/conftest.py` — shared fixtures and sample synthetic image generation
- [ ] `backend/tests/test_env.py` — verify Ultralytics and PyTorch runtime installation

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|---|---|---|---|
| Visual defect mask alignment | REQ-2.3 | Canvas visual overlay alignment against raw crack image | Open web browser on port 3001, upload test image, confirm SVG polygon contours hug crack fissures accurately in all three viewport modes (Defect contour, Split view, Raw surface) |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending 2026-09-28
