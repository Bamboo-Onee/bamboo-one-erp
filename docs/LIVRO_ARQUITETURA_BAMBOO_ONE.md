# 🎋 BAMBOO ONE: ENGENHARIA DE SOFTWARE, ARQUITETURA MODULAR E INTELIGÊNCIA LOGÍSTICA 3D
### *O Guia Definitivo de Arquitetura, Design de Sistemas e Implementação do ERP Unificado do Grupo Bamboo*

---

```
================================================================================
                                 BAMBOO ONE
                  SISTEMA INTEGRADO DE GESTÃO EMPRESARIAL
                     E OTIMIZADOR LOGÍSTICO TRIDIMENSIONAL
================================================================================
  Autor: Equipe de Engenharia e Arquitetura de Sistemas
  Versão: 1.0.0 | Padrão: Clean Architecture & Modular Monolith
  Edição Oficial: Setembro de 2026
================================================================================
```

---

## 📑 SUMÁRIO GERAL

- [Prefácio: O Desafio de Unificar 5 Sistemas Legados](#prefácio-o-desafio-de-unificar-5-sistemas-legados)
- [PARTE I: FUNDAMENTOS E VISÃO ESTRATÉGICA](#parte-i-fundamentos-e-visão-estratégica)
  - [Capítulo 1: A Gênese do Bamboo One e o Diagnóstico do Legado](#capítulo-1-a-gênese-do-bamboo-one-e-o-diagnóstico-do-legado)
  - [Capítulo 2: Diretrizes Arquiteturais: O Dilema Monolito vs. Microsserviços](#capítulo-2-diretrizes-arquiteturais-o-dilema-monolito-vs-microsserviços)
- [PARTE II: CLEAN ARCHITECTURE E MONOLITO MODULAR](#parte-ii-clean-architecture-e-monolito-modular)
  - [Capítulo 3: As Quatro Camadas da Clean Architecture](#capítulo-3-as-quatro-camadas-da-clean-architecture)
  - [Capítulo 4: Bounded Contexts e Isolamento de Domínios](#capítulo-4-bounded-contexts-e-isolamento-de-domínios)
  - [Capítulo 5: O Modelo C4: Diagramas e Visualização Arquitetural](#capítulo-5-o-modelo-c4-diagramas-e-visualização-arquitetural)
- [PARTE III: ENGENHARIA DE DADOS, CONCORRÊNCIA E PERSISTÊNCIA](#parte-iii-engenharia-de-dados-concorrência-e-persistência)
  - [Capítulo 6: Persistência Assíncrona com SQLAlchemy 2.0 Async](#capítulo-6-persistência-assíncrona-com-sqlalchemy-20-async)
  - [Capítulo 7: Modelagem Relacional Unificada (ERD)](#capítulo-7-modelagem-relacional-unificada-erd)
- [PARTE IV: O MOTOR DE CUBAGEM E OTIMIZAÇÃO LOGÍSTICA 3D](#parte-iv-o-motor-de-cubagem-e-otimização-logística-3d)
  - [Capítulo 8: O Problema da Mochila Tridimensional (3D-BPP)](#capítulo-8-o-problema-da-mochila-tridimensional-3d-bpp)
  - [Capítulo 9: Heurística Best-Fit Decreasing e Restrições Físicas](#capítulo-9-heurística-best-fit-decreasing-e-restrições-físicas)
  - [Capítulo 10: O Motor py3dbp e Geração de Coordenadas de Carregamento](#capítulo-10-o-motor-py3dbp-e-geração-de-coordenadas-de-carregamento)
- [PARTE V: SEGURANÇA DA INFORMAÇÃO, CRIPTOGRAFIA E RBAC](#parte-v-segurança-da-informação-criptografia-e-rbac)
  - [Capítulo 11: Defesa em Profundidade e Padrões OWASP ASVS](#capítulo-11-defesa-em-profundidade-e-padrões-owasp-asvs)
  - [Capítulo 12: Autenticação JWT (RFC 7519) e Criptografia com Bcrypt](#capítulo-12-autenticação-jwt-rfc-7519-e-criptografia-com-bcrypt)
  - [Capítulo 13: Controle de Acesso Baseado em Papéis (RBAC)](#capítulo-13-controle-de-acesso-baseado-em-papéis-rbac)
- [PARTE VI: FRONTEND CORPORATIVO EM REACT E EXPERIÊNCIA DO USUÁRIO](#parte-vi-frontend-corporativo-em-react-e-experiência-do-usuário)
  - [Capítulo 14: Single Page Application com React 18, TypeScript e Tailwind](#capítulo-14-single-page-application-com-react-18-typescript-e-tailwind)
  - [Capítulo 15: Engenharia de Modais CRUD, Estado e Feedback Visual](#capítulo-15-engenharia-de-modais-crud-estado-e-feedback-visual)
  - [Capítulo 16: O Assistente Virtual de IA Integrado (Tool Calling)](#capítulo-16-o-assistente-virtual-de-ia-integrado-tool-calling)
- [PARTE VII: QUALIDADE DE SOFTWARE, DEVOPS E OPERAÇÕES](#parte-vii-qualidade-de-software-devops-e-operações)
  - [Capítulo 17: Desenvolvimento Orientado a Testes (TDD com Pytest)](#capítulo-17-desenvolvimento-orientado-a-testes-tdd-com-pytest)
  - [Capítulo 18: Containerização e Orquestração com Docker Compose](#capítulo-18-containerização-e-orquestração-com-docker-compose)
  - [Capítulo 19: Guia Operacional de Execução e Manutenção](#capítulo-19-guia-operacional-de-execução-e-manutenção)
- [APÊNDICES](#apêndices)
  - [Apêndice A: Dicionário Geral da API RESTful](#apêndice-a-dicionário-geral-da-api-restful)
  - [Apêndice B: Matriz de Códigos de Resposta HTTP](#apêndice-b-matriz-de-códigos-de-resposta-http)
  - [Apêndice C: Glossário de Engenharia e Negócio](#apêndice-c-glossário-de-engenharia-e-negócio)

---

# PREFÁCIO: O DESAFIO DE UNIFICAR 5 SISTEMAS LEGADOS

A cadeia de suprimentos de produtos florestais de rápido crescimento, com destaque para o **bambu tratado**, possui peculiaridades operacionais severas. O Grupo Bamboo operou durante anos sob uma constelação fragmentada de **5 sistemas independentes**:
1. Um **CRM de Vendas** isolado para propostas comerciais.
2. Um sistema de **Compras e Rastreio de Importações** gerenciado em planilhas e scripts ad-hoc.
3. Um software legador de **Controle de Estoque (WMS)** desconectado do faturamento.
4. Uma ferramenta pontual de **Expedição e Gestão de Frota** que dependia de medições manuais de caminhões.
5. Um sistema isolado de **Contabilidade, Contas a Pagar/Receber e Recursos Humanos**.

Essa fragmentação causava atrasos na confirmação de pedidos, erros graves de cubagem de fretes (onde caminhões eram despachados com excesso de peso ou com até 50% de espaço volumétrico desperdiçado) e incompatibilidade no fluxo de caixa.

O **Bamboo One** foi concebido não apenas como um software, mas como um **ecossistema de governança digital**. Este livro documenta cada decisão de engenharia, cada equação matemática de cubagem e cada camada de código implementada na plataforma.

---

# PARTE I: FUNDAMENTOS E VISÃO ESTRATÉGICA

## CAPÍTULO 1: A GÊNESE DO BAMBOO ONE E O DIAGNÓSTICO DO LEGADO

### 1.1. O Diagnóstico Situacional
O diagnóstico inicial revelou sintomas clássicos de degradação arquitetural (*architectural decay*):
- **Duplicação de Cadastros**: Clientes cadastrados com grafias distintas em três bancos de dados diferentes.
- **Inconsistência de Estoque**: Produtos vendidos que já haviam sido reservados para industrialização.
- **Ineficiência no Carregamento**: O transporte rodoviário de cargas de bambu — caracterizadas por varas longas de 3 a 6 metros e peças volumétricas leves — sofria perdas financeiras crônicas de até 35% por viagem não otimizada.

### 1.2. Os Pilares Fundamentais do Bamboo One
Para sanar em definitivo tais fragilidades, quatro pilares foram estabelecidos:
1. **Unificação Transacional**: Um único modelo de dados relacional e assíncrono.
2. **Separação Rígida de Responsabilidades**: Domínios de negócio delimitados (Bounded Contexts) sob o padrão Clean Architecture.
3. **Logística Preditiva e Tridimensional**: Otimização algorítmica de arranjo de cargas (*3D Bin Packing*) acoplada ao processo de checkout de vendas.
4. **Agente Inteligente de Decisão**: IA corporativa com permissões controladas para responder métricas operacionais e executar diagnósticos em tempo real.

---

## CAPÍTULO 2: DIRETRIZES ARQUITETURAIS: O DILEMA MONOLITO VS. MICROSSERVIÇOS

Uma das decisões de engenharia mais cruciais foi a escolha do estilo arquitetural de distribuição.

```mermaid
graph TD
    subgraph "Dilema Arquitetural"
        A[Arquitetura do Bamboo One] --> B[Microsserviços Distribuídos]
        A --> C[Monolito Modular]
    end

    subgraph "Trade-offs de Microsserviços"
        B --> B1[Alta complexidade de rede e latência]
        B --> B2[Transações distribuídas de 2 fases / Saga]
        B --> B3[Custo elevado de infraestrutura e orquestração]
    end

    subgraph "Benefícios do Monolito Modular"
        C --> C1[Baixa latência: Chamadas in-memory]
        C --> C2[Consistência ACID em banco único]
        C --> C3[Código modular com baixo acoplamento]
        C --> C4[Evolução facilitada para microsserviços se necessário]
    end

    style C fill:#dcfce7,stroke:#16a34a,stroke-width:2px;
    style B fill:#fee2e2,stroke:#dc2626,stroke-width:1px;
```

### 2.1. Por que Rejeitamos Microsserviços Prematuros?
Adotar dezenas de microsserviços independentes traria:
- Sobrecarga operacional desnecessária (*Network Overhead* e *Serialization Tax*).
- Complexidade em manter consistência transacional entre Estoque, Vendas e Financeiro (exigindo orquestradores de Saga e mensageria distribuída com risco de falha).
- Dificuldade de depuração e testes locais em máquinas de desenvolvimento.

### 2.2. A Vitória do Monolito Modular
O **Monolito Modular** une o melhor dos dois mundos:
- **Alta Coesão e Baixo Acoplamento**: Cada módulo reside em uma pasta isolada (`src/modules/<modulo>/`), contendo suas próprias entidades, casos de uso e rotas.
- **Chamadas Locais e Velozes**: A comunicação interna entre domínios é feita via interfaces limpas em memória, sem latência HTTP ou gRPC.
- **Fácil Extração Futura**: Se o módulo de Cubagem 3D exigir computação em GPU ou escalonamento elástico extremo, ele pode ser extraído para um serviço satélite sem alterar sua lógica interna de domínio.

---

# PARTE II: CLEAN ARCHITECTURE E MONOLITO MODULAR

## CAPÍTULO 3: AS QUATRO CAMADAS DA CLEAN ARCHITECTURE

O Bamboo One implementa rigorosamente a **Arquitetura Limpa** de Robert C. Martin. A regra fundamental é a **Regra da Dependência**: *dependências de código só podem apontar para dentro, em direção às regras de alto nível de negócio.*

```
+------------------------------------------------------------------+
|                   1. APRESENTAÇÃO (Presentation)                 |
|  FastAPI Routers | Schemas Pydantic v2 | Middlewares | OpenAPI   |
|   +----------------------------------------------------------+   |
|   |                 2. APLICAÇÃO (Application)               |   |
|   |  Casos de Uso (Use Cases) | DTOs | Interfaces de Repositório |
|   |   +--------------------------------------------------+   |   |
|   |   |               3. DOMÍNIO (Domain Core)           |   |   |
|   |   |  Entidades Puras | Objetos de Valor | Invariantes|   |   |
|   |   +--------------------------------------------------+   |   |
+---+---+------------------------------------------------------+---+
|                   4. INFRAESTRUTURA (Infrastructure)             |
|  SQLAlchemy 2.0 Async | SQLite / PostgreSQL | Py3dbp | Logging   |
+------------------------------------------------------------------+
```

### 3.1. Camada de Domínio (`domain/`)
- Contém a lógica de negócio mais pura da empresa.
- **Zero Dependências**: Nenhuma referência a frameworks (nem FastAPI, nem SQLAlchemy, nem bibliotecas externas).
- Exemplo prático de entidade de domínio:

```python
# backend/src/modules/cadastros_mestres/domain/entities.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    name: str
    sku: str
    width: float
    height: float
    depth: float
    weight: float
    category: str
    id: Optional[int] = None

    def __post_init__(self):
        """Invariantes de Domínio: Dimensões e pesos devem ser estritamente positivos."""
        if not self.sku or not self.sku.strip():
            raise ValueError("O SKU do produto não pode ser vazio.")
        if self.width <= 0 or self.height <= 0 or self.depth <= 0:
            raise ValueError("As dimensões tridimensionais devem ser maiores que zero.")
        if self.weight <= 0:
            raise ValueError("O peso do item deve ser positivo.")

    @property
    def volume_m3(self) -> float:
        """Calcula o volume cúbico unitário em metros cúbicos."""
        return round(self.width * self.height * self.depth, 6)
```

### 3.2. Camada de Aplicação (`application/`)
- Orquestra os fluxos que realizam as intenções dos usuários.
- Não sabe como os dados são gravados no disco, dependendo exclusivamente de **Portas/Interfaces abstratas** (`ports/repository.py`).
- Exemplo:

```python
# backend/src/modules/cadastros_mestres/application/use_cases.py
from typing import List
from ..domain.entities import Product
from .ports import IProductRepository

class CreateProductUseCase:
    def __init__(self, repository: IProductRepository):
        self._repo = repository

    async def execute(self, product_data: dict) -> Product:
        product = Product(**product_data)
        return await self._repo.save(product)
```

### 3.3. Camada de Infraestrutura (`infrastructure/`)
- Fornece as implementações concretas para as interfaces de aplicação.
- Mapeia entidades de domínio para modelos relacionais ORM através do SQLAlchemy 2.0 Async.
- Executa queries SQL otimizadas com statements tipados.

### 3.4. Camada de Apresentação (`presentation/`)
- Controladores HTTP expostos via **FastAPI**.
- Valida payloads recebidos com **Pydantic v2**, serializa respostas e captura exceções retornando status codes RFC adequados (200, 201, 400, 401, 403, 404, 422).

---

## CAPÍTULO 4: BOUNDED CONTEXTS E ISOLAMENTO DE DOMÍNIOS

A estrutura de módulos do Bamboo One reflete a decomposição do negócio em 11 subdomínios:

| Módulo | Bounded Context | Descrição Operacional |
| :--- | :--- | :--- |
| `auth` | Segurança & Identidade | Gestão de credenciais, RBAC, tokens JWT e auditoria de acessos. |
| `cadastros_mestres` | Cadastros Fundamentais | Produtos, Clientes, Transportadoras e Veículos de Frota. |
| `logistics` | Inteligência 3D | Motor de simulação de arranjo tridimensional e cubagem física de carga. |
| `compras` | Suprimentos e Insumos | Ordens de compra, homologação de fornecedores e controle de custos. |
| `importacoes` | Comércio Exterior | Containers marítimos, portos de atracação e trâmites de desembaraço aduaneiro. |
| `estoque` | WMS e Armazenagem | Rastreamento de inventário, balanceamento de lotes e movimentações E/S. |
| `crm` | Vendas e Negociações | Funil de propostas comerciais, clientes e fechamento de pedidos de venda. |
| `producao_expedicao`| Expedição e Rastreio | Faturamento, expedição física de cargas e acompanhamento de entregas em rota. |
| `financeiro` | Controladoria | Fluxo de caixa corporativo, contas a pagar, contas a receber e DRE simplificado. |
| `rh` | Recursos Humanos | Quadro de colaboradores, departamentos, salários e histórico funcional. |
| `ai_agent` | Inteligência Aumentada| Agente de linguagem autônomo conectado às consultas operacionais do ERP. |

---

## CAPÍTULO 5: O MODELO C4: DIAGRAMAS E VISUALIZAÇÃO ARQUITETURAL

O Modelo C4 decompõe o sistema em quatro níveis de abstração progressiva.

### 5.1. Nível 1: Contexto de Sistema (System Context)

```mermaid
C4Context
    title C4 - Nível 1: Diagrama de Contexto de Sistema

    Person(userAdmin, "Administrador Master", "Gestão global de usuários, configurações e auditoria")
    Person(userLog, "Operador Logístico", "Planejamento de cubagem 3D, frotas e expedição de pedidos")
    Person(userCom, "Comercial / Vendas", "Prospecção, emissão de propostas e consulta de catálogo")

    System(bambooSystem, "Bamboo One ERP", "Plataforma central unificada de gestão industrial e logística 3D")

    System_Ext(sefazSvc, "SEFAZ / NF-e", "Autorização de notas fiscais eletrônicas")
    System_Ext(portosSvc, "Sistemas Aduaneiros", "Rastreio e atracação de containers nos portos de Santos/Paranaguá")

    Rel(userAdmin, bambooSystem, "Administra e parametriza", "HTTPS / Browser")
    Rel(userLog, bambooSystem, "Simula cubagem e despacha", "HTTPS / Browser")
    Rel(userCom, bambooSystem, "Cadastra pedidos de venda", "HTTPS / Browser")
    Rel(bambooSystem, sefazSvc, "Transmite documentos fiscais", "REST / WebService")
    Rel(bambooSystem, portosSvc, "Monitora desembaraço", "REST API")
```

### 5.2. Nível 2: Contêineres (Container Diagram)

```mermaid
C4Container
    title C4 - Nível 2: Diagrama de Contêineres da Aplicação

    Container(reactApp, "Single Page Application (SPA)", "React 18, TypeScript, Tailwind CSS", "Interface web unificada com dashboards, modais interativos e assistente flutuante de IA")
    Container(fastApiApp, "API Monolítica Modular", "Python 3.12, FastAPI, Clean Architecture", "Roteadores REST, injeção de dependência, validação Pydantic v2 e segurança RBAC")
    Container(enginePack, "Motor de Cubagem 3D", "Python py3dbp, NumPy", "Heurística 3D-BPP com 6 graus de rotação espacial e validação de tara/capacidade")
    ContainerDb(relDb, "Banco de Dados Relacional", "SQLite (Local) / PostgreSQL 16 (Produção)", "Persistência transacional com SQLAlchemy 2.0 Async")

    Rel(reactApp, fastApiApp, "Requisições RESTful autenticadas com JWT", "HTTP / JSON")
    Rel(fastApiApp, enginePack, "Simula empacotamento tridimensional", "In-Process Call")
    Rel(fastApiApp, relDb, "Leitura e escrita de entidades", "Async Engine / SQLAlchemy")
```

---

# PARTE III: ENGENHARIA DE DADOS, CONCORRÊNCIA E PERSISTÊNCIA

## CAPÍTULO 6: PERSISTÊNCIA ASSÍNCRONA COM SQLALCHEMY 2.0 ASYNC

O Bamboo One emprega **I/O Assíncrono não-bloqueante** para todas as transações de banco de dados.

### 6.1. O Padrão Unit of Work e Sessão Assíncrona
A gerência de ciclo de vida das transações é centralizada no módulo `src/core/database.py`:

```python
# backend/src/core/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency Provider para injeção de sessões FastAPI com Rollback automático."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 6.2. Portabilidade entre SQLite e PostgreSQL
Graças ao SQLAlchemy 2.0, alternar do SQLite local (arquivo `crm_bamboo.db`) para o PostgreSQL de produção em alta disponibilidade exige apenas a alteração da variável de ambiente `DATABASE_URL`:
- **Desenvolvimento**: `sqlite+aiosqlite:///./crm_bamboo.db`
- **Produção**: `postgresql+asyncpg://user:pass@db-cluster.bamboo.internal:5432/bamboo_one`

---

## CAPÍTULO 7: MODELAGEM RELACIONAL UNIFICADA (ERD)

O diagrama abaixo ilustra o esquema de dados central consolidado no arquivo `src/core/models.py`:

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : "audita"
    CUSTOMERS ||--o{ SALES_ORDERS : "emite"
    PRODUCTS ||--o{ ORDER_ITEMS : "compoe"
    SALES_ORDERS ||--|{ ORDER_ITEMS : "contem"
    SALES_ORDERS ||--o| DELIVERIES : "despachada_em"
    VEHICLES ||--o{ DELIVERIES : "transporta"
    PRODUCTS ||--o{ STOCK_MOVEMENTS : "movimenta"
    PRODUCTS ||--o{ STOCK_BALANCES : "tem_saldo"
    PURCHASES ||--o{ STOCK_MOVEMENTS : "alimenta"
    SALES_ORDERS ||--o{ FINANCIAL_ENTRIES : "gera_receita"
    PURCHASES ||--o{ FINANCIAL_ENTRIES : "gera_despesa"
    IMPORT_PROCESSES ||--o{ FINANCIAL_ENTRIES : "custos_aduaneiros"

    USERS {
        int id PK
        string email UK
        string name
        string password_hash
        string role
        boolean is_active
        datetime created_at
    }

    PRODUCTS {
        int id PK
        string sku UK
        string name
        string category
        float price
        float weight_kg
        float length_m
        float width_m
        float height_m
        boolean is_active
    }

    CUSTOMERS {
        int id PK
        string name
        string document UK
        string email
        string phone
        string delivery_address
        float credit_limit
        boolean is_active
    }

    VEHICLES {
        int id PK
        string plate UK
        string model
        string body_type
        float length_m
        float width_m
        float height_m
        float max_payload_kg
        boolean is_active
    }

    DELIVERIES {
        int id PK
        string delivery_number UK
        string customer_name
        string destination_city
        int total_volumes
        string vehicle_plate
        string status
        datetime created_at
    }

    STOCK_BALANCES {
        int id PK
        string product_sku FK
        string product_name
        string warehouse_name
        int quantity_available
        int quantity_reserved
        datetime updated_at
    }

    FINANCIAL_ENTRIES {
        int id PK
        string entry_type
        string description
        string entity_name
        string category
        float amount
        string due_date
        string status
        datetime created_at
    }

    IMPORT_PROCESSES {
        int id PK
        string process_number UK
        string supplier_name
        string container_number
        string origin_port
        string destination_port
        string status
        float total_usd
        float landed_cost_brl
    }

    EMPLOYEES {
        int id PK
        string name
        string cpf UK
        string role
        string department
        float salary
        string admission_date
        string status
    }
```

---

# PARTE IV: O MOTOR DE CUBAGEM E OTIMIZAÇÃO LOGÍSTICA 3D

## CAPÍTULO 8: O PROBLEMA DA MOCHILA TRIDIMENSIONAL (3D-BPP)

O **3D Bin Packing Problem (3D-BPP)** é classificado como NP-Difícil (*NP-Hard*). Ele consiste em acomodar um conjunto de paralelepípedos retângulos $I = \{i_1, i_2, \dots, i_n\}$ dentro de um contêiner $C$ de dimensões $(W, H, D)$ e capacidade de carga $M$, maximizando a utilização do volume útil sem violar restrições físicas de sobreposição e peso.

### 8.1. Modelo Matemático Formal

Seja cada item $i \in I$ definido pela tupla $(w_i, h_i, d_i, m_i)$.  
Seja o contêiner $C$ caracterizado por $(W, H, D, M)$.

Para cada item $i$, definem-se as coordenadas espaciais de sua origem no canto inferior traseiro esquerdo:
$$(x_i, y_i, z_i) \in [0, W - w_i'] \times [0, H - h_i'] \times [0, D - d_i']$$

Onde $(w_i', h_i', d_i')$ representam as dimensões efetivas do item de acordo com sua orientação de rotação escolhida $r_i \in \{1, 2, 3, 4, 5, 6\}$.

#### Função Objetivo:
Maximizar a ocupação volumétrica total dos itens alocados:
$$\max \sum_{i \in I_{\text{alocados}}} (w_i \cdot h_i \cdot d_i)$$

#### Restrição 1: Limite de Capacidade de Peso (Tara da Frota)
$$\sum_{i \in I_{\text{alocados}}} m_i \le M$$

#### Restrição 2: Invariante de Não-Sobreposição Espacial (Colisão 3D)
Para qualquer par de itens distintos $i, j \in I_{\text{alocados}}$, a interseção volumétrica deve ser nula:
$$(x_i + w_i' \le x_j) \;\lor\; (x_j + w_j' \le x_i) \;\lor\; (y_i + h_i' \le y_j) \;\lor\; (y_j + h_j' \le y_i) \;\lor\; (z_i + d_i' \le z_j) \;\lor\; (z_j + d_j' \le z_i)$$

---

## CAPÍTULO 9: HEURÍSTICA BEST-FIT DECREASING E RESTRIÇÕES FÍSICAS

Como soluções exatas via Programação Linear Inteira Mista (MILP) exigem minutos ou horas de processamento computacional para dezenas de itens, o Bamboo One implementa a heurística **Best-Fit Decreasing (BFD)** com complexidade $O(N \log N + N \cdot K)$:

```mermaid
flowchart TD
    Start([Início da Otimização 3D]) --> Sort[Ordenação Decrescente de Itens por Volume e Densidade]
    Sort --> PickItem{Há itens pendentes?}
    PickItem -- Não --> Report[Calcular Taxa de Ocupação e Gerar Coordenadas]
    PickItem -- Sim --> EvalRot[Avaliar as 6 Permutações de Rotação Espacial]
    EvalRot --> FindPocket[Localizar Melhor Posição Válida: Menor Desperdício de Coordenada]
    FindPocket --> CheckFit{Cabe no Baú e Respeita Peso Máximo?}
    CheckFit -- Sim --> Place[Fixar Caixa nas Coordenadas x, y, z e Atualizar Malha]
    CheckFit -- Não --> Reject[Marcar Item como Não Acomodado / Overflow]
    Place --> PickItem
    Reject --> PickItem
    Report --> End([Fim do Processamento])
```

---

## CAPÍTULO 10: O MOTOR PY3DBP E GERAÇÃO DE COORDENADAS DE CARREGAMENTO

O serviço de logística (`src/modules/logistics/application/packing_service.py`) utiliza a biblioteca `py3dbp` encapsulada pela porta de aplicação:

```python
# Trecho da Integração do Motor de Empacotamento
from py3dbp import Packer, Bin, Item

class PackingSimulationService:
    @staticmethod
    def simulate(bin_spec: dict, items_spec: list) -> dict:
        packer = Packer()
        # Registra o baú do veículo ou container marítimo
        truck_bin = Bin(
            name=bin_spec["name"],
            width=bin_spec["width"],
            height=bin_spec["height"],
            depth=bin_spec["depth"],
            max_weight=bin_spec["max_weight"]
        )
        packer.add_bin(truck_bin)

        # Registra a carga fracionada
        for it in items_spec:
            for qty in range(it["quantity"]):
                packer.add_item(Item(
                    name=f"{it['name']} #{qty+1}",
                    width=it["width"],
                    height=it["height"],
                    depth=it["depth"],
                    weight=it["weight"]
                ))

        packer.pack(bigger_first=True)
        return format_packing_response(truck_bin)
```

O resultado provê à equipe de expedição o mapa exato com **coordenadas $(x, y, z)$** e indicação da rotação adotada para cada fardo de bambu, eliminando o erro humano no pátio de carregamento.

---

# PARTE V: SEGURANÇA DA INFORMAÇÃO, CRIPTOGRAFIA E RBAC

## CAPÍTULO 11: DEFESA EM PROFUNDIDADE E PADRÕES OWASP ASVS

A arquitetura do Bamboo One segue o princípio da **Defesa em Profundidade** (*Defense in Depth*):

```
[ Nível de Rede ]: CORS com Lista Branca de Domínios Confiáveis
       │
[ Nível de Transporte ]: TLS 1.3 / HTTPS Obrigatório
       │
[ Nível de Gateway ]: Validação de Assinatura JWT RFC 7519 (HS256)
       │
[ Nível de Rota / RBAC ]: Injeção de Dependências FastAPI (require_roles)
       │
[ Nível de Domínio ]: Invariantes de Entidade e Proteção contra Mass-Assignment
       │
[ Nível de Persistência ]: Queries Parametrizadas SQLAlchemy (Anti-SQLi)
```

---

## CAPÍTULO 12: AUTENTICAÇÃO JWT (RFC 7519) E CRIPTOGRAFIA COM BCRYPT

### 12.1. Criptografia Segura de Senhas
Senhas nunca são registradas em formato plano. O sistema utiliza `bcrypt` com salt aleatório gerado a cada execução e custo de trabalho configurado em 12 rounds:

```python
# backend/src/core/security.py
import bcrypt

def hash_password(plain_password: str) -> str:
    """Gera hash salgado com bcrypt e fator de trabalho 12."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara a senha em tempo constante, prevenindo Timing Attacks."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
```

### 12.2. O Token de Acesso JWT
Após a autenticação em `POST /api/v1/auth/login`, é emitido um token JWT com expiração configurada para 60 minutos, contendo os seguintes claims essenciais:
- `sub`: Identificador de e-mail do usuário.
- `role`: Perfil de acesso autorizado (`ADMIN`, `LOGISTICA`, `VENDAS`, etc.).
- `exp`: Timestamp de expiração universal (UTC).

---

## CAPÍTULO 13: CONTROLE DE ACESSO BASEADO EM PAPÉIS (RBAC)

A autorização é governada pela fábrica de dependências `require_roles`:

```python
# backend/src/modules/auth/presentation/routes/auth_routes.py
def require_roles(allowed_roles: List[str]):
    async def role_checker(current_user: UserORM = Depends(get_current_user)) -> UserORM:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Perfil requerido: {allowed_roles}, perfil atual: {current_user.role}"
            )
        return current_user
    return role_checker
```

### Matriz Corporativa de Permissões:

| Módulo do Sistema | ADMIN | LOGISTICA | VENDAS | COMPRAS | FINANCEIRO |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Painel Geral (KPIs) | Total | Total | Total | Total | Total |
| Cadastros Mestres (Criar/Editar)| Total | Leitura | Leitura | Leitura | Leitura |
| Exclusão de Itens Mestres | Total | 🚫 Negado | 🚫 Negado | 🚫 Negado | 🚫 Negado |
| Otimizador Logístico 3D | Total | Total | 🚫 Negado | 🚫 Negado | 🚫 Negado |
| Despacho & Entregas | Total | Total | Leitura | 🚫 Negado | 🚫 Negado |
| WMS / Estoque | Total | Total | Leitura | Leitura | 🚫 Negado |
| CRM & Pedidos de Venda | Total | 🚫 Negado | Total | 🚫 Negado | Leitura |
| Compras & Fornecedores | Total | 🚫 Negado | 🚫 Negado | Total | Leitura |
| Importações de Containers | Total | Total | 🚫 Negado | Total | Leitura |
| Financeiro & Caixa | Total | 🚫 Negado | 🚫 Negado | 🚫 Negado | Total |
| Recursos Humanos (RH) | Total | 🚫 Negado | 🚫 Negado | 🚫 Negado | 🚫 Negado |

---

# PARTE VI: FRONTEND CORPORATIVO EM REACT E EXPERIÊNCIA DO USUÁRIO

## CAPÍTULO 14: SINGLE PAGE APPLICATION COM REACT 18, TYPESCRIPT E TAILWIND

O frontend do Bamboo One (`frontend/src/App.tsx`) foi construído com:
- **React 18 & Hooks Modernos**: `useState`, `useEffect`, `useCallback` para gerenciamento determinístico de ciclo de vida.
- **Tipagem Estrita com TypeScript**: Interfaces para todas as entidades de negócio (Produtos, Veículos, Clientes, Ordens, etc.).
- **Tailwind CSS**: Estilização baseada em utilitários de alta performance, sem arquivos CSS inchados.
- **Ícones Semânticos (Lucide React)**: Representação visual intuitiva para cada operação de armazém e logística.

---

## CAPÍTULO 15: ENGENHARIA DE MODAIS CRUD, ESTADO E FEEDBACK VISUAL

Para assegurar que o usuário final execute cadastros sem recarregar a tela ou sofrer com formulários estáticos, cada uma das **10 abas operacionais** possui um modal dedicado com:
1. **Validação de Entrada de Dados**: Proteção contra strings vazias e conversão numérica segura.
2. **Tratamento Inteligente de Erros do Pydantic**: Caso o backend rejeite uma submissão, a lista de erros em array do Pydantic é convertida em mensagens amigáveis em português:
   ```typescript
   if (Array.isArray(errData.detail)) {
     const msg = errData.detail.map((d: any) => `${d.loc.join('.')}: ${d.msg}`).join('\n');
     alert("Erro de Validação:\n" + msg);
   }
   ```
3. **Toast Notifications Reativas**: Um toast flutuante no canto superior direito notifica o sucesso do cadastro por 3.5 segundos, enquanto a tabela recarrega imediatamente em segundo plano.

---

## CAPÍTULO 16: O ASSISTENTE VIRTUAL DE IA INTEGRADO (TOOL CALLING)

Para não obstruir a visualização de relatórios e tabelas de dados, o assistente inteligente foi desacoplado de uma barra fixa e migrado para um **Widget Flutuante no Canto Inferior Direito** (`fixed bottom-6 right-6 z-50`).

O assistente opera sob o padrão **Tool Calling**:
- O usuário digita comandos em linguagem natural (ex: *"Qual o estoque atual de bambu tratado?"* ou *"Quantos caminhões estão disponíveis?"*).
- O backend consulta os repositórios correspondentes e devolve respostas consolidadas e contextualizadas.

---

# PARTE VII: QUALIDADE DE SOFTWARE, DEVOPS E OPERAÇÕES

## CAPÍTULO 17: DESENVOLVIMENTO ORIENTADO A TESTES (TDD COM PYTEST)

A integridade do sistema é garantida por uma bateria automatizada de testes cobrindo todas as camadas:

```bash
backend/tests/
├── conftest.py
└── unit/
    ├── test_auth_rbac.py          # Hashing bcrypt, JWT e proteção de rotas
    ├── test_product_domain.py     # Invariantes de entidades puras e cubagem
    ├── test_packing_service.py    # Algoritmo de 3D-BPP e overflow de carga
    ├── test_cadastros_api.py      # Endpoints REST e serialização Pydantic
    ├── test_full_modules.py       # Fluxo de compras, estoque, vendas e finanças
    └── test_health.py             # Health check e disponibilidade da API
```

**Resultado dos Testes Automatizados**:
$$\text{Sucesso: } 15/15 \text{ Testes Verdes (100\% Passing)}$$

---

## CAPÍTULO 18: CONTAINERIZAÇÃO E ORQUESTRAÇÃO COM DOCKER COMPOSE

O projeto é 100% conteinerizado através do arquivo `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=sqlite+aiosqlite:///./crm_bamboo.db
      - JWT_SECRET_KEY=bamboo_super_secret_corporate_key_2026
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped
```

---

## CAPÍTULO 19: GUIA OPERACIONAL DE EXECUÇÃO E MANUTENÇÃO

A pasta `scripts/` na raiz do projeto reúne atalhos prontos para a equipe de desenvolvimento e sustentação:

| Script | Finalidade Operacional |
| :--- | :--- |
| **`start_all.bat`** | Inicia a API FastAPI (Porta 8000) e o Frontend React (Porta 5173) simultaneamente. |
| **`start_backend.bat`** | Executa isoladamente o Uvicorn com hot-reload habilitado. |
| **`start_frontend.bat`** | Executa isoladamente o Vite Dev Server. |
| **`run_tests.bat`** | Dispara a suíte Pytest exibindo relatórios de cobertura. |
| **`setup_environment.bat`** | Instala automaticamente as dependências Python (`pip`) e Node (`npm`). |

---

# APÊNDICES

## APÊNDICE A: DICIONÁRIO GERAL DA API RESTFUL

```
AUTENTICAÇÃO & ACESSO
  POST   /api/v1/auth/login            Autenticação de credenciais e emissão de JWT
  POST   /api/v1/auth/register         Cadastro de novos operadores (Admin)
  GET    /api/v1/auth/me               Dados do operador autenticado no momento
  GET    /api/v1/auth/users            Listagem de todos os usuários corporativos (Admin)

CADASTROS MESTRES
  GET    /api/v1/products              Listagem de produtos e especificações físicas
  POST   /api/v1/products              Inclusão de novo produto no catálogo
  DELETE /api/v1/products/{id}         Exclusão de produto (Exclusivo Admin)
  GET    /api/v1/customers             Listagem de clientes corporativos e documentos
  POST   /api/v1/customers             Inclusão de novo cliente corporativo
  DELETE /api/v1/customers/{id}        Exclusão de cliente (Exclusivo Admin)
  GET    /api/v1/vehicles              Listagem de veículos de frota e cubagens
  POST   /api/v1/vehicles              Inclusão de novo veículo
  DELETE /api/v1/vehicles/{id}         Exclusão de veículo (Exclusivo Admin)

LOGÍSTICA & CUBAGEM 3D
  POST   /api/v1/logistics/pack-simulation  Simulação algorítmica de cubagem e empacotamento 3D

OPERAÇÕES INDUSTRIAIS & WMS
  GET    /api/v1/purchases             Histórico de ordens de compra
  POST   /api/v1/purchases             Emissão de novo pedido de suprimentos
  GET    /api/v1/imports               Rastreio de containers marítimos e alfândega
  POST   /api/v1/imports               Registro de novo container
  GET    /api/v1/stock/balances        Consulta de saldos de estoque por armazém
  GET    /api/v1/stock/movements       Livro de movimentações e rastreabilidade WMS
  POST   /api/v1/stock/movements       Registro de entrada ou saída física de estoque
  GET    /api/v1/sales                 Pipeline de pedidos comerciais
  POST   /api/v1/sales                 Emissão de pedido de venda
  GET    /api/v1/deliveries            Painel de despacho de cargas e rotas
  POST   /api/v1/deliveries            Início de viagem de entrega e romaneio
  GET    /api/v1/finance               Extrato consolidado de contas
  GET    /api/v1/finance/summary       Resumo executivo de receitas, despesas e saldo líquido
  POST   /api/v1/finance               Lançamento de conta a pagar ou receber
  GET    /api/v1/employees             Quadro funcional de colaboradores
  POST   /api/v1/employees             Admissão funcional de colaborador

INTELIGÊNCIA ARTIFICIAL
  POST   /api/v1/ai/chat               Prompt contextualizado e tool calling com dados do ERP
```

---

## APÊNDICE B: MATRIZ DE CÓDIGOS DE RESPOSTA HTTP

- `200 OK`: Consulta executada com sucesso ou autenticação deferida.
- `201 Created`: Novo registro persistido com sucesso no banco de dados.
- `400 Bad Request`: Invariante de domínio violada (ex: dimensões menores ou iguais a zero).
- `401 Unauthorized`: Token JWT ausente, expirado ou com assinatura inválida.
- `403 Forbidden`: Operador autenticado não possui papel suficiente na matriz RBAC.
- `404 Not Found`: Entidade ou recurso inexistente no banco de dados.
- `422 Unprocessable Entity`: Falha nos esquemas de tipagem ou validação do Pydantic v2.

---

## APÊNDICE C: GLOSSÁRIO DE ENGENHARIA E NEGÓCIO

- **3D-BPP (Three-Dimensional Bin Packing Problem)**: Desafio matemático combinatório de arranjo ideal de caixas tridimensionais em contêineres finitos.
- **Bounded Context**: Limite conceitual explícito dentro do qual um modelo de domínio de software se aplica de forma coesa (padrão Domain-Driven Design).
- **Clean Architecture**: Filosofia arquitetural focada no desacoplamento entre regras de negócio centrais e detalhes técnicos de frameworks ou bancos de dados.
- **Invariante de Domínio**: Condição que deve permanecer verdadeira em todos os momentos válidos do ciclo de vida de uma entidade.
- **Modular Monolith**: Padrão arquitetural em que todo o código é empacotado e executado como um único artefato, mas internamente dividido em módulos estritamente independentes.
- **RBAC (Role-Based Access Control)**: Mecanismo de restrição de acesso a recursos do sistema baseado nos papéis e responsabilidades atribuídos aos usuários.
- **Tara**: Peso do veículo ou contêiner vazio, essencial para o cálculo do peso líquido transportável.

---

```
================================================================================
                       FIM DO LIVRO OFICIAL DE ENGENHARIA
                              GRUPO BAMBOO - 2026
================================================================================
```
