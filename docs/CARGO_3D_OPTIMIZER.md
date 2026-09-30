# Motor de Otimização e Cubagem 3D de Carga (3D Bin Packing)

## 1. Contexto do Problema
O transporte de derivados de bambu (painéis estruturais, esteiras, mourões, fardos e vigas) apresenta um desafio logístico complexo devido à heterogeneidade de dimensões (itens compridos de 3 a 6 metros versus volumes cúbicos menores e pesados).

O carregamento manual tradicional em caminhões resulta comumente em:
- **Espaço ocioso (ar transportado)**: Baús com apenas 40% a 55% de cubagem aproveitada.
- **Sobrecarga de eixos**: Distribuição inadequada de massa gerando infrações nas balanças rodoviárias.
- **Avarias por empilhamento incorreto**: Caixas frágeis esmagadas sob itens densos.

---

## 2. Abordagem Matemática e Algoritmo
O módulo utiliza a biblioteca de otimização combinatória tridimensional **`py3dbp`**, baseada no clássico **Problema da Mochila Tridimensional (3D Bin Packing Problem - 3D-BPP)**, combinada com a heurística **Best-Fit Decreasing (BFD)**.

### 2.1. Formulação do Algoritmo
Para um conjunto de $N$ itens $I = \{i_1, i_2, \dots, i_n\}$ com dimensões $(w_i, h_i, d_i)$ e peso $m_i$, e um veículo $V$ com limites $(W, H, D)$ e peso máximo $M$:

1. **Ordenação Decrescente (Heurística de Volume/Densidade)**:
   $$\text{Prioridade}(i) = w_i \times h_i \times d_i \times \alpha + m_i \times \beta$$
2. **Avaliação das 6 Rotações Espaciais**:
   O algoritmo testa cada uma das 6 permutações ortogonais no espaço euclidiano 3D:
   - $(w, h, d), (w, d, h), (h, w, d), (h, d, w), (d, w, h), (d, h, w)$
   - Respeitando restrições operacionais (por exemplo: não virar itens que possuam indicador "este lado para cima").
3. **Detecção de Não-Sobreposição**:
   Dois itens $A$ e $B$ não colidem se e somente se:
   $$A.x + A.w \le B.x \quad\lor\quad B.x + B.w \le A.x \quad\lor$$
   $$A.y + A.h \le B.y \quad\lor\quad B.y + B.h \le A.y \quad\lor$$
   $$A.z + A.d \le B.z \quad\lor\quad B.z + B.d \le A.z$$
4. **Verificação de Limite de Massa**:
   $$\sum_{k \in \text{Itens Alocados}} m_k \le M$$

---

## 3. Métricas de Desempenho Retornadas
- **Aproveitamento de Volume (%)**:
  $$\eta_{\text{vol}} = \frac{\sum_{i \in \text{Alocados}} (w_i \times h_i \times d_i)}{W \times H \times D} \times 100\%$$
- **Aproveitamento de Carga Útil (%)**:
  $$\eta_{\text{peso}} = \frac{\sum_{i \in \text{Alocados}} m_i}{M} \times 100\%$$
- **Lista de Coordenadas $(x, y, z)$**:
  Posição espacial exata de cada caixa no piso do baú para guiar visualmente o operador de empilhadeira ou a equipe de carregamento na doca.
