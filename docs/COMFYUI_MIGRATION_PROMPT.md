# Prompt de implementação — Axo Image Studio 2.0

Você é um engenheiro sênior Python, ComfyUI, Gradio e Google Colab. Trabalhe exclusivamente na branch `feature/comfyui-studio-v2` do repositório `Pedroltz/AxoImageStudio`. Implemente a migração progressiva do Axo Image Studio, atualmente baseado em Forge Neo, para um backend ComfyUI com frontend Axo simples e uma opção avançada de abrir o editor nativo do ComfyUI.

## Requisitos obrigatórios

1. Preserve a branch main, Forge Neo atual, recursos de galeria, Axo Guide e notebook existente. Não substitua o notebook até haver um MVP testado; disponibilize inicialmente um notebook V2 separado.
2. Crie um instalador Colab Python 3.12 capaz de instalar ComfyUI com revisões fixadas e versões compatíveis, validar CUDA, lidar com GPU limitada e disponibilizar a interface via um túnel compatível com as condições de uso do Colab. Evite downloads repetidos. Suporte Drive opcional para modelos, referências, personagens, workflows e outputs. Não exponha tokens.
3. Integre o checkpoint Anima Base 2B, seus text encoders e VAE verificando os caminhos, nomes, workflows e compatibilidade com o ComfyUI atual. Não suponha que nodes sejam intercambiáveis com Forge Neo.
4. Implemente cliente ComfyUI com endpoints de upload de imagens, queue, history, image retrieval e status, com timeout, tratamento de falhas e segurança para localhost. Considere WebSocket como aprimoramento opcional. Não faça polling intensivo.
5. Implemente expansão recursiva limitada de wildcards `__roupas__`, `__cenarios/noturnos__`, `__character/sidecut__` com seeds reproduzíveis, proteção contra path traversal, ciclos e linhas malformadas. Exiba preview do prompt resolvido antes de submeter, registrando a seed e o prompt em metadados. Não altere prompts do workflow sem mapeamento explícito.
6. Construa Axo Characters: cadastro, edição e exclusão, nome único, tags fixas, uma ou mais imagens de referência, thumbnail, importação/exportação de perfis JSON sem caminhos arbitrários, organização no Drive quando habilitado. Não confunda usar imagem em img2img com manter identidade visual.
7. Instale e avalie nodes e weights Anima In-Context Character e alternativas de referência, observando documentação, compatibilidade com a versão base e licenças. Exija teste real de consistência visual, sem garantir fidelidade. Se indisponível, mostre claramente 'referência indisponível' e desabilite a função; nunca simule que a referência está sendo aplicada.
8. Frontend Axo simples: abas Criar, Personagens, Wildcards, Galeria, Guia, Configurações; interface em pt-BR, responsiva e leve; indicador de fila/progresso e errors legíveis. Modo avançado acessa ComfyUI nativo sem impor nodes a iniciantes.
9. Reutilize conceitos e funcionalidades de ADetailer, ControlNet/OpenPose, LoRAs e inpainting com os workflows equivalentes do ComfyUI; se um recurso ainda não estiver disponível, registre-o como pendente.
10. Mantenha dados separados de recursos efêmeros do Colab; proteja endpoints públicos de escrita sem autorização. Revise limites da plataforma e não exponha arquivos de outros diretórios.
11. Adicione testes unitários locais sem GPU para wildcard, character store, validação de workflows e ComfyUI API com mocks; testes de integração com GPU opcionais. Atualize README, docs, avisos de terceiros e CI.
12. Para cada fase faça commits pequenos, mantenha a branch implantável e explicite limitações. Não faça merge na main.

## Plano de execução

- Fase 0: auditoria do código e inventário dos recursos Forge a preservar.
- Fase 1: serviços isolados `comfy_client`, `wildcards` e `characters`, com testes.
- Fase 2: workflows JSON versionados e instalador Colab V2.
- Fase 3: interface Axo sobre a API; gerar uma imagem no Anima sem referência.
- Fase 4: referência visual testada e biblioteca integrada ao workflow.
- Fase 5: paridade de galeria, editor avançado, inpainting, ControlNet, LoRAs, documentação e hardening.

Critérios de aceite do MVP: iniciar com GPU Colab; acessar a UI; Anima produzir imagem com prompt normal; wildcard com seed reproduzível; salvar personagem e referência; geração com condicionamento efetivo do personagem (ou indicação explícita de indisponibilidade); persistência opcional no Drive; e nenhum impacto na instalação Forge original.

Comece examinando o repositório e implementando a Fase 1, apresentando arquivos modificados, testes executados e pendências reais. 
