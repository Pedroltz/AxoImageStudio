# Problemas comuns

## Banner do notebook não aparece

O banner no início do notebook usa uma célula de texto com uma imagem PNG pública do repositório. Ele aparece ao abrir o arquivo, sem executar uma célula de código ou conectar à GPU.

Se estiver usando uma cópia antiga no Drive, abra o [notebook atualizado](https://colab.research.google.com/github/Pedroltz/AxoImageStudio/blob/main/Axo_Image_Studio.ipynb) e salve uma nova cópia. A primeira célula antiga era uma célula de código; por isso, o banner dependia da execução dela.

Se a imagem ainda não carregar, confira se você consegue abrir o [PNG do banner](https://raw.githubusercontent.com/Pedroltz/AxoImageStudio/main/docs/assets/axo-banner.png). O notebook precisa conseguir acessar essa imagem pública.

## Miniaturas, prévia ou download com erro

1. Clique em **Atualizar** na galeria e confira a pasta de saída configurada.
2. Se o erro persistir, interrompa a célula que mantém o Forge em execução, sem desconectar nem excluir a sessão.
3. Execute **Diagnosticar galeria**, no fim do notebook, e consulte a mensagem de erro e as últimas linhas do log.
4. Para aplicar a versão atualizada da galeria, execute **Install and launch**. A célula **Restart** reutiliza os arquivos já instalados.

O cache da galeria é local e separado do Google Drive. A prévia é reduzida para economizar memória; **Preparar download original** disponibiliza a imagem original.

## `HEAD is a detached symbolic reference` no CivBrowser

O instalador fixa o CivBrowser no commit `7c9c32040722ee125cebb9bc3c9454322b14a2a3`. Um checkout desse tipo pode estar em **detached HEAD**, isto é, apontando diretamente para um commit em vez de uma branch.

O traceback relatado ocorre quando o Forge consulta `repo.active_branch` para ler informações da extensão. Se o painel carregar e a geração funcionar, esse aviso não indica problema no checkpoint, nos módulos Qwen ou na GPU. Não é necessário mudar a revisão instalada só para esconder a mensagem.

Se a extensão também não carregar, procure outro erro no log: o aviso de Git, sozinho, não explica todas as falhas possíveis de uma extensão.

## Falta de memória

Use batch 1 e uma resolução menor, desative Hires fix e complementos que não precisa no teste e mantenha `LOW_VRAM` habilitado. Consulte o artigo de desempenho na wiki.

## Anima e módulos

Escolha o preset `anima`, o checkpoint correspondente e os módulos `qwen_3_06b_base.safetensors` e `qwen_image_vae.safetensors`. Para SDXL, use o preset `xl` e módulos compatíveis com SDXL.

## Imagens desaparecem após encerrar a sessão

O armazenamento `/content` é temporário. Ative `USE_GOOGLE_DRIVE` antes de iniciar para persistir modelos e imagens em `MyDrive/Axo-Image-Studio-Forge`.

## Prompt Enhancer e Ollama

- **Painel ausente:** marque `ENABLE_PROMPT_ENHANCER` e execute a instalação novamente. A validação exige o painel em txt2img e img2img; consulte `forge.log` se falhar.
- **Ollama não inicia:** consulte `ollama.log` na pasta raiz do Axo. A porta 11434 deve estar livre no modo local; escolha `external` para usar um serviço existente.
- **Modelo indisponível:** no modo externo, execute `ollama pull NOME` no servidor e confira o nome/tag no notebook. O modo local baixa o modelo antes do Forge.
- **URL inacessível:** use a URL base alcançável pelo Colab, sem `/api/chat`. Um Ollama no seu PC não é o localhost do Colab.
- **Sem RAM ou resposta lenta:** escolha um LLM menor ou um backend externo. `LOW_VRAM` afeta o Forge, não a RAM usada pelo LLM em CPU. Para voltar ao fluxo habitual, desmarque a extensão e execute a instalação novamente.
- **Timeout/truncamento:** reduza a descrição e os modificadores, desative Think e tente novamente. CPU pode ultrapassar os limites de 60 s sem tokens ou 300 s totais. Use um servidor externo mais rápido se necessário.
- **YAML personalizado:** use a pasta `prompt-enhancer` na raiz do Axo. Novos arquivos exigem reiniciar o Forge; Reload atualiza o conteúdo de grupos existentes.
