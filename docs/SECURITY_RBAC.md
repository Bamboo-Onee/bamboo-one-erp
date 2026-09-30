# Política de Segurança e Controle de Acesso Baseado em Papéis (RBAC)

## 1. Princípios de Segurança da Informação
A segurança do **Bamboo One** é estruturada seguindo as melhores práticas recomendadas pela **OWASP Top 10** e o padrão de maturidade **ASVS (Application Security Verification Standard)**:
1. **Defesa em Profundidade**: Validação tanto na camada de apresentação (interface React) quanto na camada de serviços do backend (FastAPI dependency injection).
2. **Princípio do Menor Privilégio**: Usuários têm acesso estritamente aos módulos pertinentes às suas atribuições operacionais.
3. **Criptografia Forte e Segura**: Nenhuma credencial em texto plano transita ou é armazenada desprotegida.

---

## 2. Autenticação JWT (RFC 7519)
- **Algoritmo**: `HMAC-SHA256` (`HS256`).
- **Assinatura**: Chave secreta criptográfica configurável via variável de ambiente `JWT_SECRET_KEY`.
- **Validade do Token**: 60 minutos por padrão (`ACCESS_TOKEN_EXPIRE_MINUTES=60`).
- **Estrutura dos Claims do Payload**:
  ```json
  {
    "sub": "admin@bamboo.com",
    "role": "ADMIN",
    "name": "Administrador Master",
    "exp": 1788447800,
    "iat": 1788444200
  }
  ```

---

## 3. Matriz de Permissões (RBAC)

| Módulo / Funcionalidade | ADMIN | LOGISTICA | VENDAS | COMPRAS | FINANCEIRO |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Painel Geral (Dashboard)** | ✅ Total | ✅ Total | ✅ Total | ✅ Total | ✅ Total |
| **Cadastros Mestres (Produtos/Clientes/Frotas)** | ✅ Total | 👁️ Visualizar | 👁️ Visualizar | 👁️ Visualizar | 👁️ Visualizar |
| **Exclusão de Cadastros Mestres** | ✅ Total | ❌ Negado | ❌ Negado | ❌ Negado | ❌ Negado |
| **Otimizador Logístico 3D** | ✅ Total | ✅ Total | ❌ Negado | ❌ Negado | ❌ Negado |
| **Expedição e Rastreio de Entregas** | ✅ Total | ✅ Total | 👁️ Rastrear | ❌ Negado | ❌ Negado |
| **WMS / Movimentações de Estoque** | ✅ Total | ✅ Total | 👁️ Consultar | 👁️ Consultar | ❌ Negado |
| **Pipeline Comercial & Vendas (CRM)** | ✅ Total | ❌ Negado | ✅ Total | ❌ Negado | 👁️ Faturamento |
| **Compras & Suprimentos** | ✅ Total | ❌ Negado | ❌ Negado | ✅ Total | 👁️ Contas a Pagar |
| **Importações de Containers** | ✅ Total | ✅ Total | ❌ Negado | ✅ Total | 👁️ Custos Aduana |
| **Fluxo Financeiro & Contas** | ✅ Total | ❌ Negado | ❌ Negado | ❌ Negado | ✅ Total |
| **Recursos Humanos & Colaboradores** | ✅ Total | ❌ Negado | ❌ Negado | ❌ Negado | ❌ Negado |
| **Gestão de Usuários e Permissões** | ✅ Total | ❌ Negado | ❌ Negado | ❌ Negado | ❌ Negado |

---

## 4. Contas Padrão de Demonstração (Seed)

Para homologação e testes imediatos, o sistema já é inicializado com três contas corporativas pré-configuradas:

| Papel | E-mail | Senha Padrão | Escopo de Demonstração |
| :--- | :--- | :--- | :--- |
| 🛡️ **Administrador** | `admin@bamboo.com` | `admin123` | Acesso irrestrito a todos os 11 módulos e ações administrativas. |
| 🚚 **Logística** | `logistica@bamboo.com` | `logistica123` | Focado em Frotas, 3D Bin Packing, Estoque e Expedição. |
| 💼 **Vendas** | `vendas@bamboo.com` | `vendas123` | Focado em CRM Comercial, Catálogo de Produtos e Clientes. |
