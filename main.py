import uvicorn
import webbrowser
from threading import Timer
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

app = FastAPI(
    title="API Raizes do Nordeste",
    description="Trabalho de Back-End UNINTER - Gerenciamento de Pedidos Multicanal",
    version="1.0.0"
)

# --- OPÇÕES DO TRABALHO ---
class CanalPedido(str, Enum):
    balcao = "balcao"
    delivery = "delivery"
    totem = "totem"

class StatusPedido(str, Enum):
    recebido = "recebido"
    em_preparacao = "em_preparacao"
    pronto = "pronto"
    entregue = "entregue"

# --- SCHEMAS ---
class ItemPedido(BaseModel):
    item_id: int
    quantidade: int = Field(..., gt=0)

class PedidoCriar(BaseModel):
    canal: CanalPedido
    itens: List[ItemPedido]

class PedidoResponse(BaseModel):
    id: int
    canal: CanalPedido
    status: StatusPedido
    total: float
    itens_detalhados: List[dict]

# --- BANCO DE DADOS SIMULADO ---
CARDAPIO = {
    1: {"nome": "Tapioca de Carne de Sol", "preco": 15.00, "estoque": 10},
    2: {"nome": "Cuscuz Completo", "preco": 12.00, "estoque": 5},
    3: {"nome": "Suco de Caju 300ml", "preco": 6.00, "estoque": 20}
}

HISTORICO_PEDIDOS: List[Dict] = []

# --- ENDPOINTS ---
@app.get("/api/v1/pedidos", response_model=List[PedidoResponse])
def listar_pedidos(canal: Optional[CanalPedido] = None):
    """Listar Pedidos"""
    if canal:
        return [p for p in HISTORICO_PEDIDOS if p["canal"] == canal]
    return HISTORICO_PEDIDOS

@app.post("/api/v1/pedidos", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def criar_pedido(pedido: PedidoCriar):
    """Criar Pedido"""
    valor_total = 0.0
    itens_comprados = []
    
    for item in pedido.itens:
        if item.item_id not in CARDAPIO:
            raise HTTPException(status_code=404, detail="Item não encontrado.")
        produto = CARDAPIO[item.item_id]
        if produto["estoque"] < item.quantidade:
            raise HTTPException(status_code=400, detail="Estoque insuficiente.")
            
    for item in pedido.itens:
        produto = CARDAPIO[item.item_id]
        produto["estoque"] -= item.quantidade
        subtotal = produto["preco"] * item.quantidade
        valor_total += subtotal
        itens_comprados.append({
            "item_id": item.item_id,
            "nome": produto["nome"],
            "quantidade": item.quantidade,
            "subtotal": subtotal
        })
    
    novo_pedido = {
        "id": len(HISTORICO_PEDIDOS) + 1,
        "canal": pedido.canal,
        "status": StatusPedido.recebido,
        "total": valor_total,
        "itens_detalhados": itens_comprados
    }
    HISTORICO_PEDIDOS.append(novo_pedido)
    return novo_pedido

# --- FUNÇÃO PARA ABRIR O NAVEGADOR SOZINHO ---
def abrir_navegador():
    webbrowser.open("http://127.0.0")

if __name__ == "__main__":
    # Força a abertura direta no endereço local correto
    Timer(1.5, lambda: webbrowser.open("http://127.0.0")).start()
    uvicorn.run("main:app" if __package__ is None else f"{__package__}.main:app", host="127.0.0.1", port=8000, reload=True)

