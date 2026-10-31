# Prompt2Rig Blender Addon — Especificações

Autor: DemonFock (integração Blender 5.3)  
Versão do addon: 0.2.0  
Base original: https://github.com/blendi-remade/prompt2rig (Apache-2.0)

---

## 1. O que é o Prompt2Rig (backend original)

- **Tipo**: App web + worker Python (Node.js + Python CUDA)
- **Server**: `server.mjs` (zero-dependency, porta 5177 por padrão)
- **Frontend**: `public/app.js` + `retarget.js` + `stage.js`
- **Fluxo completo**:
  1. Prompt → fal.ai (`FLUX 3 Max` / `H3 Max Turbo`) gera vídeo (`/api/video`)
  2. MediaPipe faz preview de pose (live no navegador)
  3. Opcional: `hq/worker.py` (GVHMR + WiLoR) recupera motion 3D de corpo + dedos
  4. Exporta `.glb` com rig Mixamo animado
  5. Render no Blender via `tools/render_blender.py`

**Licenças dos componentes do backend (não modificados):**
- Prompt2Rig próprio: Apache-2.0
- GVHMR (movimento): educacional / não-comercial
- SMPL-X / MANO: registro obrigatório, não-comercial
- WiLoR: CC-BY-NC-ND
- MediaPipe / three.js: Apache-2.0 / MIT
- fal.ai / modelos: termos do provedor

---

## 2. Arquitetura do Addon (independente do backend)

A pasta `prompt2rig_blender/` contém:

| Arquivo | Função |
|---|---|
| `__init__.py` | Registro no Blender 5.3, `bl_info`, classes |
| `properties.py` | `P2R_Settings` com todos os campos (prompt, modelo, duração, resolução, referência, seed, etc.) |
| `operators.py` | Ações: gerar vídeo, verificar server, iniciar server, importar GLB, carregar preset, **upload de vídeo referência (`/api/upload`)** |
| `network.py` | HTTP para `localhost:5177`: POST JSON (`/api/video`, `/api/hq`), GET (`/api/hq/health`), **multipart upload** (`/api/upload`), fetch bytes |
| `ui.py` | Painel N (`VIEW_3D > Sidebar > Prompt2Rig`): Main / Generation / Import |

**Regra de projeto**: o addon **não altera** `./prompt2rig/`. Ele apenas chama o `server.mjs` existente.

---

## 3. URLs / Caminhos necessários

| Recurso | Caminho / URL | Observação |
|---|---|---|
| Backend server | `http://localhost:5177` (padrão) | Configurável em `properties.py` (`server_url`) |
| Prompt2Rig original | `/home/romachy/Work/prompt2rig/` | Onde está `server.mjs`, `public/`, `hq/`, `.env` |
| Chave fal.ai | `.env` → `FAL_KEY=...` | Obrigatória para geração; não exposta no addon |
| Pasta de takes exportados | `prompt2rig/takes/` | Onde o app salva `.glb`; usado pelo `import_glb` |
| Pasta de media upload | `prompt2rig/media/` | Onde `server.mjs` salva vídeos enviados via `/api/upload` |
| Web app original | `http://localhost:5177/` (abrir no navegador) | Contém retargeting completo (não reimplementado no addon) |

---

## 4. Como funciona o Addon (passo a passo)

1. **Configurar backend**: definir `Prompt2Rig folder` (`backend_dir`) apontando para o repo original
2. **Iniciar server**: botão `Start server` roda `node server.mjs` via `subprocess.Popen`
3. **Checar server**: `Check server` faz GET `/` e atualiza `status`
4. **Gerar vídeo por texto**: preencher `Motion prompt`, `Video model` (`h3`/`flux3`), `Duration`, `Resolution`, `Aspect ratio` → `Generate video` (chama `/api/video`)
5. **Gerar por referência de vídeo (NOVO)**: selecionar arquivo de vídeo local em `Reference video (upload)` → `Upload reference video` envia para `/api/upload`, recebe URL → `Generate video` usa essa URL como `image_url` (i2v)
6. **Importar GLB**: após gerar/baixar `.glb` (do app ou da pasta `takes/`), selecionar `GLB path` → `Import animated GLB`
7. **Retarget**: ainda requer o frontend web (`open_web_app`) para retargeting completo; o addon importa o `.glb` já animado

---

## 5. Especificações do Blender 5.3

- `bl_info`: `"blender": (5, 3, 0)`
- Importação de GLB: `bpy.ops.import_scene.gltf(filepath=path)` (extensão glTF I/O nativa do Blender 5.3)
- Propriedades: `PropertyGroup` + `PointerProperty` em `bpy.types.Scene`
- Registro: classes registradas via `bpy.utils.register_class`; desregistro reverso
- Interface: `Panel` com `bl_category = "Prompt2Rig"`
- Operadores: `invoke` para seleção de arquivo (`fileselect_add`) no import; `execute` para ações diretas

---

## 6. O que ainda precisa ser implementado (prioridades)

- [ ] **Retargeting Python** (`retarget.js` → Python/BPy): processar `.glb` do server sem depender do navegador
- [ ] **Render headless**: integrar `tools/render_blender.py` como operador do Blender (`blender -b -P ...`)
- [ ] **Preview de vídeo**: abrir `last_video_url` em player interno ou externo
- [ ] **Tradução dos labels** para português (opcional, mas o usuário pediu)
- [ ] **Testes dentro do Blender 5.3**: validar `import_scene.gltf` e propriedades

---

## 7. Arquivo .ZIP do addon

`prompt2rig_blender_53.zip` contém a pasta `prompt2rig_blender/` com todos os arquivos Python. Instalação:

```bash
# No Blender 5.3: Edit → Preferences → Add-ons → Install → selecionar prompt2rig_blender_53.zip
```

---

*Documento criado durante desenvolvimento real. Código independente, backend preservado, versão 0.2.0.*
