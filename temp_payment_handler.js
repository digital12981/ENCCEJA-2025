                    .then(data => {
                        console.log("Payment creation response:", data);
                        
                        loadingPopup.style.display = "none";
                        
                        // Iniciar o cronômetro quando o popup de pagamento é mostrado
                        countdownTimer = startCountdown();
                        
                        if (data.error) {
                            alert("Erro ao gerar pagamento: " + data.error);
                            overlay.style.display = "none";
                            return;
                        }
                        
                        // Extract transaction ID from data
                        transactionId = data.id || data.transactionId || data.transaction_id;
                        
                        // Handle PIX QR Code
                        const pixQrCodeElement = document.getElementById('pixQrCode');
                        if (data.pixQrCode) {
                            pixQrCodeElement.src = data.pixQrCode;
                        } else if (data.pix_qr_code) {
                            pixQrCodeElement.src = data.pix_qr_code;
                        }
                        
                        // Handle PIX Code Text
                        const pixCodeElement = document.getElementById('pixCodeText');
                        if (data.pixCode) {
                            pixCodeElement.value = data.pixCode;
                        } else if (data.pix_code) {
                            pixCodeElement.value = data.pix_code;
                        } else if (data.copy_paste) {
                            pixCodeElement.value = data.copy_paste;
                        } else if (data.code) {
                            pixCodeElement.value = data.code;
                        }
                        
                        // Check if we have the necessary data to show the payment popup
                        if ((data.pixQrCode || data.pix_qr_code) && 
                            (data.pixCode || data.pix_code || data.copy_paste || data.code)) {
                            pixPaymentPopup.style.display = "block";
                            startStatusCheck();
                        } else {
                            console.error("Missing QR code or PIX code data:", data);
                            alert("Erro ao processar o pagamento. Por favor, tente novamente.");
                            overlay.style.display = "none";
                        }
                    })
                    .catch(error => {
                        console.error("Error creating payment:", error);
                        loadingPopup.style.display = "none";
                        
                        // Este erro pode ocorrer mesmo quando a transação foi criada com sucesso
                        // Vamos tentar buscar novamente os dados da transação
                        if (transactionId) {
                            setTimeout(() => {
                                // Exibir o popup e iniciar a verificação de status se tivermos um ID
                                pixPaymentPopup.style.display = "block";
                                startStatusCheck();
                            }, 500);
                        } else {
                            alert("Erro ao processar o pagamento. Por favor, tente novamente.");
                            overlay.style.display = "none";
                        }
                    });
