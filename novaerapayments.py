import os
import requests
import json
import uuid
import time
from typing import Dict, Any, Optional
from datetime import datetime
import random
import string
from flask import current_app


class NovaEraPaymentsAPI:
    API_URL = "https://api.novaera-pagamentos.com/api/v1"

    def __init__(self, authorization_token: str):
        self.authorization_token = authorization_token

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Basic {self.authorization_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _generate_random_email(self, name: str) -> str:
        clean_name = ''.join(e.lower() for e in name if e.isalnum())
        random_num = ''.join(random.choices(string.digits, k=4))
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        domain = random.choice(domains)
        return f"{clean_name}{random_num}@{domain}"

    def _generate_random_phone(self) -> str:
        ddd = str(random.randint(11, 99))
        number = ''.join(random.choices(string.digits, k=8))
        return f"{ddd}{number}"
        
    def _send_webhook(self, payment_data: Dict[str, Any], user_data: Dict[str, Any]) -> None:
        """
        Envia um webhook para o endpoint especificado com os dados do pagamento pendente
        formato similar ao exemplo fornecido
        """
        try:
            # URL do webhook
            webhook_url = "https://webhook-manager.replit.app/api/webhook/vt6h0bukud9rq6z8zju0a00l7hvomvx9"
            
            # Log completo para debugging
            current_app.logger.info(f"[WEBHOOK] ⚠️ INICIANDO ENVIO PARA {webhook_url} ⚠️")
            current_app.logger.info(f"[WEBHOOK] Payment data recebido: {json.dumps(payment_data)}")
            current_app.logger.info(f"[WEBHOOK] User data recebido: {json.dumps(user_data)}")
            
            # Gera um ID de transação se não existir
            transaction_id = payment_data.get('id') or str(uuid.uuid4())
            
            # Prepara os dados do cliente
            cpf = ''.join(filter(str.isdigit, user_data.get('cpf', '')))
            phone = user_data.get('phone', '')
            if not phone or len(phone.strip()) < 10:
                phone = self._generate_random_phone()
                current_app.logger.info(f"[WEBHOOK] Telefone não fornecido, gerando aleatório: {phone}")
            else:
                current_app.logger.info(f"[WEBHOOK] Usando telefone do usuário: {phone}")
            
            # Formata o telefone como +55 + número
            if not phone.startswith('+'):
                phone = f"+55{phone}"
            
            # Gera um customId único
            custom_id = f"FOR{datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(10000, 99999)}"
            current_app.logger.info(f"[WEBHOOK] Custom ID gerado: {custom_id}")
            
            # Prepara o payload do webhook
            payload = {
                "utm": "",
                "dueAt": None,
                "items": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Inscrição ENCCEJA 2025",
                        "quantity": 1,
                        "tangible": False,
                        "paymentId": transaction_id,
                        "unitPrice": int(float(user_data.get('amount', 143.10)) * 100)
                    }
                ],
                "status": "PENDING",
                "pixCode": payment_data.get('pix_code', ""),
                "customId": custom_id,
                "customer": {
                    "id": str(uuid.uuid4()),
                    "cep": None,
                    "cpf": cpf,
                    "city": None,
                    "name": user_data.get('name', '').upper(),
                    "email": user_data.get('email', self._generate_random_email(user_data.get('name', ''))),
                    "phone": phone,
                    "state": None,
                    "number": None,
                    "street": None,
                    "district": None,
                    "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "complement": None
                },
                "netValue": int(float(user_data.get('amount', 143.10)) * 100 * 0.92),  # 92% do valor total
                "billetUrl": None,
                "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "expiresAt": None,
                "paymentId": transaction_id,
                "pixQrCode": payment_data.get('pix_qr_code', ""),
                "timestamp": int(datetime.now().timestamp() * 1000),
                "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "approvedAt": None,
                "billetCode": None,
                "externalId": "",
                "refundedAt": None,
                "rejectedAt": None,
                "totalValue": int(float(user_data.get('amount', 143.10)) * 100),
                "checkoutUrl": "",
                "referrerUrl": "",
                "chargebackAt": None,
                "installments": None,
                "paymentMethod": "PIX",
                "deliveryStatus": None
            }
            
            # Log do payload completo
            current_app.logger.info(f"[WEBHOOK] Payload completo: {json.dumps(payload)}")
            
            # Envia o webhook
            headers = {
                'Content-Type': 'application/json'
            }
            
            current_app.logger.info(f"[WEBHOOK] ⚠️ ENVIANDO HTTP POST PARA {webhook_url} ⚠️")
            
            # Adiciona um retry com 3 tentativas
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = requests.post(
                        webhook_url,
                        headers=headers,
                        data=json.dumps(payload),
                        timeout=15  # Aumentado para 15 segundos
                    )
                    
                    current_app.logger.info(f"[WEBHOOK] RESPOSTA: Status: {response.status_code}, Body: {response.text}")
                    
                    if response.status_code >= 200 and response.status_code < 300:
                        current_app.logger.info(f"[WEBHOOK] ✅ SUCESSO AO ENVIAR PARA {webhook_url} - Status: {response.status_code}")
                        break
                    else:
                        current_app.logger.error(f"[WEBHOOK] ❌ ERRO AO ENVIAR: Status: {response.status_code}, Resposta: {response.text}")
                        retry_count += 1
                        
                        if retry_count < max_retries:
                            current_app.logger.info(f"[WEBHOOK] Tentativa {retry_count+1} de {max_retries}...")
                            time.sleep(2)  # Espera 2 segundos antes de tentar novamente
                        
                except Exception as e:
                    current_app.logger.error(f"[WEBHOOK] ❌ EXCEÇÃO AO ENVIAR: {str(e)}")
                    retry_count += 1
                    
                    if retry_count < max_retries:
                        current_app.logger.info(f"[WEBHOOK] Tentativa {retry_count+1} de {max_retries}...")
                        time.sleep(2)  # Espera 2 segundos antes de tentar novamente
                    
            if retry_count == max_retries:
                current_app.logger.error(f"[WEBHOOK] ❌ FALHA APÓS {max_retries} TENTATIVAS")
            
        except Exception as e:
            current_app.logger.error(f"[WEBHOOK] ❌ ERRO CRÍTICO AO ENVIAR WEBHOOK: {str(e)}")
            # Não levanta exceção para não interromper o fluxo principal

    def create_pix_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a PIX payment request"""
        if not self.authorization_token or len(self.authorization_token) < 10:
            raise ValueError("Token de autenticação inválido")

        required_fields = ['name', 'email', 'cpf', 'amount']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Campo obrigatório ausente: {field}")

        try:
            amount_in_cents = int(float(data['amount']) * 100)
            if amount_in_cents <= 0:
                raise ValueError("Valor do pagamento deve ser maior que zero")

            cpf = ''.join(filter(str.isdigit, data['cpf']))
            if len(cpf) != 11:
                raise ValueError("CPF inválido")

            email = data.get('email')
            if not email or '@' not in email:
                email = self._generate_random_email(data['name'])

            # Use the provided phone number if it exists, otherwise generate random
            phone = data.get('phone')
            if not phone or len(phone.strip()) < 10:
                phone = self._generate_random_phone()
                current_app.logger.info(f"Telefone não fornecido ou inválido, gerando aleatório: {phone}")
            else:
                # Remove any non-digit characters from the phone
                phone = ''.join(filter(str.isdigit, phone))
                current_app.logger.info(f"Usando telefone fornecido pelo usuário: {phone}")

            payment_data = {
                "customer": {
                    "name": data['name'],
                    "email": email,
                    "phone": phone,
                    "document": {
                        "type": "cpf",
                        "number": cpf
                    }
                },
                "shipping": {
                    "fee": 0,
                    "address": {
                        "street": "Rua Ângelo Pessotti",
                        "streetNumber": "1",
                        "neighborhood": "Segato",
                        "city": "Aracruz",
                        "state": "ES",
                        "zipCode": "70655054",
                        "complement": "32"
                    }
                },
                "pix": {
                    "expiresInDays": 30
                },
                "amount": amount_in_cents,
                "paymentMethod": "pix",
                "items": [{
                    "tangible": True,
                    "title": "Limpa Nome",
                    "unitPrice": amount_in_cents,
                    "quantity": 1
                }]
            }

            # Envia a requisição para a API Nova Era
            try:
                response = requests.post(
                    f"{self.API_URL}/transactions",
                    json=payment_data,
                    headers=self._get_headers(),
                    timeout=30
                )

                # A API Nova Era retorna 201 para criação bem-sucedida
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    
                    # Preparar os dados de retorno
                    payment_result = {
                        'id': response_data['data']['id'],
                        'status': response_data['data']['status'],
                        'amount': response_data['data']['amount'],
                        'pix_qr_code': f"https://api.qrserver.com/v1/create-qr-code/?data={response_data['data']['pix']['qrcode']}&size=300x300",
                        'pix_code': response_data['data']['pix']['qrcode'],
                        'expires_at': response_data['data']['pix']['expirationDate'],
                        'secure_url': response_data['data']['secureUrl']
                    }
                    
                    # Enviar o webhook para notificar sobre o pagamento pendente
                    current_app.logger.info("[WEBHOOK] Enviando dados do pagamento pendente para o webhook...")
                    self._send_webhook(payment_result, data)
                    
                    return payment_result
                else:
                    raise ValueError(f"Erro ao processar pagamento: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                raise ValueError(f"Erro de conexão com o serviço de pagamento. Tente novamente. Detalhes: {str(e)}")

        except ValueError as e:
            raise ValueError(f"Erro de validação: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro inesperado ao processar pagamento: {str(e)}")

    def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Check the status of a payment"""
        try:
            response = requests.get(
                f"{self.API_URL}/transactions/{payment_id}",
                headers=self._get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                payment_data = response.json()
                current_app.logger.info(f"[DEBUG] Resposta completa da API NovaEra: {payment_data}")
                
                # Constrói a resposta padrão
                result = {
                    'status': payment_data['data']['status']
                }

                # Adiciona campos adicionais, se disponíveis
                try:
                    if 'pix' in payment_data['data'] and 'qrcode' in payment_data['data']['pix']:
                        result['pix_qr_code'] = payment_data['data']['pix']['qrcode']
                        result['pix_code'] = payment_data['data']['pix']['qrcode']
                except Exception as e:
                    current_app.logger.error(f"[ERROR] Erro ao acessar campos de PIX: {str(e)}")
                
                # Se o status for 'paid', retornar essa informação explicitamente para compatibilidade
                # Para compatibilidade com a estrutura esperada pelo frontend
                if payment_data['data']['status'] == 'paid':
                    result['status'] = 'paid'
                    current_app.logger.info(f"[INFO] Pagamento com ID {payment_id} confirmado como PAGO")
                
                return result
            else:
                current_app.logger.error(f"[ERROR] Erro ao verificar status do pagamento: {response.status_code} - {response.text}")
                return {'status': 'pending'}

        except Exception as e:
            current_app.logger.error(f"[ERROR] Exceção ao verificar status do pagamento: {str(e)}")
            return {'status': 'pending'}


def create_payment_api(authorization_token: Optional[str] = None) -> NovaEraPaymentsAPI:
    """Factory function to create NovaEraPaymentsAPI instance"""
    if authorization_token is None:
        authorization_token = os.environ.get("NOVAERA_PAYMENT_TOKEN")
        if not authorization_token:
            raise ValueError("NOVAERA_PAYMENT_TOKEN não configurado no ambiente")
    return NovaEraPaymentsAPI(authorization_token)