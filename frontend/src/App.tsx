import React, { useState, useEffect } from 'react';
import './index.css';

type PageId = 
  | 'dashboard'
  | 'cadastros'
  | 'compras'
  | 'importacoes'
  | 'estoque'
  | 'vendas'
  | 'entregas'
  | 'optimizer'
  | 'financeiro'
  | 'rh'
  | 'relatorios';

type UserRole = 'ADMIN' | 'LOGISTICA' | 'VENDAS' | 'COMPRAS' | 'FINANCEIRO';

interface AuthUser {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

const API_BASE = "http://127.0.0.1:8000/api/v1";

export default function App() {
  // Autenticação & Sessão
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('bamboo_token'));
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(() => {
    const saved = localStorage.getItem('bamboo_user');
    return saved ? JSON.parse(saved) : null;
  });

  // Formulário de Login
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState('');

  // Notificações Toast
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Navegação
  const [activePage, setActivePage] = useState<PageId>('dashboard');
  const [activeCadTab, setActiveCadTab] = useState<'produtos' | 'clientes' | 'veiculos'>('produtos');

  // Estados dos dados de todos os módulos
  const [products, setProducts] = useState<any[]>([]);
  const [customers, setCustomers] = useState<any[]>([]);
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [purchases, setPurchases] = useState<any[]>([]);
  const [imports, setImports] = useState<any[]>([]);
  const [stockBalances, setStockBalances] = useState<any[]>([]);
  const [salesOrders, setSalesOrders] = useState<any[]>([]);
  const [deliveries, setDeliveries] = useState<any[]>([]);
  const [financialEntries, setFinancialEntries] = useState<any[]>([]);
  const [financialSummary, setFinancialSummary] = useState({ total_payable: 0, total_receivable: 0, projected_balance: 0 });
  const [employees, setEmployees] = useState<any[]>([]);

  // Estados dos 10 Modais de Criação
  const [showProductModal, setShowProductModal] = useState(false);
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [showVehicleModal, setShowVehicleModal] = useState(false);
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showStockModal, setShowStockModal] = useState(false);
  const [showSaleModal, setShowSaleModal] = useState(false);
  const [showDeliveryModal, setShowDeliveryModal] = useState(false);
  const [showFinanceModal, setShowFinanceModal] = useState(false);
  const [showEmployeeModal, setShowEmployeeModal] = useState(false);

  // Estados de Formulários com valores padrão limpos
  const [newProduct, setNewProduct] = useState({ sku: '', name: '', category: 'Embalagens', price: 150.0, weight_kg: 25.0, length_m: 1.2, width_m: 0.8, height_m: 0.7, stackable: true, fragile: false });
  const [newCustomer, setNewCustomer] = useState({ name: '', document: '', email: '', phone: '', delivery_address: '', credit_limit: 25000.0 });
  const [newVehicle, setNewVehicle] = useState({ plate: '', model: 'Truck Baú', body_type: 'Baú Fechado', length_m: 8.2, width_m: 2.45, height_m: 2.6, max_payload_kg: 14000.0 });
  const [newPurchase, setNewPurchase] = useState({ supplier_name: '', product_name: 'Caixa Master A', product_sku: 'BAM-0082', quantity: 10, unit_price: 120.0 });
  const [newImport, setNewImport] = useState({ supplier_name: 'Bamboo Trade Asia Ltd', bl_number: 'BL-CNSHA-2026-88', container_number: 'MSCU-90214-5', origin_port: 'Shanghai (CNSHA)', destination_port: 'Santos (BRSSZ)', eta: '28/09/2026', total_usd: 35000.0, landed_cost_brl: 198000.0 });
  const [newStockMov, setNewStockMov] = useState({ movement_type: 'Entrada', product_sku: 'BAM-0082', product_name: 'Caixa Master A', warehouse_name: 'CD Principal', quantity: 25, reason: 'Recebimento de Lote de Compra' });
  const [newSale, setNewSale] = useState({ customer_name: '', representative_name: 'Vendas Diretas', product_name: 'Caixa Master A', product_sku: 'BAM-0082', quantity: 5, unit_price: 250.0 });
  const [newDelivery, setNewDelivery] = useState({ customer_name: '', destination_city: 'Recife / PE', total_volumes: 20, vehicle_plate: 'BRA-2E19', status: 'Carga pronta' });
  const [newFinance, setNewFinance] = useState({ entry_type: 'PAGAR', description: 'Frete Operacional Interestadual', entity_name: 'Transportadora Líder', category: 'Logística', amount: 4800.0, due_date: '15/10/2026', status: 'Pendente' });
  const [newEmployee, setNewEmployee] = useState({ name: '', cpf: '', role: 'Operador de Empilhadeira', department: 'Expedição', salary: 3800.0, admission_date: '01/09/2026', status: 'Ativo' });

  // AI Agent Chat
  const [isAiOpen, setIsAiOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiMessages, setAiMessages] = useState<{ sender: 'user' | 'agent'; text: string }[]>([
    { sender: 'agent', text: 'Olá! Sou o Assistente de Inteligência Logística do Grupo Bamboo. Posso calcular a cubagem do caminhão, simular empacotamento 3D ou consultar dados operacionais. Como posso ajudar?' }
  ]);

  // Otimizador de Carga 3D
  const [truckType, setTruckType] = useState<'truck' | 'toco' | 'carreta'>('truck');
  const [calcLoading, setCalcLoading] = useState(false);
  const [calcResult, setCalcResult] = useState<any>({
    truck_name: 'Truck Baú',
    status: 'Pronto para simulação',
    is_viable: true,
    volumetric_efficiency_pct: 86.4,
    weight_efficiency_pct: 74.2,
    fitted_weight_kg: 10400,
    max_payload_kg: 14000,
    total_items_allocated: '44/44',
    alert_message: '✓ Clique em "Calcular Melhor Plano Matemático" para invocar o motor py3dbp.'
  });

  // Headers com autenticação JWT
  const authHeaders = () => ({
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  });

  // Login handler
  const handleLogin = async (e?: React.FormEvent, customEmail?: string, customPassword?: string) => {
    if (e) e.preventDefault();
    setLoginLoading(true);
    setLoginError('');

    const email = customEmail || loginEmail;
    const password = customPassword || loginPassword;

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (res.ok) {
        const data = await res.json();
        setToken(data.access_token);
        setCurrentUser(data.user);
        localStorage.setItem('bamboo_token', data.access_token);
        localStorage.setItem('bamboo_user', JSON.stringify(data.user));
      } else {
        const err = await res.json();
        setLoginError(err.detail || 'Falha ao autenticar.');
      }
    } catch (err) {
      setLoginError('Não foi possível conectar ao servidor backend.');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setCurrentUser(null);
    localStorage.removeItem('bamboo_token');
    localStorage.removeItem('bamboo_user');
  };

  // Carregador central de dados da API
  const fetchAllData = async () => {
    try {
      const [pRes, cRes, vRes, poRes, impRes, stkRes, saleRes, delRes, finRes, finSumRes, empRes] = await Promise.all([
        fetch(`${API_BASE}/products`, { headers: authHeaders() }),
        fetch(`${API_BASE}/customers`, { headers: authHeaders() }),
        fetch(`${API_BASE}/vehicles`, { headers: authHeaders() }),
        fetch(`${API_BASE}/purchases`, { headers: authHeaders() }),
        fetch(`${API_BASE}/imports`, { headers: authHeaders() }),
        fetch(`${API_BASE}/stock/balances`, { headers: authHeaders() }),
        fetch(`${API_BASE}/sales`, { headers: authHeaders() }),
        fetch(`${API_BASE}/deliveries`, { headers: authHeaders() }),
        fetch(`${API_BASE}/finance`, { headers: authHeaders() }),
        fetch(`${API_BASE}/finance/summary`, { headers: authHeaders() }),
        fetch(`${API_BASE}/employees`, { headers: authHeaders() })
      ]);
      if (pRes.ok) setProducts(await pRes.json());
      if (cRes.ok) setCustomers(await cRes.json());
      if (vRes.ok) setVehicles(await vRes.json());
      if (poRes.ok) setPurchases(await poRes.json());
      if (impRes.ok) setImports(await impRes.json());
      if (stkRes.ok) setStockBalances(await stkRes.json());
      if (saleRes.ok) setSalesOrders(await saleRes.json());
      if (delRes.ok) setDeliveries(await delRes.json());
      if (finRes.ok) setFinancialEntries(await finRes.json());
      if (finSumRes.ok) setFinancialSummary(await finSumRes.json());
      if (empRes.ok) setEmployees(await empRes.json());
    } catch (e) {
      console.warn("Aguardando backend:", e);
    }
  };

  useEffect(() => {
    if (token) {
      fetchAllData();
    }
  }, [token]);

  // Envio genérico com tratamento detalhado de erros e confirmação via toast
  const handleGenericSubmit = async (url: string, payload: any, closeFn: () => void, successMsg?: string) => {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        closeFn();
        setToastMessage(successMsg || "Registro criado com sucesso no banco de dados!");
        setTimeout(() => setToastMessage(null), 3500);
        fetchAllData();
      } else {
        const err = await res.json();
        let msg = "Erro ao processar criação.";
        if (typeof err.detail === 'string') {
          msg = err.detail;
        } else if (Array.isArray(err.detail)) {
          msg = err.detail.map((d: any) => `${d.loc?.join('.')}: ${d.msg}`).join('\n');
        }
        alert(`Não foi possível salvar:\n${msg}`);
      }
    } catch (err) {
      alert("Falha na comunicação com o servidor backend.");
    }
  };

  // Exclusão genérica
  const handleGenericDelete = async (url: string, label: string) => {
    if (!confirm(`Deseja realmente excluir ${label}?`)) return;
    try {
      const res = await fetch(url, { method: 'DELETE', headers: authHeaders() });
      if (res.ok) {
        setToastMessage(`${label} excluído com sucesso!`);
        setTimeout(() => setToastMessage(null), 3000);
        fetchAllData();
      } else {
        const err = await res.json();
        alert(err.detail || "Erro ao excluir");
      }
    } catch (e) {
      alert("Falha na comunicação com o servidor.");
    }
  };

  // Chat com AI Agent
  const handleSendAiMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiPrompt.trim()) return;

    const userText = aiPrompt;
    setAiMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setAiPrompt('');
    setAiLoading(true);

    try {
      const res = await fetch(`${API_BASE}/ai/chat`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ prompt: userText, truck_name: 'Truck Baú' })
      });
      if (res.ok) {
        const data = await res.json();
        setAiMessages(prev => [...prev, { sender: 'agent', text: data.reply }]);
      }
    } catch (err) {
      setAiMessages(prev => [...prev, { sender: 'agent', text: "Erro ao conectar com o serviço de IA." }]);
    } finally {
      setAiLoading(false);
    }
  };

  // Cálculo de 3D Packing
  const handleCalculatePacking = async () => {
    setCalcLoading(true);
    let payload = {
      truck_name: 'Truck Baú',
      truck_length: 8.2,
      truck_width: 2.45,
      truck_height: 2.6,
      truck_max_weight_kg: 14000.0,
      items: [
        { name: "Caixa Master A", quantity: 24, length_m: 1.2, width_m: 0.8, height_m: 0.7, weight_kg: 185.0 },
        { name: "Pallet B", quantity: 8, length_m: 1.0, width_m: 1.0, height_m: 1.45, weight_kg: 410.0 },
        { name: "Volume Frágil", quantity: 12, length_m: 0.7, width_m: 0.55, height_m: 0.6, weight_kg: 76.0 }
      ]
    };
    if (truckType === 'toco') {
      payload.truck_name = 'Toco';
      payload.truck_length = 6.2;
      payload.truck_width = 2.4;
      payload.truck_height = 2.45;
      payload.truck_max_weight_kg = 8500.0;
    } else if (truckType === 'carreta') {
      payload.truck_name = 'Carreta LS';
      payload.truck_length = 13.5;
      payload.truck_width = 2.48;
      payload.truck_height = 2.75;
      payload.truck_max_weight_kg = 28000.0;
    }

    try {
      const res = await fetch(`${API_BASE}/logistics/pack-simulation`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(payload)
      });
      if (res.ok) setCalcResult(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setCalcLoading(false);
    }
  };

  // Helpers de RBAC
  const hasRole = (...allowed: UserRole[]) => {
    if (!currentUser) return false;
    if (currentUser.role === 'ADMIN') return true;
    return allowed.includes(currentUser.role);
  };

  // ==============================================================================
  // TELA DE LOGIN (QUANDO NÃO AUTENTICADO)
  // ==============================================================================
  if (!token || !currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0c202b] via-[#102b3a] to-[#183d4e] flex items-center justify-center p-4 text-[#18313f] font-sans">
        <div className="bg-white rounded-2xl max-w-md w-full p-8 shadow-2xl border border-slate-200">
          <div className="text-center mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#55c6b0] to-[#5fa6c9] grid place-items-center text-[#082431] font-black text-xl mx-auto mb-3 shadow-md">
              B
            </div>
            <h1 className="text-2xl font-black text-[#102b3a]">Bamboo One</h1>
            <p className="text-xs text-[#72818a] mt-1">Sistema Integrado de Gestão • Grupo Bamboo</p>
          </div>

          {loginError && (
            <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold">
              ⚠️ {loginError}
            </div>
          )}

          <form onSubmit={(e) => handleLogin(e)} className="space-y-4 text-xs">
            <div>
              <label className="font-bold text-[#60717a] block mb-1">E-mail Corporativo</label>
              <input 
                type="email"
                required
                placeholder="seu.email@bamboo.com"
                value={loginEmail}
                onChange={e => setLoginEmail(e.target.value)}
                className="w-full border border-slate-300 rounded-lg p-2.5 text-xs focus:outline-none focus:border-[#1e7a8c]"
              />
            </div>

            <div>
              <label className="font-bold text-[#60717a] block mb-1">Senha</label>
              <input 
                type="password"
                required
                placeholder="••••••••"
                value={loginPassword}
                onChange={e => setLoginPassword(e.target.value)}
                className="w-full border border-slate-300 rounded-lg p-2.5 text-xs focus:outline-none focus:border-[#1e7a8c]"
              />
            </div>

            <button 
              type="submit" 
              disabled={loginLoading}
              className="w-full bg-[#1e7a8c] hover:bg-[#176270] disabled:bg-slate-300 text-white font-bold py-2.5 rounded-lg shadow-md transition-all text-xs cursor-pointer"
            >
              {loginLoading ? "Autenticando..." : "Entrar no Sistema"}
            </button>
          </form>

          {/* ATALHOS RÁPIDOS DE DEMONSTRAÇÃO */}
          <div className="mt-6 pt-5 border-t border-slate-200 text-center">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2.5">
              Acesso Rápido de Demonstração (RBAC)
            </span>
            <div className="grid grid-cols-3 gap-2">
              <button 
                onClick={() => handleLogin(undefined, 'admin@bamboo.com', 'admin123')}
                className="p-2 border border-purple-200 hover:border-purple-400 bg-purple-50/50 hover:bg-purple-100/50 rounded-lg text-left transition-colors cursor-pointer"
              >
                <b className="block text-[11px] text-purple-900">🛡️ Admin</b>
                <span className="text-[9px] text-purple-700">Acesso Total</span>
              </button>
              <button 
                onClick={() => handleLogin(undefined, 'logistica@bamboo.com', 'logistica123')}
                className="p-2 border border-teal-200 hover:border-teal-400 bg-teal-50/50 hover:bg-teal-100/50 rounded-lg text-left transition-colors cursor-pointer"
              >
                <b className="block text-[11px] text-teal-900">🚚 Logística</b>
                <span className="text-[9px] text-teal-700">Frota & 3D</span>
              </button>
              <button 
                onClick={() => handleLogin(undefined, 'vendas@bamboo.com', 'vendas123')}
                className="p-2 border border-amber-200 hover:border-amber-400 bg-amber-50/50 hover:bg-amber-100/50 rounded-lg text-left transition-colors cursor-pointer"
              >
                <b className="block text-[11px] text-amber-900">💼 Vendas</b>
                <span className="text-[9px] text-amber-700">Comercial</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ==============================================================================
  // APLICAÇÃO AUTENTICADA (COM CONTROLE RBAC)
  // ==============================================================================
  return (
    <div className="grid grid-cols-[250px_1fr] min-h-screen font-sans bg-[#f4f7f8] text-[#18313f] relative">
      {/* TOAST DE FEEDBACK DE SUCESSO */}
      {toastMessage && (
        <div className="fixed top-5 right-5 z-[9999] bg-emerald-600 text-white px-5 py-3 rounded-xl shadow-2xl font-bold text-xs flex items-center gap-2.5 animate-in slide-in-from-top-3">
          <span>✓</span>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* SIDEBAR */}
      <aside className="bg-gradient-to-b from-[#102b3a] to-[#0b2230] text-white p-5 sticky top-0 h-screen overflow-y-auto">
        <div className="flex items-center gap-2.5 pb-5 font-black text-lg">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#55c6b0] to-[#5fa6c9] grid place-items-center text-[#082431] font-black text-sm">
            B
          </div>
          <div>
            Bamboo One
            <div className="text-[11px] text-[#b8cad2] font-medium tracking-normal">Gestão Integrada</div>
          </div>
        </div>

        <nav className="space-y-1">
          <div className="px-2 pt-3 pb-1 text-[#7fa0ad] text-[11px] font-bold uppercase tracking-wider">Visão</div>
          <button onClick={() => setActivePage('dashboard')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'dashboard' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>▦</span> <span>Visão geral</span>
          </button>

          <div className="px-2 pt-4 pb-1 text-[#7fa0ad] text-[11px] font-bold uppercase tracking-wider">Operações</div>
          <button onClick={() => setActivePage('cadastros')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'cadastros' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>◫</span> <span>Cadastros mestres</span>
          </button>
          
          <button onClick={() => setActivePage('compras')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'compras' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>🛒</span> <span>Compras ({purchases.length})</span>
          </button>

          <button onClick={() => setActivePage('importacoes')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'importacoes' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>⚓</span> <span>Importações ({imports.length})</span>
          </button>

          <button onClick={() => setActivePage('estoque')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'estoque' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>▣</span> <span>Estoque ({stockBalances.length})</span>
          </button>

          <button onClick={() => setActivePage('vendas')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'vendas' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>◈</span> <span>Comercial ({salesOrders.length})</span>
          </button>

          <button onClick={() => setActivePage('entregas')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'entregas' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>▤</span> <span>Produção & Entregas ({deliveries.length})</span>
          </button>

          <button onClick={() => setActivePage('optimizer')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'optimizer' ? 'bg-[#183d4e] text-white font-bold ring-1 ring-[#55c6b0]/50' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span className="text-[#55c6b0]">✦</span> <span className="font-bold text-[#55c6b0]">Otimizador de Carga 3D</span>
          </button>

          <div className="px-2 pt-4 pb-1 text-[#7fa0ad] text-[11px] font-bold uppercase tracking-wider">Administrativo</div>
          
          <button onClick={() => setActivePage('financeiro')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'financeiro' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>R$</span> <span>Financeiro ({financialEntries.length})</span>
          </button>

          <button onClick={() => setActivePage('rh')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'rh' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>♙</span> <span>RH ({employees.length})</span>
          </button>

          <button onClick={() => setActivePage('relatorios')} className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${activePage === 'relatorios' ? 'bg-[#183d4e] text-white font-bold' : 'text-[#d8e5e9] hover:bg-[#183d4e]/60'}`}>
            <span>▥</span> <span>Relatórios & Auditoria</span>
          </button>
        </nav>
      </aside>

      {/* MAIN CONTENT */}
      <main className="min-w-0">
        <header className="h-[68px] bg-white border-b border-[#dce5e8] flex items-center justify-between px-7 sticky top-0 z-10">
          <div className="w-[min(460px,45vw)] relative">
            <span className="absolute left-3 top-2.5 text-[#7f8c93]">⌕</span>
            <input type="text" placeholder="Buscar produto, pedido, fornecedor, BL, cliente..." className="w-full pl-9 pr-3.5 py-2 border border-[#dce5e8] rounded-lg bg-[#f8fafb] text-sm focus:outline-none focus:border-[#1e7a8c]" />
          </div>

          {/* PERFIL DO USUÁRIO COM BADGE RBAC E LOGOUT */}
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="font-bold text-sm text-[#18313f]">{currentUser.name}</div>
              <div className="flex items-center gap-1.5 justify-end">
                <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${
                  currentUser.role === 'ADMIN' ? 'bg-purple-100 text-purple-800' :
                  currentUser.role === 'LOGISTICA' ? 'bg-teal-100 text-teal-800' :
                  currentUser.role === 'VENDAS' ? 'bg-amber-100 text-amber-800' :
                  'bg-slate-100 text-slate-800'
                }`}>
                  {currentUser.role}
                </span>
                <span className="text-[11px] text-[#72818a]">• Grupo Bamboo</span>
              </div>
            </div>
            
            <div className="w-9 h-9 rounded-full bg-[#d9e9ed] grid place-items-center font-bold text-xs text-[#18313f]">
              {currentUser.name.slice(0, 2).toUpperCase()}
            </div>

            <button 
              onClick={handleLogout}
              title="Encerrar Sessão Segura"
              className="ml-2 text-xs font-bold text-rose-600 hover:text-rose-800 p-2 rounded-lg hover:bg-rose-50 transition-colors cursor-pointer"
            >
              Sair ➔
            </button>
          </div>
        </header>

        <div className="p-7">
          {/* DASHBOARD */}
          {activePage === 'dashboard' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-5">
                <div>
                  <h1 className="text-2xl font-black">Visão geral</h1>
                  <div className="text-xs text-[#72818a] mt-1">
                    Operação integrada • Conectado como <b>{currentUser.name} ({currentUser.role})</b>
                  </div>
                </div>
                <button onClick={() => setActivePage('cadastros')} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-sm px-4 py-2.5 rounded-lg shadow-sm transition-colors cursor-pointer">
                  Acessar Cadastros ➔
                </button>
              </div>

              <div className="grid grid-cols-4 gap-3.5 mb-5">
                <div className="bg-white border border-[#dce5e8] rounded-xl p-4 shadow-sm">
                  <div className="text-xs text-[#72818a]">Pedidos de compra abertos</div>
                  <div className="text-2xl font-black my-1">{purchases.length}</div>
                  <div className="text-xs text-[#2e9e83] font-medium">Fluxo Integrado c/ Estoque</div>
                </div>
                <div className="bg-white border border-[#dce5e8] rounded-xl p-4 shadow-sm">
                  <div className="text-xs text-[#72818a]">Importações em trânsito</div>
                  <div className="text-2xl font-black my-1">{imports.length}</div>
                  <div className="text-xs text-[#c77b29] font-medium">Com Landed Cost Rateado</div>
                </div>
                <div className="bg-white border border-[#dce5e8] rounded-xl p-4 shadow-sm">
                  <div className="text-xs text-[#72818a]">Saldo a Receber Previsto</div>
                  <div className="text-2xl font-black my-1 text-[#27755f]">
                    R$ {financialSummary.total_receivable ? financialSummary.total_receivable.toLocaleString('pt-BR') : '0'}
                  </div>
                  <div className="text-xs text-[#2e9e83] font-medium">Contas Integradas a Vendas</div>
                </div>
                <div className="bg-white border border-[#dce5e8] rounded-xl p-4 shadow-sm">
                  <div className="text-xs text-[#72818a]">Colaboradores Ativos</div>
                  <div className="text-2xl font-black my-1">{employees.length}</div>
                  <div className="text-xs text-[#1e7a8c] font-medium">RH & Folha Integrada</div>
                </div>
              </div>

              {/* OPERAÇÕES RECENTES & ATENÇÃO */}
              <div className="grid grid-cols-[1.4fr_0.85fr] gap-4 mb-5">
                <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm">
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-base font-bold">Atenção Operacional & Cargas</h2>
                    <span className="text-[11px] bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full font-bold">Em andamento</span>
                  </div>
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                        <th className="py-2 px-2">Documento</th>
                        <th className="py-2 px-2">Entidade / Rota</th>
                        <th className="py-2 px-2">Módulo</th>
                        <th className="py-2 px-2">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#edf2f3]">
                      <tr className="hover:bg-slate-50">
                        <td className="py-2.5 px-2 font-bold text-[#1e7a8c]">VEN-2026-0081</td>
                        <td className="py-2.5 px-2">Cliente Atlântico Ltda</td>
                        <td className="py-2.5 px-2 text-[#72818a]">Comercial</td>
                        <td className="py-2.5 px-2"><span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full text-[10px] font-bold">Em separação</span></td>
                      </tr>
                      <tr className="hover:bg-slate-50">
                        <td className="py-2.5 px-2 font-bold text-[#1e7a8c]">IMP-2026-041</td>
                        <td className="py-2.5 px-2">Shanghai Port (CNSHA)</td>
                        <td className="py-2.5 px-2 text-[#72818a]">Importação</td>
                        <td className="py-2.5 px-2"><span className="bg-sky-100 text-sky-800 px-2 py-0.5 rounded-full text-[10px] font-bold">Em trânsito</span></td>
                      </tr>
                      <tr className="hover:bg-slate-50">
                        <td className="py-2.5 px-2 font-bold text-[#1e7a8c]">ENT-00618</td>
                        <td className="py-2.5 px-2">Recife / PE • 44 vol</td>
                        <td className="py-2.5 px-2 text-[#72818a]">Expedição</td>
                        <td className="py-2.5 px-2"><span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full text-[10px] font-bold">Carga pronta</span></td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm flex flex-col justify-between">
                  <h2 className="text-base font-bold mb-2">Acesso Rápido a Rotinas</h2>
                  <div className="space-y-2">
                    <button 
                      onClick={() => setActivePage('optimizer')}
                      className="w-full text-left p-2.5 border border-[#1e7a8c]/30 rounded-lg bg-[#eef7f8] hover:bg-[#e2f2f4] flex items-center justify-between transition-colors cursor-pointer"
                    >
                      <div>
                        <strong className="block text-xs text-[#1e7a8c]">✦ Otimizador de Carga 3D</strong>
                        <span className="text-[10px] text-[#1e7a8c]/80">Cálculo matemático de baú</span>
                      </div>
                      <span className="text-[#1e7a8c] font-bold">➔</span>
                    </button>
                    <button 
                      onClick={() => { setActivePage('cadastros'); setActiveCadTab('produtos'); setShowProductModal(true); }}
                      className="w-full text-left p-2.5 border border-[#dce5e8] rounded-lg bg-[#fbfcfc] hover:bg-slate-100 flex items-center justify-between transition-colors cursor-pointer"
                    >
                      <div>
                        <strong className="block text-xs">+ Cadastrar Novo Produto</strong>
                        <span className="text-[10px] text-[#72818a]">Base mestre com cubagem</span>
                      </div>
                      <span className="text-slate-400 font-bold">➔</span>
                    </button>
                    <button 
                      onClick={() => setShowSaleModal(true)}
                      className="w-full text-left p-2.5 border border-[#dce5e8] rounded-lg bg-[#fbfcfc] hover:bg-slate-100 flex items-center justify-between transition-colors cursor-pointer"
                    >
                      <div>
                        <strong className="block text-xs">+ Emitir Novo Pedido de Venda</strong>
                        <span className="text-[10px] text-[#72818a]">Comercial integrado ao estoque</span>
                      </div>
                      <span className="text-slate-400 font-bold">➔</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* ATALHOS */}
              <div className="grid grid-cols-4 gap-3">
                <div onClick={() => setActivePage('compras')} className="bg-white border border-[#dce5e8] p-4 rounded-xl shadow-sm hover:border-[#1e7a8c] cursor-pointer">
                  <strong className="block text-sm font-bold">🛒 Compras Nacionais</strong>
                  <span className="text-xs text-[#72818a]">Emitir PO e gerenciar entregas</span>
                </div>
                <div onClick={() => setActivePage('importacoes')} className="bg-white border border-[#dce5e8] p-4 rounded-xl shadow-sm hover:border-[#1e7a8c] cursor-pointer">
                  <strong className="block text-sm font-bold">⚓ Importações</strong>
                  <span className="text-xs text-[#72818a]">BL, Câmbio e Landed Cost</span>
                </div>
                <div onClick={() => setActivePage('estoque')} className="bg-white border border-[#dce5e8] p-4 rounded-xl shadow-sm hover:border-[#1e7a8c] cursor-pointer">
                  <strong className="block text-sm font-bold">▣ Estoque</strong>
                  <span className="text-xs text-[#72818a]">Movimentações e inventários</span>
                </div>
                <div onClick={() => setActivePage('vendas')} className="bg-white border border-[#dce5e8] p-4 rounded-xl shadow-sm hover:border-[#1e7a8c] cursor-pointer">
                  <strong className="block text-sm font-bold">◈ Comercial</strong>
                  <span className="text-xs text-[#72818a]">Pedidos com reserva de saldo</span>
                </div>
              </div>
            </div>
          )}

          {/* COMPRAS NACIONAIS */}
          {activePage === 'compras' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-4">
                <div>
                  <h1 className="text-2xl font-black">Compras nacionais (PO Sequencial)</h1>
                  <div className="text-xs text-[#72818a] mt-1">Gestão de pedidos de compra integrados com entrada de estoque e financeiro</div>
                </div>
                <button onClick={() => setShowPurchaseModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">
                  + Novo Pedido de Compra
                </button>
              </div>
              <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                      <th className="py-2 px-2">Nº do Pedido (PO)</th>
                      <th className="py-2 px-2">Fornecedor</th>
                      <th className="py-2 px-2">Valor Total</th>
                      <th className="py-2 px-2">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#edf2f3]">
                    {purchases.map(p => (
                      <tr key={p.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 font-bold text-[#1e7a8c]">{p.po_number}</td>
                        <td className="py-3 px-2 font-medium">{p.supplier_name}</td>
                        <td className="py-3 px-2 font-bold text-[#2e9e83]">R$ {p.total_amount ? p.total_amount.toLocaleString('pt-BR', {minimumFractionDigits: 2}) : '0,00'}</td>
                        <td className="py-3 px-2"><span className="bg-[#e8f4ef] text-[#27755f] px-2.5 py-1 rounded-full text-xs font-bold">{p.status}</span></td>
                      </tr>
                    ))}
                    {purchases.length === 0 && (
                      <tr><td colSpan={4} className="py-6 text-center text-slate-400">Nenhum pedido de compra emitido ainda. Clique em "+ Novo Pedido de Compra".</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* IMPORTAÇÕES */}
          {activePage === 'importacoes' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-4">
                <div>
                  <h1 className="text-2xl font-black">Importações Internacionais & Landed Cost</h1>
                  <div className="text-xs text-[#72818a] mt-1">Acompanhamento aduaneiro, BL, containers, cronograma ETA e rateio de custos</div>
                </div>
                <button onClick={() => setShowImportModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">
                  + Nova Importação
                </button>
              </div>
              <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                      <th className="py-2 px-2">Processo</th>
                      <th className="py-2 px-2">Fornecedor Internacional</th>
                      <th className="py-2 px-2">BL / Container</th>
                      <th className="py-2 px-2">Rota Portuária</th>
                      <th className="py-2 px-2">Previsão (ETA)</th>
                      <th className="py-2 px-2">Total USD</th>
                      <th className="py-2 px-2">Custo Final BRL (Landed)</th>
                      <th className="py-2 px-2">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#edf2f3]">
                    {imports.map(i => (
                      <tr key={i.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 font-bold text-[#1e7a8c]">{i.process_number}</td>
                        <td className="py-3 px-2 font-medium">{i.supplier_name}</td>
                        <td className="py-3 px-2 text-[#72818a]">{i.bl_number} • {i.container_number}</td>
                        <td className="py-3 px-2 text-[#72818a]">{i.origin_port} ➔ {i.destination_port}</td>
                        <td className="py-3 px-2 font-bold">{i.eta}</td>
                        <td className="py-3 px-2 font-medium">US$ {i.total_usd ? i.total_usd.toLocaleString('en-US') : '0'}</td>
                        <td className="py-3 px-2 font-bold text-[#2e9e83]">R$ {i.landed_cost_brl ? i.landed_cost_brl.toLocaleString('pt-BR') : '0'}</td>
                        <td className="py-3 px-2"><span className="bg-[#fff1df] text-[#9b641f] px-2.5 py-1 rounded-full text-xs font-bold">{i.status}</span></td>
                      </tr>
                    ))}
                    {imports.length === 0 && (
                      <tr><td colSpan={8} className="py-6 text-center text-slate-400">Nenhum processo de importação registrado. Clique em "+ Nova Importação".</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ESTOQUE */}
          {activePage === 'estoque' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-4">
                <div>
                  <h1 className="text-2xl font-black">Estoque & Rastreabilidade Transacional</h1>
                  <div className="text-xs text-[#72818a] mt-1">Saldos por depósito, quantidades disponíveis e reservadas para expedição</div>
                </div>
                <button onClick={() => setShowStockModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">
                  + Registrar Movimentação
                </button>
              </div>
              <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                      <th className="py-2.5 px-3">SKU</th>
                      <th className="py-2.5 px-3">Nome do Produto</th>
                      <th className="py-2.5 px-3">Depósito</th>
                      <th className="py-2.5 px-3 font-bold text-[#27755f]">Qtd Disponível</th>
                      <th className="py-2.5 px-3 font-bold text-[#9b641f]">Qtd Reservada</th>
                      <th className="py-2.5 px-3">Total Físico</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#edf2f3]">
                    {stockBalances.map(s => (
                      <tr key={s.id} className="hover:bg-slate-50">
                        <td className="py-3 px-3 font-bold text-[#1e7a8c]">{s.product_sku}</td>
                        <td className="py-3 px-3 font-medium">{s.product_name}</td>
                        <td className="py-3 px-3 text-[#72818a]">{s.warehouse_name}</td>
                        <td className="py-3 px-3 font-black text-emerald-600 text-sm">{s.quantity_available}</td>
                        <td className="py-3 px-3 font-black text-amber-600 text-sm">{s.quantity_reserved}</td>
                        <td className="py-3 px-3 font-bold">{s.quantity_available + s.quantity_reserved} un</td>
                      </tr>
                    ))}
                    {stockBalances.length === 0 && (
                      <tr><td colSpan={6} className="py-6 text-center text-slate-400">Nenhum saldo cadastrado. Registre uma movimentação no botão acima.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* COMERCIAL & VENDAS */}
          {activePage === 'vendas' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-4">
                <div>
                  <h1 className="text-2xl font-black">Comercial & Vendas</h1>
                  <div className="text-xs text-[#72818a] mt-1">Pedidos de venda com reserva automática de estoque e geração de títulos a receber</div>
                </div>
                <button onClick={() => setShowSaleModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">
                  + Novo Pedido de Venda
                </button>
              </div>
              <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                      <th className="py-2.5 px-3">Nº Venda</th>
                      <th className="py-2.5 px-3">Cliente</th>
                      <th className="py-2.5 px-3">Representante</th>
                      <th className="py-2.5 px-3">Valor Total</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#edf2f3]">
                    {salesOrders.map(so => (
                      <tr key={so.id} className="hover:bg-slate-50">
                        <td className="py-3 px-3 font-bold text-[#1e7a8c]">{so.order_number}</td>
                        <td className="py-3 px-3 font-semibold">{so.customer_name}</td>
                        <td className="py-3 px-3 text-[#72818a]">{so.representative_name}</td>
                        <td className="py-3 px-3 font-black text-[#2e9e83]">R$ {so.total_amount ? so.total_amount.toLocaleString('pt-BR', {minimumFractionDigits: 2}) : '0,00'}</td>
                        <td className="py-3 px-3"><span className="bg-[#e8f4ef] text-[#27755f] px-2.5 py-1 rounded-full text-xs font-bold">{so.status}</span></td>
                      </tr>
                    ))}
                    {salesOrders.length === 0 && (
                      <tr><td colSpan={5} className="py-6 text-center text-slate-400">Nenhum pedido de venda registrado. Clique em "+ Novo Pedido de Venda".</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* PRODUÇÃO & ENTREGAS */}
          {activePage === 'entregas' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-4">
                <div>
                  <h1 className="text-2xl font-black">Produção & Entregas (Romaneios)</h1>
                  <div className="text-xs text-[#72818a] mt-1">Planejamento de rotas, separação e vínculo obrigatório com o plano de carga 3D</div>
                </div>
                <button onClick={() => setShowDeliveryModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">
                  + Nova Entrega
                </button>
              </div>
              <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                      <th className="py-2.5 px-3">Entrega</th>
                      <th className="py-2.5 px-3">Cliente</th>
                      <th className="py-2.5 px-3">Destino</th>
                      <th className="py-2.5 px-3">Carga / Volumes</th>
                      <th className="py-2.5 px-3">Caminhão Vinculado</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#edf2f3]">
                    {deliveries.map(d => (
                      <tr key={d.id} className="hover:bg-slate-50">
                        <td className="py-3 px-3 font-bold text-[#1e7a8c]">{d.delivery_number}</td>
                        <td className="py-3 px-3 font-semibold">{d.customer_name}</td>
                        <td className="py-3 px-3 text-[#72818a]">{d.destination_city}</td>
                        <td className="py-3 px-3 font-bold">{d.total_volumes} volumes</td>
                        <td className="py-3 px-3 font-mono text-slate-600">{d.vehicle_plate || '—'}</td>
                        <td className="py-3 px-3"><span className="bg-[#e8f4ef] text-[#27755f] px-2.5 py-1 rounded-full text-xs font-bold">{d.status}</span></td>
                      </tr>
                    ))}
                    {deliveries.length === 0 && (
                      <tr><td colSpan={6} className="py-6 text-center text-slate-400">Nenhum romaneio de entrega cadastrado. Clique em "+ Nova Entrega".</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* OTIMIZADOR DE CARGA 3D */}
          {activePage === 'optimizer' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-3">
                <div>
                  <h1 className="text-2xl font-black flex items-center gap-2">
                    <span>Otimizador inteligente de carga 3D</span>
                    <span className="text-xs bg-[#55c6b0]/20 text-[#1e7a8c] font-bold px-2 py-0.5 rounded-full">py3dbp Engine</span>
                  </h1>
                  <div className="text-xs text-[#72818a] mt-1">Encaixe geométrico determinístico + peso máximo + restrições operacionais</div>
                </div>
              </div>

              <div className="grid grid-cols-[380px_1fr] gap-4">
                <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm">
                  <h2 className="text-sm font-black mb-3">1. Parâmetros de Carga</h2>
                  <div className="mb-3">
                    <label className="text-[11px] font-bold text-[#60717a] block mb-1">Veículo Selecionado</label>
                    <select value={truckType} onChange={(e) => setTruckType(e.target.value as any)} className="w-full border border-[#dce5e8] rounded-lg p-2 text-xs bg-white font-medium">
                      <option value="truck">Truck Baú — 8,20 × 2,45 × 2,60 m (14 t)</option>
                      <option value="toco">Toco Urbano — 6,20 × 2,40 × 2,45 m (8,5 t)</option>
                      <option value="carreta">Carreta LS — 13,50 × 2,48 × 2,75 m (28 t)</option>
                    </select>
                  </div>
                  <div className="mt-3 pt-3 border-t border-[#dce5e8]">
                    <div className="text-xs font-bold mb-2">Volumes a Alocar</div>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center p-2.5 border border-[#dce5e8] rounded-lg bg-[#fbfcfc]">
                        <div><b className="text-xs block">BAM-0082 • Caixa Master A</b><small className="text-[10px] text-[#72818a] block">24 un • 1,20 × 0,80 × 0,70 m • 185 kg</small></div>
                        <span className="bg-[#e8f4ef] text-[#27755f] font-black text-xs px-2 py-0.5 rounded-full">24</span>
                      </div>
                      <div className="flex justify-between items-center p-2.5 border border-[#dce5e8] rounded-lg bg-[#fbfcfc]">
                        <div><b className="text-xs block">BAM-0154 • Pallet B</b><small className="text-[10px] text-[#72818a] block">8 un • 1,00 × 1,00 × 1,45 m • 410 kg</small></div>
                        <span className="bg-[#e6f2f5] text-[#277088] font-black text-xs px-2 py-0.5 rounded-full">8</span>
                      </div>
                      <div className="flex justify-between items-center p-2.5 border border-[#dce5e8] rounded-lg bg-[#fbfcfc]">
                        <div><b className="text-xs block">BAM-0221 • Volume Frágil</b><small className="text-[10px] text-[#72818a] block">12 un • 0,70 × 0,55 × 0,60 m • 76 kg</small></div>
                        <span className="bg-[#fff1df] text-[#9b641f] font-black text-xs px-2 py-0.5 rounded-full">12</span>
                      </div>
                    </div>
                  </div>
                  <button onClick={handleCalculatePacking} disabled={calcLoading} className="w-full mt-4 bg-[#1e7a8c] hover:bg-[#176270] disabled:bg-slate-300 text-white font-bold text-xs py-2.5 rounded-lg transition-colors shadow-sm cursor-pointer">
                    {calcLoading ? "Calculando com py3dbp..." : "✦ Calcular Melhor Plano Matemático"}
                  </button>
                </div>

                <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm min-h-[520px] flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <div><b className="text-base font-black">{calcResult.truck_name}</b><div className="text-xs text-[#72818a]">Motor Matemático: py3dbp</div></div>
                      <span className={`text-xs font-bold px-3 py-1 rounded-full ${!calcResult.is_viable ? 'bg-[#fff1df] text-[#9b641f]' : 'bg-[#e8f4ef] text-[#27755f]'}`}>{calcResult.status}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2.5 mb-3">
                      <div className="bg-[#f7fafb] border border-[#dce5e8] p-2.5 rounded-lg"><small className="text-[11px] text-[#72818a] block">Ocupação Volumétrica</small><b className="text-lg font-black">{calcResult.volumetric_efficiency_pct}%</b></div>
                      <div className="bg-[#f7fafb] border border-[#dce5e8] p-2.5 rounded-lg"><small className="text-[11px] text-[#72818a] block">Peso Utilizado</small><b className="text-lg font-black">{calcResult.fitted_weight_kg ? calcResult.fitted_weight_kg.toLocaleString('pt-BR') : '10.400'} kg</b></div>
                      <div className="bg-[#f7fafb] border border-[#dce5e8] p-2.5 rounded-lg"><small className="text-[11px] text-[#72818a] block">Volumes Alocados</small><b className="text-lg font-black">{calcResult.total_items_allocated}</b></div>
                    </div>
                    <div className="h-[260px] border-4 border-[#4a6977] rounded-lg relative overflow-hidden bg-[#f8fbfb] bg-[linear-gradient(rgba(120,145,154,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(120,145,154,0.1)_1px,transparent_1px)] bg-[size:32px_32px]">
                      <div className="absolute left-[4%] top-[55%] w-[22%] h-[40%] border-2 border-[rgba(20,70,80,0.7)] rounded bg-[rgba(71,169,156,0.36)] flex items-center justify-center font-bold text-xs text-[#163744]">Master A</div>
                      <div className="absolute left-[27%] top-[55%] w-[22%] h-[40%] border-2 border-[rgba(20,70,80,0.7)] rounded bg-[rgba(71,169,156,0.36)] flex items-center justify-center font-bold text-xs text-[#163744]">Master A</div>
                      <div className="absolute left-[51%] top-[38%] w-[18%] h-[57%] border-2 border-[rgba(20,70,80,0.7)] rounded bg-[rgba(80,137,190,0.33)] flex items-center justify-center font-bold text-xs text-[#163744]">Pallet B</div>
                      <div className="absolute left-[70%] top-[38%] w-[18%] h-[57%] border-2 border-[rgba(20,70,80,0.7)] rounded bg-[rgba(80,137,190,0.33)] flex items-center justify-center font-bold text-xs text-[#163744]">Pallet B</div>
                      <div className="absolute left-[4%] top-[10%] w-[14%] h-[35%] border-2 border-[rgba(20,70,80,0.7)] rounded bg-[rgba(221,160,70,0.36)] flex items-center justify-center font-bold text-xs text-[#163744]">Frágil</div>
                    </div>
                    <div className={`mt-3 p-2.5 rounded-lg text-xs border ${!calcResult.is_viable ? 'bg-[#fff8f0] text-[#9b641f] border-[#fae2c8]' : 'bg-[#edf7f3] text-[#285f50] border-[#d3ebe3]'}`}>
                      {calcResult.alert_message}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* CADASTROS MESTRES */}
          {activePage === 'cadastros' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-4">
                <div>
                  <h1 className="text-2xl font-black">Cadastros mestres (Base Única)</h1>
                  <div className="text-xs text-[#72818a] mt-1">Produtos, clientes e veículos persistidos com isolamento de dados</div>
                </div>
                <div className="flex gap-2">
                  {activeCadTab === 'produtos' && (
                    <button onClick={() => setShowProductModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">+ Novo Produto</button>
                  )}
                  {activeCadTab === 'clientes' && (
                    <button onClick={() => setShowCustomerModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">+ Novo Cliente</button>
                  )}
                  {activeCadTab === 'veiculos' && (
                    <button onClick={() => setShowVehicleModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">+ Novo Veículo</button>
                  )}
                </div>
              </div>

              <div className="flex gap-2 border-b border-[#dce5e8] mb-4 text-xs font-bold">
                <button onClick={() => setActiveCadTab('produtos')} className={`py-2 px-4 cursor-pointer ${activeCadTab === 'produtos' ? 'text-[#1e7a8c] border-b-2 border-[#1e7a8c]' : 'text-[#72818a]'}`}>Produtos ({products.length})</button>
                <button onClick={() => setActiveCadTab('clientes')} className={`py-2 px-4 cursor-pointer ${activeCadTab === 'clientes' ? 'text-[#1e7a8c] border-b-2 border-[#1e7a8c]' : 'text-[#72818a]'}`}>Clientes ({customers.length})</button>
                <button onClick={() => setActiveCadTab('veiculos')} className={`py-2 px-4 cursor-pointer ${activeCadTab === 'veiculos' ? 'text-[#1e7a8c] border-b-2 border-[#1e7a8c]' : 'text-[#72818a]'}`}>Veículos & Frotas ({vehicles.length})</button>
              </div>

              {/* ABA PRODUTOS */}
              {activeCadTab === 'produtos' && (
                <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                        <th className="py-2.5 px-3">SKU</th>
                        <th className="py-2.5 px-3">Nome</th>
                        <th className="py-2.5 px-3">Preço</th>
                        <th className="py-2.5 px-3">Dimensões</th>
                        <th className="py-2.5 px-3">Volume Unit.</th>
                        <th className="py-2.5 px-3">Peso</th>
                        <th className="py-2.5 px-3 text-right">Ações</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#edf2f3]">
                      {products.map(p => (
                        <tr key={p.id} className="hover:bg-slate-50">
                          <td className="py-3 px-3 font-bold text-[#1e7a8c]">{p.sku}</td>
                          <td className="py-3 px-3 font-semibold">{p.name}</td>
                          <td className="py-3 px-3">R$ {p.price.toFixed(2)}</td>
                          <td className="py-3 px-3 text-[#72818a]">{p.length_m}m × {p.width_m}m × {p.height_m}m</td>
                          <td className="py-3 px-3 font-bold text-[#2e9e83]">{p.volume_m3} m³</td>
                          <td className="py-3 px-3">{p.weight_kg} kg</td>
                          <td className="py-3 px-3 text-right">
                            <button onClick={() => handleGenericDelete(`${API_BASE}/products/${p.id}`, `Produto ${p.sku}`)} className="text-rose-600 font-bold hover:underline cursor-pointer">
                              Excluir
                            </button>
                          </td>
                        </tr>
                      ))}
                      {products.length === 0 && (
                        <tr><td colSpan={7} className="py-6 text-center text-slate-400">Nenhum produto cadastrado ainda. Clique em "+ Novo Produto".</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}

              {/* ABA CLIENTES */}
              {activeCadTab === 'clientes' && (
                <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                        <th className="py-2.5 px-3">Nome / Razão</th>
                        <th className="py-2.5 px-3">CPF/CNPJ</th>
                        <th className="py-2.5 px-3">E-mail</th>
                        <th className="py-2.5 px-3">Telefone</th>
                        <th className="py-2.5 px-3">Endereço de Entrega</th>
                        <th className="py-2.5 px-3">Limite de Crédito</th>
                        <th className="py-2.5 px-3 text-right">Ações</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#edf2f3]">
                      {customers.map(c => (
                        <tr key={c.id} className="hover:bg-slate-50">
                          <td className="py-3 px-3 font-bold">{c.name}</td>
                          <td className="py-3 px-3 font-mono text-[#1e7a8c]">{c.document}</td>
                          <td className="py-3 px-3 text-[#72818a]">{c.email}</td>
                          <td className="py-3 px-3">{c.phone}</td>
                          <td className="py-3 px-3 text-[#72818a]">{c.delivery_address}</td>
                          <td className="py-3 px-3 font-bold text-[#2e9e83]">R$ {c.credit_limit ? c.credit_limit.toFixed(2) : '0,00'}</td>
                          <td className="py-3 px-3 text-right">
                            <button onClick={() => handleGenericDelete(`${API_BASE}/customers/${c.id}`, `Cliente ${c.name}`)} className="text-rose-600 font-bold hover:underline cursor-pointer">
                              Excluir
                            </button>
                          </td>
                        </tr>
                      ))}
                      {customers.length === 0 && (
                        <tr><td colSpan={7} className="py-6 text-center text-slate-400">Nenhum cliente cadastrado ainda. Clique em "+ Novo Cliente".</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}

              {/* ABA VEÍCULOS */}
              {activeCadTab === 'veiculos' && (
                <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                        <th className="py-2.5 px-3">Placa</th>
                        <th className="py-2.5 px-3">Modelo</th>
                        <th className="py-2.5 px-3">Carroceria</th>
                        <th className="py-2.5 px-3">Dimensões Úteis (C × L × A)</th>
                        <th className="py-2.5 px-3">Volume Útil</th>
                        <th className="py-2.5 px-3">Carga Útil Máxima</th>
                        <th className="py-2.5 px-3 text-right">Ações</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#edf2f3]">
                      {vehicles.map(v => (
                        <tr key={v.id} className="hover:bg-slate-50">
                          <td className="py-3 px-3 font-bold text-[#1e7a8c]">{v.plate}</td>
                          <td className="py-3 px-3 font-semibold">{v.model}</td>
                          <td className="py-3 px-3 text-[#72818a]">{v.body_type}</td>
                          <td className="py-3 px-3 text-[#72818a]">{v.length_m}m × {v.width_m}m × {v.height_m}m</td>
                          <td className="py-3 px-3 font-bold text-[#2e9e83]">{v.useful_volume_m3 ? v.useful_volume_m3.toFixed(2) : (v.length_m * v.width_m * v.height_m).toFixed(2)} m³</td>
                          <td className="py-3 px-3 font-black">{v.max_payload_kg ? v.max_payload_kg.toLocaleString('pt-BR') : '0'} kg</td>
                          <td className="py-3 px-3 text-right">
                            <button onClick={() => handleGenericDelete(`${API_BASE}/vehicles/${v.id}`, `Veículo ${v.plate}`)} className="text-rose-600 font-bold hover:underline cursor-pointer">
                              Excluir
                            </button>
                          </td>
                        </tr>
                      ))}
                      {vehicles.length === 0 && (
                        <tr><td colSpan={7} className="py-6 text-center text-slate-400">Nenhum veículo cadastrado na frota. Clique em "+ Novo Veículo".</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* FINANCEIRO */}
          {activePage === 'financeiro' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-4">
                <div>
                  <h1 className="text-2xl font-black">Financeiro (AP/AR & Fluxo de Caixa)</h1>
                  <div className="text-xs text-[#72818a] mt-1">Títulos a pagar e a receber com liquidação e integração transacional</div>
                </div>
                <button onClick={() => setShowFinanceModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">
                  + Novo Lançamento
                </button>
              </div>

              <div className="grid grid-cols-3 gap-3.5 mb-5">
                <div className="bg-white border border-[#dce5e8] rounded-xl p-4 shadow-sm">
                  <div className="text-xs text-[#72818a]">Total a Pagar (AP)</div>
                  <div className="text-2xl font-black text-rose-600 my-1">R$ {financialSummary.total_payable.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
                  <div className="text-xs text-[#72818a]">Alimentado por Compras/RH</div>
                </div>
                <div className="bg-white border border-[#dce5e8] rounded-xl p-4 shadow-sm">
                  <div className="text-xs text-[#72818a]">Total a Receber (AR)</div>
                  <div className="text-2xl font-black text-emerald-600 my-1">R$ {financialSummary.total_receivable.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
                  <div className="text-xs text-[#72818a]">Alimentado por Vendas</div>
                </div>
                <div className="bg-white border border-[#dce5e8] rounded-xl p-4 shadow-sm">
                  <div className="text-xs text-[#72818a]">Saldo Projetado</div>
                  <div className={`text-2xl font-black my-1 ${financialSummary.projected_balance >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                    R$ {financialSummary.projected_balance.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                  </div>
                  <div className="text-xs text-[#72818a]">Fluxo de Caixa em Aberto</div>
                </div>
              </div>

              <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                      <th className="py-2.5 px-3">Tipo</th>
                      <th className="py-2.5 px-3">Descrição</th>
                      <th className="py-2.5 px-3">Entidade (Cliente/Fornecedor)</th>
                      <th className="py-2.5 px-3">Categoria</th>
                      <th className="py-2.5 px-3">Vencimento</th>
                      <th className="py-2.5 px-3">Valor</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#edf2f3]">
                    {financialEntries.map(f => (
                      <tr key={f.id} className="hover:bg-slate-50">
                        <td className="py-3 px-3">
                          <span className={`px-2 py-0.5 rounded text-[11px] font-black ${f.entry_type === 'PAGAR' ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                            {f.entry_type}
                          </span>
                        </td>
                        <td className="py-3 px-3 font-semibold">{f.description}</td>
                        <td className="py-3 px-3 text-[#72818a]">{f.entity_name}</td>
                        <td className="py-3 px-3 text-[#72818a]">{f.category}</td>
                        <td className="py-3 px-3 font-medium">{f.due_date}</td>
                        <td className="py-3 px-3 font-black text-sm">R$ {f.amount.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                        <td className="py-3 px-3"><span className="bg-[#fff1df] text-[#9b641f] px-2.5 py-1 rounded-full text-xs font-bold">{f.status}</span></td>
                      </tr>
                    ))}
                    {financialEntries.length === 0 && (
                      <tr><td colSpan={7} className="py-6 text-center text-slate-400">Nenhum título financeiro cadastrado. Clique em "+ Novo Lançamento".</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* RECURSOS HUMANOS (RH) */}
          {activePage === 'rh' && (
            <div>
              <div className="flex items-end justify-between gap-4 mb-4">
                <div>
                  <h1 className="text-2xl font-black">Recursos Humanos (RH)</h1>
                  <div className="text-xs text-[#72818a] mt-1">Colaboradores, cargos, evolução salarial e folha com envio ao financeiro</div>
                </div>
                <button onClick={() => setShowEmployeeModal(true)} className="bg-[#1e7a8c] hover:bg-[#176270] text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm cursor-pointer">
                  + Novo Funcionário
                </button>
              </div>
              <div className="bg-white border border-[#dce5e8] rounded-xl p-5 shadow-sm overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#dce5e8] text-[#667780] uppercase tracking-wider">
                      <th className="py-2.5 px-3">Nome</th>
                      <th className="py-2.5 px-3">CPF</th>
                      <th className="py-2.5 px-3">Cargo</th>
                      <th className="py-2.5 px-3">Departamento</th>
                      <th className="py-2.5 px-3">Salário</th>
                      <th className="py-2.5 px-3">Admissão</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#edf2f3]">
                    {employees.map(e => (
                      <tr key={e.id} className="hover:bg-slate-50">
                        <td className="py-3 px-3 font-bold">{e.name}</td>
                        <td className="py-3 px-3 font-mono text-[#1e7a8c]">{e.cpf}</td>
                        <td className="py-3 px-3 font-semibold">{e.role}</td>
                        <td className="py-3 px-3 text-[#72818a]">{e.department}</td>
                        <td className="py-3 px-3 font-black text-emerald-600">R$ {e.salary.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                        <td className="py-3 px-3 text-[#72818a]">{e.admission_date}</td>
                        <td className="py-3 px-3"><span className="bg-[#e8f4ef] text-[#27755f] px-2.5 py-1 rounded-full text-xs font-bold">{e.status}</span></td>
                      </tr>
                    ))}
                    {employees.length === 0 && (
                      <tr><td colSpan={7} className="py-6 text-center text-slate-400">Nenhum funcionário cadastrado. Clique em "+ Novo Funcionário".</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* RELATÓRIOS & AUDITORIA */}
          {activePage === 'relatorios' && (
            <div className="bg-white border border-[#dce5e8] rounded-xl p-6 shadow-sm">
              <h1 className="text-xl font-black mb-2">Relatórios Gerenciais & Auditoria Imutável</h1>
              <p className="text-xs text-[#72818a] mb-4">Exportação de visões corporativas, controle de permissões e log de eventos.</p>
              <div className="grid grid-cols-3 gap-3">
                <div className="border border-slate-200 p-4 rounded-lg bg-slate-50"><h3 className="font-bold text-xs mb-1">DRE Consolidado</h3><p className="text-[11px] text-slate-500">Alimentado por compras, vendas e folha.</p></div>
                <div className="border border-slate-200 p-4 rounded-lg bg-slate-50"><h3 className="font-bold text-xs mb-1">Acuracidade de Inventário</h3><p className="text-[11px] text-slate-500">Histórico de divergências e ajustes.</p></div>
                <div className="border border-slate-200 p-4 rounded-lg bg-slate-50"><h3 className="font-bold text-xs mb-1">Taxa de Ocupação de Frota</h3><p className="text-[11px] text-slate-500">Métricas de cubagem e pesos transportados.</p></div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* ===================================================================== */}
      {/* OS 10 MODAIS DE CRIAÇÃO (CRUD COMPLETO) */}
      {/* ===================================================================== */}

      {/* 1. MODAL PRODUTO */}
      {showProductModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Cadastrar Novo Produto</h3>
            <form onSubmit={(e) => { 
              e.preventDefault(); 
              handleGenericSubmit(`${API_BASE}/products`, newProduct, () => {
                setShowProductModal(false);
                setNewProduct({ sku: '', name: '', category: 'Embalagens', price: 150.0, weight_kg: 25.0, length_m: 1.2, width_m: 0.8, height_m: 0.7, stackable: true, fragile: false });
              }, `Produto ${newProduct.sku} criado com sucesso!`); 
            }} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">SKU do Produto *</label>
                  <input required placeholder="Ex: BAM-0099" value={newProduct.sku} onChange={e => setNewProduct({...newProduct, sku: e.target.value.toUpperCase()})} className="border border-slate-300 p-2 rounded w-full font-bold uppercase" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Nome Comercial *</label>
                  <input required placeholder="Ex: Caixa Master B" value={newProduct.name} onChange={e => setNewProduct({...newProduct, name: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Categoria</label>
                  <input placeholder="Categoria" value={newProduct.category} onChange={e => setNewProduct({...newProduct, category: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Preço de Venda (R$)</label>
                  <input type="number" step="0.01" value={newProduct.price} onChange={e => setNewProduct({...newProduct, price: parseFloat(e.target.value) || 0})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
              </div>
              <div>
                <span className="block font-bold text-[#1e7a8c] mb-1">Dimensões & Peso (Cubagem 3D)</span>
                <div className="grid grid-cols-4 gap-2">
                  <div>
                    <label className="text-[10px] text-slate-500 block">Comp (m)</label>
                    <input type="number" step="0.01" required value={newProduct.length_m} onChange={e => setNewProduct({...newProduct, length_m: parseFloat(e.target.value) || 0.1})} className="border border-slate-300 p-2 rounded w-full" />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-500 block">Larg (m)</label>
                    <input type="number" step="0.01" required value={newProduct.width_m} onChange={e => setNewProduct({...newProduct, width_m: parseFloat(e.target.value) || 0.1})} className="border border-slate-300 p-2 rounded w-full" />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-500 block">Alt (m)</label>
                    <input type="number" step="0.01" required value={newProduct.height_m} onChange={e => setNewProduct({...newProduct, height_m: parseFloat(e.target.value) || 0.1})} className="border border-slate-300 p-2 rounded w-full" />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-500 block">Peso (kg)</label>
                    <input type="number" step="0.1" required value={newProduct.weight_kg} onChange={e => setNewProduct({...newProduct, weight_kg: parseFloat(e.target.value) || 1.0})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                  </div>
                </div>
              </div>
              <div className="flex gap-4 pt-1">
                <label className="flex items-center gap-1.5 cursor-pointer font-bold">
                  <input type="checkbox" checked={newProduct.stackable} onChange={e => setNewProduct({...newProduct, stackable: e.target.checked})} />
                  <span>Empilhável</span>
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer font-bold">
                  <input type="checkbox" checked={newProduct.fragile} onChange={e => setNewProduct({...newProduct, fragile: e.target.checked})} />
                  <span className="text-amber-700">Frágil</span>
                </label>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowProductModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Salvar Produto</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 2. MODAL CLIENTE */}
      {showCustomerModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Cadastrar Novo Cliente</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              handleGenericSubmit(`${API_BASE}/customers`, newCustomer, () => {
                setShowCustomerModal(false);
                setNewCustomer({ name: '', document: '', email: '', phone: '', delivery_address: '', credit_limit: 25000.0 });
              }, `Cliente ${newCustomer.name} criado com sucesso!`);
            }} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold mb-1">Nome / Razão Social *</label>
                <input required placeholder="Ex: Comercial Nordeste Distribuidora Ltda" value={newCustomer.name} onChange={e => setNewCustomer({...newCustomer, name: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">CPF / CNPJ *</label>
                  <input required placeholder="12.345.678/0001-90" value={newCustomer.document} onChange={e => setNewCustomer({...newCustomer, document: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-mono" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Limite de Crédito (R$)</label>
                  <input type="number" step="0.01" value={newCustomer.credit_limit} onChange={e => setNewCustomer({...newCustomer, credit_limit: parseFloat(e.target.value) || 0})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">E-mail *</label>
                  <input type="email" required placeholder="contato@empresa.com" value={newCustomer.email} onChange={e => setNewCustomer({...newCustomer, email: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Telefone *</label>
                  <input required placeholder="(81) 98888-7777" value={newCustomer.phone} onChange={e => setNewCustomer({...newCustomer, phone: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
              </div>
              <div>
                <label className="block font-bold mb-1">Endereço Completo de Entrega *</label>
                <input required placeholder="Av. Agamenon Magalhães, 500, Recife/PE" value={newCustomer.delivery_address} onChange={e => setNewCustomer({...newCustomer, delivery_address: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowCustomerModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Salvar Cliente</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 3. MODAL VEÍCULO */}
      {showVehicleModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Cadastrar Novo Veículo na Frota</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              handleGenericSubmit(`${API_BASE}/vehicles`, newVehicle, () => {
                setShowVehicleModal(false);
                setNewVehicle({ plate: '', model: 'Truck Baú', body_type: 'Baú Fechado', length_m: 8.2, width_m: 2.45, height_m: 2.6, max_payload_kg: 14000.0 });
              }, `Veículo ${newVehicle.plate} cadastrado na frota!`);
            }} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Placa do Veículo *</label>
                  <input required placeholder="Ex: BRA-9A82" value={newVehicle.plate} onChange={e => setNewVehicle({...newVehicle, plate: e.target.value.toUpperCase()})} className="border border-slate-300 p-2 rounded w-full font-bold uppercase font-mono" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Modelo Comercial *</label>
                  <input required placeholder="Ex: Mercedes-Benz Atego" value={newVehicle.model} onChange={e => setNewVehicle({...newVehicle, model: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Tipo de Carroceria</label>
                  <select value={newVehicle.body_type} onChange={e => setNewVehicle({...newVehicle, body_type: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-medium">
                    <option>Baú Fechado</option><option>Sider / Cortina</option><option>Carreta Aberta</option><option>Refrigerado</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold mb-1">Carga Útil Máxima (kg) *</label>
                  <input type="number" required value={newVehicle.max_payload_kg} onChange={e => setNewVehicle({...newVehicle, max_payload_kg: parseFloat(e.target.value) || 1000})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
              </div>
              <div>
                <span className="block font-bold text-[#1e7a8c] mb-1">Dimensões Úteis Internas do Baú (metros)</span>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-[10px] text-slate-500 block">Comprimento (m)</label>
                    <input type="number" step="0.01" required value={newVehicle.length_m} onChange={e => setNewVehicle({...newVehicle, length_m: parseFloat(e.target.value) || 1.0})} className="border border-slate-300 p-2 rounded w-full" />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-500 block">Largura (m)</label>
                    <input type="number" step="0.01" required value={newVehicle.width_m} onChange={e => setNewVehicle({...newVehicle, width_m: parseFloat(e.target.value) || 1.0})} className="border border-slate-300 p-2 rounded w-full" />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-500 block">Altura (m)</label>
                    <input type="number" step="0.01" required value={newVehicle.height_m} onChange={e => setNewVehicle({...newVehicle, height_m: parseFloat(e.target.value) || 1.0})} className="border border-slate-300 p-2 rounded w-full" />
                  </div>
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowVehicleModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Cadastrar Veículo</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 4. MODAL COMPRA */}
      {showPurchaseModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Emitir Pedido de Compra Nacional (PO)</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              const payload = {
                supplier_name: newPurchase.supplier_name,
                items: [{ product_sku: newPurchase.product_sku, product_name: newPurchase.product_name, quantity: newPurchase.quantity, unit_price: newPurchase.unit_price }]
              };
              handleGenericSubmit(`${API_BASE}/purchases`, payload, () => {
                setShowPurchaseModal(false);
                setNewPurchase({ supplier_name: '', product_name: 'Caixa Master A', product_sku: 'BAM-0082', quantity: 10, unit_price: 120.0 });
              }, "Pedido de Compra emitido com sucesso!");
            }} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold mb-1">Fornecedor Nacional *</label>
                <input required placeholder="Ex: Fornecedor Madeiras do Brasil S.A." value={newPurchase.supplier_name} onChange={e => setNewPurchase({...newPurchase, supplier_name: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">SKU do Item *</label>
                  <input required placeholder="BAM-0082" value={newPurchase.product_sku} onChange={e => setNewPurchase({...newPurchase, product_sku: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-mono uppercase" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Nome do Item *</label>
                  <input required placeholder="Caixa Master A" value={newPurchase.product_name} onChange={e => setNewPurchase({...newPurchase, product_name: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Quantidade *</label>
                  <input type="number" required min="1" value={newPurchase.quantity} onChange={e => setNewPurchase({...newPurchase, quantity: parseInt(e.target.value) || 1})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Preço Unitário (R$) *</label>
                  <input type="number" step="0.01" required value={newPurchase.unit_price} onChange={e => setNewPurchase({...newPurchase, unit_price: parseFloat(e.target.value) || 0})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
              </div>
              <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg flex justify-between items-center font-bold">
                <span>Valor Total da PO:</span>
                <span className="text-[#2e9e83] text-sm">R$ {(newPurchase.quantity * newPurchase.unit_price).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowPurchaseModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Emitir Pedido</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 5. MODAL IMPORTAÇÃO */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Registrar Processo de Importação</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              handleGenericSubmit(`${API_BASE}/imports`, newImport, () => {
                setShowImportModal(false);
              }, "Processo de Importação registrado com sucesso!");
            }} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold mb-1">Fornecedor Internacional *</label>
                <input required placeholder="Ex: Bamboo Trade Asia Ltd" value={newImport.supplier_name} onChange={e => setNewImport({...newImport, supplier_name: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Nº do Conhecimento (BL) *</label>
                  <input required placeholder="BL-CNSHA-2026" value={newImport.bl_number} onChange={e => setNewImport({...newImport, bl_number: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-mono" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Nº do Container</label>
                  <input placeholder="MSCU-90214-5" value={newImport.container_number} onChange={e => setNewImport({...newImport, container_number: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-mono" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Porto Origem</label>
                  <input value={newImport.origin_port} onChange={e => setNewImport({...newImport, origin_port: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Porto Destino</label>
                  <input value={newImport.destination_port} onChange={e => setNewImport({...newImport, destination_port: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block font-bold mb-1">Previsão (ETA)</label>
                  <input value={newImport.eta} onChange={e => setNewImport({...newImport, eta: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Total USD</label>
                  <input type="number" step="0.01" value={newImport.total_usd} onChange={e => setNewImport({...newImport, total_usd: parseFloat(e.target.value) || 0})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Landed BRL</label>
                  <input type="number" step="0.01" value={newImport.landed_cost_brl} onChange={e => setNewImport({...newImport, landed_cost_brl: parseFloat(e.target.value) || 0})} className="border border-slate-300 p-2 rounded w-full font-bold text-[#2e9e83]" />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowImportModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Salvar Importação</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 6. MODAL ESTOQUE */}
      {showStockModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Registrar Movimentação de Estoque</h3>
            <form onSubmit={(e) => { 
              e.preventDefault(); 
              handleGenericSubmit(`${API_BASE}/stock/movements`, newStockMov, () => {
                setShowStockModal(false);
              }, "Movimentação de estoque gravada com recálculo de saldo!"); 
            }} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Tipo de Movimento *</label>
                  <select value={newStockMov.movement_type} onChange={e => setNewStockMov({...newStockMov, movement_type: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold">
                    <option>Entrada</option><option>Saída</option><option>Ajuste</option><option>Transferência</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold mb-1">Depósito *</label>
                  <input value={newStockMov.warehouse_name} onChange={e => setNewStockMov({...newStockMov, warehouse_name: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">SKU do Produto *</label>
                  <input required placeholder="BAM-0082" value={newStockMov.product_sku} onChange={e => setNewStockMov({...newStockMov, product_sku: e.target.value.toUpperCase()})} className="border border-slate-300 p-2 rounded w-full font-bold font-mono uppercase" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Nome do Produto</label>
                  <input placeholder="Caixa Master A" value={newStockMov.product_name} onChange={e => setNewStockMov({...newStockMov, product_name: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
              </div>
              <div>
                <label className="block font-bold mb-1">Quantidade de Itens *</label>
                <input type="number" required min="1" value={newStockMov.quantity} onChange={e => setNewStockMov({...newStockMov, quantity: parseInt(e.target.value) || 1})} className="border border-slate-300 p-2 rounded w-full font-black text-sm" />
              </div>
              <div>
                <label className="block font-bold mb-1">Motivo / Justificativa *</label>
                <input required placeholder="Ex: Entrada por recebimento de compra" value={newStockMov.reason} onChange={e => setNewStockMov({...newStockMov, reason: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowStockModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Gravar Movimentação</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 7. MODAL VENDA */}
      {showSaleModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Registrar Pedido de Venda Comercial</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              const payload = {
                customer_name: newSale.customer_name,
                representative_name: newSale.representative_name || 'Vendas Diretas',
                items: [{ product_sku: newSale.product_sku, product_name: newSale.product_name, quantity: newSale.quantity, unit_price: newSale.unit_price }]
              };
              handleGenericSubmit(`${API_BASE}/sales`, payload, () => {
                setShowSaleModal(false);
              }, `Venda para ${newSale.customer_name} confirmada!`);
            }} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold mb-1">Cliente *</label>
                <input required placeholder="Ex: Comercial Atlântico Ltda" value={newSale.customer_name} onChange={e => setNewSale({...newSale, customer_name: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Representante</label>
                  <input value={newSale.representative_name} onChange={e => setNewSale({...newSale, representative_name: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
                <div>
                  <label className="block font-bold mb-1">SKU *</label>
                  <input required placeholder="BAM-0082" value={newSale.product_sku} onChange={e => setNewSale({...newSale, product_sku: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-mono uppercase" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Quantidade *</label>
                  <input type="number" required min="1" value={newSale.quantity} onChange={e => setNewSale({...newSale, quantity: parseInt(e.target.value) || 1})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Preço de Venda (R$) *</label>
                  <input type="number" step="0.01" required value={newSale.unit_price} onChange={e => setNewSale({...newSale, unit_price: parseFloat(e.target.value) || 0})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
              </div>
              <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg flex justify-between items-center font-bold">
                <span>Total da Venda:</span>
                <span className="text-[#2e9e83] text-sm">R$ {(newSale.quantity * newSale.unit_price).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowSaleModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Confirmar Venda</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 8. MODAL ENTREGA */}
      {showDeliveryModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Cadastrar Romaneio de Entrega</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              handleGenericSubmit(`${API_BASE}/deliveries`, newDelivery, () => {
                setShowDeliveryModal(false);
              }, "Romaneio de entrega gerado com sucesso!");
            }} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold mb-1">Cliente Destinatário *</label>
                <input required placeholder="Ex: Cliente Atlântico Ltda" value={newDelivery.customer_name} onChange={e => setNewDelivery({...newDelivery, customer_name: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Cidade Destino *</label>
                  <input required placeholder="Recife / PE" value={newDelivery.destination_city} onChange={e => setNewDelivery({...newDelivery, destination_city: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Total de Volumes *</label>
                  <input type="number" required min="1" value={newDelivery.total_volumes} onChange={e => setNewDelivery({...newDelivery, total_volumes: parseInt(e.target.value) || 1})} className="border border-slate-300 p-2 rounded w-full font-bold" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Veículo / Placa</label>
                  <input placeholder="BRA-2E19" value={newDelivery.vehicle_plate} onChange={e => setNewDelivery({...newDelivery, vehicle_plate: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-mono uppercase" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Status da Carga</label>
                  <select value={newDelivery.status} onChange={e => setNewDelivery({...newDelivery, status: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold">
                    <option>Carga pronta</option><option>Em rota</option><option>Entregue</option><option>Pendente</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowDeliveryModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Gravar Romaneio</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 9. MODAL FINANCEIRO */}
      {showFinanceModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Novo Lançamento Financeiro</h3>
            <form onSubmit={(e) => { 
              e.preventDefault(); 
              handleGenericSubmit(`${API_BASE}/finance`, newFinance, () => {
                setShowFinanceModal(false);
              }, "Título financeiro registrado com sucesso!"); 
            }} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Natureza do Título *</label>
                  <select value={newFinance.entry_type} onChange={e => setNewFinance({...newFinance, entry_type: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold">
                    <option value="PAGAR">Conta a Pagar (AP)</option><option value="RECEBER">Conta a Receber (AR)</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold mb-1">Descrição do Lançamento *</label>
                  <input required placeholder="Ex: Pagamento Frete Rodoviário" value={newFinance.description} onChange={e => setNewFinance({...newFinance, description: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Entidade (Fornecedor/Cliente) *</label>
                  <input required placeholder="Ex: Transportadora Líder" value={newFinance.entity_name} onChange={e => setNewFinance({...newFinance, entity_name: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-semibold" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Valor do Título (R$) *</label>
                  <input type="number" step="0.01" required value={newFinance.amount} onChange={e => setNewFinance({...newFinance, amount: parseFloat(e.target.value) || 0})} className="border border-slate-300 p-2 rounded w-full font-black text-sm" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Categoria de Custo</label>
                  <input value={newFinance.category} onChange={e => setNewFinance({...newFinance, category: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Data de Vencimento</label>
                  <input placeholder="15/10/2026" value={newFinance.due_date} onChange={e => setNewFinance({...newFinance, due_date: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowFinanceModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Salvar Título</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 10. MODAL RH */}
      {showEmployeeModal && (
        <div className="fixed inset-0 bg-black/50 z-50 grid place-items-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-black text-base mb-3 text-[#102b3a]">Cadastrar Novo Colaborador</h3>
            <form onSubmit={(e) => { 
              e.preventDefault(); 
              handleGenericSubmit(`${API_BASE}/employees`, newEmployee, () => {
                setShowEmployeeModal(false);
              }, `Colaborador ${newEmployee.name} admitido no sistema!`); 
            }} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold mb-1">Nome Completo *</label>
                <input required placeholder="Ex: Roberto Carlos Albuquerque" value={newEmployee.name} onChange={e => setNewEmployee({...newEmployee, name: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-bold" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">CPF *</label>
                  <input required placeholder="123.456.789-00" value={newEmployee.cpf} onChange={e => setNewEmployee({...newEmployee, cpf: e.target.value})} className="border border-slate-300 p-2 rounded w-full font-mono" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Cargo *</label>
                  <input required placeholder="Ex: Operador Logístico" value={newEmployee.role} onChange={e => setNewEmployee({...newEmployee, role: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold mb-1">Departamento</label>
                  <input value={newEmployee.department} onChange={e => setNewEmployee({...newEmployee, department: e.target.value})} className="border border-slate-300 p-2 rounded w-full" />
                </div>
                <div>
                  <label className="block font-bold mb-1">Salário (R$) *</label>
                  <input type="number" step="0.01" required value={newEmployee.salary} onChange={e => setNewEmployee({...newEmployee, salary: parseFloat(e.target.value) || 0})} className="border border-slate-300 p-2 rounded w-full font-bold text-emerald-600" />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button type="button" onClick={() => setShowEmployeeModal(false)} className="border border-slate-300 px-3 py-1.5 rounded cursor-pointer">Cancelar</button>
                <button type="submit" className="bg-[#1e7a8c] hover:bg-[#176270] text-white px-4 py-1.5 rounded font-bold cursor-pointer shadow-sm">Admitir Colaborador</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* WIDGET FLUTUANTE DE ASSISTENTE DE IA (CANTO INFERIOR DIREITO) */}
      {!isAiOpen && (
        <button 
          onClick={() => setIsAiOpen(true)}
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 bg-gradient-to-r from-[#102b3a] to-[#1e7a8c] hover:from-[#0c202b] hover:to-[#176270] text-white px-4 py-3 rounded-full shadow-2xl border border-teal-400/30 transition-all transform hover:scale-105 cursor-pointer"
        >
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-xs font-bold flex items-center gap-1.5">
            <span>✦</span> Assistente IA • Carga 3D
          </span>
        </button>
      )}

      {isAiOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-96 max-w-[calc(100vw-32px)] h-[520px] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4">
          {/* HEADER DO CHAT */}
          <div className="bg-gradient-to-r from-[#102b3a] to-[#183d4e] text-white p-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <b className="text-xs font-bold text-emerald-300">Assistente Logístico Bamboo</b>
              <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded-full text-slate-300">py3dbp</span>
            </div>
            <button 
              onClick={() => setIsAiOpen(false)}
              className="text-slate-300 hover:text-white font-bold p-1 rounded hover:bg-white/10 transition-colors cursor-pointer"
              title="Fechar Assistente"
            >
              ✕
            </button>
          </div>

          {/* MENSAGENS */}
          <div className="flex-1 p-3.5 overflow-y-auto space-y-2.5 text-xs bg-slate-50">
            {aiMessages.map((m, idx) => (
              <div key={idx} className={`p-2.5 rounded-xl ${m.sender === 'user' ? 'bg-[#1e7a8c] text-white ml-8 rounded-br-none shadow-sm' : 'bg-white border border-slate-200 text-slate-800 mr-8 rounded-bl-none shadow-sm'}`}>
                <b className={`text-[10px] block mb-1 ${m.sender === 'user' ? 'text-teal-100' : 'text-slate-500'}`}>
                  {m.sender === 'user' ? 'Você' : 'Assistente IA'}
                </b>
                <p className="whitespace-pre-line leading-relaxed">{m.text}</p>
              </div>
            ))}
            {aiLoading && (
              <div className="p-2.5 rounded-xl bg-white border border-slate-200 text-slate-500 text-xs italic">
                O assistente está calculando o plano matemático 3D...
              </div>
            )}
          </div>

          {/* SUGESTÕES RÁPIDAS */}
          <div className="px-3 py-1.5 bg-white border-t border-slate-100 flex gap-1.5 overflow-x-auto text-[10px]">
            <button 
              onClick={() => setAiPrompt("Quantas caixas padrão cabem no baú do Truck?")}
              className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 rounded-full whitespace-nowrap cursor-pointer"
            >
              📦 Carga no Truck
            </button>
            <button 
              onClick={() => setAiPrompt("Simular carga no Toco Urbano")}
              className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 rounded-full whitespace-nowrap cursor-pointer"
            >
              🚚 Toco Urbano
            </button>
          </div>

          {/* INPUT FORM */}
          <form onSubmit={handleSendAiMessage} className="p-2.5 bg-white border-t border-slate-200 flex gap-1.5">
            <input 
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="Digite sua dúvida ou comando..."
              className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#1e7a8c]"
            />
            <button 
              type="submit" 
              disabled={aiLoading}
              className="bg-[#1e7a8c] hover:bg-[#176270] disabled:bg-slate-300 text-white font-bold text-xs px-3 py-2 rounded-lg transition-colors cursor-pointer"
            >
              Enviar
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
