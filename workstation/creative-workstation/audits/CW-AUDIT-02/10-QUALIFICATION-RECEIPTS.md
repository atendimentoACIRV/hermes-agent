# 10 — Recibos de qualificação executada (Windows 2026-10-11)

## Ambiente e isolamento
Remote Desktop Commander device DESKTOP-3NA47UH. Source worktree docs/cw-audit02-20261011 origin/main a2b56db1bc. Exigido HERMES_HOME=/c/Temp/hermes-cw-audit02-isolated; executor Python /c/Github/hermes-agent-p0-kanban-effects/.venv/Scripts/python.exe. Não instaladas dependências. Não executado Electron empacotado ou engines de referências. Root dirty preservado.

## Comando executado
Git Bash: cd /c/Github/hermes-agent-cw-audit02; export HERMES_HOME=/c/Temp/hermes-cw-audit02-isolated; export HERMES_PYTHON=/c/Github/hermes-agent-p0-kanban-effects/.venv/Scripts/python.exe; scripts/run_tests.sh workstation/tests/test_creative_*.py -j 8 -q

## Resultado exato
- 22 arquivos encontrados / aproximadamente 98 testes anunciados pelo runner.
- 21 arquivos coletados com **96 testes PASS, 0 falhas de asserção**.
- 1 arquivo workstation/tests/test_creative_runtime.py com **COLLECTION_ERROR**, ModuleNotFoundError No module named yaml (import yaml linha 5). Exit code 1. Portanto suite global **NOT GREEN**.
- Tempo runner reportado 31.9s, paralelismo 8. NÃO usar tempo como benchmark de preview/render ou baseline para usuário.
- test_creative_export.py contribuiu 2 PASS, mas não contém o caso negativo descoberto de decoder fallback.

## POC de bug de export
- Script isolado C:/Temp/cw_audit02_export_poc.py (não parte do source repo) importa workstation.creative_export._decode_frame_hash e RationalFps, passa arquivo inexistente e mocka subprocess.run com CompletedProcess returncode=1, stdout vazio.
- Output: decode_exit=1; input_missing=True; helper_returned_nonempty_SHA=True; length=64. A função retorna SHA plausível de metadados sintéticos mesmo sem decodificar. **BUG REPRODUZIDO** em código existente. Não produz vídeo real; não atesta falha de outro adapter.
- Source: workstation/creative_export.py:88–110 fallback de hashlib.sha256(nome+frame+time); export_composition_to_video :194–215 usa valores em verified_sample_frames e receipt verified=True. Failing negative test deverá ser adicionado ao PR de correção, exigindo raise/erro em vez de SHA falso.
- No CÓDIGO, quando first_clip/asset não existe, :153–164 passa input lavfi color black, potencial false content; este caso é SOURCE_INSPECTED, não testado por POC nesta sessão.

## Conclusões de qualificação
- Em main há capacidades unitárias relevantes: documento/transações, NLE, GLB parser e adapters; NÃO há demonstração integrada humano+IA/source/pixels/MP4 via UI nativa.
- PR #77 local test pass relatado em sua própria branch, não executado nesta CW-AUDIT-02.
- P0 export verificador permanece BLOCKED até RED→GREEN fail-closed, independent decoder and preview frame parity.
- O erro yaml é pré-requisito do ambiente de teste, não demonstra defeito do produto. Corrigir em qualificação posterior respeitando lock/install policy; não instalar automaticamente para mudar semântica de evidência.
- NUNCA relatar 96/96 total como 22 suítes verdes; só 96 testes passaram com 1 erro de coleta.
