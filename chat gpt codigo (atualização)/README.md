# Prompt2Rig Bridge — atualização para Blender 5.3

Esta pasta contém uma atualização de integração do addon com o **Prompt2Rig original**.

## Princípio da atualização

O processamento de vídeo local já existe no frontend original. Esta ponte não tenta reimplementar MediaPipe, retarget ou o palco Three.js, nem usa indevidamente o endpoint `/api/video` (que pertence ao fluxo opcional fal.ai).

Fluxo preservado:
1. Selecionar um vídeo local no estúdio original.
2. O frontend original executa o rastreamento MediaPipe.
3. O retarget original gera a animação.
4. O palco 3D original apresenta o preview no navegador.
5. Exportar o take em GLB.
6. Importar o GLB animado no Blender.

## O que o addon faz

- Inicia `node server.mjs` no diretório do repositório original.
- Verifica o servidor local.
- Abre o frontend original no navegador.
- Importa o GLB mais recente da pasta `takes/` ou permite escolher outro arquivo.
- Pode monitorar `takes/` e importar automaticamente novos GLBs concluídos.

## Limite importante do preview

O preview fiel do Prompt2Rig continua no navegador, onde rodam Three.js, MediaPipe Tasks Vision e o frontend upstream. Este addon não incorpora um navegador dentro do painel do Blender nem afirma oferecer esse preview embutido.

## Requisitos

- Blender 4.5+ (incluindo 5.3).
- Node.js 18+.
- Repositório original Prompt2Rig completo, com `server.mjs` e `public/`.
- Navegador para abrir o estúdio original.

## Instalação

1. Baixe esta pasta do repositório.
2. Coloque a pasta `prompt2rig_blender` (que contém `__init__.py`) no diretório de addons do Blender, ou compacte essa pasta em ZIP e instale por **Edit → Preferences → Add-ons → Install from Disk**.
3. Ative **Prompt2Rig Bridge**.
4. Na Viewport 3D, pressione `N` e abra a aba **Prompt2Rig**.
5. Configure a pasta raiz do repositório original, aquela que contém `server.mjs`.

## Uso

1. Clique **Iniciar servidor original**.
2. Clique **Verificar servidor**.
3. Clique **Abrir estúdio Prompt2Rig**.
4. No navegador, processe o vídeo local usando o fluxo original e exporte o take GLB.
5. No Blender, clique **Importar último take**.
6. Para automatizar a etapa final, marque **Importar GLB automaticamente** e clique **Ativar monitoramento**.

A porta padrão é 5177. O log do servidor iniciado pelo addon fica em `/tmp/prompt2rig-blender-server.log`.

## Sem FAL_KEY

O fluxo de vídeo local → MediaPipe → retarget → GLB do frontend original não depende de FAL_KEY. Recursos opcionais de geração por prompt/fal.ai ou processamento HQ podem ter requisitos próprios.
