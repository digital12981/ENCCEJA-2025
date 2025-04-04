            // Função para iniciar o cronômetro de 10 minutos
            function startCountdown() {
                let duration = 10 * 60; // 10 minutos em segundos
                const countdownElement = document.getElementById('countdown');
                
                if (!countdownElement) return;
                
                const timer = setInterval(function() {
                    const minutes = Math.floor(duration / 60);
                    let seconds = duration % 60;
                    
                    seconds = seconds < 10 ? "0" + seconds : seconds;
                    
                    countdownElement.textContent = minutes + ":" + seconds;
                    
                    if (--duration < 0) {
                        clearInterval(timer);
                        countdownElement.textContent = "TEMPO ESGOTADO";
                        countdownElement.style.color = "#ffcccc";
                    }
                }, 1000);
                
                return timer;
            }
            
            // Variável para armazenar o intervalo do cronômetro
            let countdownTimer = null;
