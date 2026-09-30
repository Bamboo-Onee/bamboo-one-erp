# 🎋 Bamboo One - Sistema Integrado de Gestão & Otimizador Logístico 3D
> **Plataforma Modular Corporativa desenvolvida para o Grupo Bamboo**  
> Consolidando 5 sistemas legados sob os padrões **Clean Architecture** e **Monolito Modular**, com testes automatizados (TDD), controle de acesso RBAC e motor de cubagem tridimensional de frotas.

---

## 🏛️ 1. Padrão Arquitetural

O projeto foi projetado com foco em **baixo acoplamento, alta coesão e testabilidade contínua**:

```
BambooOne-ERP/
├── backend/                       # API Modular FastAPI em Clean Architecture
│   ├── src/
│   │   ├── config/                # Central de configurações e variáveis de ambiente
│   │   ├── core/                  # Recursos transversais (Security, Async DB, ORM Base, Seed)
│   │   ├── modules/               # Bounded Contexts isolados (Monolito Modular)
│   │   │   ├── auth/              # Autenticação JWT, bcrypt e autorização RBAC
│   │   │   ├── cadastros_mestres/ # Produtos, Clientes e Veículos/Frotas
│   │   │   ├── logistics/         # Motor de Cubagem e Acomodação 3D (py3dbp)
│   │   │   ├── compras/           # Gestão de Pedidos e Fornecedores
│   │   │   ├── importacoes/       # Containers e Rastreio Portuário/Aduaneiro
│   │   │   ├── estoque/           # Balanço WMS e Movimentações com Rastreabilidade
│   │   │   ├── crm/               # Pipeline Comercial e Pedidos de Venda
│   │   │   ├── producao_expedicao/# Despacho e Rastreio de Entregas
│   │   │   ├── financeiro/        # Contas a Pagar/Receber e Fluxo de Caixa
│   │   │   ├── rh/                # Quadro Funcional e Admissões
│   │   │   └── ai_agent/          # Assistente de IA Corporativo (Tool Calling)
│   │   └── main.py                # Ponto de entrada e agregação de rotas
│   ├── tests/                     # Suíte de Testes Automatizados (TDD com Pytest)
│   │   └── unit/                  # Testes de Domínio, UseCases, Segurança e Cubagem
│   ├── Dockerfile                 # Contêiner Docker para o Backend
│   ├── requirements.txt           # Dependências Python estritas
│   └── pyproject.toml             # Configurações do projeto e do Pytest
│
├── frontend/                      # Single Page Application (SPA) React Moderna
│   ├── src/
│   │   ├── components/            # Componentes reutilizáveis
│   │   ├── App.tsx                # Dashboard integrado com 10 modais CRUD e Auth
│   │   ├── main.tsx               # Ponto de montagem React DOM
│   │   └── index.css              # Estilos utilitários Tailwind CSS
│   ├── Dockerfile                 # Contêiner Docker multi-stage Nginx
│   ├── package.json               # Dependências Node.js
│   ├── tailwind.config.js         # Configurações de tema visual
│   ├── tsconfig.json              # Configurações do TypeScript
│   └── vite.config.ts             # Configurações do Vite Dev Server
│
├── docs/                          # Documentação de Engenharia e Arquitetura
│   ├── ARCHITECTURE.md            # Especificação profunda C4 e Clean Architecture
│   ├── API_SPECIFICATION.md       # Dicionário de endpoints e schemas da API REST
│   ├── SECURITY_RBAC.md           # Política de segurança e matriz de permissões
│   ├── CARGO_3D_OPTIMIZER.md      # Formulação matemática do algoritmo de cubagem 3D
│   ├── plano_arquitetural_grupo_bamboo.pdf # Blueprint arquitetural oficial (PDF)
│   └── relatorio_requisitos_arquitetura_grupo_bamboo.pdf # Relatório de requisitos (PDF)
│
├── scripts/                       # Utilitários de Automação para Windows
│   ├── start_all.bat              # Inicia Backend e Frontend simultaneamente em 1 clique
│   ├── start_backend.bat          # Inicia apenas a API FastAPI (Porta 8000)
│   ├── start_frontend.bat         # Inicia apenas o Frontend React (Porta 5173)
│   ├── run_tests.bat              # Executa os testes automatizados do Pytest
│   └── setup_environment.bat      # Instala dependências Python e Node em nova máquina
│
├── .env.example                   # Modelo de variáveis de ambiente
├── docker-compose.yml             # Orquestrador de contêineres para Produção/Dev
├── .gitignore                     # Filtros para versionamento seguro no Git
└── README.md                      # Este manual de instruções
```

---

## ⚡ 2. Como Executar o Sistema

### Opção A: Execução em 1-Clique (Recomendado para Windows)
Na pasta do projeto, entre em `scripts/` e execute:
```cmd
scripts\start_all.bat
```
O script abrirá duas janelas automaticamente:
- **Backend API**: `http://127.0.0.1:8000` (Docs interativas: `http://127.0.0.1:8000/docs`)
- **Frontend Web**: `http://127.0.0.1:5173`

---

### Opção B: Execução Manual

#### 1. Iniciar o Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Iniciar o Frontend
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

---

### Opção C: Execução com Docker Compose
Caso prefira rodar em contêineres isolados:
```bash
docker compose up --build
```

---

## 🔐 3. Credenciais Padrão de Demonstração (Seed)

O banco de dados SQLite (`backend/crm_bamboo.db`) já vem populado com contas para teste rápido na tela de login:

| Perfil | E-mail | Senha | Acesso |
| :--- | :--- | :--- | :--- |
| 🛡️ **Administrador** | `admin@bamboo.com` | `admin123` | Acesso pleno a todos os 11 módulos e ações de exclusão |
| 🚚 **Logística** | `logistica@bamboo.com` | `logistica123` | Focado em Frotas, Cubagem 3D, WMS e Expedição |
| 💼 **Vendas** | `vendas@bamboo.com` | `vendas123` | Focado em Clientes, Pedidos Comerciais e Produtos |

*(Na tela de login, há botões de 1-clique para preenchimento imediato das credenciais).*

---

## 🧪 4. Testes Automatizados (TDD)

Para verificar a integridade da suíte de testes:
```bash
cd backend
python -m pytest -v tests/
```
Ou dê dois cliques em `scripts/run_tests.bat`.

---

## 📚 5. Documentação Complementar
- 📖 **[Livro Oficial: Engenharia de Software e Arquitetura do Bamboo One](docs/LIVRO_ARQUITETURA_BAMBOO_ONE.md)** *(Manual Completo em Formato de Livro com Sumário, Teoria, Matemática e Código)*
- [Especificação de Arquitetura e C4](docs/ARCHITECTURE.md)
- [Contratos da API RESTful](docs/API_SPECIFICATION.md)
- [Matriz de Permissões e Segurança RBAC](docs/SECURITY_RBAC.md)
- [Algoritmo Matemático de Cubagem 3D](docs/CARGO_3D_OPTIMIZER.md)
- [Blueprint Arquitetural em PDF](docs/plano_arquitetural_grupo_bamboo.pdf)
- [Relatório Detalhado de Requisitos em PDF](docs/relatorio_requisitos_arquitetura_grupo_bamboo.pdf)

