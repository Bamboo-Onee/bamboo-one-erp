# Especificação da API RESTful: Bamboo One ERP

**Base URL**: `http://localhost:8000/api/v1`  
**Swagger UI interativo**: `http://localhost:8000/docs`  
**ReDoc**: `http://localhost:8000/redoc`  
**Autenticação**: Header padrão HTTP `Authorization: Bearer <TOKEN_JWT>`

---

## 1. Módulo de Autenticação & Usuários (`/auth`)

### 1.1. Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Acesso**: Público
- **Payload de Requisição**:
  ```json
  {
    "email": "admin@bamboo.com",
    "password": "admin123"
  }
  ```
- **Resposta de Sucesso (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "Administrador Master",
      "email": "admin@bamboo.com",
      "role": "ADMIN"
    }
  }
  ```

### 1.2. Usuário Autenticado Atual
- **Endpoint**: `GET /api/v1/auth/me`
- **Acesso**: Qualquer usuário autenticado

### 1.3. Cadastro de Usuário
- **Endpoint**: `POST /api/v1/auth/register`
- **Acesso**: Restrito a `ADMIN`

---

## 2. Cadastros Mestres (`/products`, `/customers`, `/vehicles`)

### 2.1. Produtos
- **Listar**: `GET /api/v1/products` (Qualquer perfil)
- **Criar**: `POST /api/v1/products` (Qualquer perfil / Admin)
  ```json
  {
    "name": "Bambu Tratado Premium 3m",
    "sku": "BMB-3M-TRAT",
    "width": 0.15,
    "height": 0.15,
    "depth": 3.0,
    "weight": 5.2,
    "category": "Materia-Prima"
  }
  ```
- **Excluir**: `DELETE /api/v1/products/{id}` (Restrito a `ADMIN`)

### 2.2. Clientes
- **Listar**: `GET /api/v1/customers`
- **Criar**: `POST /api/v1/customers`
  ```json
  {
    "name": "EcoConstrucoes Sustentaveis Ltda",
    "document": "12.345.678/0001-90",
    "email": "compras@ecoconstrucoes.com.br",
    "phone": "(11) 98765-4321",
    "city": "Sao Paulo"
  }
  ```

### 2.3. Veículos / Frotas
- **Listar**: `GET /api/v1/vehicles`
- **Criar**: `POST /api/v1/vehicles`
  ```json
  {
    "plate": "BMB-2026",
    "model": "Carreta Scania R450",
    "max_weight": 25000.0,
    "max_volume": 90.0
  }
  ```

---

## 3. Otimizador de Carga 3D (`/logistics`)

### 3.1. Simulação de Cubagem 3D
- **Endpoint**: `POST /api/v1/logistics/pack`
- **Acesso**: `ADMIN`, `LOGISTICA`
- **Payload de Requisição**:
  ```json
  {
    "container": {
      "name": "Bau Truck 45m3",
      "width": 2.4,
      "height": 2.6,
      "depth": 7.2,
      "max_weight": 14000.0
    },
    "items": [
      {
        "name": "Fardo Painel Bambu G",
        "width": 1.2,
        "height": 0.8,
        "depth": 2.0,
        "weight": 150.0,
        "quantity": 10
      }
    ]
  }
  ```
- **Resposta de Sucesso (200 OK)**:
  ```json
  {
    "fitted_items": [...],
    "unfitted_items": [],
    "volume_utilization_pct": 74.2,
    "weight_utilization_pct": 68.5,
    "status": "TOTAL_FIT"
  }
  ```

---

## 4. Módulos Operacionais Adicionais

| Módulo | Endpoint Base | Operações Disponíveis |
| :--- | :--- | :--- |
| **Compras** | `/api/v1/purchases` | `GET` (Listar), `POST` (Novo Pedido de Fornecedor) |
| **Importações** | `/api/v1/imports` | `GET` (Listar Containers), `POST` (Registrar Container) |
| **Estoque** | `/api/v1/stock/movements` | `GET` (Histórico), `POST` (Entrada/Saída de Material) |
| **Vendas (CRM)** | `/api/v1/sales` | `GET` (Listar Pedidos), `POST` (Emitir Pedido de Venda) |
| **Expedição** | `/api/v1/deliveries` | `GET` (Rastreio de Entregas), `POST` (Despachar Carga) |
| **Financeiro** | `/api/v1/finance` | `GET` (Extrato), `POST` (Lançamento Receita/Despesa) |
| **RH** | `/api/v1/employees` | `GET` (Quadro Funcional), `POST` (Admissão de Colaborador) |
| **IA Corporativa**| `/api/v1/ai/query` | `POST` (Prompt contextualizado para o assistente virtual) |
