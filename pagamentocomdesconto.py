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
        url = f"{self.API_URL}/transaction.purchase"
        
        # Email é requerido pela API, gerar um baseado no nome
        email = data.get('email', self._generate_random_email(data.get('nome', '')))
        
        # Formatar o telefone (remover caracteres especiais)
        phone = data.get('telefone', '')
        phone = ''.join(filter(str.isdigit, phone))
        
        # Formatar o CPF (remover caracteres especiais)
        cpf = data.get('cpf', '').replace(".", "").replace("-", "")
        
        # Valor com desconto: R$49,70 em centavos
        amount_in_cents = 4970
        
        # Payload no formato correto para a API
        payload = {
            "name": data.get('nome', ''),
            "email": email,
            "cpf": cpf,
            "phone": phone,
            "paymentMethod": "PIX",
            "amount": amount_in_cents,
            "items": [{
                "title": "Taxa de Inscrição ENCCEJA 2025 com Desconto",
                "quantity": 1,
                "unitPrice": amount_in_cents,
                "tangible": False
            }]
        }
        
        try:
            current_app.logger.info(f"Chamando API de pagamento PIX com desconto: {url}")
            current_app.logger.info(f"Dados enviados: {payload}")
            
            response = requests.post(url, headers=self._get_headers(), json=payload, timeout=30)
            
            current_app.logger.info(f"Resposta recebida (Status: {response.status_code})")
            
            response_data = response.json()
            
            # Formatar a resposta no formato esperado pelo frontend
            formatted_response = {
                'id': response_data.get('id') or response_data.get('transactionId'),
                'pix_code': response_data.get('pixCode') or response_data.get('pix', {}).get('code'),
                'pix_qr_code': response_data.get('pixQrCode') or response_data.get('pix', {}).get('qrCode'),
                'original_status': response_data.get('status', 'PENDING'),
                'discount_applied': True,
                'regular_price': 7340,  # R$73,40 em centavos
                'discount_price': 4970  # R$49,70 em centavos
            }
            
            current_app.logger.info(f"Resposta formatada: {formatted_response}")
            return formatted_response
        except Exception as e:
            current_app.logger.error(f"Erro ao criar pagamento com desconto: {str(e)}")
            return {"error": str(e)}

    def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Verifica o status de um pagamento na API For4Payments"""
        url = f"{self.API_URL}/transaction.status?id={payment_id}"
        
        try:
            current_app.logger.info(f"Verificando status do pagamento com desconto: {payment_id}")
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            
            current_app.logger.info(f"Resposta recebida (Status: {response.status_code})")
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Formatar a resposta no formato esperado pelo frontend
                formatted_response = {
                    'id': payment_id,
                    'original_status': response_data.get('status', 'PENDING'),
                    'status': response_data.get('status', 'PENDING')
                }
                
                current_app.logger.info(f"Status do pagamento: {formatted_response}")
                return formatted_response
            else:
                current_app.logger.error(f"Erro ao verificar status: {response.status_code} - {response.text}")
                return {"error": f"Erro ao verificar status: {response.status_code}"}
                
        except Exception as e:
            current_app.logger.error(f"Erro ao verificar status do pagamento com desconto: {str(e)}")
            return {"error": str(e)}


def create_payment_with_discount_api(secret_key: Optional[str] = None) -> PagamentoComDescontoAPI:
    """Factory function para criar a instância da API de pagamento com desconto"""
    # Usar a chave do ambiente ou a passada como parâmetro
    api_key = secret_key or os.environ.get("FOR4PAYMENTS_SECRET_KEY", "")
    return PagamentoComDescontoAPI(api_key)