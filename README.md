# RaizDigital

RaizDigital é uma plataforma de nicho voltada para brasileiros que buscam a cidadania estrangeira (principalmente portuguesa e italiana) e precisam localizar certidões civis antigas sem saber em qual cartório o documento está.  Diferentemente de despachantes digitais que exigem que você indique o cartório, o RaizDigital utiliza um motor de busca automatizado para varrer múltiplas fontes públicas de dados e entregar um relatório completo com a localização do documento ou, caso nada seja encontrado, um relatório exaustivo de buscas negativas.

## Arquitetura

A plataforma é composta por dois componentes principais: um back‑end em Python com **FastAPI**, responsável pela API, persistência, autenticação e orquestração das buscas, e um front‑end em **React/TypeScript**, que fornece a interface web para os usuários.  O fluxo básico é o seguinte:

```
  [Usuário] --interage--> [Frontend React]
        |                         |
        |  requisita API          |
        v                         v
  [FastAPI] --------> [Celery Worker] --invoca--> [Robôs Selenium]
        |                                         |
        |  grava resultados no Banco de Dados     |
        +--------------<--PostgreSQL/Redis--------+
```

* **Frontend React**: Interface do usuário construída com Vite, React, Material‑UI, Zustand e React Router.  Permite cadastro/login, recuperação e redefinição de senha, criação de pedidos, checkout via Stripe (simulado) e visualização de resultados em uma área de membros com histórico e detalhamento de pedidos.  Há também uma página de perfil onde o usuário pode alterar nome, e‑mail e senha.
* **API (FastAPI)**: Exposição de endpoints REST para autenticação, gestão de usuários (registro, login, refresh token, esqueci/reset de senha, atualização de perfil), criação e listagem de pedidos, geração de sessões de pagamento e recebimento de resultados de busca.  Utiliza SQLAlchemy (modo assíncrono) com PostgreSQL, autenticação JWT e integração com Stripe.  Notificações por e‑mail são enviadas via SMTP (ou logadas no console em desenvolvimento) em cada etapa relevante (boas‑vindas, confirmação de pedido, conclusão da busca e redefinição de senha).
* **Celery/Redis**: As tarefas de busca são executadas de forma assíncrona através do Celery.  O Redis atua como broker e backend de resultados.
* **Robôs de Busca**: Implementados com Selenium e BeautifulSoup (simulados nesta versão), cada robô consulta uma fonte específica (RegistroCivil.org.br, FamilySearch.org e TJSPortal) e envia os resultados de volta para a API.

## Pré‑requisitos

- **Docker** e **Docker Compose** instalados em sua máquina.
- Uma chave de API da **Stripe** para pagamentos e o webhook secret (veja `.env.example`).

## Configuração do Ambiente

1. Clone ou copie este repositório.
2. Acesse o diretório `backend` e copie o arquivo `.env.example` para `.env`:

   ```bash
   cd backend
   cp .env.example .env
   ```

3. Edite o arquivo `.env` com as suas configurações:

   - `DATABASE_URL`: URL de conexão com o PostgreSQL (já predefinido para o serviço `db` do docker-compose).
   - `SECRET_KEY`: chave secreta para assinar JWTs.
   - `STRIPE_API_KEY` e `STRIPE_WEBHOOK_SECRET`: credenciais da Stripe.
   - `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`: URLs do Redis.
   - `INTERNAL_API_KEY`: chave interna usada pelo robô para postar resultados.
   - `FRONTEND_BASE_URL`: URL base do front‑end utilizada na construção de links enviados por e‑mail (por exemplo, `http://localhost:5173` em desenvolvimento ou `https://app.raizdigital.com` em produção).
   - `EMAIL_SENDER`: endereço que aparecerá como remetente nos e‑mails.
   - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: servidor SMTP e credenciais para envio real de e‑mails.  Se deixados vazios, os e‑mails serão apenas impressos no console.

## Rodando em Desenvolvimento

Com as variáveis de ambiente configuradas, basta subir toda a stack com o **docker‑compose** dentro da pasta `backend`:

```bash
docker-compose up --build
```

Isso iniciará quatro containers:

1. **backend**: o servidor FastAPI escutando em `http://localhost:8000`;
2. **celery_worker**: o worker Celery responsável por executar as tarefas de busca;
3. **db**: banco de dados PostgreSQL;
4. **redis**: instância do Redis usada como broker/result backend.

Após subir os serviços, acesse `http://localhost:8000/docs` para visualizar a documentação interativa gerada pelo FastAPI e testar os endpoints.

Para o front‑end, abra outro terminal, navegue até a pasta `frontend`, instale as dependências e rode o Vite:

```bash
cd frontend
npm install
npm run dev
```

O aplicativo React ficará disponível em `http://localhost:5173` (porta padrão do Vite) e se comunicará com o backend em `http://localhost:8000`.  Se quiser utilizar outra porta ou domínio para o backend, crie um arquivo `.env` na pasta `frontend` definindo a variável `VITE_API_URL`, por exemplo `VITE_API_URL=http://localhost:8000`.

## Build e Deploy para Produção

### Backend

O backend está conteinerizado e pronto para produção.  Para fazer o deploy em um provedor de nuvem (AWS ECS, Google Cloud Run, DigitalOcean App Platform, etc.), siga estes passos gerais:

1. Crie um registro de container e faça o *build* da imagem do backend:

   ```bash
   docker build -t sua-conta/raizdigital-backend:latest backend
   docker push sua-conta/raizdigital-backend:latest
   ```

2. Configure um serviço usando a imagem publicada e defina as variáveis de ambiente (`DATABASE_URL`, `SECRET_KEY`, `STRIPE_API_KEY` etc.) no painel do provedor.

3. Provisione um banco de dados PostgreSQL gerenciado e um serviço Redis (ou use alternativas como SQS/RabbitMQ conforme suporte do provedor) e atualize as URLs no ambiente.

4. Crie um segundo serviço/worker a partir da mesma imagem para executar o comando Celery: `celery -A app.tasks worker -l info`.

### Frontend

Para gerar os arquivos estáticos otimizados do front‑end:

```bash
cd frontend
npm install
npm run build
```

Os arquivos serão produzidos na pasta `dist`.  Para o deploy você pode servir esses arquivos usando um servidor web como o **Nginx** (há um `Dockerfile.prod` pronto para isso) ou hospedá‑los em serviços de sites estáticos como Vercel, Netlify ou AWS S3 + CloudFront.

Para empacotar em uma imagem Docker usando Nginx:

```bash
docker build -t sua-conta/raizdigital-frontend:latest -f frontend/Dockerfile.prod frontend
docker push sua-conta/raizdigital-frontend:latest
```

Depois, crie um serviço que execute essa imagem.  Ela serve os arquivos em porta 80 por padrão.

## Estrutura do Projeto

- **backend/**: código fonte da API, tarefas Celery e robôs de busca.
  - `app/` contém módulos da aplicação (configurações, modelos, esquemas, rotas, robôs e tarefas).
  - `Dockerfile` define a imagem Docker do backend.
  - `docker-compose.yml` orquestra os serviços para desenvolvimento.
  - `.env.example` serve de modelo para as variáveis de ambiente.
- **frontend/**: código fonte da interface web.
  - `src/` contém os componentes, páginas, stores e utilidades.
  - `index.html`, `vite.config.ts` e `tsconfig.json` configuram o Vite.
  - `Dockerfile.prod` gera uma imagem otimizada usando Nginx para servir os arquivos estáticos em produção.

## Jornada do Usuário

O RaizDigital foi pensado para acompanhar o usuário em toda a sua jornada, desde o primeiro acesso até a obtenção do resultado da busca.  Resumidamente:

1. **Acesso e Cadastro** – ao clicar em “Iniciar minha busca” na landing page, o usuário é convidado a criar uma conta ou fazer login.  O registro solicita nome completo, e‑mail e senha; ao completar, um e‑mail de boas‑vindas é enviado.
2. **Autenticação** – o login gera dois tokens (de acesso e de atualização) que são salvos localmente e enviados em todas as requisições.  Um endpoint `/auth/refresh` permite renovar o token de acesso usando o token de atualização.
3. **Recuperação de Senha** – na tela “Esqueci minha senha”, o usuário informa seu e‑mail.  Um link temporário de redefinição é enviado; ao clicar, ele acessa uma página onde define uma nova senha.  Os tokens expiram em 1 hora.
4. **Criação de Pedido** – autenticado, o usuário preenche um formulário multi‑etapas com os dados que possui do antepassado (nome, data de nascimento aproximada, cidade, estado, nomes dos pais e informações adicionais).  Ao submeter, um registro é criado no banco com status `PENDING_PAYMENT`.
5. **Checkout** – em seguida, o backend cria uma sessão do Stripe (ou um pagamento simulado em desenvolvimento).  Após o pagamento, o webhook da Stripe atualiza o status do pedido para `PROCESSING`, envia um e‑mail de confirmação e dispara as tarefas de busca via Celery.
6. **Execução da Busca** – os robôs Selenium consultam cada fonte pública (RegistroCivil.org.br, FamilySearch.org e TJSPortal) e armazenam os resultados.  Quando todas as fontes retornam, o pedido é marcado como `COMPLETED_SUCCESS` (caso algum resultado seja encontrado) ou `COMPLETED_FAILURE`.  O usuário recebe um e‑mail avisando do resultado.
7. **Área de Membros** – acessando `/app/dashboard`, o usuário vê uma lista dos seus pedidos com status e datas.  Clicando em um pedido, ele acessa a página de detalhes (`/app/pedidos/{id}`) que exibe se o documento foi localizado (com dados e fonte) ou se foi gerado um relatório negativo, além de listar o status de cada fonte consultada com links para as provas (screenshots).  Na aba de perfil (`/app/perfil`), é possível alterar nome, e‑mail e senha.

## Observações

Esta implementação inclui um robô de busca simplificado que devolve resultados simulados em vez de realmente acessar os portais externos.  Para uso real em produção, implemente a lógica de scraping em `backend/app/robots/*` utilizando Selenium e BeautifulSoup, respeitando os termos de uso dos sites e considerando técnicas de retenção de sessão, espera por elementos e tratamento de erros.  Os endpoints internos e o Celery foram pensados para que essa substituição seja transparente para o restante da plataforma.


## Como rodar

### Rodar Backend
cd backend
docker compose up --build

### Rodar Frontend
cd frontend
yarn install
yarn dev

### Rodar
cd frontend
npm install
npm run build
npx serve -s dist

### Se quiser aplicar as migrações do banco
docker exec -it raizdigital_backend alembic upgrade head


### Git
