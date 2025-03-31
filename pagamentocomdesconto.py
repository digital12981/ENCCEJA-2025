import os
import requests
from datetime import datetime
from flask import current_app
from typing import Dict, Any, Optional, Tuple

class PagamentoComDescontoAPI:
    API_URL = "https://app.for4payments.com.br/api/v1"

    def __init__(self, secret_key: str):
        """
        Inicializa a API de pagamento com desconto
        """
        self.secret_key = secret_key

    def _get_headers(self) -> Dict[str, str]:
        """Retorna os headers para autenticação na API"""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def _generate_random_email(self, name: str) -> str:
        """Gera um email aleatório baseado no nome do cliente"""
        sanitized_name = name.lower().replace(" ", "").replace(".", "").replace("-", "")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{sanitized_name}{timestamp}@tempmail.com"

    def create_pix_payment_with_discount(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um pagamento PIX com desconto no valor de R$49,70
        """
        # Use API v1 do For4Payments para criar um pagamento PIX
        url = f"{self.API_URL}/charges/pix"
        
        # Email é requerido pela API, gerar um baseado no nome
        email = data.get('email', self._generate_random_email(data.get('nome', '')))
        
        payload = {
            "customer": {
                "name": data.get('nome', ''),
                "email": email,
                "tax_id": data.get('cpf', '').replace(".", "").replace("-", ""),
                "phone_number": data.get('telefone', '').replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            },
            "items": [
                {
                    "name": "Taxa de Inscrição ENCCEJA 2025 com Desconto",
                    "description": "Taxa de inscrição para o ENCCEJA 2025 com desconto promocional",
                    "quantity": 1,
                    "amount": 4970  # R$49,70 em centavos
                }
            ],
            "ip": "127.0.0.1"
        }
        
        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response_data = response.json()
            
            # Adicionar informação de desconto para usar na interface
            response_data['discount_applied'] = True
            response_data['regular_price'] = 7340  # R$73,40 em centavos
            response_data['discount_price'] = 4970  # R$49,70 em centavos
            
            return response_data
        except Exception as e:
            current_app.logger.error(f"Erro ao criar pagamento com desconto: {str(e)}")
            return {"error": str(e)}

    def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Verifica o status de um pagamento na API For4Payments"""
        url = f"{self.API_URL}/charges/{payment_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            return response.json()
        except Exception as e:
            current_app.logger.error(f"Erro ao verificar status do pagamento com desconto: {str(e)}")
            return {"error": str(e)}


def create_payment_with_discount_api(secret_key: Optional[str] = None) -> PagamentoComDescontoAPI:
    """Factory function para criar a instância da API de pagamento com desconto"""
    # Usar a chave do ambiente ou a passada como parâmetro
    api_key = secret_key or os.environ.get("FOR4PAYMENTS_SECRET_KEY", "")
    return PagamentoComDescontoAPI(api_key)